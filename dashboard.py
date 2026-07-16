import flet as ft
from profile_page import show_profile_page
from database import SessionLocal, Jatekos


def show_dashboard(page:ft.Page, current_user:str):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_profile(e):
        page.controls.clear()
        show_profile_page(page)
        page.update()

    #felhasználó adatok lekérése
    db = SessionLocal()
    felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
    print(felhasznalo.__dict__)


    top_row = ft.Row(
        [
            ft.Container(
                content = ft.CircleAvatar(
                    content = ft.Icon(ft.Icons.PERSON),
                    bgcolor = "bluegrey",
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