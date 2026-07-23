import flet as ft
from database import (
    SessionLocal, Jatek, JatekosJatek, Jatekos, Szerep, JelenlegiKor,
    SoronVan, JatekosSzerep, JatekosErv, Dijak, DijSzavazas, DijatKapott, NulladikKor
)

#Érv kártya custom control osztály
class ErvKartya(ft.Container):
    def __init__(self, jatekos_nev: str, kor:int, erv_szoveg: str, ertekeles_atlag: float):
        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jatekos_nev}", size = 16, weight = "bold"),
                        ft.Text(f"{kor}. kör", italic = True, size = 14, color = "onSurfaceVariant")
                    ]
                ),
                ft.Text(erv_szoveg, text_align = "justify"),
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.STAR, color = "amber", size = 18),
                        ft.Text(f"Értékelés: {ertekeles_atlag}", weight = "w500"),
                    ],
                    alignment = "end"
                )
            ]
        )

        #Keret definiálása
        vonal = ft.BorderSide(1, "outline")
        keret = ft.Border(top = vonal, right = vonal, bottom = vonal, left = vonal)

        #Margó definiálása
        margo = ft.Margin(left = 0, bottom = 0, right = 0, top = 0)

        super().__init__(
            content = kartya_tartalom,
            padding = 15,
            border_radius = 8,
            border = keret,
            margin = margo,
            bgcolor = "surfaceVariant"
        )
def show_game_page(page:ft.Page,jatek_id, current_user, on_back_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    #Korábbi érveket tároló oszlop
    korabbi_ervek = ft.Column()

    #Korábbi érvek lekérése
    def betolt_korabbi_ervek():
        db = SessionLocal()
        try:
            #Felhasználó adatainak lekérése
            felhasznalo = db.query(Jatekos).filter(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            ).first()

            if not felhasznalo: return

            #Aktuális kör lekérése
            aktualis_kor = db.query(JelenlegiKor.kor).filter(JelenlegiKor.jatek_id == jatek_id).scalar()

            #Játékos szerepének lekérése
            aktualis_szerep = db.query(JatekosSzerep.szerep).filter(
                JatekosSzerep.jatek_id == jatek_id,
                JatekosSzerep.jatekos_id == felhasznalo.id,
                JatekosSzerep.kor == aktualis_kor
            ).scalar()

            #Korábbi érvek lekérése, ahol a kör kisebb, mint a jelenlegi és a szerep megegyezik a játékos szerepével
            ervek = db.query(JatekosErv, Jatekos).join(
                Jatekos, JatekosErv.jatekos_id == Jatekos.id
            ).filter(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.szerep == aktualis_szerep,
                JatekosErv.kor < aktualis_kor,
            ).order_by(JatekosErv.kor.desc()).all()

            #Felület kiürítése és újra feltöltése
            korabbi_ervek.controls.clear()
            korabbi_ervek.controls.append(
                ft.Text(f"Korábbi érvek a(z) {aktualis_szerep} szerepből:", size = 20, weight = ft.FontWeight.BOLD)
            )
            if not ervek:
                korabbi_ervek.controls.append(ft.Text("Ehhez a szerephez még nem születtek érvek"))
            else:
                for erv, erv_szerzo in ervek:
                    #Custom kártya példányosítása
                    kartya = ErvKartya(
                        jatekos_nev = erv_szerzo.felhasznalonev,
                        kor = erv.kor,
                        erv_szoveg = erv.erv,
                        ertekeles_atlag = erv.ertekeles_atlag
                    )
                    korabbi_ervek.controls.append(kartya)
            page.update()

        except Exception as e:
            print(f"Hiba a korábbi érvek betöltése során: {e}")
            korabbi_ervek.controls.append(ft.Text("Hiba az érvek betöltésekor"))
            page.update()
        finally:
            db.close()

    page.add(korabbi_ervek)

    betolt_korabbi_ervek()