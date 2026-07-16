import flet as ft
from login import show_login_dialog
from dashboard import show_dashboard
from register import show_register_dialog


def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Ez fut le sikeres bejelentkezéskor
    def handle_successful_login(email_cim):
        page.controls.clear()
        #Átirányít a dashboard képernyőre
        show_dashboard(page, email_cim)
        page.update()

    #Sikeres regisztráció után visszatérünk a login ablakba
    def handle_successful_register():
        open_login()

    #'Mégse' gomb is visszairányít a login ablakra
    def handle_register_cancel():
        open_login()

    #Regisztráció gomb handler
    def handle_register_click():
        register_dialog = show_register_dialog(
            page,
            on_register_success = handle_successful_register,
            on_cancel = handle_register_cancel
        )
        page.show_dialog(register_dialog)

    #Login ablakot meghívó függvény
    def open_login():
        login_dialog = show_login_dialog(
            page,
            on_login_success=handle_successful_login,
            on_register_click=handle_register_click
        )
        page.show_dialog(login_dialog)

    #Bejelentkezés ablak azonnali megnyitása indításkor
    open_login()

if __name__ == '__main__':
    ft.run(main, view = ft.AppView.WEB_BROWSER)