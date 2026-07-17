import flet as ft
from pygments.lexers import sieve, automation

from database import SessionLocal, Jatek, JatekosJatek, Kerdoiv, Szerep, Dijak, NulladikKor, JelenlegiKor

def show_create_page(page:ft.Page, current_user):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
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

    #Fő szekció
    main_section = ft.Column(
        controls = [
            ft.Text("Kérlek add meg a játék adatait", weight = ft.FontWeight.BOLD, size = 30, text_align = ft.TextAlign.CENTER),
            ft.Column(
                controls = [
                    #cím
                    ft.Column(
                        controls = [
                            ft.Text("Cím:"),
                            title_input
                        ]
                    ),
                    #ismertetés
                    ft.Column(
                        controls = [
                            ft.Text("Ismertetés:"),
                            description_input
                        ]
                    ),
                    #szerepek
                    ft.Column(
                        controls = [
                            ft.Text("Szerepek:"),
                            positions_input
                        ]
                    ),
                    #díjak
                    ft.Column(
                        controls = [
                          ft.Text("Díjak"),
                          awards_input
                      ]
                    ),
                    #kérdések
                    ft.Column(
                        controls = [
                            ft.Text("Kérdőív kérdés:"),
                            questions_input
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