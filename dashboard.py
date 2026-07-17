import flet as ft
from database import SessionLocal, Jatekos, JatekosErv, Jatek


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
        on_create_click(felhasznalo.id)

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
    #Csak a játék címek kigyűjtése
    jatek_cimek = {}
    for erv, jatek in erveim:
        jatek_cimek[jatek.id] = jatek

    jatekok = ft.Column(
        controls = [
            ft.Column(
                controls=[
                    ft.Text(f"{jatek.cim}")
                ]
            )
            for jatek in jatek_cimek.values()
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