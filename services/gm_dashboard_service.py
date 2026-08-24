from sqlalchemy import select, func, desc
from sqlalchemy.orm import aliased
from database import (
    SessionLocal, Jatek, Jatekos, JatekosJatek, JatekosSzerep, JelenlegiKor, JatekosErv, ErtekeltekMar, ErveltekMar,
    SoronVan, ErvRendszer, ErtekelesIndoklas, Szerep, SzavaztakMar, DijSzavazas, DijatKapott
)
import random
from datetime import datetime
import asyncio
from services import email_service

#Cache változó, hogy elég legyen csak egyszer lekérni a csatlakozott játékosok számát
jatekosok_szama_cache = {}

#Játék lekérdezése
async def get_game_by_id(jatek_id: int):
    async with SessionLocal() as db:
        result =  await db.execute(select(Jatek).where(Jatek.id == jatek_id))
        return result.scalars().first()

#Jelenlegi és max kör lekérdezése
async def get_rounds(jatek_id: int):
    async with SessionLocal() as db:
        stmt = (
            select(JelenlegiKor.kor, Jatek.max_kor)
            .join(Jatek, JelenlegiKor.jatek_id == jatek_id)
            .where(Jatek.id == jatek_id)
        )
        result = await db.execute(stmt)
        return result.first()


#Játékmester adatainak lekérdezése
async def get_user(email_vagy_nev: str):
    async with SessionLocal() as db:
        stmt = select(Jatekos).where(
            (Jatekos.email == email_vagy_nev) |
            (Jatekos.felhasznalonev == email_vagy_nev)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

#Csatlakozott játékosok és szerepeinek lekérése
async def get_joined_players(jatek_id: int):
    async with SessionLocal() as db:
        #Jelenlegi kör lekérése
        stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == jatek_id)
        aktualis_kor = await db.scalar(stmt_kor)

        #Soron levő játékos lekérése
        stmt_soron_van = select(SoronVan.jatekos_id).where(
            (SoronVan.jatek_id == jatek_id) &
            (SoronVan.kor == aktualis_kor)
        ).order_by(SoronVan.time.desc())
        soron_levo_id = await db.scalar(stmt_soron_van)

        #Játékosok és szerepeik lekérése
        stmt = (
            select(
                Jatekos.felhasznalonev,
                JatekosSzerep.szerep,
                (Jatekos.id == soron_levo_id).label("soron_van") #Dinamikus logikai oszlop
            )
            .join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id)
            .outerjoin(
                JatekosSzerep,
                (Jatekos.id == JatekosSzerep.jatekos_id) &
                (JatekosSzerep.jatek_id == jatek_id) &
                (JatekosSzerep.kor == aktualis_kor)
            )
            .where(
                (JatekosJatek.jatek_id == jatek_id) &
                (JatekosJatek.jatekmester == False) &
                (Jatekos.active == True)
            )
        )

        result = await db.execute(stmt)
        resztvevok = result.all()

        #Játékosok száma mentése a cache-be
        jatekosok_szama_cache[jatek_id] = len(resztvevok)

        return resztvevok

#Összes érv lekérése
async def get_all_arguments(jatek_id: int):
    async with SessionLocal() as db:
        stmt =(
            select(JatekosErv, Jatekos)
            .join(Jatekos, JatekosErv.jatekos_id == Jatekos.id)
            .where(JatekosErv.jatek_id == jatek_id)
            .order_by(JatekosErv.time.desc())
        )
        result = await db.execute(stmt)
        return result.all()

#Érveltek már lekérdezése
async def get_erveltek_mar(jatek_id: int, kor:int):
    async with SessionLocal() as db:
        try:
            stmt = select(ErveltekMar.erveltek).where(
                ErveltekMar.jatek_id == jatek_id,
                ErveltekMar.kor == kor
            )
            result = await db.execute(stmt)
            erveltek_mar = result.scalar_one_or_none()

            return erveltek_mar if erveltek_mar is not None else 0
        except Exception as ex:
            print(f"Hiba a már érvelt játékosok lekérése során: {ex}")
            return 0

