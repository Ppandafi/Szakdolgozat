import flet as ft

def show_profile_page(page:ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_dashboard(e):
        from dashboard import show_dashboard
        page.controls.clear()
        show_dashboard(page)
        page.update()


    page.add(
        ft.Text(f"Ez lesz a profil oldal", weight = ft.FontWeight.BOLD, size = 15),
        ft.Button("Vissza a kezdőképernyőre", on_click = go_to_dashboard)
    )