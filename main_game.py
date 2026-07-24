from datetime import datetime
import flet as ft
from database import (
    SessionLocal, Jatek, JatekosJatek, Jatekos, Szerep, JelenlegiKor,
    SoronVan, JatekosSzerep, JatekosErv, Dijak, DijSzavazas, DijatKapott, NulladikKor
)

#Érv kártya custom control osztály
class ErvKartya(ft.Container):
    def __init__(self, jatekos_nev: str, cimke: str, erv_szoveg: str, ertekeles_atlag: float, ertekeles_lathato: bool):
        #Kártya tartalom inicializálása
        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jatekos_nev}", size = 16, weight = "bold"),
                        ft.Text(f"{cimke}", italic = True, size = 14, color = "onSurfaceVariant")
                    ]
                ),
                ft.Text(erv_szoveg, text_align = "justify")
            ]
        )

        if ertekeles_lathato:
            kartya_tartalom.controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.STAR, color="amber", size=18),
                        ft.Text(f"Értékelés: {ertekeles_atlag}", weight="w500"),
                    ],
                    alignment="end"
                )
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

    ertekelo_oszlop = ft.Column(
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
    )

    #Korábbi érveket tároló oszlop
    korabbi_ervek = ft.Column(expand = True)

    #Kártyákat tároló oszlop
    kartyak = ft.Column(
        scroll = ft.ScrollMode.AUTO,
        expand = True
    )

    #Érvelés beviteli mező
    erveles = ft.TextField(label = "Ide írd az érvelésed", expand = True)

    def send_argument(felhasznalo, aktualis_szerep, aktualis_kor):
        db = SessionLocal()
        print("Érv küldése...")
        try:
            uj_erv = JatekosErv(
                jatek_id=jatek_id,
                jatekos_id=felhasznalo.id,
                szerep=aktualis_szerep,
                kor=aktualis_kor,
                erv=erveles.value,
                time=datetime.now()
            )
            print(uj_erv.erv)
            db.add(uj_erv)
            db.commit()
            erveles.value = ""
            page.update()
            page.pubsub.send_all_on_topic(f"jatek_{jatek_id}", "uj_erveles")
        except Exception as e:
            db.rollback()
            print(f"Hiba az érv mentése során: {e}")
        finally:
            db.close()

    #Érv értékelése
    def ertekelo_felulet():
        db = SessionLocal()
        try:
            #Adatok lekérése
            #aktuális felhasználó
            felhasznalo = db.query(Jatekos).filter(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            ).first()
            #aktuális kör
            aktualis_kor = db.query(JelenlegiKor.kor).filter(JelenlegiKor.jatek_id == jatek_id).scalar()
            #soron levő játékos id
            soron_levo = db.query(SoronVan.jatekos_id).filter(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == aktualis_kor
            ).order_by(SoronVan.time.desc()).first()
            #soron levő játékos adatai
            soron_levo_jatekos = db.query(Jatekos).filter(Jatekos.id == soron_levo[0]).first()
            #soron levő játékos szerepe
            soron_levo_szerep = db.query(JatekosSzerep.szerep).filter(
                JatekosSzerep.jatek_id == jatek_id,
                JatekosSzerep.kor == aktualis_kor,
                JatekosSzerep.jatekos_id == soron_levo_jatekos.id
            ).scalar()
            #soron levő játékos érvelése
            soron_levo_erv = db.query(JatekosErv.erv).filter(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.kor == aktualis_kor,
                JatekosErv.jatekos_id == soron_levo_jatekos.id
            ).scalar()

            #Ellenőrzés: ha az aktuális és a soron levő játékos megegyezik, nem írjuk ki neki az új érvet
            if felhasznalo and felhasznalo.id == soron_levo_jatekos.id:
                ertekelo_oszlop.controls.clear()
                page.update()
                return #kilépés, hogy ne is generálja le az érvkártyát

            #Kártya feltöltése
            kartya = ErvKartya(
                jatekos_nev = soron_levo_jatekos.felhasznalonev,
                cimke = soron_levo_szerep,
                erv_szoveg = soron_levo_erv,
                ertekeles_atlag = 0,
                ertekeles_lathato = False
            )

            if soron_levo_erv:
                ertekelo_oszlop.controls.clear()
                ertekelo_oszlop.controls.append(kartya)
                ertekelo_oszlop.controls.append(
                    ft.Row(
                        controls = [
                            ft.SegmentedButton(
                                segments=[ft.Segment(value=str(i), label=ft.Text(str(i))) for i in range(1, 11)],
                                allow_multiple_selection=False,
                                selected=["5"],
                                expand=True
                            ),
                            ft.Button("Küldés")
                        ],
                        expand = True
                    )
                )
            else:
                ertekelo_oszlop.controls.clear()
                ertekelo_oszlop.controls.append(ft.Text("A soron levő játékos még nem érvelt, kérlek várj..."))
            page.update()

        except Exception as e:
            print(f"Hiba az értékelendő érv betöltésekor: {e}")
        finally:
            db.close()

    def handle_pubsub_message(topic, message):
        if message == "uj_erveles":
            ertekelo_felulet()

    page.pubsub.subscribe_topic(f"jatek_{jatek_id}", handle_pubsub_message)


    #Korábbi érvek lekérése
    def betolt_korabbi_ervek():

        # Küldés gomb
        send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            on_click=lambda e: send_argument(felhasznalo, aktualis_szerep, aktualis_kor),
            disabled = False
        )

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

            #Lekérjük, hogy a játékos éppen soron van-e
            #Soron levő játékos ID lekérdezése
            soron_levo = db.query(SoronVan.jatekos_id).filter(
                SoronVan.jatek_id == jatek_id,
                SoronVan.kor == aktualis_kor,
            ).order_by(SoronVan.time.desc()).first()

            soron_van = (soron_levo[0] == felhasznalo.id)
            print(f"Soron van = {felhasznalo.felhasznalonev} {soron_van}")

            #Soron levő játékos érvének lekérése - remélhetőleg üres értéket ad, csak a küldés gomb letiltásához kell
            soron_levo_erv = db.query(JatekosErv.erv).filter(
                JatekosErv.jatek_id == jatek_id,
                JatekosErv.kor == aktualis_kor,
                JatekosErv.jatekos_id == soron_levo[0]
            ).scalar()

            #Ha már a játékos érvelt, a küldés gombot letiltjuk
            if soron_levo_erv:
                send_button.disabled = True
                page.update()

            #Felület kiürítése és újra feltöltése
            korabbi_ervek.controls.clear()
            ertekelo_oszlop.controls.clear()
            kartyak.controls.clear()
            if soron_van:
                #Csak az érvelő felület látszódjon
                korabbi_ervek.visible = True
                ertekelo_oszlop.visible = False

                #Ha a játékos éppen soron van, akkor a korábbi érveket látja
                kartyak.controls.append(
                    ft.Text(f"Korábbi érvek a(z) {aktualis_szerep} szerepből:", size=20, weight=ft.FontWeight.BOLD)
                )
                if not ervek:
                    kartyak.controls.append(ft.Text("Ehhez a szerephez még nem születtek érvek"))
                else:
                    for erv, erv_szerzo in ervek:
                        # Custom kártya példányosítása
                        kartya = ErvKartya(
                            jatekos_nev=erv_szerzo.felhasznalonev,
                            cimke = f"{erv.kor}. kör",
                            erv_szoveg=erv.erv,
                            ertekeles_atlag=erv.ertekeles_atlag,
                            ertekeles_lathato= True
                        )
                        kartyak.controls.append(kartya)
                korabbi_ervek.controls.append(kartyak)
                korabbi_ervek.controls.append(
                    ft.Row(
                        controls=[
                            erveles,
                            send_button
                        ]
                    )
                )
            else:
                #Ha a játékos nincsen soron, csak az értékelő oszlop látszódjon
                korabbi_ervek.visible = False
                ertekelo_oszlop.visible = True
                ertekelo_felulet()
            page.update()

        except Exception as e:
            print(f"Hiba a korábbi érvek betöltése során: {e}")
            korabbi_ervek.controls.append(ft.Text("Hiba az érvek betöltésekor"))
            page.update()
        finally:
            db.close()

    page.add(korabbi_ervek, ertekelo_oszlop)

    ertekelo_felulet()

    betolt_korabbi_ervek()