import flet as ft
from sqlalchemy.sql.functions import current_user

from login import show_login_dialog
from dashboard import show_dashboard
from register import show_register_dialog
from profile_page import show_profile_page
from connect_to_game import show_connect_dialog
from create_game import show_create_page
from answer import show_answer_page


def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Kijelentkezés gomb kezelő
    def handle_logout():
        page.controls.clear()
        open_login()
        page.update()

    #Átirányítás a kérdőív kitöltéséhez
    def handle_answer_page(current_user, jatek_id):
        page.controls.clear()
        show_answer_page(
            page,
            jatek_id,
            on_back_click = lambda: handle_dashboard_click(current_user)
        )
        page.update()

    #Játékhoz csatlakozás ablak
    def handle_connect_click(current_user, jatekos_id):
        connect_dialog = show_connect_dialog(
            page,
            jatekos_id,
            on_connect_success = lambda csatlakozo_jatek_id: handle_answer_page(current_user, csatlakozo_jatek_id)
        )
        page.show_dialog(connect_dialog)

    #Dashboard -> profil navigáció
    def handle_profile_click(current_user):
        page.controls.clear()
        show_profile_page(
            page,
            current_user,
            on_logout = handle_logout,
            on_dashboard_click = lambda: handle_dashboard_click(current_user),
        )

    #Új játék felvétele gomb
    def handle_create_click(current_user, uj_id):
        page.controls.clear()
        show_create_page(
            page,
            current_user,
            uj_id,
            on_cancel = lambda: handle_dashboard_click(current_user)
        )


    #Profil -> dashboard navigáció
    def handle_dashboard_click(current_user):
        page.controls.clear()
        show_dashboard(
            page,
            current_user,
            on_logout = handle_logout,
            on_profile_click = lambda: handle_profile_click(current_user),
            on_connect_click = lambda jatekos_id: handle_connect_click(current_user, jatekos_id),
            on_create_click = handle_create_click,
            on_answer_click = lambda jatek_id : handle_answer_page(current_user, jatek_id)
        )

    #Ez fut le sikeres bejelentkezéskor
    def handle_successful_login(email_cim):
        #Átirányítjuk a dashboard képernyőre
        handle_dashboard_click(email_cim)

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