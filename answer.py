import flet as ft
from services import answer_service
from game.events import jatek_topic, Uzenet

async def create_answer_view(page: ft.Page, jatek_id: int, on_back_click, on_start_game_click, on_award_redirect = None):
    #Felhasználó lekérése
    current_user = page.session.store.get("current_user")

    async def back_clicked(e):
        await on_back_click()

    #Javaslat ablak
    proposal_input = ft.TextField(
        label = "Javaslat",
        border_radius = 8,
        filled = True,
        prefix_icon = ft.Icons.LIGHTBULB_OUTLINE,
        autofocus = True
    )

    proposal_dropdown = ft.Dropdown(
        options = [
            ft.DropdownOption(key = "szerep", text = "Szerepkör"),
            ft.DropdownOption(key = "dij", text = "Díj")
        ],
        label = "Javaslat típusa",
        border_radius = 8,
        filled = True
    )

    proposal_error = ft.Text(
        value = "",
        color = ft.Colors.ERROR,
        visible = False,
        size = 13,
        weight = ft.FontWeight.W_500
    )

    async def cancel_proposal(e):
        proposal_input.value = ""
        proposal_dropdown.value = None
        proposal_error.visible = False
        page.pop_dialog()
        page.update()

    #Javaslat mentése
    async def submit_proposal(e):
        if not proposal_input.value or not proposal_dropdown.value:
            proposal_error.value = "Kérlek minden mezőt tölts ki"
            proposal_error.color = ft.Colors.ERROR
            proposal_error.visible = True
            page.update()
            return

        szerep_dij = (proposal_dropdown.value == "szerep")
        sikeres = await answer_service.save_proposal(jatek_id, proposal_input.value.strip(), szerep_dij)

        if sikeres:
            proposal_input.value = ""
            proposal_dropdown.value = None
            proposal_error.visible = False
            page.pop_dialog()
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_JAVASLAT)
        else:
            proposal_error.value = "Hiba történt az adatbázis mentése során"
            proposal_error.color = ft.Colors.ERROR
            proposal_error.visible = True
        page.update()

    proposal_input.on_submit = submit_proposal

    #Javaslat alertdialog
    proposal_dialog = ft.AlertDialog(
        modal = False,
        shape = ft.RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.ADD_COMMENT, color = ft.Colors.PRIMARY),
                ft.Text("Új javaslat tétele", weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY)
            ]
        ),
        content = ft.Column(
            controls = [
                ft.Text(
                    "Javasolj egy új szerepkört vagy díjat!",
                    size = 14, color = ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Container(height = 5),
                ft.Row(controls = [proposal_input, proposal_dropdown]),
                proposal_error
            ],
            tight = True,
            spacing = 15,
            #width = 400,
            horizontal_alignment =ft.CrossAxisAlignment.STRETCH
        ),
        actions = [
            ft.TextButton("Mégse", on_click = cancel_proposal),
            ft.FilledButton("Beküldés", icon = ft.Icons.SEND, on_click = submit_proposal)
        ],
        actions_padding = ft.Padding(right = 20, left = 20, bottom = 20, top = 10),
        content_padding = ft.Padding(left = 24, right = 24, top = 10, bottom = 10)
    )

    #Változók a válasz mentéséhez
    valasz = {}
    aktualis_fazis = None

    #Beküldés gomb
    bekuldes_gomb = ft.FilledButton("Beküldés", width = 250, icon = ft.Icons.SEND, disabled = True)

    #Többi játékos kiírása
    jatekosok = ft.Column()

    #Javaslat gom
    javaslat_gomb = ft.FilledButton("Javaslattétel", icon = ft.Icons.ADD_COMMENT, width = 250, on_click = lambda e: page.show_dialog(proposal_dialog))

    gombok = ft.Column(
        controls = [
            bekuldes_gomb,
            javaslat_gomb,
            ft.OutlinedButton("Vissza a kezdőképernyőre", icon = ft.Icons.ARROW_BACK, width = 250, on_click = back_clicked)
        ],
        spacing = 15,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
    )

    #Oldalsó menü
    sidebar = ft.Card(
        elevation = 4,
        margin = ft.Margin(0, 0, 10, 0),
        content = ft.Container(
            padding = 20,
            content = ft.Column(
                controls = [
                    ft.Text("Műveletek", size = 20, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    ft.Container(content = gombok, alignment = ft.Alignment.CENTER),
                    ft.Divider(height = 30),
                    ft.Text("Játékosok", size = 18, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Container(content = jatekosok, expand = True)
                ],
                expand = True
            )
        ),
        expand = 1
    )

    #Fő szekció
    main_section = ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.START,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        scroll = ft.ScrollMode.AUTO
    )

    #Fő szekció kártyába csomagolása
    main_card = ft.Card(
        elevation = 4,
        margin = ft.Margin(10, 0, 0, 0),
        content = ft.Container(
            padding = 30,
            content = main_section
        ),
        expand = 3
    )

    #Csatlakozott játékosok lekérése
    async def update_csatlakozott_jatekosok(topic=None, message=None):
        resztvevok, aktualis_nev = await answer_service.get_connected_players(jatek_id, current_user)
        jatekosok.controls.clear()

        for nev in resztvevok:
            if nev == aktualis_nev:
                jatekosok.controls.append(ft.Text(f"- {nev} (Ön)"))
            else:
                jatekosok.controls.append(ft.Text(f"- {nev}"))
        page.update()

    #Kérdések betöltése
    async def betolt_kerdesek(message):
        nonlocal aktualis_fazis

        if message == Uzenet.KERDOIVEK_PRE:
            aktualis_fazis = "pre"
            javaslat_gomb.disabled = False
        elif message == Uzenet.KERDOIVEK_POST:
            aktualis_fazis = "post"
            javaslat_gomb.disabled = True
        else:
            return

        kerdesek = await answer_service.get_questions(jatek_id, aktualis_fazis)

        main_section.controls.clear()
        valasz.clear()
        main_section.alignment = ft.MainAxisAlignment.START
        main_section.controls.append(
            ft.Row(
                controls = [
                    ft.Icon(ft.Icons.ASSIGNMENT, color = ft.Colors.PRIMARY, size = 32),
                    ft.Text("Kérlek a következő kérdéseket pontozd 1-től 10-ig, hogy mennyire értesz egyet velük",
                            size=22, weight=ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                ],
                alignment = ft.MainAxisAlignment.CENTER,
            )
        )
        main_section.controls.append(ft.Divider(height = 20))

        if not kerdesek:
            main_section.controls.append(ft.Text("Nincsenek megjeleníthető kérdések"))
        else:
            for kerdes in kerdesek:
                uj_gomb = ft.SegmentedButton(
                    segments = [ft.Segment(value = str(i), label = ft.Text(str(i))) for i in range(1, 11)],
                    allow_empty_selection = True,
                    allow_multiple_selection = False
                )
                valasz[kerdes.kerdes_id] = uj_gomb

                main_section.controls.append(
                    ft.Container(
                        content = ft.Column(
                            controls = [
                                ft.Text(kerdes.kerdes, size = 16, weight = ft.FontWeight.W_500),
                                uj_gomb,
                            ],
                            spacing = 15
                        ),
                        padding = 20,
                        margin = ft.Margin(bottom = 20, top = 0, left = 0, right = 0),
                        border_radius = 8,
                        border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
                    )
                )
        bekuldes_gomb.disabled = False
        page.update()

    async def handle_pubsub_message(topic, message):
        if message in [Uzenet.KERDOIVEK_PRE, Uzenet.KERDOIVEK_POST]:
            await betolt_kerdesek(message)
        elif message == Uzenet.UJ_JATEKOS:
            await update_csatlakozott_jatekosok()
        elif message == Uzenet.START_GAME:
            page.pop_dialog()
            await on_start_game_click(jatek_id)

    page.pubsub.subscribe_topic(jatek_topic(jatek_id), handle_pubsub_message)

    #Indításkori lekérdezés: várakoztató szöveg lesz megjelenítve, vagy kérdések
    aktualis_jatek = await answer_service.get_game_status(jatek_id)
    if aktualis_jatek:
        if aktualis_jatek.jatek_lezarva:
            await betolt_kerdesek(Uzenet.KERDOIVEK_POST)
        elif aktualis_jatek.kerdoivek_kikuldve:
            await betolt_kerdesek(Uzenet.KERDOIVEK_PRE)
        else:
            main_section.controls.append(
                ft.Column(
                    controls = [
                        ft.Icon(ft.Icons.HOURGLASS_EMPTY, size = 80, color = ft.Colors.PRIMARY),
                        ft.Text("Kérlek várj, amíg a játékmester kiküldi a kérdőíveket!", size=25,
                                weight=ft.FontWeight.BOLD, text_align = ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    alignment = ft.MainAxisAlignment.CENTER,
                )
            )

    #Válaszok mentése
    async def bekuldes_click(e):
        if not aktualis_fazis or not valasz:
            return

        valasz_dict = {}
        #Értékek begyűjtése a gombokból
        for kerdes_id, gomb in valasz.items():
            if gomb.selected:
                valasz_ertek = int(list(gomb.selected)[0])
                valasz_dict[kerdes_id] = valasz_ertek

        sikeres = await answer_service.save_answers(jatek_id, current_user, aktualis_fazis, valasz_dict)

        if sikeres:
            bekuldes_gomb.disabled = True
            main_section.controls.append(ft.Text("Válaszok sikeresen mentve!", color = ft.Colors.GREEN))

            if aktualis_fazis == "post" and on_award_redirect:
                await on_award_redirect()
        else:
            main_section.controls.append(ft.Text("Hiba a válaszok mentése során", color = ft.Colors.RED))
        page.update()

    bekuldes_gomb.on_click = bekuldes_click

    await  update_csatlakozott_jatekosok()

    proposal_input.on_submit = submit_proposal

    #View visszaadása a main.py-nak
    return ft.View(
        route = f"/answer/{jatek_id}",
        controls = [
            ft.Row(
                controls = [
                    sidebar,
                    main_card,
                ],
                expand = True,
            )
        ]
    )