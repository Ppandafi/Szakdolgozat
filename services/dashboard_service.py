import random
import string
from sqlalchemy import select, func
from database import SessionLocal, Jatek, Jatekos, JelenlegiKor, NulladikKor, JatekosJatek, JatekosErv, DijatKapott

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
        #uj_nulladik_kor = NulladikKor(jatek_id = uj_id)
        uj_jatekmester = JatekosJatek(jatek_id = uj_id, jatekos_id = jatekos_id, jatekmester = True)

        #Adatok mentése
        db.add_all([uj_jatek, uj_jelenlegi_kor, uj_jatekmester])
        await db.commit()
        return uj_id

#Érvek lekérése
async def get_user_arguments(jatekos_id: int):
    async with SessionLocal() as db:
        stmt = select(JatekosErv, Jatek).join(Jatek, JatekosErv.jatek_id == Jatek.id).where(JatekosErv.jatekos_id == jatekos_id)
        result = await db.execute(stmt)
        return result.all() #(JatekosErv, Jatek) tuple-ök listát ad vissza

async def get_user_games(jatekos_id: int):
    async with SessionLocal() as db:
        stmt = select(Jatek, JelenlegiKor.kor, JatekosJatek.jatekmester)\
        .join(JatekosJatek, Jatek.id == JatekosJatek.jatek_id)\
        .join(JelenlegiKor, Jatek.id == JelenlegiKor.jatek_id)\
        .where(JatekosJatek.jatekos_id == jatekos_id)
        result = await db.execute(stmt)
        return result.all()

async def get_game_status(jatek_cim: str, jatekos_id: int):
    async with SessionLocal() as db:
        #Cél játék lekérése
        stmt_jatek = select(Jatek).where(Jatek.cim == jatek_cim)
        cel_jatek = (await db.execute(stmt_jatek)).scalars().first()

        if not cel_jatek:
            return None, None, None, None

        #Aktuális kör lekérése
        stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == cel_jatek.id)
        aktualis_kor = await db.scalar(stmt_kor)

        #Játékmesteri jogosultság lekérése
        stmt_szerep = select(JatekosJatek.jatekmester).where(
            JatekosJatek.jatek_id == cel_jatek.id,
            JatekosJatek.jatekos_id == jatekos_id
        )
        is_jatekmester = await db.scalar(stmt_szerep)

        return cel_jatek.id, aktualis_kor, is_jatekmester, cel_jatek.jatek_lezarva, cel_jatek.eredmenyek_osszesitve

async def connect_to_game(jatekos_id: int, beirt_kod: str):
    async with SessionLocal() as db:
        try:
            #Olyan játék keresése, ahol a lobby_code megegyezik a megadott kóddal és a 0. körben tart
            stmt_jatek = select(Jatek.id).join(
                JelenlegiKor, JelenlegiKor.jatek_id == Jatek.id
            ).where(
                Jatek.lobby_code == beirt_kod,
                JelenlegiKor.kor == 0
            )
            jatek_id = await db.scalar(stmt_jatek)

            if not jatek_id:
                return False, "Nincs ilyen csatlakozható játék!", None

            #Ellenőrizzük, hogy a játékos szerepel-e már a játékban
            stmt_szerepel = select(JatekosJatek).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekos_id == jatekos_id
            )
            mar_szerepel = (await db.execute(stmt_szerepel)).scalars().first()

            if mar_szerepel:
                return False, "Már csatlakoztál ehhez a játékhoz!", None

            #Sikeres csatlakozás
            uj_resztvevo = JatekosJatek(
                jatekos_id = jatekos_id,
                jatek_id = jatek_id,
                jatekmester = False
            )
            db.add(uj_resztvevo)
            await db.commit()

            return True, "Sikeres csatlakozás!", jatek_id

        except Exception as e:
            print(f"Hiba a csatlakozás során: {e}")
            return False, "Hiba az adatbázis kapcsolat során", None

#Profile page: globális érv átlag
async def get_user_global_average(jatekos_id: int):
    #Lekéri a játékos összes érvének globális átlagát
    async with SessionLocal() as db:
        try:
            stmt = select(func.avg(JatekosErv.ertekeles_atlag)).where(
                JatekosErv.jatekos_id == jatekos_id,
                JatekosErv.ertekeles_atlag.isnot(None) #Csak az olyan érvek számítanak, amik már kaptak értékelést
            )
            result = await db.scalar(stmt)
            return round(result, 2) if result else 0.0
        except Exception as ex:
            print(f"Hiba a globális átlag lekérése során: {ex}")
            return 0.0

#Profile page: díjcsarnok
async def get_user_awards(jatekos_id: int):
    #Lekéri a játékos által kapott díjakat és a játékok címeit, ahol kapta őket
    async with SessionLocal() as db:
        try:
            stmt = select(DijatKapott.dij, Jatek.cim).join(
                Jatek, DijatKapott.jatek_id == Jatek.id
            ).where(DijatKapott.jatekos_id == jatekos_id)
            result = await db.execute(stmt)
            return result.all()
        except Exception as ex:
            print(f"Hiba a díjak lekérése során: {ex}")
            return []