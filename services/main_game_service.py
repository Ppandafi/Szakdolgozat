from datetime import datetime
from sqlalchemy import select, func
from database import(
    SessionLocal, Jatekos, JelenlegiKor, SoronVan, JatekosSzerep,
    JatekosErv, ErveltekMar, JatekosJatek, ErtekelesIndoklas, ErtekeltekMar, Jatek
)
import asyncio
from services import email_service

async def get_current_user_context(jatek_id: int, current_user: str):
    #Aktuális felhasználó, kör és szerep lekérése
    async with SessionLocal() as db:
        try:
            stmt_felhasznalo = select(Jatekos).where(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            )
            felhasznalo = (await db.execute(stmt_felhasznalo)).scalars().first()
            if not felhasznalo:
                return None, None, None

            stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == jatek_id)
            aktualis_kor = await db.scalar(stmt_kor)

            stmt_szerep = select(JatekosSzerep.szerep).where(
                JatekosSzerep.jatek_id == jatek_id,
                JatekosSzerep.jatekos_id == felhasznalo.id,
                JatekosSzerep.kor == aktualis_kor
            )
            aktualis_szerep = await db.scalar(stmt_szerep)

            return felhasznalo, aktualis_kor, aktualis_szerep
        except Exception as ex:
            print(f"Hiba a kontextus lekérése során: {ex}")
            return None, None, None

async def save_argument(jatek_id: int, jatekos_id: int, szerep: str, kor: int, erv_szoveg: str):
    #Elmenti a játékos érvét és frissíti az érvelők számát
    async with SessionLocal() as db:
        try:
            uj_erv = JatekosErv(
                jatek_id = jatek_id,
                jatekos_id = jatekos_id,
                szerep = szerep,
                kor = kor,
                erv = erv_szoveg,
                time = datetime.now()
            )
            db.add(uj_erv)

            #Érveltek már frissítése
            stmt_erveltek = select(ErveltekMar).where(
                ErveltekMar.jatek_id == jatek_id,
                ErveltekMar.kor == kor,
            )
            ennyien_erveltek_obj = (await db.execute(stmt_erveltek)).scalars().first()

            if ennyien_erveltek_obj:
                ennyien_erveltek_obj.erveltek += 1
            else:
                db.add(ErveltekMar(jatek_id = jatek_id, kor = kor, erveltek = 1))

            await db.commit()
            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az érv mentése során: {ex}")
            return False

async def get_evaluation_context(jatek_id: int, felhasznalo_id: int, aktualis_kor: int):
    #Lekéri a soron levő játékost és a hozzá tartozó értékelendő érvet
    async with SessionLocal() as db:
        try:
            stmt_soron_levo = select(SoronVan.jatekos_id).where(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == aktualis_kor
            ).order_by(SoronVan.time.desc())
            soron_levo_id = await db.scalar(stmt_soron_levo)

            if not soron_levo_id or soron_levo_id == felhasznalo_id:
                return None, None, None

            stmt_jatekos = select(Jatekos).where(Jatekos.id == soron_levo_id)
            soron_levo_jatekos = (await db.execute(stmt_jatekos)).scalars().first()

            stmt_szerep = select(JatekosSzerep.szerep).where(
                JatekosSzerep.jatek_id == jatek_id,
                JatekosSzerep.kor == aktualis_kor,
                JatekosSzerep.jatekos_id == soron_levo_id
            )
            soron_levo_szerep = await db.scalar(stmt_szerep)

            stmt_erv = select(JatekosErv.erv).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.kor == aktualis_kor,
                JatekosErv.jatekos_id == soron_levo_id
            )
            soron_levo_erv = await db.scalar(stmt_erv)

            return soron_levo_jatekos, soron_levo_szerep, soron_levo_erv
        except Exception as ex:
            print(f"Hiba az értékelendő érv betöltésekor: {ex}")
            return None, None, None

