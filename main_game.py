import flet as ft
from database import (
    SessionLocal, Jatek, JatekosJatek, Jatekos, Szerep, JelenlegiKor,
    SoronVan, JatekosSzerep, JatekosErv, Dijak, DijSzavazas, DijatKapott, NulladikKor
)

#Érv kártya custom control osztály
class ErvKartya(ft.Container):
    def __init__(self, jateks_nev: str, szerep: str, erv_szoveg: str, ertekeles_atlag: float):
        super().__init__()
        #Kárya stílusának megadása
        self.padding = 15
        self.border_radius = 8
        self.border = ft.Border.all(1, ft.Colors.OUTLINE)
        self.margin = ft.Margin.only(bottom = 10)
        self.bgcolor = ft.Colors.SURFACE_VARIANT

        #Kártya tartalmának felépítése
        self.content = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jateks_nev}", size = 16, weight = ft.FontWeight.BOLD),
                        ft.Text(f"{szerep}", italic = True, size = 14, color = ft.Colors.ON_SURFACE_VARIANT)
                    ]
                ),
                ft.Text(erv_szoveg, text_align = ft.TextAlign.JUSTIFY),
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.STAR, color = ft.Colors.AMBER, size = 18),
                        ft.Text(f"Értékelés: {ertekeles_atlag}", weight = ft.FontWeight.W_500)
                    ],
                    alignment = ft.MainAxisAlignment.END
                )
            ]
        )

def show_game_page(page:ft.Page,jatek_id, current_user, on_back_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(ft.Text("Ez lesz a fő játék oldal", size = 30, weight = ft.FontWeight.BOLD))