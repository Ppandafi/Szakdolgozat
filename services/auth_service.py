from database import SessionLocal, Jatekos

async def authenticate_user(email_vagy_nev, jelszo):
    #Ellenőrzi a felhasználói adatokat az adatbázisban
    db = SessionLocal()
    try:
        felhasznalo = db.query(Jatekos).filter(
            (Jatekos.email == email_vagy_nev) |
            (Jatekos.felhasznalonev == email_vagy_nev)
        ).first()
        if felhasznalo and felhasznalo.jelszo == jelszo:
            return True, felhasznalo.email
        return False, "Helytelen email/felhasználónév vagy jelszó!"
    except Exception as ex:
        print(f"Hiba a bejelentkezés során: {ex}")
        return False, "Hiba az adatbázis kapcsolat során"
    finally:
        db.close()

async def register_user(email, felhasznalonev, jelszo):
    #Új felhasználó regisztrálása az adatbázisban
    db = SessionLocal()
    try:
        #Lekérjük, hogy szerepel-e már az adatbázisban ilyen email / felhasználónév
        felhasznalo = db.query(Jatekos).filter(
            (Jatekos.email == email) |
            (Jatekos.felhasznalonev == felhasznalonev)
        ).first()
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
        db.commit()
        return True, "Sikeres regisztráció!"
    except Exception as ex:
        print(f"Hiba a regisztráció során: {ex}")
        return False, "Hiba az adatbázis kapcsolat során"
    finally:
        db.close()