async def save_evaluation(jatek_id: int, ertek: int, ertekelt_id: int, ertekelt_szerep: str, ertekelo_id: int):
    #Kiszámolja és elmenti az érve adott pontszámot
    async with SessionLocal() as db:
        try:
            stmt_jatekosok = select(Jatekos.id).join(
                JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id
            ).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekmester == False,
                Jatekos.active == True,
                Jatekos.id != ertekelt_id
            )
            jatekosok = (await db.execute(stmt_jatekosok)).scalars().all()

            jatekosok_szama = len(jatekosok)

            stmt_erv = select(JatekosErv).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.jatekos_id == ertekelt_id,
                JatekosErv.szerep == ertekelt_szerep
            )
            ertekelt_erv = (await db.execute(stmt_erv)).scalars().first()

            if ertekelt_erv and jatekosok_szama > 0:
                #Értékelés átlagának frissítése
                jelenlegi_atlag = ertekelt_erv.ertekeles_atlag or 0.0
                ertekeles = ertek / jatekosok_szama
                ertekelt_erv.ertekeles_atlag = round(jelenlegi_atlag + ertekeles, 2)

                #Értékeltek már frissítése
                #lekérdezzük, eddig hányan értékelték az adott érvet
                stmt_eddigiek = select(ErtekeltekMar).where(
                    ErtekeltekMar.jatek_id == jatek_id,
                    ErtekeltekMar.erv_szerzo_id == ertekelt_id,
                    ErtekeltekMar.szerep == ertekelt_szerep
                )
                eddigi_ertekelesek = (await db.execute(stmt_eddigiek)).scalars().all()
                eddigiek_szama = len(eddigi_ertekelesek)

                #Új rekord hozzáadása, eddigiek száma + 1-el
                uj_ertekelt_mar = ErtekeltekMar(
                    jatek_id = jatek_id,
                    ertekelo_jatekos_id = ertekelo_id,
                    erv_szerzo_id = ertekelt_id,
                    szerep = ertekelt_szerep,
                    ertekeltek = eddigiek_szama + 1
                )
                db.add(uj_ertekelt_mar)

                #Minden változás mentése egyetlen tranzakcióval
                await db.commit()

                #Kör vége ellenőrzése és játékmester értesítése
                total_players = len(jatekosok) + 1

                stmt_erveltek = select(ErveltekMar.erveltek).where(
                    ErveltekMar.jatek_id == jatek_id,
                    ErveltekMar.kor == ertekelt_erv.kor
                )
                erveltek_szama = await db.scalar(stmt_erveltek) or 0

                mindenki_ertekelt = False

                #Ha mindenki érvelt a körben
                if erveltek_szama == total_players:
                    stmt_ervek = select(JatekosErv).where(
                        JatekosErv.jatek_id == jatek_id,
                        JatekosErv.kor == ertekelt_erv.kor
                    )
                    ervek = (await db.execute(stmt_ervek)).scalars().all()

                    mindenki_ertekelt = True

                    elvart_ertekelesek = total_players - 1
                    for erv in ervek:
                        stmt_ertekelesek = select(func.count(ErtekeltekMar.ertekeltek)).where(
                            ErtekeltekMar.jatek_id == jatek_id,
                            ErtekeltekMar.erv_szerzo_id == erv.jatekos_id,
                            ErtekeltekMar.szerep == erv.szerep
                        )
                        ertekelesek_szama = await db.scalar(stmt_ertekelesek) or 0
                        if ertekelesek_szama < elvart_ertekelesek:
                            mindenki_ertekelt = False
                            break

                    if mindenki_ertekelt:
                        stmt_gm = select(Jatekos.email, Jatek.cim).join(
                            JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id
                        ).join(
                            Jatek, Jatek.id == JatekosJatek.jatek_id
                        ).where(
                            JatekosJatek.jatek_id == jatek_id,
                            JatekosJatek.jatekmester == True
                        )
                        gm_data = (await db.execute(stmt_gm)).first()

                        if gm_data:
                            gm_email, jatek_cim = gm_data
                            asyncio.create_task(email_service.send_round_ended_notification(gm_email, jatek_cim, ertekelt_erv.kor))

                return True

            return False
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az értékelés mentése során: {ex}")
            return False

async def save_reason(jatek_id: int, ertekelo_id: int, ervelo_id: int, ervelo_szerep: str, aktualis_kor: int, indoklas_szoveg: str, ertek: int):
    #Szélsőséges értékelés indoklásának mentése
    async with SessionLocal() as db:
        try:
            indoklas = ErtekelesIndoklas(
                jatek_id = jatek_id,
                ertekelo_jatekos_id = ertekelo_id,
                erv_szerzo_id = ervelo_id,
                kor = aktualis_kor,
                szerep = ervelo_szerep,
                indoklas = indoklas_szoveg,
                ertek = ertek,
                time = datetime.now()
            )
            db.add(indoklas)
            await db.commit()
            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az indoklás mentése során: {ex}")
            return False

async def get_previous_arguments_and_turn_status(jatek_id: int, felhasznalo_id: int, aktualis_szerep: str, aktualis_kor: int):
    async with SessionLocal() as db:
        try:
            #Korábbi érvek lekérése
            stmt_ervek = select(JatekosErv, Jatekos).join(
                Jatekos, JatekosErv.jatekos_id == Jatekos.id
            ).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.szerep == aktualis_szerep,
                JatekosErv.kor < aktualis_kor
            ).order_by(JatekosErv.kor.desc())

            ervek = (await db.execute(stmt_ervek)).all()

            #Soron levő játékos lekérése
            stmt_soron = select(SoronVan.jatekos_id).where(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == aktualis_kor
            ).order_by(SoronVan.time.desc())
            soron_levo_id = await db.scalar(stmt_soron)

            soron_van = (soron_levo_id == felhasznalo_id)

            #Ellenőrizzük, hogy érvelt-e már a soron levő játékos (küldés gomb letiltásához)
            stmt_erv_ellenorzes = select(JatekosErv.erv).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.kor == aktualis_kor,
                JatekosErv.jatekos_id == soron_levo_id
            )
            soron_levo_erv = await db.scalar(stmt_erv_ellenorzes)

            return ervek, soron_van, bool(soron_levo_erv)
        except Exception as ex:
            print(f"Hiba a korábbi érvek betöltése során: {ex}")
            return [], False, True