import flet as ft

from database import SessionLocal, Jatek, JelenlegiKor, Jatekos, JatekosJatek

def show_connect_dialog(page : ft.Page, jatekos_id):
    #Beviteli mező definiálása
    code_input = ft.TextField(
        label = "Szoba kódja",
        width = 300,
        autofocus= True
    )

    #Hibaüzenet
    error_text = ft.Text(
        value = "",
        color = ft.Colors.RED,
        visible = False
    )

    def cancel_click(e):
        page.pop_dialog()

    def connect_click(e):
        #Ellenőrizzük, hogy a játékos kitöltötte-e a mezőt
        if not code_input.value:
            error_text.value = "Kérlek add meg a szoba kódját!"
            error_text.visible = True
            page.update()
            return
        # Adatbázis megnyitása
        db = SessionLocal()
        try:
            szabad_kodok_query = db.query(Jatek.lobby_code, Jatek.id).join(JelenlegiKor, Jatek.id == JelenlegiKor.jatek_id).filter(JelenlegiKor.kor == 0).all()
            szabad_kodok = {kod[0]: kod[1] for kod in szabad_kodok_query}

            #Ha nincs olyan kódú csatlakozható szoba
            if code_input.value.upper() not in szabad_kodok and code_input.value != "":
                error_text.value = "Nincs ilyen csatlakozható játék!"
                error_text.visible = True
                page.update()
            #Sikeres csatlakozás
            else:
                uj_resztvevo = JatekosJatek(
                    jatekos_id = jatekos_id,
                    jatek_id = szabad_kodok[code_input.value.upper()],
                    jatekmester = False
                )
                db.add(uj_resztvevo)
                db.commit()
                error_text.value = "Sikerres csatlakozás"
                error_text.color = ft.Colors.GREEN
                error_text.visible = True
                page.update()

        except Exception as e:
            error_text.value = "Hiba az adatbázis kapcsolat során"
            error_text.visible = True
            page.update()
            print(e)
        finally:
            db.close()

    code_input.on_submit = connect_click

    dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Csatlakozás játékoz"),
        content = ft.Column(
            controls = [
                code_input,
                error_text
            ],
            tight = True,
        ),
        actions = [
            ft.Button("Mégse", on_click = cancel_click),
            ft.Button("Csatlakozás", on_click = connect_click)
        ]
    )
    return dialog