#Értékeltek már lekérdezése
async def get_ertekeltek_mar(jatek_id: int, erv_szerzo_id: int, szerep: str):
    async with SessionLocal() as db:
        try:
            stmt = select(func.max(ErtekeltekMar.ertekeltek)).where(
                ErtekeltekMar.jatek_id == jatek_id,
                ErtekeltekMar.erv_szerzo_id == erv_szerzo_id,
                ErtekeltekMar.szerep == szerep
            )
            result = await db.execute(stmt)
            mar_ertekeltek = result.scalar_one_or_none()

            return mar_ertekeltek if mar_ertekeltek is not None else 0
        except Exception as ex:
            print(f"Hiba a már értékeltek számának lekérésekor: {ex}")
            return 0

#Soron levő játékos lekérése
async def get_soron_levo(jatek_id: int):
    async with SessionLocal() as db:
        #Jelenlegi kör lekérése
        stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == jatek_id)
        aktualis_kor = await db.scalar(stmt_kor)

        if not aktualis_kor: return None

        #Soron levő játékos lekérése
        stmt_soron_van = select(SoronVan.jatekos_id).where(
            (SoronVan.jatek_id == jatek_id) &
            (SoronVan.kor == aktualis_kor)
        ).order_by(SoronVan.time.desc())
        soron_levo_id = await db.scalar(stmt_soron_van)

        if not soron_levo_id: return None, None

        #Érvelő szerepének lekérése
        stmt_szerep = select(JatekosSzerep.szerep).where(
            (JatekosSzerep.jatek_id == jatek_id) &
            (JatekosSzerep.jatekos_id == soron_levo_id) &
            (JatekosSzerep.kor == aktualis_kor)
        )
        szerep = await db.scalar(stmt_szerep)

        return soron_levo_id, szerep

#Szélsőséges értékelés és indoklása lekérése
async def get_extreme_evaluations(jatek_id: int):
    async with SessionLocal() as db:
        try:
            Ertekelo = aliased(Jatekos)
            Szerzo = aliased(Jatekos)

            stmt = (
                select(
                    Szerzo.felhasznalonev.label("ertekelt_jatekos_nev"),
                    ErtekelesIndoklas.szerep.label("ertekelt_jatekos_szerep"),
                    Ertekelo.felhasznalonev.label("ertekelo_nev"),
                    ErtekelesIndoklas.ertek.label("ertekeles_erteke"),
                    ErtekelesIndoklas.indoklas,
                    ErtekelesIndoklas.kor.label("kor"),
                    ErtekelesIndoklas.time.label("time")
                )
                .join(Szerzo, ErtekelesIndoklas.erv_szerzo_id == Szerzo.id)
                .join(Ertekelo, ErtekelesIndoklas.ertekelo_jatekos_id == Ertekelo.id)
                .where(ErtekelesIndoklas.jatek_id == jatek_id)
            )

            result = await db.execute(stmt)
            return result.all()

        except Exception as ex:
            print(f"Hiba az értékelés indoklások lekérése során: {ex}")
            return []

