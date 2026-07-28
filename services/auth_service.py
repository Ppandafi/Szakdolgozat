from sqlalchemy import select
from database import SessionLocal, Jatekos

async def authenticate_user(email_vagy_nev, jelszo):
    #Ellenőrzi a felhasználói adatokat az adatbázisban
    async with SessionLocal() as db:
        try:
            stmt = select(Jatekos).where(
                (Jatekos.email == email_vagy_nev) |
                (Jatekos.felhasznalonev == email_vagy_nev)
            )
            result = await db.execute(stmt)
            felhasznalo = result.scalars().first()
            if felhasznalo and felhasznalo.jelszo == jelszo:
                return True, felhasznalo.email
            return False, "Helytelen email/felhasználónév vagy jelszó!"
        except Exception as ex:
            print(f"Hiba a bejelentkezés során: {ex}")
            return False, "Hiba az adatbázis kapcsolat során"

async def register_user(email, felhasznalonev, jelszo):
    #Új felhasználó regisztrálása az adatbázisban
    async with SessionLocal() as db:
        try:
            #Lekérjük, hogy szerepel-e már az adatbázisban ilyen email / felhasználónév
            stmt = select(Jatekos).where(
                (Jatekos.email == email) |
                (Jatekos.felhasznalonev == felhasznalonev)
            )
            result = await db.execute(stmt)
            felhasznalo = result.scalars().first()

            if felhasznalo:
                if felhasznalo.email == email:
                    return False, "Ez az email-cím már foglalt!"
                return False, "Ez a felhasználónév már foglalt!"

            uj_jatekos = Jatekos(
                felhasznalonev = felhasznalonev,
                email = email,
                jelszo = jelszo
            )
            db.add(uj_jatekos)
            await db.commit()
            return True, "Sikeres regisztráció!"
        except Exception as ex:
            print(f"Hiba a regisztráció során: {ex}")
            return False, "Hiba az adatbázis kapcsolat során"

async def change_password(email_vagy_nev: str, uj_jelszo: str):
    async with SessionLocal() as db:
        try:
            stmt = select(Jatekos).where(
                (Jatekos.email == email_vagy_nev) |
                (Jatekos.felhasznalonev == email_vagy_nev)
            )
            result = await db.execute(stmt)
            felhasznalo = result.scalars().first()

            if felhasznalo:
                #Adatbázis módosítása és mentés
                felhasznalo.jelszo = uj_jelszo
                await db.commit()
                return True, "A jelszó sikeresen megváltoztatva!"
            return False, "A felhasználó nem található!"
        except Exception as ex:
            print(f"Hiba a jelszóváltoztatás során: {ex}")
            return False, "Hiba az adatbázis kapcsolat során"