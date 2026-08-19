import flet as ft

def create_login_view(page: ft.Page, on_login_attempt, on_register_click):
    email_input = ft.TextField(
        label = "Email vagy felhasználónév",
        autofocus = True,
        prefix_icon = ft.Icons.PERSON,
        border_radius = 8,
        filled = True
    )

    password_input = ft.TextField(
        label = "Jelszó",
        password = True,
        can_reveal_password = True,
        prefix_icon = ft.Icons.LOCK,
        border_radius = 8,
        filled = True
    )

    error_text = ft.Text(value = "", color = ft.Colors.RED, visible = False)

    async def login_click(e):
        if not email_input.value or not password_input.value:
            error_text.value = "Kérlek tölts ki minden mezőt!"
            error_text.visible = True
            page.update()
            return
        #A main.py-ból kapott ellenőrző függvény meghívása
        success, msg = await on_login_attempt(email_input.value, password_input.value)

        if success:
            error_text.visible = False
        else:
            error_text.value = msg
            error_text.visible = True
            page.update()

    #ENTER gomb megnyomásakor is működjön
    email_input.on_submit = login_click
    password_input.on_submit = login_click

    #Login felület felépítése
    return ft.View(
        route = "/login",
        scroll = ft.ScrollMode.AUTO,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.ResponsiveRow(
                alignment = ft.MainAxisAlignment.CENTER,
                controls = [
                    ft.Column(
                        col = {"xs": 11, "sm": 8, "md": 6, "lg": 4},
                        controls = [
                            ft.Card(
                                elevation=4,
                                content=ft.Container(
                                    padding=40,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=20,
                                        controls=[
                                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=60, color=ft.Colors.PRIMARY),
                                            ft.Text("Bejeleentkezés", size=32, weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.PRIMARY),
                                            email_input,
                                            password_input,
                                            error_text,
                                            ft.Container(height=10),
                                            ft.Row(
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    ft.TextButton("Regisztráció", on_click=on_register_click),
                                                    ft.FilledButton("Bejelentkezés", on_click=login_click, width=150,
                                                                    height=45),
                                                ]
                                            )
                                        ]
                                    )
                                )
                            )
                        ]
                    )
                ]
            )
        ]
    )