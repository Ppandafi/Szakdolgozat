import flet as ft

def show_dashboard(page:ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Text(f"Ez lesz a dashboard felület", weight = ft.FontWeight.BOLD, size = 15)
    )