#Következő érvelő kiválasztása
async def set_next_player(jatek_id: int):
    async with SessionLocal() as db:
        try:
            #aktuális kör lekérése
            stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == jatek_id)
            aktualis_kor = await db.scalar(stmt_kor)

            if not aktualis_kor: return False, "Nincs aktív kör"

            #összes (nem játékmester) játékos lekérése
            stmt_jatekosok = select(JatekosJatek.jatekos_id).join(
                Jatekos, Jatekos.id == JatekosJatek.jatekos_id
            ).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekmester == False,
                Jatekos.active == True
            )
            osszes_jatekos_id = (await db.execute(stmt_jatekosok)).scalars().all()

            #azon játékosok lekérdezése, akik voltak már soron
            stmt_volt_mar = select(SoronVan.jatekos_id).where(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == aktualis_kor
            )
            voltak_mar_id = (await db.execute(stmt_volt_mar)).scalars().all()

            #még nem volt soron levők kiszűrése
            elerheto_jatekosok = [j_id for j_id in osszes_jatekos_id if j_id not in voltak_mar_id]
            if not elerheto_jatekosok:
                return False, "Mindenki volt már ebben a körben"

            kovetkezo_jatekos_id = random.choice(elerheto_jatekosok)

            #új soron levő mentése
            uj_soron_van = SoronVan(
                jatek_id = jatek_id,
                jatekos_id = kovetkezo_jatekos_id,
                kor = aktualis_kor,
                soron_van = True,
                time = datetime.now(),
            )
            db.add(uj_soron_van)
            await db.commit()

            stmt_email = select(Jatekos.email).where(Jatekos.id == kovetkezo_jatekos_id)
            jatekos_email = await db.scalar(stmt_email)
            stmt_jatek = select(Jatek.cim).where(Jatek.id == jatek_id)
            jatek_cim = await db.scalar(stmt_jatek)

            if jatekos_email and jatek_cim:
                asyncio.create_task(email_service.send_turn_notification(jatekos_email, jatek_cim))

            return True, "Új játékos sikeresen kiválasztva"

        except Exception as ex:
            await db.rollback()
            print(f"Hiba a következő érvelő kiválasztása során: {ex}")
            return False, "Adatbázis hiba"

#Játék lezárását ellenőrző függvény
async def check_ready_to_end(jatek_id: int):
    async with SessionLocal() as db:
        try:
            #jelenlegi- és max kör lekérése
            kor_adatok = await get_rounds(jatek_id)
            if not kor_adatok:
                return False
            else:
                jelenlegi_kor, max_kor = kor_adatok

            if not max_kor or jelenlegi_kor != max_kor:
                return False

            #játékosok számának lekérése
            stmt_jatekosok = select(func.count()).select_from(JatekosJatek).join(
                Jatekos, Jatekos.id == JatekosJatek.jatekos_id
            ).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekmester == False,
                Jatekos.active == True
            )
            jatekosok_szama = await db.scalar(stmt_jatekosok)

            if jatekosok_szama == 0:
                return False

            #Ellenőrzés: mindenki érvelt-e az aktuális körben?
            stmt_erveltek = select(ErveltekMar.erveltek).where(
                ErveltekMar.jatek_id == jatek_id,
                ErveltekMar.kor == jelenlegi_kor
            )
            erveltek_szama = await db.scalar(stmt_erveltek) or 0

            if erveltek_szama < jatekosok_szama:
                return False

            #Ellenőrzés: mindenki értékelt mindenkit?
            stmt_ervek = select(JatekosErv).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.kor == jelenlegi_kor
            )
            ervek = (await db.execute(stmt_ervek)).scalars().all()

            elvart_ertekelesek = jatekosok_szama - 1
            for erv in ervek:
                stmt_ertekelesek = select(func.max(ErtekeltekMar.ertekeltek)).where(
                    ErtekeltekMar.jatek_id == jatek_id,
                    ErtekeltekMar.erv_szerzo_id == erv.jatekos_id,
                    ErtekeltekMar.szerep == erv.szerep
                )
                ertekelesek_szama = await db.scalar(stmt_ertekelesek) or 0
                if ertekelesek_szama < elvart_ertekelesek:
                    return False

            #Ha eddig eljutott, akkor minden feltétel teljesült
            return True
        except Exception as ex:
            print(f"Hiba a lezárási feltételek ellenőrzése folyamán: {ex}")
            return False

#Játék lezárása
async def set_game_ended(jatek_id: int):
    async with SessionLocal() as db:
        try:
            jatek = (await db.execute(select(Jatek).where(Jatek.id == jatek_id))).scalars().first()
            if jatek:
                jatek.jatek_lezarva = True
                await db.commit()

                #Játékosok értesítése a játék lezárásáról
                stmt_emails = select(Jatekos.email).join(
                    JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id
                ).where(
                    JatekosJatek.jatek_id == jatek_id,
                    JatekosJatek.jatekmester == False,
                    Jatekos.active == True
                )
                emails = (await db.execute(stmt_emails)).scalars().all()

                if emails:
                    asyncio.create_task(email_service.send_game_ended_notification(emails, jatek.cim))

                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a játék lezárása során: {ex}")
            return False

