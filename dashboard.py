import flet as ft
from profile_page import show_profile_page
from database import SessionLocal, Jatekos


def show_dashboard(page:ft.Page, current_user:str):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_profile(e):
        page.controls.clear()
        show_profile_page(page, current_user)
        page.update()

    #felhasználó adatok lekérése
    db = SessionLocal()
    felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
    print(felhasznalo.__dict__)

    #Avatar színét kiválasztó függvény
    def szin(nev):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(nev) % len(colors_lookup)]

    def kezdobetu(nev):
        return nev[:1].capitalize()

    top_row = ft.Row(
        [
            ft.Container(
                content = ft.CircleAvatar(
                    content = ft.Text(kezdobetu(felhasznalo.felhasznalonev)),
                    bgcolor = szin(felhasznalo.felhasznalonev),
                    color = "white",
                    radius = 20
                ),
                on_click = go_to_profile,
                tooltip = "Profil megnyitása",
                #ink = True #Ripple effekt kattintáskor
            )
        ],
        alignment = ft.MainAxisAlignment.END,
    )

    dashboard_content = ft.Column(
        [
            ft.Text(f"Üdv {felhasznalo.felhasznalonev}", weight=ft.FontWeight.BOLD, size=15)
        ],
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        expand = True
    )


    page.add(
        ft.Container(content = top_row, padding = ft.Padding.only(right = 20, top = 10)),
        dashboard_content
    )
    page.update()