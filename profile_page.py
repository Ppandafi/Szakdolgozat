from cProfile import label

import flet as ft
from database import SessionLocal, Jatekos


def show_profile_page(page:ft.Page, current_user, on_logout):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Kijelentkezés gombot kezelő
    def handle_logout_click(e):
        on_logout()

    def go_to_dashboard(e):
        from dashboard import show_dashboard
        page.controls.clear()
        show_dashboard(page, current_user)
        page.update()


    #Felhasználói adatok betöltése
    db = SessionLocal()
    felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()

    #Új jelszó beviteli mező
    uj_jelszo = ft.TextField(
        label = "Új jelszó",
        width = 1300,
        height = 30,
        password = True
    )

    error_text = ft.Text(
        value = "Az új jelszó mező nem lehet üres!",
        color = ft.Colors.RED,
        size = 15,
        visible = False
    )

    def jelszo_valtoztat(e):
        if uj_jelszo.value == "":
            error_text.visible = True
            page.update()
        else:
            felhasznalo.jelszo = uj_jelszo.value
            db.commit()
            uj_jelszo.value = ""
            error_text.visible = False
            page.update()


    main_section = ft.Column(
        [
            ft.Text(f"{felhasznalo.felhasznalonev}", weight = ft.FontWeight.BOLD, size = 40),
            ft.Text(f"Jelszó megváltoztatása", size = 15),
            uj_jelszo,
            error_text,
            ft.Button("Jelszó megváltoztatása", on_click = jelszo_valtoztat),
        ]
    )

    #UX - ENTER lenyomásakor is működjön
    uj_jelszo.on_submit = jelszo_valtoztat

    page.add(
        main_section,
        ft.Button("Vissza a kezdőképernyőre", on_click = go_to_dashboard),
        ft.Button("Kijelentkezés", on_click = handle_logout_click)
    )