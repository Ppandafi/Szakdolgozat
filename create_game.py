import flet as ft
from pygments.lexers import sieve, automation

from database import SessionLocal, Jatek, JatekosJatek, Kerdoiv, Szerep, Dijak, NulladikKor, JelenlegiKor

def show_create_page(page:ft.Page, current_user, on_cancel):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def cancel_click(e):
        on_cancel()
        #TODO: a félkész játékot majd törölni kell a DB-ből

    #Csatlakozott játékosok
    csatlakozok = ft.Text("Itt lesznek a csatlakozó játékosok")

    #Javaslatok
    javaslatok = ft.Text("Itt lesznek a díj/szerep javaslatok")

    #Csatlakozott játékok és javaslatok
    l_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = csatlakozok),
                ft.Container(content = javaslatok),
            ],
            width = 300,
            scroll = ft.ScrollMode.AUTO,
        ),
        #bgcolor = ft.Colors.CYAN_700
    )

    #Eddig felvett adatok (cím, szerepek, díjak, kérdések)
    r_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Text(f"Eddig felvéve:", weight = ft.FontWeight.BOLD),
                ft.Text("Cím:"),
                ft.Text("Itt lesz a cím"),
                ft.Text("Szerepek:"),
                ft.Column(
                    controls = [
                        ft.Text("Ide jönnek a szerepek egy ft.Column-ban")
                    ]
                ),
                ft.Text("Díjak:"),
                ft.Column(
                    controls=[
                        ft.Text("Ide jönnek a díjak egy ft.Column-ban")
                    ]
                ),
                ft.Text("Kérdések:"),
                ft.Column(
                    controls=[
                        ft.Text("Ide jönnek a kérdések egy ft.Column-ban")
                    ]
                ),
            ],
            width = 300,
            scroll = ft.ScrollMode.AUTO,
        ),
        #bgcolor = ft.Colors.CYAN_700
    )

    #BEVITELI MEZŐK
    #Cím
    title_input = ft.TextField(expand = True)

    #Ismertetés
    description_input = ft.TextField(expand = True, multiline = True)

    #Szerepek
    positions_input = ft.TextField(expand = True)

    #Díjak
    awards_input = ft.TextField(expand = True)

    #Kérdések
    questions_input = ft.TextField(expand = True)
    elott_utan = ft.Dropdown(
        options=[
            ft.DropdownOption(key="post", text="Csak játék utáni"),
            ft.DropdownOption(key="both", text="Játék előtti és utáni")
        ],
        label="Kérlek válassz...",
    )

    #Értesítő szöveg konstruktor
    def create_alert_text():
        return ft.Text(value = "", color = ft.Colors.RED, visible = False)

    #Külön értesítő szöveg minden beviteli mezőhöz
    title_alert = create_alert_text()
    description_alert = create_alert_text()
    positions_alert = create_alert_text()
    award_alert = create_alert_text()
    questions_alert = create_alert_text()

    #BEÍRT ADATOK MENTÉSE
    #cím
    def title_save(e):
        #Ellenőrzés, hogy ki van-e töltve a cím
        if not title_input.value:
            title_alert.value = "Kérlek add meg a játék címét!"
            title_alert.color = ft.Colors.RED
            title_alert.visible = True
            page.update()
        else:
            title_alert.value = "Cím sikeresen mentve!"
            title_alert.color = ft.Colors.GREEN
            title_alert.visible = True
            page.update()

    #ismertetés
    def description_save(e):
        #Ellenőrzés, hogy ki van-e töltve az ismertetés
        if not description_input.value:
            description_alert.value = "Kérlek add meg a játék az ismertetést!"
            description_alert.color = ft.Colors.RED
            description_alert.visible = True
            page.update()
        else:
            description_alert.value = "Ismertetés sikeresen mentve!"
            description_alert.color = ft.Colors.GREEN
            description_alert.visible = True
            page.update()

    #szerepek
    def add_position(e):
        #Ellenőrzés, hogy van-e beírva szerep
        if not positions_input.value:
            positions_alert.value = "Kérlek add meg a szerepet!"
            positions_alert.color = ft.Colors.RED
            positions_alert.visible = True
            page.update()
        else:
            positions_alert.value = "Szerep sikeresen mentve!"
            positions_alert.color = ft.Colors.GREEN
            positions_alert.visible = True
            page.update()

    #díjak
    def add_award(e):
        #Ellenőrzés, hogy van-e beírva díj
        if not awards_input.value:
            award_alert.value = "Kérlek add meg a díjat!"
            award_alert.color = ft.Colors.RED
            award_alert.visible = True
            page.update()
        else:
            award_alert.value = "Díj sikeresen mentve!"
            award_alert.color = ft.Colors.GREEN
            award_alert.visible = True
            page.update()

    #kérdések
    def add_question(e):
        #Ellenőrzés: ki van-e töltve a kérdés és a dropdown is
        if not questions_input.value:
            questions_alert.value = "Kérlek add meg a kérdést!"
            questions_alert.color = ft.Colors.RED
            questions_alert.visible = True
            page.update()
        elif not elott_utan.value:
            questions_alert.value = "Kérlek válassz a legördülő menüből!"
            questions_alert.visible = True
            page.update()
        else:
            questions_alert.value = "Kérdés sikeresen felvéve!"
            questions_alert.color = ft.Colors.GREEN
            questions_alert.visible = True
            page.update()


    #Fő szekció
    main_section = ft.Column(
        controls = [
            ft.Text("Kérlek add meg a játék adatait", weight = ft.FontWeight.BOLD, size = 30, text_align = ft.TextAlign.CENTER),
            ft.Text(
                "FIGYELEM: A 'Véglegesít' gombra csak akkor kattints, ha már mindent hozzáadtál a játékhoz, amit szeretnél. A véglegesítés előtt a 'Hozzáad' gombbal tudod menteni a hozzáadott adatokat",
                color = ft.Colors.RED
                ),
            ft.Column(
                controls = [
                    #cím
                    ft.Column(
                        controls = [
                            ft.Text("Cím:"),
                            ft.Row(
                                controls = [
                                    title_input,
                                    ft.Button("Mentés", on_click = title_save)
                                ]
                            ),
                            title_alert
                        ]
                    ),
                    #ismertetés
                    ft.Column(
                        controls = [
                            ft.Text("Ismertetés:"),
                            ft.Row(
                                controls = [
                                    description_input,
                                    ft.Button("Mentés", on_click = description_save)
                                ]
                            ),
                            description_alert
                        ]
                    ),
                    #szerepek
                    ft.Column(
                        controls = [
                            ft.Text("Szerepek:"),
                            ft.Row(
                                controls = [
                                    positions_input,
                                    ft.Button("Hozzáad", on_click = add_position)
                                ]
                            ),
                            positions_alert
                        ]
                    ),
                    #díjak
                    ft.Column(
                        controls = [
                          ft.Text("Díjak"),
                          ft.Row(
                              controls = [
                                  awards_input,
                                  ft.Button("Hozzáad", on_click = add_award)
                              ]
                          ),
                            award_alert
                      ]
                    ),
                    #kérdések
                    ft.Column(
                        controls = [
                            ft.Text("Kérdőív kérdés:"),
                            ft.Row(
                                controls = [
                                    questions_input,
                                    elott_utan,
                                    ft.Button("Hozzáad", on_click = add_question)
                                ]
                            ),
                            questions_alert
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Button("Mégse", on_click = cancel_click),
                            ft.Button("Véglegesít", color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE)
                        ]
                    )
                ]
            )
        ],
        scroll = ft.ScrollMode.AUTO,
        expand = True,
    )
    page.add(
        ft.Row(
            controls = [
                l_sidebar,
                main_section,
                r_sidebar
            ],
            expand = True,
        )
    )
    page.update()