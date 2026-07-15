import flet as ft
from profile import show_profile_page

def show_dashboard(page:ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_profile(e):
        page.controls.clear()
        show_profile_page(page)
        page.update()

    page.add(
        ft.Text(f"Ez lesz a dashboard felület", weight = ft.FontWeight.BOLD, size = 15),
        ft.Button(f"Profil", on_click = go_to_profile)
    )
    page.update()