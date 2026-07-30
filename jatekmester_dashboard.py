import flet as ft
from game.events import jatek_topic, Uzenet

async def create_gm_dashboard_view(page: ft.Page, jatek_id: int):
    #Felhasználó lekérése a session-ből
    current_user = page.session.store.get("current_user")

    #Fő UI elemek
    #Bal oldali menüsáv
    l_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Text("Jelenlegi kör: XY/AB"),
                ft.Text("Itt lesznek a játékosok és szerepeik")
            ]
        ),
        bgcolor = "lightblue",
        expand=1
    )

    #Jobb oldali szekció
    r_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Text("Itt lesz, hogy hányan érveltek a körben"),
                ft.Text("Itt lesz, hogy hányan értékelték a jelenleg soron levőt")
            ]
        ),
        bgcolor = "lightblue",
        expand=1
    )

    #Fő szekció
    main_section = ft.Container(
        ft.Column(
            controls = [
                ft.Text("Itt lesz felsorolva MINDEN érv"),
                ft.Row(
                    controls = [
                        ft.Button("Következő játékos"),
                        ft.Button("Következő kör"),
                        ft.Button("Játék lezárása")
                    ],
                    expand = True
                )
            ]
        ),
        expand=3
    )


    return ft.View(
        route = f"/gm_dashboard/{jatek_id}",
        controls = [
            ft.Row(
                controls = [l_sidebar, main_section, r_sidebar],
                expand = True
            )
        ]
    )