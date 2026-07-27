from email import message

import flet as ft

def create_login_view(page: ft.Page, on_login_attempt, on_register_click):
    email_input = ft.TextField(label = "email vagy felhasználónév", width = 300, autofocus = True)
    password_input = ft.TextField(label = "Jelszó", password = True, can_reveal_password = True, width = 300)
    error_text = ft.Text(value = "", color = ft.Colors.RED, visible = False)

    def login_click(e):
        if not email_input or not password_input:
            error_text.value = "Kérlek tölts ki minden mezőt!"
            error_text.visible = True
            page.update()
            return
        #A main.py-ból kapott ellenőrző függvény meghívása
        success = on_login_attempt(email_input.value, password_input.value)

        if success:
            error_text.visible = False
        else:
            error_text.value = message
            error_text.visible = True
            page.update()

    #ENTER gomb megnyomásakor is működjön
    email_input.on_submit = login_click
    password_input.on_submit = login_click

    #Login felület felépítése
    return ft.View(
        route = "/login",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Text("Bejelentkezés", size = 30, weight = ft.FontWeight.BOLD),
            email_input,
            password_input,
            error_text,
            ft.Row(
                controls = [
                    ft.Text("Nincs még fiókod?", size=12),
                    ft.TextButton("Regisztráció", on_click = lambda _: on_register_click()),
                    ft.Button("Belépés", on_click = login_click),
                ],
                alignment = ft.MainAxisAlignment.CENTER
            )
        ]
    )