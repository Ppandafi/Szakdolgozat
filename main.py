import flet as ft
from login import show_login_dialog

def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # Javítva: A vertical_alignment MainAxisAlignment-et vár
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Ez fut le sikeres bejelentkezéskor
    def handle_successful_login(email_cim):
        page.controls.clear()
        page.add(
            ft.Text(f"Sikeres belépés a(z) {email_cim} email címmel"),
            ft.Button("Tovább a játékba (Fejlesztés alatt)")
        )
        page.update()

    #Bejelentkezés ablak azonnali megnyitása indításkor
    login_dialog = show_login_dialog(page, on_login_success = handle_successful_login)
    page.show_dialog(login_dialog)

if __name__ == '__main__':
    ft.run(main, view = ft.AppView.WEB_BROWSER)