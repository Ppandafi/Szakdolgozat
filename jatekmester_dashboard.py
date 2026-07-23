import flet as ft

def show_jatekmester_dashbdoard(page:ft.Page, jatek_id, current_user):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Text("Ez lesz a játékmester kezelőfelület", size = 30, weight = ft.FontWeight.BOLD)
    )