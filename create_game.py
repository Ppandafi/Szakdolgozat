import flet as ft

from services import create_game_service, gm_dashboard_service
from game.events import jatek_topic, Uzenet

async def create_game_view(page: ft.Page, uj_id: int, on_cancel, on_gm_click):
    #Felhasználó lekérése session-ből
    current_user = page.session.store.get("current_user")

    #Kezdeti adatok betöltése
    szerkesztett_jatek = await create_game_service.get_game_by_id(uj_id)
    felhasznalo = await create_game_service.get_user_by_identifier(current_user)

    async def cancel_click(e):
        page.show_dialog(backdialog)
        page.update()

    async def confirm_cancel(e):
        sikeres = await create_game_service.delete_game(uj_id)
        page.pop_dialog()
        if sikeres:
            await on_cancel()

    async def decline_cancel(e):
        page.pop_dialog()
        page.update()

    #Játék törlése ablak
    backdialog = ft.AlertDialog(
        modal = False,
        shape = ft.RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ERROR),
                ft.Text("Játék elvetése", weight = ft.FontWeight.BOLD, color = ft.Colors.ERROR),
            ]
        ),
        content = ft.Column(
            controls = [
                ft.Text(
                    "Biztosan törölni szeretnéd a játékot? Ezt a műveletet később nem vonhatod vissza",
                    size = 14, color = ft.Colors.ON_SURFACE_VARIANT
                )
            ],
            tight = True,
            horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        ),
        actions = [
            ft.TextButton("Szerkesztés folytatása", on_click = decline_cancel),
            ft.FilledButton(
                "Játék törlése",
                icon = ft.Icons.DELETE_FOREVER,
                style = ft.ButtonStyle(bgcolor = ft.Colors.ERROR, color = ft.Colors.WHITE),
                on_click = confirm_cancel
            )
        ],
        actions_padding = ft.Padding(right = 20, bottom = 20, left = 20, top = 10),
        content_padding = ft.Padding(left = 24, right = 24, top = 10, bottom = 10)
    )

    csatlakozok_lista = ft.Column()

    #Játékhoz csatlakozott játékosok lekérése
    async def update_csatlakozott_jatekosok(topic=None, uzenet=None):
        resztvevok = await create_game_service.get_connected_players(uj_id)
        csatlakozok_lista.controls.clear()
        csatlakozok_lista.controls.append(ft.Text("Csatlakozott játékosok: ", weight = ft.FontWeight.BOLD, size = 20))

        for nev in resztvevok:
            if felhasznalo and nev == felhasznalo.felhasznalonev:
                csatlakozok_lista.controls.append(ft.Text(f"- {nev} (Ön)"))
            else:
                csatlakozok_lista.controls.append(ft.Text(f"- {nev}"))
        page.update()

    page.pubsub.subscribe_topic(jatek_topic(uj_id), update_csatlakozott_jatekosok)
    await update_csatlakozott_jatekosok()

    javaslatok_lista = ft.Column()

    #Javaslatok lekérése
    async def update_javaslatok(topic=None, uzenet=None):
        javaslatok = await create_game_service.get_suggestions(uj_id)
        javaslatok_lista.controls.clear()
        javaslatok_lista.controls.append(ft.Text("Javaslatok: ", size = 20, weight = ft.FontWeight.BOLD))

        for j in javaslatok:
            tipus = "szerep" if j.szerep_dij == 1 else "dij"
            javaslatok_lista.controls.append(
                ft.Row(
                    controls = [
                        ft.Text(f"{j.javaslat} - "),
                        ft.Text(tipus, weight = ft.FontWeight.BOLD)
                    ]
                )
            )
        page.update()

    page.pubsub.subscribe_topic(jatek_topic(uj_id), update_javaslatok)
    await update_javaslatok()

    #Bal oldali menüsáv
    l_sidebar = ft.Card(
        elevation = 4,
        margin = ft.Margin(0, 0, 10, 0),
        content = ft.Container(
            padding = 20,
            content = ft.Column(
                controls = [
                    ft.Text("Közösség & Javaslatok", size = 20, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    ft.Container(content = csatlakozok_lista),
                    ft.Divider(height = 20),
                    ft.Container(content = javaslatok_lista)
                ],
                scroll = ft.ScrollMode.AUTO
            )
        ),
        expand = 1
    )

    #Eddig felvett adatokat kimutató szövegek
    cim_info = ft.Text(szerkesztett_jatek.cim if szerkesztett_jatek else "")
    szerep_info = ft.Column()
    dij_info = ft.Column()
    kerdes_info = ft.Column()
    min_info = ft.Text(str(szerkesztett_jatek.min_kor) if szerkesztett_jatek and szerkesztett_jatek.min_kor else "")
    max_info = ft.Text(str(szerkesztett_jatek.max_kor) if szerkesztett_jatek and szerkesztett_jatek.max_kor else "")

    async def feltolt_info():
        szerepek = await create_game_service.get_roles(uj_id)
        for sz in szerepek:
            szerep_info.controls.append(ft.Text(f"- {sz}"))

        dijak = await create_game_service.get_awards(uj_id)
        for d in dijak:
            dij_info.controls.append(ft.Text(f"- {d}"))

        kerdesek = await create_game_service.get_questions(uj_id)
        for k, jatek_elott_utan in kerdesek:
            tipus = "Játék előtt és után" if jatek_elott_utan else "Csak játék után"
            kerdes_info.controls.append(ft.Text(f"- {k} - {tipus}"))

    await feltolt_info()

    #Jobb oldali menüsáv
    r_sidebar = ft.Card(
        elevation = 4,
        margin = ft.Margin(10, 0, 0, 0),
        content = ft.Container(
            padding = 20,
            content = ft.Column(
                controls = [
                    ft.Text("Játék adatai:", size = 20, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    ft.Container(
                        content = ft.Text(f"SZOBAKÓD: {szerkesztett_jatek.lobby_code if szerkesztett_jatek else ''}", weight = ft.FontWeight.BOLD, size = 20, selectable = True, color = ft.Colors.SECONDARY),
                        #bgcolor = ft.Colors.ON_SURFACE_VARIANT,
                        padding = 10,
                        border_radius = 8
                    ),
                    ft.Divider(height = 20),
                    ft.Text("- Cím:", weight = ft.FontWeight.BOLD), cim_info,
                    ft.Row(
                        controls = [
                            ft.Text("Min. kör: ", weight = ft.FontWeight.BOLD), min_info,
                            ft.Text("Max. kör: ", weight = ft.FontWeight.BOLD), max_info,
                        ]
                    ),
                    ft.Text("- Szerepek:", weight = ft.FontWeight.BOLD), szerep_info,
                    ft.Text("- Díjak:", weight = ft.FontWeight.BOLD), dij_info,
                    ft.Text("- Kérdések:", weight = ft.FontWeight.BOLD), kerdes_info,
                ],
                scroll = ft.ScrollMode.AUTO
            )
        ),
        expand = 1
    )

    #Beviteli mezők
    title_input = ft.TextField(expand = True, border_radius = 8, filled = True, prefix_icon = ft.Icons.TITLE)
    description_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.DESCRIPTION)
    positions_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.WORK)
    awards_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.MILITARY_TECH)
    min_round_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.MINIMIZE)
    max_round_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.MAXIMIZE)
    question_input = ft.TextField(expand = True,  border_radius = 8, filled = True, prefix_icon = ft.Icons.QUESTION_MARK)
    elott_utan = ft.Dropdown(
        options = [
            ft.DropdownOption(key = "post", text = "Csak játék után"),
            ft.DropdownOption(key = "both", text = "Játék előtt és után")
        ],
        label = "Kérlek válassz...",
        border_radius = 8,
        filled = True,
        expand = True,
    )

    #Értesítő szövegek
    def create_alert_text():
        return ft.Text(value = "", color = ft.Colors.RED, visible = False)

    title_alert = create_alert_text()
    description_alert = create_alert_text()
    positions_alert = create_alert_text()
    awards_alert = create_alert_text()
    questions_alert = create_alert_text()
    min_round_alert = create_alert_text()
    max_round_alert = create_alert_text()

    async def save_title(e):
        if not title_input.value:
            title_alert.value = "Kérlek add meg a játék címét!"
            title_alert.color = ft.Colors.RED
        else:
            sikeres = await create_game_service.update_game_title(uj_id, title_input.value)
            if sikeres:
                cim_info.value = title_input.value
                title_alert.value = "Cím sikeresen mentve!"
                title_alert.color = ft.Colors.GREEN
                title_input.value = ""
            else:
                title_alert.value = "Hiba az adatbázis mentése során"
                title_alert.color = ft.Colors.RED
        title_alert.visible = True
        page.update()

    async def save_description(e):
        if not description_input.value:
            description_alert.value = "Kérlek add meg a játék ismertetését!"
            description_alert.color = ft.Colors.RED
        else:
            sikeres = await create_game_service.update_description(uj_id, description_input.value)
            if sikeres:
                description_alert.value = "Ismertetés sikeresen mentve!"
                description_alert.color = ft.Colors.GREEN
                description_input.value = ""
            else:
                description_alert.value = "Hiba az adatbázis mentése során!"
                description_alert.color = ft.Colors.RED
        description_alert.visible = True
        page.update()

    async def add_positon(e):
        if not positions_input.value:
            positions_alert.value = "Kérlek adj meg szerep(ek)et!"
            positions_alert.color = ft.Colors.RED
        else:
            tisztitott_szerepek = [sz.strip() for sz in positions_input.value.split(',') if sz.strip()]
            if not tisztitott_szerepek:
                positions_alert.value = "Kérlek érvényes formátumban (vesszővel elválasztva) add meg a szerepeket!"
                positions_alert.color = ft.Colors.RED
            else:
                egyedi_szerepek = list(dict.fromkeys(tisztitott_szerepek))
                hozzaadott = await create_game_service.add_roles(uj_id, egyedi_szerepek)

                if hozzaadott > 0:
                    for uj_sz in egyedi_szerepek[-hozzaadott:]:
                        szerep_info.controls.append(ft.Text(f"{uj_sz}"))
                    positions_alert.value = f"{hozzaadott} új szerep hozzáadva!"
                    positions_alert.color = ft.Colors.GREEN
                    positions_input.value = ""
                elif hozzaadott == 0:
                    positions_alert.value = "A megadott szerep(ek) már szerepel(nek)!"
                    positions_alert.color = ft.Colors.RED
                else:
                    positions_alert.value = "Hiba az adatbázis mentése során"
                    positions_alert.color = ft.Colors.RED

        positions_alert.visible = True
        page.update()

    async def add_award(e):
        if not awards_input.value:
            awards_alert.value = "Kérlek add meg a díj(ak)at!"
            awards_alert.color = ft.Colors.RED
        else:
            dijak_tisztitott = [dij.strip() for dij in awards_input.value.split(',') if dij.strip()]
            if not dijak_tisztitott:
                awards_alert.value = "Kérlek érvényes formátumban (vesszővel elválasztve) add meg a díjakat!"
                awards_alert.color = ft.Colors.RED
            else:
                egyedi_dijak = list(dict.fromkeys(dijak_tisztitott))
                hozzaadott = await create_game_service.add_awards(uj_id, egyedi_dijak)

                if hozzaadott > 0:
                    for uj_dij in egyedi_dijak[-hozzaadott:]:
                        dij_info.controls.append(ft.Text(f"{uj_dij}"))
                    awards_alert.value = f"{hozzaadott} új díj hozzáadva!"
                    awards_alert.color = ft.Colors.GREEN
                    awards_input.value = ""
                elif hozzaadott == 0:
                    awards_alert.value = "A megadott díj(ak) már szerepel(nek)!"
                    awards_alert.color = ft.Colors.RED
                else:
                    awards_alert.value = "Hiba az adatbázis mentése során"
                    awards_alert.color = ft.Colors.RED

        awards_alert.visible = True
        page.update()

    async def add_question(e):
        if not question_input.value:
            questions_alert.value = "Kérlek add meg a kérdést!"
            questions_alert.color = ft.Colors.RED
        elif not elott_utan.value:
            questions_alert.value = "Kérlek válassz a legördülő menüből!"
            questions_alert.color = ft.Colors.RED
        else:
            is_both = (elott_utan.value == "both")
            sikeres = await create_game_service.add_questions(uj_id, question_input.value, is_both)

            if sikeres:
                questions_alert.value = "Kérdés sikeresen felvéve!"
                questions_alert.color = ft.Colors.GREEN
                tipus_szoveg = "Játék előtt és után" if is_both else "Csak játék után"
                kerdes_info.controls.append(ft.Text(f"{question_input.value} - {tipus_szoveg}"))
                question_input.value = ""
                elott_utan.value = None
            else:
                questions_alert.value = "Hiba az adatbázis mentése során"
                questions_alert.color = ft.Colors.GREEN

        questions_alert.visible = True
        page.update()

    async def save_limit(e, input_field, alert_field, info_field, limit_type):
        if not input_field.value or not input_field.value.isdigit():
            alert_field.value = "Kérlek adj meg egy érvényes számot!"
            alert_field.color = ft.Colors.RED
        else:
            ertek = int(input_field.value)
            sikeres = await create_game_service.update_round_limits(uj_id, ertek, limit_type)
            if sikeres:
                info_field.value = str(ertek)
                alert_field.value = "Sikeresen mentve!"
                alert_field.color = ft.Colors.GREEN
                input_field.value = ""
            else:
                alert_field.value = "Hiba az adatbázis mentése során"
                alert_field.color = ft.Colors.RED

        alert_field.visible = True
        page.update()

    async def save_min(e):
        await save_limit(e, min_round_input, min_round_alert, min_info, "min")

    async def save_max(e):
        await save_limit(e, max_round_input, max_round_alert, max_info, "max")

    async def send_question(e):
        save_title_button.disabled = True
        save_description_button.disabled = True
        add_question_button.disabled = True
        save_min_button.disabled = True
        save_max_button.disabled = True

        sikeres = await create_game_service.set_questios_sent(uj_id)
        if sikeres:
            page.pubsub.send_all_on_topic(jatek_topic(uj_id), Uzenet.KERDOIVEK_PRE)
        else:
            print("Nem sikerült frissíteni az adatbázist a kérdőívek kiküldéséhez")
        page.update()

    async def start_game(e):
        sikeres, msg = await gm_dashboard_service.start_next_round(uj_id)

        if sikeres:
            await gm_dashboard_service.set_next_player(uj_id)
            await create_game_service.notify_game_started(uj_id)
            page.pubsub.send_all_on_topic(jatek_topic(uj_id), Uzenet.START_GAME)
            await on_gm_click()
        else:
            print(f"Hiba a játék indítása során: {msg}")

    flag = szerkesztett_jatek.kerdoivek_kikuldve if szerkesztett_jatek else False

    save_title_button = ft.FilledButton("Mentés", icon = ft.Icons.SAVE, disabled = flag, on_click = save_title)
    save_description_button = ft.FilledButton("Mentés", icon = ft.Icons.SAVE, disabled = flag, on_click = save_description)
    add_positon_button = ft.FilledButton("Hozzáad", disabled = False, icon = ft.Icons.ADD, on_click = add_positon)
    add_award_button = ft.FilledButton("Hozzáad", disabled = False, icon = ft.Icons.ADD, on_click = add_award)
    add_question_button = ft.FilledButton("Hozzáad", disabled = flag, icon = ft.Icons.ADD, on_click = add_question)
    save_min_button = ft.FilledButton("Mentés", disabled = flag, icon = ft.Icons.SAVE, on_click = save_min)
    save_max_button = ft.FilledButton("Mentés", disabled = flag, icon = ft.Icons.SAVE, on_click = save_max)
    send_question_button = ft.FilledButton("Kérdőívek kiküldése", icon = ft.Icons.SEND, disabled = flag, on_click = send_question)

    #Oszloparányok
    title_input.col = {"xs":12, "sm": 9}; description_input.col = {"xs": 12, "sm": 9}
    positions_input.col = {"xs": 12, "sm": 9}; awards_input.col = {"xs": 12, "sm": 9}
    save_title_button.col = {"xs": 12, "sm": 3}; save_description_button.col = {"xs": 12, "sm": 3}
    add_positon_button.col = {"xs": 12, "sm": 3}; add_award_button.col = {"xs": 12, "sm": 3}
    question_input.col = {"xs": 12, "md": 6}
    elott_utan.col = {"xs": 12, "md": 4}
    add_question_button.col = {"xs": 12, "md": 2}
    min_round_input.col = {"xs": 12, "sm": 7}; save_min_button.col = {"xs": 12, "sm": 5}
    max_round_input.col = {"xs": 12, "sm": 7}; save_max_button.col = {"xs": 12, "sm": 5}

    min_oszlop = ft.Column(
        col = {"xs": 12, "md": 6},
        controls = [ft.ResponsiveRow(controls = [min_round_input, save_min_button]), min_round_alert]
    )

    max_oszlop = ft.Column(
        col = {"xs": 12, "md": 6},
        controls = [ft.ResponsiveRow(controls = [max_round_input, save_max_button]), max_round_alert]
    )

    #Fő szekció (beviteli form)
    main_section = ft.Card(
        elevation = 4,
        content = ft.Container(
            padding = 30,
            content = ft.Column(
                controls = [
                    ft.Row(
                        controls = [
                            ft.Icon(ft.Icons.EDIT_DOCUMENT, color = ft.Colors.PRIMARY, size = 32),
                            ft.Text("Játék adatainak megadása", weight = ft.FontWeight.BOLD, size = 28, color = ft.Colors.PRIMARY)
                        ],
                        alignment = ft.MainAxisAlignment.CENTER
                    ),
                    ft.Text(
                        "FIGYELEM: A 'kérdőívek kiküldése' csak akkor kattints, ha már mindent hozzáadtál a játékhoz, amit szeretnél!",
                        color = ft.Colors.RED_700, weight = ft.FontWeight.W_500, text_align = ft.TextAlign.CENTER
                    ),
                    ft.Divider(height = 30),
                    ft.Column(
                        controls = [
                            ft.Text("Cím és a játék ismertetése", weight = ft.FontWeight.BOLD, size = 18),
                            ft.ResponsiveRow(controls = [title_input, save_title_button]), title_alert,
                            ft.ResponsiveRow(controls = [description_input, save_description_button]), description_alert,
                            ft.Divider(height = 20),
                            ft.Text("Min. és Max. kör", weight = ft.FontWeight.BOLD, size = 18),
                            ft.ResponsiveRow(
                                controls = [
                                    min_oszlop, max_oszlop
                                ]
                            ),
                            ft.Divider(height = 20),
                            ft.Text("Szerepek és díjak", weight = ft.FontWeight.BOLD, size = 18),
                            ft.ResponsiveRow(controls = [positions_input, add_positon_button]), positions_alert,
                            ft.ResponsiveRow(controls = [awards_input, add_award_button]), awards_alert,
                            ft.Divider(height = 20),
                            ft.Text("Kérdőívek", weight = ft.FontWeight.BOLD, size = 18),
                            ft.ResponsiveRow(controls = [question_input, elott_utan, add_question_button]), questions_alert
                        ],
                        expand = True,
                        spacing = 10,
                        scroll=ft.ScrollMode.AUTO
                    ),
                    ft.Divider(height = 10),
                    ft.ResponsiveRow(
                        controls = [
                            ft.Container(
                                ft.OutlinedButton("Játék elvetése", on_click=cancel_click, icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, style=ft.ButtonStyle(color=ft.Colors.RED)),
                                col = {"xs":12, "lg": 6, "xl": 3}
                            ),
                            ft.Container(
                                ft.OutlinedButton("Vissza a kezdőképernyőre", on_click=on_cancel, icon=ft.Icons.ARROW_BACK),
                                col={"xs": 12, "lg": 6, "xl": 3}
                            ),
                            ft.Container(
                                send_question_button,
                                col={"xs": 12, "lg": 6, "xl": 3}
                            ),
                            ft.Container(
                                ft.FilledButton("Játék indítása", icon=ft.Icons.PLAY_ARROW, on_click=start_game),
                                col = {"xs": 12, "lg": 6, "xl": 3}
    )
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
            )
        ),
        expand = 3
    )

    #Kezelők, hogy ne csak a mentés gombokkal lehessen elmenteni a változtatásokat, hanem az ENTER lenyomásával is
    title_input.on_submit = save_title
    description_input.on_submit = save_description
    positions_input.on_submit = add_positon
    awards_input.on_submit = add_award
    min_round_input.on_submit = save_min
    max_round_input.on_submit = save_max
    question_input.on_submit = add_question

    l_sidebar.col = {"xs": 12, "md": 4, "lg": 3}
    main_section.col = {"xs": 12, "md": 8, "lg": 6}
    r_sidebar.col = {"xs": 12, "md": 12, "lg": 3}

    content_row = ft.ResponsiveRow(
        controls=[l_sidebar, main_section, r_sidebar],
        expand=True,
    )

    create_game_view = ft.View(
        route = f'/create/{uj_id}',
        controls = [
            content_row,
        ]
    )

    def page_resize(e=None):
        if not page.route.startswith(f"/create/"):
            return

        is_mobile = page.width < 768

        if is_mobile:
            create_game_view.scroll = ft.ScrollMode.AUTO
            content_row.expand = False
            l_sidebar.expand = False
            main_section.expand = False
            r_sidebar.expand = False
            l_sidebar.height = 450
            main_section.height = 800
            r_sidebar.height = 450
        else:
            create_game_view.scroll = None
            content_row.expand = True
            l_sidebar.expand = 1
            main_section.expand = 3
            r_sidebar.expand = 1
            l_sidebar.height = None
            main_section.height = None
            r_sidebar.height = None

        page.update()

    page.on_resize = page_resize
    page_resize()

    return create_game_view