async def start_next_round(jatek_id: int):
    async with SessionLocal() as db:
        try:
            #Jelenlegi kör lekérése és léptetése
            stmt_kor = select(JelenlegiKor).where(JelenlegiKor.jatek_id == jatek_id)
            jelenlegi_kor_obj = (await db.execute(stmt_kor)).scalars().first()

            if not jelenlegi_kor_obj:
                return False, "Nem található a játékhoz tartozó kör adat"

            uj_kor = jelenlegi_kor_obj.kor + 1
            jelenlegi_kor_obj.kor = uj_kor

            #Összes elérhető szerep lekérése
            stmt_szerepek = select(Szerep.szerepkor).where(Szerep.jatek_id == jatek_id)
            osszes_szerep = (await db.execute(stmt_szerepek)).scalars().all()

            #Játékosok lekérése
            stmt_jatekosok = select(JatekosJatek.jatekos_id).join(
                Jatekos, Jatekos.id == JatekosJatek.jatekos_id
            ).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekmester == False,
                Jatekos.active == True
            )
            jatekosok = (await db.execute(stmt_jatekosok)).scalars().all()

            if not jatekosok:
                return False, "Nincsenek csatlakozott játékosok"

            kiosztott_szerepek_ebben_a_korben = []

            #Eddig még be nem töltött szerepek kiosztása
            for jatekos_id in jatekosok:
                #lekérjük a játékos eddigi szerepeit
                stmt_korabbi = select(JatekosSzerep.szerep).where(
                    JatekosSzerep.jatek_id == jatek_id,
                    JatekosSzerep.jatekos_id == jatekos_id
                )
                korabbi_szerepek = (await db.execute(stmt_korabbi)).scalars().all()

                #elérhető szerepek szűrése
                elerheto_szerepek = [
                    sz for sz in osszes_szerep
                    if sz not in korabbi_szerepek and sz not in kiosztott_szerepek_ebben_a_korben
                ]

                safety_net_aktivalva = 0 #flag, hogy az esetleges szereposztás-duplikációt melyik safety net okozta

                #Safety net: Ha elfogytak az egyedi szerepek (mert pl. több jáékos van mint szerep),
                #Akkor kaphat olyat, amit más már megkapott a jelenlegi körben, de ő még a játékban nem
                if not elerheto_szerepek:
                    elerheto_szerepek = [sz for sz in osszes_szerep if sz not in korabbi_szerepek]
                    safety_net_aktivalva = 1
                    #Safety net2: Ha már minden létező szerepet betöltött a korábbi körökben
                    if not elerheto_szerepek:
                        elerheto_szerepek = osszes_szerep
                        safety_net_aktivalva = 2

                uj_szerep = random.choice(elerheto_szerepek)

                if safety_net_aktivalva == 1:
                    print(f"Safety net1: {jatekos_id} ID-jű játékos kapta a(z) {uj_szerep} szerepet (Körön belüli duplikáció)")
                elif safety_net_aktivalva == 2:
                    print(f"Safety net2: {jatekos_id} ID-jű játékos kapta a(z) {uj_szerep} szerepet (Korábban már betöltött szerep ismétlése")

                #Elmentjük az adott körben kiosztott összes szerepet, hogy mindenki más szerepet kapjon
                kiosztott_szerepek_ebben_a_korben.append(uj_szerep)

                db.add(JatekosSzerep(
                    jatek_id = jatek_id,
                    jatekos_id = jatekos_id,
                    kor=uj_kor,
                    szerep=uj_szerep,
                ))

            await db.commit()
            return True, "Következő kör sikeresen indítva"


        except Exception as ex:
            await db.rollback()
            print(f"Hiba a kör léptetése során: {ex}")
            return False, "Hiba az adatbázis kapcsolat során"

