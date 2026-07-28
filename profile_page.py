import flet as ft
from pydantic.mypy import error_extra_fields_on_root_model

from services import dashboard_service

async def create_profile_view(
        page: ft.Page, current_user: str, on_password_change_attempt,
        on_logout_click, on_dashboard_click
):
    #Felhasználó adatainak lekérése
    felhasznalo = await dashboard_service.get_user(current_user)

    if not felhasznalo:
        return ft.View(route = "/profile", controls = [ft.Text("Hiba történt a felhasználó betöltésekor!")])

    uj_jelszo = ft.TextField(
        label = "Új jelszó",
        width = 300,
        password = True,
        can_reveal_password = True
    )

    error_text = ft.Text(value = "", color = ft.Colors.RED, size = 15, visible = False)
    success_text = ft.Text(value = "", color = ft.Colors.GREEN, size = 15, visible = False)

    async def jelszot_valtoztat(e):
        if not uj_jelszo.value:
            error_text.value = "Kérlek töltsd ki az új jelszó mezőt!"
            error_text.visible = True,
            success_text.visible = False,
            page.update()
            return

        #Delegálás a main.py-nak
        success, msg = await on_password_change_attempt(current_user, uj_jelszo.value)

        if success:
            success_text.value = msg
            success_text.visible = True
            error_text.visible = False
            uj_jelszo.value = ""
        else:
            error_text.value = msg
            error_text.visible = True
            success_text.visible = False
        page.update()

    #Az ENTER megnyomására is működjön
    uj_jelszo.on_submit = jelszot_valtoztat

    main_section = ft.Column(
        controls = [
            ft.Text(f"{felhasznalo.felhasznalonev}", weight = ft.FontWeight.BOLD, size = 40),
            ft.Text("Jelszó megváltoztatása", size = 15),
            uj_jelszo,
            error_text,
            success_text,
            ft.Button("Jelszó megváltoztatása", on_click = jelszot_valtoztat)
        ],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
    )

    #UI felépítése
    return ft.View(
        route = "/profile",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            main_section,
            ft.Row(
                controls = [
                    ft.Button("Vissza a kezdőképernyőre", on_click = on_dashboard_click),
                    ft.Button("Kijelentkezés", on_click = on_logout_click),
                ],
                alignment = ft.MainAxisAlignment.CENTER
           )
        ]
    )