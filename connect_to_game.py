import flet as ft

from database import SessionLocal, Jatek, JelenlegiKor, Jatekos, JatekosJatek

def show_connect_dialog(page : ft.Page, jatekos_id, on_connect_success):
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
        beirt_kod = code_input.value.upper()
        #Ellenőrizzük, hogy a játékos kitöltötte-e a mezőt
        if not beirt_kod:
            error_text.value = "Kérlek add meg a szoba kódját!"
            error_text.visible = True
            page.update()
            return
        # Adatbázis megnyitása
        db = SessionLocal()
        try:
            #Lekérjük az olyan játékok kódjait és id-jét amikhez lehet csatlakozni
            szabad_kodok_query = db.query(Jatek.lobby_code, Jatek.id).join(JelenlegiKor, Jatek.id == JelenlegiKor.jatek_id).filter(JelenlegiKor.kor == 0).all()
            szabad_kodok = {kod[0]: kod[1] for kod in szabad_kodok_query}

            #Lekérjük, hogy a játékos már szerepel-e a játéban, amihez csatlakozni akar
            mar_szerepel = db.query(JatekosJatek).join(Jatek, JatekosJatek.jatek_id == Jatek.id).filter(JatekosJatek.jatekos_id == jatekos_id, Jatek.lobby_code == beirt_kod).first()
            if mar_szerepel:
                error_text.value = "Már csatlakoztál ehhez a játékhoz!"
                error_text.color = ft.Colors.ORANGE
                error_text.visible = True
                page.update()
                return

            #Ellenőrizzük, hogy létezik-e ilyen csatlakozható kód
            if beirt_kod not in szabad_kodok:
                error_text.value = "Nincs ilyen csatlaokzható játék!"
                error_text.color = ft.Colors.RED
                error_text.visible = True
                page.update()
                return

            #Sikeres csatlakozás
            else:
                uj_jatek_id = szabad_kodok[beirt_kod]

                uj_resztvevo = JatekosJatek(
                    jatekos_id = jatekos_id,
                    jatek_id = uj_jatek_id,
                    jatekmester = False
                )
                db.add(uj_resztvevo)
                db.commit()

                #Ablak bezárása
                page.pop_dialog()

                #Átadjuk a csatlakozott játék id-jét
                csatlakozott_id = szabad_kodok[code_input.value.upper()]
                on_connect_success(csatlakozott_id)

                #Értesítés: értesítjük a pub sub csatornát, hogy a játékhoz új játékos csatlakozott
                page.pubsub.send_all_on_topic(f"jatek_{uj_jatek_id}", "uj_jatekos")

                error_text.value = "Sikeres csatlakozás"
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