#Soron voltak számláló
async def get_soron_voltak_szama(jatek_id: int, kor: int):
    async with SessionLocal() as db:
        try:
            stmt = select(func.count(SoronVan.jatekos_id)).where(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == kor
            )
            result = await db.execute(stmt)
            soron_voltak = result.scalar_one_or_none()

            return soron_voltak if soron_voltak is not None else 0
        except Exception as ex:
            print(f"Hiba a soron voltak lekérése során: {ex}")
            return 0

#Szavaztak már számláló
async def get_szavaztak_mar(jatek_id: int):
    async with SessionLocal() as db:
        try:
            stmt_szavaztak = select(func.count(SzavaztakMar.jatekos_id)).where(
                SzavaztakMar.jatek_id == jatek_id
            )
            result = await db.execute(stmt_szavaztak)
            szavaztak = result.scalar_one_or_none()

            return szavaztak if szavaztak is not None else 0

        except Exception as ex:
            print(f"Hiba a szavazók lekérése során: {ex}")
            return 0

#Játék tényleges lezárása -> díj szavazatok összesítése és érvrendszer összeállítása
async def finalize_game_results(jatek_id: int):
    async with SessionLocal() as db:
        try:
            #játék státuszának átállítása lezárt-ra
            stmt_jatek = select(Jatek).where(Jatek.id == jatek_id)
            jatek_obj = (await db.execute(stmt_jatek)).scalars().first()

            if jatek_obj:
                jatek_obj.jatek_lezarva = True
                jatek_obj.eredmenyek_osszesitve = True
                jatek_cim = jatek_obj.cim
            else:
                jatek_cim = "Imseretlen játék"

            #1. érvrendszer kialakítása (5.0 átlagnál jobbra értékelt érvek összegyűjtése)
            stmt_ervek = select(JatekosErv).where(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.ertekeles_atlag >= 5.0
            )
            jo_ervek = (await db.execute(stmt_ervek)).scalars().all()

            hozzaadott_ervek = 0
            for erv in jo_ervek:
                #duplikáció ellenőrzése
                stmt_check = select(ErvRendszer).where(
                    ErvRendszer.jatek_id == jatek_id,
                    ErvRendszer.erv == erv.erv
                )
                exists = (await db.execute(stmt_check)).scalars().first()

                if not exists:
                    uj_erv = ErvRendszer(
                        jatek_id = jatek_id,
                        jatek_cim = jatek_cim,
                        erv = erv.erv,
                        erv_atlag = erv.ertekeles_atlag
                    )
                    db.add(uj_erv)
                    hozzaadott_ervek += 1

            stmt_dijak = select(DijSzavazas.jatek_dij).where(
                DijSzavazas.jatek_id == jatek_id,
            ).distinct()
            dijak = (await db.execute(stmt_dijak)).scalars().all()

            kiosztott_dijak = []
            for dij in dijak:
                stmt_max = select(DijSzavazas).where(
                    DijSzavazas.jatek_id == jatek_id,
                    DijSzavazas.jatek_dij == dij
                ).order_by(desc(DijSzavazas.kapott_szavazatok)).limit(1)

                nyertes = (await db.execute(stmt_max)).scalars().first()

                if nyertes and nyertes.kapott_szavazatok > 0:
                    stmt_check_dij = select(DijatKapott).where(
                        DijatKapott.jatek_id == jatek_id,
                        DijatKapott.dij == dij
                    )
                    exists_dij = (await db.execute(stmt_check_dij)).scalars().first()

                    if not exists_dij:
                        db.add(DijatKapott(
                            jatek_id = jatek_id,
                            jatekos_id = nyertes.jatekos_id,
                            dij = dij
                        ))

                    #játékos nevének lekérése a UI visszajelzéshez
                    stmt_nev = select(Jatekos.felhasznalonev).where(Jatekos.id == nyertes.jatekos_id)
                    nyertes_nev = await db.scalar(stmt_nev)

                    kiosztott_dijak.append(f"{dij}: {nyertes_nev} ({nyertes.kapott_szavazatok} szavazat)")

            await db.commit()
            return True, hozzaadott_ervek, kiosztott_dijak
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az eredmények összesítése során: {ex}")
            return False, 0, []