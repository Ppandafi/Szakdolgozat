import flet as ft
from database import SessionLocal, Jatekos

def show_login_dialog(page:ft.Page, on_login_success):
    #Megjelenít egy felugró ablakot

    #Beviteli mezők definiálása
    email_input = ft.TextField(
        label="Email vagy felhasználónév",
        width = 300,
        autofocus= True
    )
    password_input = ft.TextField(
        label="Password",
        autofocus= True,
        password= True,
        width = 300
    )

    #Hibaüzenet (alapból rejtett)
    error_text = ft.Text(value = "", color = ft.Colors.RED, visible = False)

    def login_click(e):
        #Ki van-e töltve minden mező?
        if not email_input.value or not password_input.value:
            error_text.value = "Minden mező kitöltése kötelező!"
            error_text.visible = True
            page.update()
            return

        #Megadott adatok ellenőrzése
        db = SessionLocal()
        try:
            felhasznalo = db.query(Jatekos).filter((Jatekos.email == email_input.value) | (Jatekos.felhasznalonev == email_input.value)).first()

            if felhasznalo and felhasznalo.jelszo == password_input.value:
                error_text.value = ""
                error_text.visible = False
                page.pop_dialog()

                #Sikeres bejelentkezés esetén továbbítjuk az adatokat
                on_login_success(email_input.value)
            else:
                #Sikertelen belépés
                error_text.value = "Helytelen email vagy jelszó!"
                error_text.visible = True
                page.update()

        except Exception as e:
            error_text.value = "Hiba történt az adatbázis kapcsolat során"
            print({e})
            error_text.visible = True
            page.update()

        finally:
            #Minden esetben lezárjuk az adatbázis sessiont
            db.close()

    def cancel_click(e):
        page.pop_dialog()

    #UX - ENTER lenyomására is működjön a hitelesítés
    email_input.on_submit = login_click
    password_input.on_submit = login_click

    #Dialog ablak összeállítása
    dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Bejelentkezés"),
        content = ft.Column(
          controls = [
              email_input,
              password_input,
              error_text
          ],
            tight = True,
        ),
        actions = [
            ft.TextButton("Mégse", on_click = cancel_click),
            ft.TextButton("Belépés", on_click = login_click),
        ],
        actions_alignment = ft.MainAxisAlignment.END,
    )
    return dialog