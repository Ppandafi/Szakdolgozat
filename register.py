import flet as ft
from database import SessionLocal, Jatekos


def show_register_dialog(page:ft.Page, on_register_success, on_cancel):
    #Beviteli mezők definiálása
    email_input = ft.TextField(
        label = "Email",
        width = 300,
        autofocus= True
    )
    username_input = ft.TextField(
        label = "Felhasználónév",
        width = 300,
        autofocus= True
    )
    password_input = ft.TextField(
        label = "Jelszó",
        autofocus= True,
        password= True,
        width = 300
    )

    #Hiabüzenet (alapból rejtett)
    error_text = ft.Text(value = "", color = ft.Colors.RED, visible = False)

    def register_click(e):
        if not email_input.value or not username_input.value or not password_input.value :
            error_text.value = "Minden mező kitöltése kötelező!"
            error_text.visible = True
            page.update()
            return

        #Adatbázis session megnyitása
        db = SessionLocal()

        try:
            # Adatok lekérése, hogy ne legyen duplikált email / username
            felhasznalo = db.query(Jatekos).filter((Jatekos.email == email_input.value) | (Jatekos.felhasznalonev == username_input.value)).first()

            #A megadott email / username már foglalt
            if felhasznalo and felhasznalo.email == email_input.value:
                error_text.value = "Ez az email cím már foglalt!"
                error_text.visible = True
                page.update()
            elif felhasznalo and felhasznalo.felhasznalonev == username_input.value:
                error_text.value = "Ez felhasználónév már foglalt!"
                error_text.visible = True
                page.update()

            #Nem foglalt email / username páros, új felhasználó felvétele
            else:
                uj_jatekos = Jatekos(
                    felhasznalonev = username_input.value,
                    email = email_input.value,
                    jelszo = username_input.value,
                )
                db.add(uj_jatekos)
                db.commit()
                page.pop_dialog()
                on_register_success()

        except Exception as e:
            error_text.value = "Hiba történt az adatbázis kapcsolat során"
            print({e})
            error_text.visible = True
            page.update()

        finally:
            #Adatbázis lezárása
            db.close()



    def cancel_click(e):
        page.pop_dialog()
        on_cancel()

    #UX - ENTER lenyomására is működjön a regisztráció
    email_input.on_submit = register_click
    username_input.on_submit = register_click
    password_input.on_submit = register_click

    dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Regisztráció"),
        content = ft.Column(
            controls = [ email_input, username_input, password_input, error_text ],
            tight = True,
        ),
        actions = [
            ft.Button("Mégse", on_click = cancel_click),
            ft.Button("Regisztráció", on_click = register_click),
        ],
    )

    #Dialog visszaadása, hogy a main meg tudja nyitni
    return dialog