import flet as ft
import random
import string
from sqlalchemy import func
from database import SessionLocal, Jatekos, JatekosErv, Jatek, JelenlegiKor, NulladikKor, JatekosJatek


def show_dashboard(page:ft.Page, current_user:str, on_logout, on_profile_click, on_connect_click, on_create_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def go_to_profile(e):
        on_profile_click()

    #felhasználó adatok lekérése
    db = SessionLocal()
    felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
    print(felhasznalo.__dict__)

    def go_to_connect(e):
        on_connect_click(felhasznalo.id)

    def go_to_create(e):
        db = SessionLocal()
        #Új játék ID meghatározása - az adatbázisban szereplő legnagyobb Jatek.id + 1
        max_id = db.query(func.max(Jatek.id)).scalar()
        uj_id = (max_id or 0) + 1

        #Új szobakód generálása
        while True:
            betuk = ''.join(random.choices(string.ascii_uppercase, k = 4)) #4 nagybetű generálása
            szamok = ''.join(random.choices(string.digits, k = 4)) #4 szám geneálása
            uj_szobakod = f"{betuk}-{szamok}"

            #Ellenőrizzük, hogy a generált kód egyedi-e
            letezo = db.query(Jatek).filter(Jatek.lobby_code == uj_szobakod).first()
            if not letezo: #Ha a generált egyedi, kilép a while ciklusból
                break

        #Új játék kezdeti adatainak felvétele az adatbázisba
        uj_jatek = Jatek(
            id = uj_id,
            cim = "Új játék (szerkesztés alatt)",
            lobby_code = uj_szobakod
        )
        db.add(uj_jatek)

        #Jelenlegi kör - az új játék a 0. körben tart
        uj_jelenlegi_kor = JelenlegiKor(
            jatek_id = uj_id,
            kor = 0
        )
        db.add(uj_jelenlegi_kor)

        #Nulladik kör eset létrehozása a későbbi javaslatokhoz
        uj_nulladik_kor = NulladikKor(
            jatek_id = uj_id
        )
        db.add(uj_nulladik_kor)

        #Játékos felvétele, mint az új játék játékmestere
        uj_jatekmester = JatekosJatek(
            jatek_id = uj_id,
            jatekos_id = felhasznalo.id,
            jatekmester = True
        )
        db.add(uj_jatekmester)

        #Új adatok mentése
        db.commit()

        #Átirányítás a "Játék létrehozása oldalra
        on_create_click(current_user, uj_id)

    #Érvek lekérése adatokkal
    erveim = db.query(JatekosErv, Jatek).join(Jatek, JatekosErv.jatek_id == Jatek.id).filter(JatekosErv.jatekos_id == felhasznalo.id).all()
    erv_lista = ft.Column(
        controls=[
            ft.Column(
                controls=[
                    #Egy érv szét van szedve 3 ft.Text-re, hogy külön formázhatók legyenek a szöveg bizonyos részei
                    ft.Text(
                        spans=[
                            ft.TextSpan(f"{jatek.cim}", ft.TextStyle(weight=ft.FontWeight.BOLD)),
                            ft.TextSpan(f" - {erv.szerep} - ({erv.kor}. kör)"),
                        ]
                    ),
                    ft.Text(
                        f"{erv.erv}",
                        text_align=ft.TextAlign.JUSTIFY
                    ),
                    ft.Text(
                        f"Értékelés: {erv.ertekeles_atlag}\n",
                        weight=ft.FontWeight.BOLD
                    ),
                ],
                spacing=5,
            )
            for erv, jatek in erveim
        ],
        expand = True,
    )

    #Avatar színét kiválasztó függvény
    def szin(nev):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(nev) % len(colors_lookup)]

    def kezdobetu(nev):
        return nev[:1].capitalize()

    def kor_ellenoriz(jatek_cim):
        db = SessionLocal()
        try:
            cel_jatek = db.query(Jatek).filter(Jatek.cim == jatek_cim).first()
            print(f"Kattintva: {cel_jatek}")
            aktualis_kor = db.query(JelenlegiKor.kor).filter(JelenlegiKor.jatek_id == cel_jatek.id).first()
            print(f"Kör: {aktualis_kor}")
            if aktualis_kor.kor == 0:
                print("Átirányítás a create_game felületre...")
                on_create_click(current_user, cel_jatek.id)
        except Exception as e:
            print(f"Hiba a kör lekérése során: {e}")
        finally:
            db.close()

    top_row = ft.Row(
        [
            ft.Container(
                content = ft.CircleAvatar(
                    content = ft.Text(kezdobetu(felhasznalo.felhasznalonev)),
                    bgcolor = szin(felhasznalo.felhasznalonev),
                    color = "white",
                    radius = 20
                ),
                on_click = go_to_profile,
                tooltip = "Profil megnyitása"
            )
        ],
        alignment = ft.MainAxisAlignment.END,
    )

    dashboard_content = ft.Column(
        [
            ft.Text(f"Saját érveim", weight=ft.FontWeight.BOLD, size=30),
            erv_lista
        ],
        expand = True
    )

    #Az oldal két részre bontása a menüsáv kialakításához
    #Oldalsáv
    #Gombok
    gombok = ft.Column(
        controls = [
            ft.Button("Csatlakozás játékhoz", width = 210, on_click = go_to_connect),
            ft.Button("Játék létrehozása", width = 210, on_click = go_to_create),
        ]
    )
    #Játékok
    #Saját játékok lekérése
    jatekaim = (
        db.query(Jatek, JelenlegiKor.kor)
        .join(JatekosJatek, Jatek.id == JatekosJatek.jatek_id)
        .join(JelenlegiKor, Jatek.id == JelenlegiKor.jatek_id)
        .filter(JatekosJatek.jatekos_id == felhasznalo.id).all()
    )

    jatekok = ft.Column(
        controls = [
            ft.Column(
                controls=[
                    #A címeket plusz ft.Container-be kell tenni, hogy később kattinthatók legyenek
                    ft.Container(content = ft.Text(f"{jatek.cim} - {kor}. kör"), on_click = lambda e, cim = jatek.cim: kor_ellenoriz(cim))
                ]
            )
            for jatek, kor in jatekaim
        ],
        scroll = ft.ScrollMode.AUTO,
    )
    sidebar = ft.Container(
        ft.Column(
            controls=[
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékaim:", weight=ft.FontWeight.BOLD),
                ft.Container(content = jatekok, padding = ft.Padding.only(left = 20, top = 10)),
            ],
        ),
        width = 250,
        #bgcolor = ft.Colors.LIGHT_BLUE #Világoskék háttérszín, hogy a tesztelés folyamán látható legyen a még üres menüsáv
    )

    #Fő blokk az érvekkel
    main_content = ft.Column(
        controls = [
            ft.Container(content = top_row, padding = ft.Padding.only(right = 20, top = 10)),
            dashboard_content,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand = True
    )

    page.add(
        ft.Row(
            controls = [
                sidebar,
                main_content
            ],
            expand = True
        )
    )
    db.close()
    page.update()