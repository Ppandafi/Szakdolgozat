import flet as ft

from services import answer_service
from game.events import jatek_topic, Uzenet

async def create_answer_view(page: ft.Page, jatek_id: int, on_back_click, on_start_game_click):
    #Felhasználó lekérése
    current_user = page.session.store.get("current_user")

    async def back_clicked(e):
        await on_back_click()

    #Javaslat ablak inputok
    proposal_input = ft.TextField(label = "Javaslat")
    proposal_dropdown = ft.Dropdown(
        options = [
            ft.DropdownOption(key = "dij", text = "Díj"),
            ft.DropdownOption(key = "szerep", text = "Szerep")
        ],
        label = "Kérlek válassz..."
    )

    #Javaslat mentése
    async def submit_proposal(e):
        if proposal_input.value and proposal_dropdown.value:
            szerep_dij = (proposal_dropdown.value == "szerep")

            sikeres = await answer_service.save_proposal(jatek_id, proposal_input.value, szerep_dij)

            if sikeres:
                proposal_input.value = ""
                proposal_dropdown.value = ""
                #Értesítés küldése a pubsub csatornára
                page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_JAVASLAT)
            else:
                proposal_column.controls.append(ft.Text("Kérlek tölts ki minden mezőt!", color = ft.Colors.RED))
            page.update()

    proposal_column = ft.Column(
        controls = [
            ft.Row(
                controls = [
                    proposal_input,
                    proposal_dropdown,
                    ft.Button("Küldés", on_click = submit_proposal),
                    ft.Button("Mégse", on_click = lambda e: page.pop_dialog())
                ],
                tight = True
            )
        ],
        tight = True
    )

    proposal_dialog = ft.AlertDialog(
        modal = True,
        title = "Javaslat",
        content = proposal_column
    )

    #Változók a válasz mentéséhez
    valasz = {}
    aktualis_fazis = None

    #Beküldés gomb
    bekuldes_gomb = ft.Button("Beküldés", width = 210)

    #Többi játékos kiírása
    jatekosok = ft.Column()

    gombok = ft.Column(
        controls = [
            bekuldes_gomb,
            ft.Button("Javaslattétel", width = 210, on_click = lambda e: page.show_dialog(proposal_dialog)),
            ft.Button("Vissza", width = 210, on_click = back_clicked)
        ]
    )

    #Oldalsó menü
    sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékosok:", weight = ft.FontWeight.BOLD),
                ft.Container(content = jatekosok)
            ]
        ),
        expand = 1
    )

    #Fő szekció
    main_section = ft.Column(
        expand = 3,
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
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
        elif message == Uzenet.KERDOIVEK_POST:
            aktualis_fazis = "post"
        else:
            return

        kerdesek = await answer_service.get_questions(jatek_id, aktualis_fazis)

        main_section.controls.clear()
        valasz.clear()
        main_section.alignment = ft.MainAxisAlignment.START
        main_section.controls.append(
            ft.Text("Kérlek a következő kérdéseket pontozd 1-től 10-ig, hogy mennyire értesz egyet velük", size = 20, weight = ft.FontWeight.BOLD)
        )

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
                    ft.Column([
                        ft.Text(kerdes.kerdes, size = 15),
                        uj_gomb
                    ])
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
    if aktualis_jatek and aktualis_jatek.kerdoivek_kikuldve:
        await betolt_kerdesek(Uzenet.KERDOIVEK_PRE)
    else:
        main_section.controls.append(
            ft.Text("Kérlek várj, amíg a játékmester kiküldi a kérdőíveket...", size = 30, weight = ft.FontWeight.BOLD)
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
        else:
            main_section.controls.append(ft.Text("Hiba a válaszok mentése során", color = ft.Colors.RED))
        page.update()

    bekuldes_gomb.on_click = bekuldes_click

    await  update_csatlakozott_jatekosok()

    #View visszaadása a main.py-nak
    return ft.View(
        route = f"/answer/{jatek_id}",
        controls = [
            ft.Row(
                controls = [
                    sidebar,
                    main_section,
                ],
                expand = True,
            )
        ]
    )