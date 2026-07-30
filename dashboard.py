import flet as ft
from services import dashboard_service
from game.events import jatek_topic, Uzenet

async def create_dashboard_view(
    page: ft.Page, current_user: str, on_logout, on_profile_click, on_connect_click,
    on_create_click, on_answer_click, on_main_game_click
):
    #Felhasználó adatainak lekérése
    felhasznalo = await dashboard_service.get_user(current_user)

    if not felhasznalo:
        return ft.View(route = "/dashboard", controls = [ft.Text("Hiba történt a felhasználó betöltésekor")])

    #Érvek és saját játékok betöltése
    erveim = await dashboard_service.get_user_arguments(felhasznalo.id)
    jatekaim = await dashboard_service.get_user_games(felhasznalo.id)

    #Eseménykezelő függvények
    async def go_to_profile(e):
        if on_profile_click: await on_profile_click()

    #Csatlakozás játékhoz popup
    code_input = ft.TextField(
        label = "Szoba kódja",
        width = 300,
        autofocus = True
    )

    error_text = ft.Text(
        value = "",
        color = ft.Colors.RED,
        visible = False
    )

    async def cancel_connect_click(e):
        page.pop_dialog()
        page.update()

    async def attempt_connect(e):
        beirt_kod = code_input.value
        if not beirt_kod:
            error_text.value = "Kérlek add meg a szoba kódját!"
            error_text.color = ft.Colors.RED
            error_text.visible = True
            page.update()
            return

        #Service meghívása az adatbázis műveletekhez
        sikeres, msg, jatek_id = await dashboard_service.connect_to_game(felhasznalo.id, beirt_kod)

        if sikeres:
            error_text.value = msg,
            error_text.color = ft.Colors.GREEN
            error_text.visible = True

            #Pubsub csatorna értesítése
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_JATEKOS)

            page.pop_dialog()

            #Játékaim lista frissítése az oldal újratöltése nélkül
            uj_jatekaim = await dashboard_service.get_user_games(felhasznalo.id)
            jatekok.controls.clear()
            for jatek, kor, jatekmester in uj_jatekaim:
                jatekok.controls.append(
                    ft.Column(
                        controls = [
                            ft.Container(
                                content = ft.Text(f"{jatek.cim} - {kor}. kör"),
                                on_click = create_kor_ellenoriz_handler(jatek.cim)
                            )
                        ]
                    )
                )
            page.update()
        else:
            error_text.value = msg
            error_text.color = ft.Colors.ORANGE if "Már csatlakoztál" in msg else ft.Colors.RED
            error_text.visible = True
            page.update()

    code_input.on_submit = attempt_connect

    connect_dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Csatlakozás játékhoz"),
        content = ft.Column(
            controls = [
                code_input,
                error_text
            ],
            tight = True
        ),
        actions = [
            ft.Button("Mégse", on_click = cancel_connect_click),
            ft.Button("Csatlakozás", on_click = attempt_connect)
        ]
    )

    async def go_to_connect(e):
        code_input.value = ""
        error_text.visible = False
        page.show_dialog(connect_dialog)
        page.update()

    async def go_to_create(e):
        uj_id = await dashboard_service.create_new_game(felhasznalo.id)
        if on_create_click: await on_create_click(current_user, uj_id)

    #Segédfüggvény a dinamikus kattintások (játékra kattintás) kezelésére
    def create_kor_ellenoriz_handler(jatek_cim):
        async def handler(e):
            jatek_id, aktualis_kor, is_jatekmester = await dashboard_service.get_game_status(jatek_cim, felhasznalo.id)
            if jatek_id is None:
                return

            #Átirányítás a jogosultságoknak megfelelően
            if aktualis_kor == 0:
                if is_jatekmester:
                    print("Játékmester, átirányítás a játék szerkesztése felületre...")
                    if on_create_click: await on_create_click(current_user, jatek_id)
                else:
                    print("Játékos, átirányítás a kérdőív felüetre...")
                    if on_answer_click: await on_answer_click(jatek_id)
            elif aktualis_kor > 0:
                if is_jatekmester:
                    print("Játékmester, átirányítás a kezelőfelületre...")
                    #Ide jön majd a game_master_dashboard
                else:
                    print("Játékos, átirányítás a játékra...")
                    if on_main_game_click: await on_main_game_click(jatek_id)
        return handler

    #UI összeállítása
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
            ft.Colors.YELLOW
        ]
        return colors_lookup[hash(nev) % len(colors_lookup)]
    def kezdobetu(nev):
        return nev[0].capitalize() if nev else "?"

    top_row = ft.Row(
        controls = [
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
        alignment = ft.MainAxisAlignment.END
    )

    erv_lista = ft.Column(
        controls = [
            ft.Column(
                controls = [
                    ft.Text(
                        spans = [
                            ft.TextSpan(f"{jatek.cim}", ft.TextStyle(weight = ft.FontWeight.BOLD)),
                            ft.TextSpan(f"{erv.szerep} - ({erv.kor}. kör)")
                        ]
                    ),
                    ft.Text(f"{erv.erv}", text_align = ft.TextAlign.JUSTIFY),
                    ft.Text(f"Értékelés: {erv.ertekeles_atlag}\n", weight = ft.FontWeight.BOLD),
                ],
                spacing = 5
            )
            for erv, jatek in erveim
        ],
        expand = True
    )

    dashboard_content =ft.Column(
        controls = [
            ft.Text("Saját érveim: ", weight = ft.FontWeight.BOLD, size = 30),
            erv_lista
        ],
        expand = True
    )

    gombok = ft.Column(
        controls = [
            ft.Button("Csatlakozás játékhoz", width = 210, on_click = go_to_connect),
            ft.Button("Játék létrehozása", width = 210, on_click = go_to_create)
        ]
    )

    jatekok = ft.Column(
        controls = [
            ft.Column(
                controls = [
                    ft.Container(
                        content = ft.Text(f"{jatek.cim} - {kor}. kör"),
                        on_click = create_kor_ellenoriz_handler(jatek.cim)
                    )
                ]
            )
            for jatek, kor, jatekmester in jatekaim
        ],
        scroll = ft.ScrollMode.AUTO
    )

    sidebar = ft.Container(
        content = ft.Column(
            controls = [
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékaim:", weight = ft.FontWeight.BOLD),
                ft.Container(content = jatekok, padding = ft.Padding.only(left = 20, top = 10))
            ],
        ),
        expand = 1
    )

    main_content = ft.Column(
        controls = [
            ft.Container(content = top_row, padding = ft.Padding.only(right = 20, top = 10)),
            dashboard_content,
        ],
        scroll = ft.ScrollMode.AUTO,
        expand = 3
    )

    #Visszatérés a View-val, amit a main.py hozzáadhat a view listához
    return ft.View(
        route = "/dashboard",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Row(
                controls = [
                    sidebar,
                    main_content,
                ],
                expand = True
            )
        ]
    )