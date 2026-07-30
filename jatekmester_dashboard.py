import flet as ft
from game.events import jatek_topic, Uzenet

async def create_gm_dashboard_view(page: ft.Page, jatek_id: int):
    return ft.View(
        route = "/gm_dashboard",
        controls = [
            ft.Text("Ez lesz a játékmester kezelőfelület", size = 30, weight = ft.FontWeight.BOLD),
        ]
    )