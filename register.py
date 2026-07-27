import flet as ft

def create_register_view(page: ft.Page, on_register_attempt, on_cancel_click):
    email_input = ft.TextField(label = "email", width = 300, autofocus = True)
    username_input = ft.TextField(label = "felhasználónév", width = 300, autofocus = True)
    password_input = ft.TextField(label = "jelszó", width = 300, autofocus = True)
    error_text = ft.Text(value = "", color = ft.Colors.RED, visible = False)
    success_text = ft.Text(value = "", color = ft.Colors.GREEN, visible = False)

    async def register_click(e):
        if not email_input.value or not password_input.value or not username_input.value:
            error_text.value = "Kérlek tölts ki minden mezőt!"
            error_text.visible = True
            page.update()
            return

        #Delegálás a main.py-nak
        success, message = on_register_attempt(email_input.value, username_input.value, password_input.value)

        if success:
            error_text.visible = False
            success_text.value = message
            success_text.visible = True
            page.update()
            on_cancel_click()
        else:
            error_text.value = message
            error_text.visible = True
            page.update()

    #ENTER gomb megnyomásakor is működjön
    email_input.on_submit = register_click
    username_input.on_submit = register_click
    password_input.on_submit = register_click

    #Register felület felépítése
    return ft.View(
        route = "/register",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Text("Regisztráció", size = 30, weight = ft.FontWeight.BOLD),
            email_input,
            username_input,
            password_input,
            error_text,
            success_text,
            ft.Row(
                controls = [
                    ft.TextButton("Mégse", on_click = lambda _: on_cancel_click()),
                    ft.Button("Regisztráció", on_click = register_click),
                ],
                alignment = ft.MainAxisAlignment.CENTER
            )
        ]
    )