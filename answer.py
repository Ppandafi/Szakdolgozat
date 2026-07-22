import flet as ft
from database import SessionLocal, Jatek, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost, JatekosJatek

pre_post_flag = "both" #ez a flag adja meg, hogy éppen játék előtti vagy utáni kérdőív kerül kitöltésre (both = előtt / post = után)

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

    sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékosok:"),
                ft.Container(content = jatekosok),
            ]
        ),
        width = 250,
        bgcolor = ft.Colors.LIGHT_BLUE,
    )

    page.add(
        ft.Row(
            controls = [
                sidebar,
                ft.Text("Ez lesz a kérdőív kitöltő mező")
            ],
            expand = True,
        )
    )
    page.update()