import flet as ft
from database import SessionLocal, Jatek, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost, JatekosJatek

def show_answer_page(page:ft.Page, jatek_id, on_back_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.update()

    def back_clicked(e):
        on_back_click()

    #Többi játékos kiírása
    jatekosok = ft.Column(
        controls = [
            ft.Text("Itt lesz kiírva a többi játékos")
        ]
    )

    #Gombok
    gombok = ft.Column(
        controls = [
            ft.Button("Beküldés", width = 210),
            ft.Button("Vissza", width = 210, on_click = back_clicked)
        ]
    )

    #Oldalsó sáv
    sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékosok:"),
                ft.Container(content = jatekosok),
            ]
        ),
        expand = 1,
        bgcolor = ft.Colors.LIGHT_BLUE,
    )

    #Fő szekció
    main_section = ft.Column(
        controls = [
            ft.Text("Kérlek várj, amíg a játékmester kiküldi a kérdőíveket...", size = 30, weight = ft.FontWeight.BOLD)
        ],
        expand = 3,
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
    )

    #Üzenetkezelő függvény
    def handle_pubsub_message(topic, message):
        #Ellenőrzés: a kérdőívek kiírásáról szól az üzenet
        if message in ["kerdoivek_pre", "kerdoivek_post"]:
            #Adatbázis megnyitása
            db = SessionLocal()
            try:
                #Kérdések lekérése a kapott üzenet alapján
                if message == "kerdoivek_pre":
                    #Csak a játék előtti kérdések lekérése
                    kerdesek = db.query(Kerdoiv).filter(
                        Kerdoiv.jatek_id == jatek_id,
                        Kerdoiv.jatek_elott_utan == True,
                    ).all()
                elif message == "kerdoivek_post":
                    #Minden kérdés lekérése
                    kerdesek = db.query(Kerdoiv).filter(Kerdoiv.jatek_id == jatek_id).all()

                #Felület kiürítése és kérdések betöltése
                main_section.controls.clear()
                main_section.alignment = ft.MainAxisAlignment.START

                main_section.controls.append(
                    ft.Text("Kérlek a következő kérdéseket pontozd 1-től 10-ig, hogy mennyire értesz egyet velük:", size = 20, weight = ft.FontWeight.BOLD)
                )

                if not kerdesek:
                    main_section.controls.append(ft.Text("Nincsenek megjeleníthető kérdések..."))
                else:
                    for kerdes in kerdesek:
                        main_section.controls.append(
                            ft.Column([
                                ft.Text(kerdes.kerdes, size = 15),
                                ft.Slider(min = 1, max = 10, divisions = 9, label = "{value} pont")
                            ])
                        )

                page.update()

            except Exception as e:
                print(f"Hiba a kérdések betöltése során: {e}")
                main_section.controls.append(ft.Text("Hiba az adatok betöltésekor"))
                page.update()
            finally:
                db.close()

    page.pubsub.subscribe_topic(f"jatek_{jatek_id}", handle_pubsub_message)

    page.add(
        ft.Row(
            controls = [
                sidebar,
                main_section
            ],
            expand = True,
        )
    )
    page.update()