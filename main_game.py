import flet as ft
from database import (
    SessionLocal, Jatek, JatekosJatek, Jatekos, Szerep, JelenlegiKor,
    SoronVan, JatekosSzerep, JatekosErv, Dijak, DijSzavazas, DijatKapott, NulladikKor
)

def show_game_page(page:ft.Page,jatek_id, current_user, on_back_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(ft.Text("Ez lesz a fő játék oldal", size = 30, weight = ft.FontWeight.BOLD))