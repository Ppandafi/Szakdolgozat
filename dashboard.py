import flet as ft
from flet.controls import border

from services import dashboard_service
from game.events import jatek_topic, Uzenet

async def create_dashboard_view(
    page: ft.Page, current_user: str, on_logout, on_profile_click, on_connect_click,
    on_create_click, on_answer_click, on_main_game_click, on_gm_dashboard_click, on_summary_click = None
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
        autofocus = True,
        prefix_icon = ft.Icons.KEY,
        border_radius = 8,
        filled = True
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
                                content = ft.Row(
                                    controls = [
                                        *get_game_icons(jatek, jatekmester),
                                        ft.Text(f"{jatek.cim} - {kor}. kör")
                                    ]
                                ),
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
        modal = False,
        shape = ft.RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.LOGIN, color=ft.Colors.PRIMARY),
                ft.Text("Csatlakozás játékhoz", weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY)
            ]
        ),
        content = ft.Column(
            controls = [
                ft.Text("Kérlek add meg a szobakódot a játékhoz való csatlakozáshoz!", size = 14, color = ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height = 10),
                code_input,
                error_text
            ],
            tight = True,
            horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        ),
        actions = [
            ft.TextButton("Mégse", on_click = cancel_connect_click),
            ft.FilledButton("Csatlakozás", icon = ft.Icons.ARROW_FORWARD, on_click = attempt_connect)
        ],
        actions_padding = ft.Padding(right = 20, bottom = 20, left = 20, top = 10),
        content_padding = ft.Padding(left = 10, right = 10, top = 10, bottom = 10)
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
            jatek_id, aktualis_kor, is_jatekmester, jatek_lezarva, eredmenyek_osszegezve = await dashboard_service.get_game_status(jatek_cim, felhasznalo.id)
            if jatek_id is None:
                return

            #Átirányítás, ha már lezárt játékba akarunk belépni
            if jatek_lezarva:
                if eredmenyek_osszegezve:
                    print("Eredmények összegezve, átirányítás a summary felületre...")
                    if on_summary_click: await on_summary_click(jatek_id)
                else:
                    if is_jatekmester:
                        print("Játék lezárva, de még nincs összegezve; átirányítás a játékmester kezelőfelületre...")
                        if on_gm_dashboard_click: await on_gm_dashboard_click(jatek_id)
                    else:
                        print("Játék lezárva, átriányítás a játék utáni kérdőívre...")
                        if on_answer_click: await on_answer_click(jatek_id)

                return

            #Átirányítás a jogosultságoknak megfelelően (ha még tart a játék)
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
                    if on_gm_dashboard_click: await on_gm_dashboard_click(jatek_id)
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
            ft.Text("Saját érveim", weight=ft.FontWeight.BOLD, size=32, color=ft.Colors.PRIMARY),
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
        alignment = ft.MainAxisAlignment.SPACE_BETWEEN
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
                spacing = 5,
            )
            for erv, jatek in erveim
        ],
        expand = True,
        horizontal_alignment = ft.CrossAxisAlignment.STRETCH
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
            ft.FilledButton("Csatlakozás játékhoz", height = 45, icon = ft.Icons.LOGIN, on_click = go_to_connect),
            ft.FilledButton("Játék létrehozása", height = 45, icon = ft.Icons.ADD_CIRCLE, on_click = go_to_create),
        ],
        spacing = 45,
        horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    )

    #Segédfüggvény az ikonok betöltéséhez
    def get_game_icons(jatek, jatekmester):
        icons = []

        #játékmester ikon
        if jatekmester:
            icons.append(ft.Icon(ft.Icons.MANAGE_ACCOUNTS, color = "amber", tooltip = "játékmester vagy"))

        #státusz ikonok
        if getattr(jatek, 'eredmenyek_osszesitve', False):
            icons.append(ft.Icon(ft.Icons.EMOJI_EVENTS, color = "green", tooltip = "összegezve, eredmények elérhetők"))
        elif getattr(jatek, 'jatek_lezarva', False):
            icons.append(ft.Icon(ft.Icons.DONE_ALL, color = "blue", tooltip = "lezárva (összesítsésre vár)"))

        return icons

    jatekok = ft.Column(
        controls = [
            ft.Container(
                content = ft.Row(
                    controls = [
                        *get_game_icons(jatek, jatekmester),
                        ft.Text(f"{jatek.cim} - {kor}.kör", weight = ft.FontWeight.W_500),
                    ]
                ),
                padding = ft.Padding(5, 5, 5, 5),
                border_radius = 8,
                ink = True,
                on_click = create_kor_ellenoriz_handler(jatek.cim)
            )
            for jatek, kor, jatekmester in jatekaim
        ],
        scroll = ft.ScrollMode.AUTO
    )

    sidebar = ft.Card(
        elevation = 4,
        margin = ft.Margin(0, 0, 10, 0),
        content = ft.Container(
            padding = 30,
            content = ft.Column(
                controls = [
                    ft.Text("Vezérlőpult", size = 24, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    gombok,
                    ft.Divider(height = 40),
                    ft.Text("Játékaim:", size = 18, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Container(content = jatekok, padding = ft.Padding.only(top = 10), expand = True)
                ]
            )
        ),
        expand = 1
    )

    main_content = ft.Card(
        elevation = 4,
        margin = ft.Margin(10, 0, 0, 0),
        content = ft.Container(
            padding = 30,
            content = ft.Column(
                controls = [
                    top_row,
                    ft.Divider(height=20),
                    ft.Column(
                        controls = [
                            erv_lista
                        ],
                        scroll = ft.ScrollMode.AUTO,
                        expand = True
                    )
                ],
                expand = True
            )
        ),
        expand = 3
    )

    sidebar.col = {"xs": 12, "md": 4, "lg": 3}
    main_content.col = {"xs": 12, "md": 8, "lg": 9}

    #Visszatérés a View-val, amit a main.py hozzáadhat a view listához
    dashboard_view = ft.View(
        route = "/dashboard",
        #scroll=ft.ScrollMode.AUTO,
        #bgcolor = ft.Colors.ON_SURFACE_VARIANT,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.ResponsiveRow(
                controls = [
                    sidebar,
                    main_content,
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.CENTER,
            )
        ]
    )

    def page_resize(e = None):
        if page.route != "/dashboard":
            return

        is_mobile = page.width < 768

        if is_mobile:
            dashboard_view.scroll = ft.ScrollMode.AUTO
            sidebar.expand = False
            main_content.expand = False
            sidebar.height = 450
            main_content.height = 700
        else:
            dashboard_view.scroll = None
            sidebar.expand = 1
            main_content.expand = 3
            sidebar.height = None
            main_content.height = None

        page.update()

    page.on_resize = page_resize
    page_resize()

    return dashboard_view