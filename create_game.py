import flet as ft
from services import create_game_service
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
        modal = True,
        title = ft.Text("FIGYELEM"),
        content = ft.Text("Biztosan törölni szeretnéd a játékot?"),
        actions = [
            ft.Button("Játék törlése", on_click = confirm_cancel, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
            ft.Button("Szerkesztés folytatása", on_click = decline_cancel)
        ]
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
    l_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(
                    content = csatlakozok_lista
                ),
                ft.Container(
                    content = javaslatok_lista
                )
            ],
            expand = 1,
            scroll = ft.ScrollMode.AUTO
        )
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
    r_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Text("Játék adatai:", weight = ft.FontWeight.BOLD, size = 20),
                ft.Text(f"SZOBAKÓD: {szerkesztett_jatek.lobby_code if szerkesztett_jatek else ''}", weight = ft.FontWeight.BOLD, size = 20),
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
            expand = 1,
            scroll = ft.ScrollMode.AUTO
        )
    )

    #Bevitlei mezők
    title_input = ft.TextField(expand = True)
    description_input = ft.TextField(expand = True)
    positions_input = ft.TextField(expand = True)
    awards_input = ft.TextField(expand = True)
    min_round_input = ft.TextField(expand = True)
    max_round_input = ft.TextField(expand = True)
    question_input = ft.TextField(expand = True)
    elott_utan = ft.Dropdown(
        options = [
            ft.DropdownOption(key = "post", text = "Csak játék után"),
            ft.DropdownOption(key = "both", text = "Játék előtt és után")
        ],
        label = "Kérlek válassz..."
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
        page.pubsub.send_all_on_topic(jatek_topic(uj_id), Uzenet.START_GAME)
        await create_game_service.increment_round(uj_id)
        await on_gm_click()

    flag = szerkesztett_jatek.kerdoivek_kikuldve if szerkesztett_jatek else False

    save_title_button = ft.Button("Mentés", disabled = flag, on_click = save_title)
    save_description_button = ft.Button("Mentés", disabled = flag, on_click = save_description)
    add_positon_button = ft.Button("Hozzáad", disabled = False, on_click = add_positon)
    add_award_button = ft.Button("Hozzáad", disabled = False, on_click = add_award)
    add_question_button = ft.Button("Hozzáad", disabled = flag, on_click = add_question)
    save_min_button = ft.Button("Mentés", disabled = flag, on_click = save_min)
    save_max_button = ft.Button("Mentés", disabled = flag, on_click = save_max)
    send_question_button = ft.Button("Kérdőívek kiküldése", disabled = flag, on_click = send_question)

    #Fő szekció (beviteli form)
    main_section = ft.Column(
        controls = [
            ft.Text("Kérlek add meg a játék adatait", weight = ft.FontWeight.BOLD, size = 30, text_align = ft.TextAlign.CENTER),
            ft.Text(
                "FIGYELEM: A 'Véglegesít' gombra csak akkor kattints, ha már mindent hozzáadtál a játékhoz, amit szeretnél!",
                color = ft.Colors.RED
            ),
            ft.Column(
                controls = [
                    ft.Column(
                        controls = [ft.Text("Cím:"), ft.Row(controls = [title_input, save_title_button]), title_alert]
                    ),
                    ft.Column(
                        controls = [
                            ft.Text("Ismertetés:"), ft.Row(controls = [description_input, save_description_button]), description_alert
                        ]
                    ),
                    ft.Column(
                        controls = [
                            ft.Row(
                                controls = [
                                    ft.Column(
                                        controls = [ft.Text("Minimum kör:"), ft.Row(controls = [min_round_input, save_min_button]),
                                                    min_round_alert], expand = True
                                    ),
                                    ft.Column(
                                        controls = [ft.Text("Maximum kör:"), ft.Row(controls = [max_round_input, save_max_button]),
                                                    max_round_alert], expand = True
                                    )
                                ], expand = True
                            )
                        ]
                    ),
                    ft.Column(
                        controls = [
                            ft.Text("Szerepek:"), ft.Row(controls = [positions_input, add_positon_button]), positions_alert
                        ]
                    ),
                    ft.Column(
                        controls = [
                            ft.Text("Díjak:"), ft.Row(controls = [awards_input, add_award_button]), awards_alert
                        ]
                    ),
                    ft.Column(
                        controls = [
                            ft.Text("Kérdőív kérdés:"),
                            ft.Row(controls = [question_input, elott_utan, add_question_button]),
                            questions_alert
                        ]
                    ),
                    ft.Row(
                        controls = [
                            ft.Button("Játék elvetése", on_click = cancel_click, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
                            ft.Button("Vissza a kezdőképernyőre", on_click = on_cancel),
                            send_question_button,
                            ft.Button("Játék indítása", color = ft.Colors.WHITE, bgcolor = ft.Colors.BLUE, on_click = start_game),
                        ]
                    )
                ]
            )
        ],
        scroll = ft.ScrollMode.AUTO,
        expand = 3
    )

    return ft.View(
        route = f'/create/{uj_id}',
        controls = [
            ft.Row(
                controls = [l_sidebar, main_section, r_sidebar],
                expand = True
            )
        ]
    )