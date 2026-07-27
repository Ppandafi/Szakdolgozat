import random
import string
from sqlalchemy import select, func
from database import SessionLocal, Jatek, Jatekos, JelenlegiKor, NulladikKor, JatekosJatek, JatekosErv

async def get_user(current_user: str):
    async with SessionLocal() as db:
        #A felhasználó adatainak lekérése
        stmt = select(Jatekos).where(
            (Jatekos.email == current_user) |
            (Jatekos.felhasznalonev == current_user)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

async def create_new_game(jatekos_id: int):
    async with SessionLocal() as db:
        #Új játék ID meghatározása
        stmt = select(func.max(Jatek.id))
        max_id = await db.scalar(stmt)
        uj_id = (max_id or 0) + 1

        #Egyedi szobakód generálása
        while True:
            betuk = ''.join(random.choices(string.ascii_uppercase, k = 4))
            szamok = ''.join(random.choices(string.digits, k = 4))
            uj_szobakod = f"{betuk}-{szamok}"

            #Ellenőrzés
            stmt_check = select(Jatek).where(Jatek.lobby_code == uj_szobakod)
            letezo = (await db.execute(stmt_check)).scalars().first()
            if not letezo:
                break

        #Új adatok példányosítása
        uj_jatek = Jatek(id = uj_id, cim = "Új játék(szerkesztés alatt)", lobby_code = uj_szobakod)
        uj_jelenlegi_kor = JelenlegiKor(jatek_id = uj_id, kor = 0)
        uj_nulladik_kor = NulladikKor(jatek_id = uj_id)
        uj_jatekmester = JatekosJatek(jatek_id = uj_id, jatekos_id = jatekos_id, jatekmester = True)

        #Adatok mentése
        db.add_all([uj_jatek, uj_jelenlegi_kor, uj_nulladik_kor, uj_jatekmester])
        await db.commit()
        return uj_id

#Érvek lekérése
async def get_user_arguments(jatekos_id: int):
    async with SessionLocal() as db:
        stmt = select(JatekosErv, Jatek).join(Jatek, JatekosErv.jatek_id == Jatek.id).where(JatekosErv.jatekos_id == jatekos_id)
        result = await db.execute(stmt)
        return result.all() #(JatekosErv, Jatek) tuple-ök listát ad vissza