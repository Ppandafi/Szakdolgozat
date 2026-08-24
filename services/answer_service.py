from sqlalchemy import select
from database import SessionLocal, Jatek, Jatekos, JatekosJatek, Kerdoiv, NulladikKor, JatekosValaszolPre, JatekosValaszolPost
from services.gm_dashboard_service import check_and_notify_for_summary


async def save_proposal(jatek_id: int, javaslat: str, szerep_dij: bool):
    async with SessionLocal() as db:
        try:
            uj_javaslat = NulladikKor(jatek_id=jatek_id, javaslat=javaslat, szerep_dij=szerep_dij)
            db.add(uj_javaslat)
            await db.commit()
            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a javaslat mentése során: {ex}")
            return False

async def get_connected_players(jatek_id: int, current_user: str):
    async with SessionLocal() as db:
        try:
            #Csatlakozott felhasználók lekérése
            stmt_resztvevok = select(Jatekos.felhasznalonev, Jatekos.active).join(
                JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id
            ).where(JatekosJatek.jatek_id == jatek_id)
            resztvevok_raw = (await db.execute(stmt_resztvevok)).all()

            resztvevok = [nev if active else "Törölt felhasználó" for nev, active in resztvevok_raw]

            #Aktuális felhasználó adatainak lekérése
            stmt_aktualis = select(Jatekos.felhasznalonev).where(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            )
            aktualis_nev = (await db.execute(stmt_aktualis)).scalars().first()

            return resztvevok, aktualis_nev
        except Exception as ex:
            print(f"Hiba a csatlakozott játékosok lekérése során: {ex}")
            return [], ""

async def get_questions(jatek_id: int, phase: str):
    async with SessionLocal() as db:
        try:
            if phase == "pre":
                stmt = select(Kerdoiv).where(Kerdoiv.jatek_id == jatek_id, Kerdoiv.jatek_elott_utan == True)
            else:
                stmt = select(Kerdoiv).where(Kerdoiv.jatek_id == jatek_id)
            result = await db.execute(stmt)
            return result.scalars().all()
        except Exception as ex:
            print(f"Hiba a kérdések betöltése során: {ex}")
            return []

async def get_game_status(jatek_id: int):
    async with SessionLocal() as db:
        try:
            stmt = select(Jatek).where(Jatek.id == jatek_id)
            return (await db.execute(stmt)).scalars().first()
        except Exception as ex:
            print(f"Hiba a játék állapotának lekérése során: {ex}")
            return None

async def save_answers(jatek_id: int, current_user: str, phase: str, valasz_dict: dict):
    async with SessionLocal() as db:
        try:
            #Játékos id lekérése
            stmt_felhasznalo = select(Jatekos).where(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            )
            felhasznalo = (await db.execute(stmt_felhasznalo)).scalars().first()
            if not felhasznalo:
                return False

            for kerdes_id, valasz_ertek in valasz_dict.items():
                if phase == "pre":
                    stmt_meglevo = select(JatekosValaszolPre).where(
                        JatekosValaszolPre.jatek_id == jatek_id,
                        JatekosValaszolPre.jatekos_id == felhasznalo.id,
                        JatekosValaszolPre.kerdes_id == kerdes_id
                    )
                    meglevo = (await db.execute(stmt_meglevo)).scalars().first()

                    if meglevo:
                        meglevo.valasz = valasz_ertek
                    else:
                        db.add(JatekosValaszolPre(
                            jatek_id = jatek_id,
                            jatekos_id = felhasznalo.id,
                            kerdes_id = kerdes_id,
                            valasz = valasz_ertek
                        ))

                elif phase == "post":
                    stmt_meglevo = select(JatekosValaszolPost).where(
                        JatekosValaszolPost.jatek_id == jatek_id,
                        JatekosValaszolPost.jatekos_id == felhasznalo.id,
                        JatekosValaszolPost.kerdes_id == kerdes_id
                    )
                    meglevo = (await db.execute(stmt_meglevo)).scalars().first()

                    if meglevo:
                        meglevo.valasz = valasz_ertek
                    else:
                        db.add(JatekosValaszolPost(
                            jatek_id = jatek_id,
                            jatekos_id = felhasznalo.id,
                            kerdes_id = kerdes_id,
                            valasz = valasz_ertek
                        ))
            await db.commit()

            if phase == "post":
                import asyncio
                from services import email_service
                asyncio.create_task(check_and_notify_for_summary(jatek_id))

            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az adatok mentése során: {ex}")
            return False