import flet as ft

def create_register_view(page: ft.Page, on_register_attempt, on_cancel_click):
    email_input = ft.TextField(
        label = "Email",
        width = 320,
        autofocus = True,
        prefix_icon = ft.Icons.EMAIL,
        border_radius = 8,
        filled = True
    )

    username_input = ft.TextField(
        label = "Felhasználónév",
        width = 320,
        prefix_icon = ft.Icons.PERSON,
        border_radius = 8,
        filled = True
    )

    password_input = ft.TextField(
        label = "Jelszó",
        width = 320,
        password = True,
        can_reveal_password = True,
        prefix_icon = ft.Icons.LOCK,
        border_radius = 8,
        filled = True
    )

    error_text = ft.Text(value = "", color = ft.Colors.ERROR, visible = False, weight = ft.FontWeight.W_500)
    success_text = ft.Text(value = "", color = ft.Colors.GREEN, visible = False, weight = ft.FontWeight.W_500)

    async def register_click(e):
        if not email_input.value or not password_input.value or not username_input.value:
            error_text.value = "Kérlek tölts ki minden mezőt!"
            error_text.visible = True
            page.update()
            return

        #Delegálás a main.py-nak
        success, message = await on_register_attempt(email_input.value, username_input.value, password_input.value)

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
            ft.Card(
                elevation = 4,
                content = ft.Container(
                    padding = 40,
                    content = ft.Column(
                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                        spacing = 20,
                        controls = [
                            ft.Icon(ft.Icons.PERSON_ADD, size = 60, color = ft.Colors.PRIMARY),
                            ft.Text("Regisztráció", size = 32, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                            email_input,
                            username_input,
                            password_input,
                            error_text,
                            success_text,
                            ft.Container(height = 10),
                            ft.Row(
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                                width = 320,
                                controls = [
                                    ft.TextButton("Mégse", on_click = on_cancel_click),
                                    ft.FilledButton("Regisztráció", on_click = register_click, width = 150, height = 45),
                                ]
                            )
                        ]
                    )
                )
            )
        ]
    )