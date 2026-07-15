import flet as ft
from login import show_login_dialog
from dashboard import show_dashboard


def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Ez fut le sikeres bejelentkezéskor
    def handle_successful_login(email_cim):
        page.controls.clear()
        #Átirányít a dashboard képernyőre
        show_dashboard(page)
        page.update()

    #Bejelentkezés ablak azonnali megnyitása indításkor
    login_dialog = show_login_dialog(page, on_login_success = handle_successful_login)
    page.show_dialog(login_dialog)

if __name__ == '__main__':
    ft.run(main, view = ft.AppView.WEB_BROWSER)