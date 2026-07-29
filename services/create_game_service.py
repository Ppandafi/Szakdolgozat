from sqlalchemy import select, delete
from database import SessionLocal, Jatek, Jatekos, JatekosJatek, Kerdoiv, Szerep, Dijak, NulladikKor, JelenlegiKor

async def get_game_by_id(jatek_id: int):
    async with SessionLocal() as db:
        result = await db.execute(select(Jatek).where(Jatek.id == jatek_id))
        return result.scalars().first()

async def get_user_by_identifier(email_vagy_nev: str):
    async with SessionLocal() as db:
        stmt = select(Jatekos).where(
            (Jatekos.email == email_vagy_nev) |
            (Jatekos.felhasznalonev == email_vagy_nev)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

async def delete_game(jatek_id: int):
    async with SessionLocal() as db:
        try:
            #noinspection DuplicatedCode
            await db.execute(delete(NulladikKor).where(NulladikKor.jatek_id == jatek_id))
            await db.execute(delete(JelenlegiKor).where(JelenlegiKor.jatek_id == jatek_id))
            await db.execute(delete(JatekosJatek).where(JatekosJatek.jatek_id == jatek_id))
            # noinspection DuplicatedCode
            await db.execute(delete(Szerep).where(Szerep.jatek_id == jatek_id))
            await db.execute(delete(Dijak).where(Dijak.jatek_id == jatek_id))
            await db.execute(delete(Kerdoiv).where(Kerdoiv.jatek_id == jatek_id))
            await db.execute(delete(Jatek).where(Jatek.id == jatek_id))
            await db.commit()
            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a törlés közben: {ex}")

async def get_connected_players(jatek_id: int):
    async with SessionLocal() as db:
        stmt = select(Jatekos.felhasznalonev).join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id).where(JatekosJatek.jatek_id == jatek_id)
        result = await db.execute(stmt)
        return result.scalars().all()

async def get_suggestions(jatek_id: int):
    async with SessionLocal() as db:
        stmt = select(NulladikKor).where(NulladikKor.jatek_id == jatek_id)
        result = await db.execute(stmt)
        return result.scalars().all()

async def get_roles(jatek_id: int):
    async with SessionLocal() as db:
        stmt = select(Szerep.szerepkor).where(Szerep.jatek_id == jatek_id)
        result = await db.execute(stmt)
        return result.scalars().all()

async def get_awards(jatek_id: int):
    async with SessionLocal() as db:
        stmt = select(Dijak.dij).where(Dijak.jatek_id == jatek_id)
        result = await db.execute(stmt)
        return result.scalars().all()

async def get_questions(jatek_id: int):
    async with SessionLocal() as db:
        stmt = select(Kerdoiv.kerdes, Kerdoiv.jatek_elott_utan).where(Kerdoiv.jatek_id == jatek_id)
        result = await db.execute(stmt)
        return result.all()

async def update_game_title(jatek_id: int, uj_cim: str):
    async with SessionLocal() as db:
        try:
            jatek = (await db.execute(select(Jatek).where(Jatek.id == jatek_id))).scalars().first()
            if jatek:
                jatek.cim = uj_cim
                await db.commit()
                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a játék címének mentése során: {ex}")
        return False

async def update_description(jatek_id: int, uj_leiras: str):
    async with SessionLocal() as db:
        try:
            jatek = (await db.execute(select(Jatek).where(Jatek.id == jatek_id))).scalars().first()
            if jatek:
                jatek.ismertetes = uj_leiras
                await db.commit()
                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba az ismertetés mentésekor: {ex}")
        return False

async def add_roles(jatek_id: int, roles_list: list):
    async with SessionLocal() as db:
        try:
            letezo_szerepek_query = await db.execute(select(Szerep.szerepkor).where(Szerep.jatek_id == jatek_id))
            letezo_szerepek = letezo_szerepek_query.scalars().all()

            hozzaadott = 0
            for uj_szerep_nev in roles_list:
                if uj_szerep_nev not in letezo_szerepek:
                    uj_szerep = Szerep(
                        jatek_id = jatek_id,
                        szerepkor = uj_szerep_nev
                    )
                    db.add(uj_szerep)
                    hozzaadott += 1
            await db.commit()
            return hozzaadott
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a szerepek mentése során: {ex}")
            return -1

async def add_awards(jatek_id: int, award_list: list):
    async with SessionLocal() as db:
        try:
            letezo_dijak_query = await db.execute(select(Dijak.dij).where(Dijak.jatek_id == jatek_id))
            letezo_dijak = letezo_dijak_query.scalars().all()

            hozzaadott = 0
            for uj_dij_nev in award_list:
                if uj_dij_nev not in letezo_dijak:
                    uj_dij = Dijak(
                        jatek_id = jatek_id,
                        dij = uj_dij_nev
                    )
                    db.add(uj_dij)
                    hozzaadott += 1
            await db.commit()
            return hozzaadott
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a díjak mentése közben: {ex}")
            return -1

async def add_questions(jatek_id: int, question: str, is_both: bool):
    async with SessionLocal() as db:
        try:
            uj_kerdes = Kerdoiv(
            jatek_id = jatek_id,
            kerdes = question,
            jatek_elott_utan = is_both
            )
            db.add(uj_kerdes)
            await db.commit()
            return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a kérdés mentése során: {ex}")
            return False

async def update_round_limits(jatek_id: int, value: int, limit_type: str):
    async with SessionLocal() as db:
        try:
            jatek = (await db.execute(select(Jatek).where(Jatek.id == jatek_id))).scalars().first()
            if jatek:
                if limit_type == "min":
                    jatek.min_kor = value
                elif limit_type == "max":
                    jatek.max_kor = value
                await db.commit()
                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a minimum- és maximum kör mentése során: {ex}")
        return False

async def set_questios_sent(jatek_id: int):
    async with SessionLocal() as db:
        try:
            jatek = (await db.execute(select(Jatek).where(Jatek.id == jatek_id))).scalars().first()
            if jatek:
                jatek.kerdoivek_kikuldve = True
                await db.commit()
                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a játék állapotának frissítése folyamán: {ex}")
        return False

async def increment_round(jatek_id: int):
    async with SessionLocal() as db:
        try:
            aktualis_kor = (await db.execute(select(JelenlegiKor).where(JelenlegiKor.jatek_id == jatek_id))).scalars().first()
            if aktualis_kor:
                aktualis_kor = aktualis_kor.kor + 1
                await db.commit()
                return True
        except Exception as ex:
            await db.rollback()
            print(f"Hiba a kör léptetése során: {ex}")
        return False