import flet as ft
from profile import show_profile_page

def show_dashboard(page:ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_profile(e):
        page.controls.clear()
        show_profile_page(page)
        page.update()

    top_row = ft.Row(
        [
            ft.Button(f"Profil", on_click=go_to_profile)
        ],
        alignment = ft.MainAxisAlignment.END,
    )

    dashboard_content = ft.Column(
        [
            ft.Text(f"Ez lesz a dashboard felület", weight=ft.FontWeight.BOLD, size=15)
        ],
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        expand = True
    )


    page.add(
        ft.Container(content = top_row, padding = ft.Padding.only(right = 20, top = 10)),
        dashboard_content
    )
    page.update()