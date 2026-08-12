import flet as ft

from services import award_service
from game.events import jatek_topic, Uzenet

async def create_award_voting_view(page:ft.Page, jatek_id: int, on_back_click):
    current_user = page.session.store.get("current_user")

    #UI elemek inicializálása
    main_section = ft.Column(
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        expand = True
    )

    vote_dropdowns = {}

    bekuldes_gomb = ft.Button("Szavazatok beküldése", width = 250)
    kihagyas_gomb = ft.Button("Nem szeretnék szavazni", width = 250, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED)
    vissza_gomb = ft.Button("Vissza a kezdőképernyőre", width = 250)

    eredmeny_szoveg = ft.Text(value = "", visible = False, size = 16, weight = ft.FontWeight.BOLD)

    async def vissza_click(e):
        await on_back_click()

    vissza_gomb.on_click = vissza_click

    #Szavazatok beküldése
    async def bekuldes_click(e):
        bekuldes_gomb.disabled = True
        kihagyas_gomb.disabled = True
        page.update()

        #szavazatok összegyűjtése
        szavazatok = {}
        for dij_nev, dropdown in vote_dropdowns.items():
            if dropdown.value:
                szavazatok[dij_nev] = int(dropdown.value)

        if not szavazatok:
            eredmeny_szoveg.value = "Kérlek szavazz legalább egy díjra, vagy válaszd a kihagyást!"
            eredmeny_szoveg.color = ft.Colors.RED
            eredmeny_szoveg.visible = True
            bekuldes_gomb.disabled = False
            kihagyas_gomb.disabled = False
            page.update()
            return

        sikeres = await award_service.save_votes(jatek_id, current_user, szavazatok, skipped=False)

        if sikeres:
            eredmeny_szoveg.value = "Szavazatok sikeresen mentve! Köszönjük a részvételt"
            eredmeny_szoveg.color = ft.Colors.GREEN
            for dropdown in vote_dropdowns.values():
                dropdown.disabled = True
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_SZAVAZAT)
        else:
            eredmeny_szoveg.value = "Hiba történt a szavazatok mentésekor"
            eredmeny_szoveg.color = ft.Colors.RED
            bekuldes_gomb.disabled = False
            kihagyas_gomb.disabled = False

        eredmeny_szoveg.visible = True
        page.update()

    #Alertdialog és logika, ha a játékos ki akarja hagyni a szavazást
    async def confirm_skip_click(e):
        page.pop_dialog()
        bekuldes_gomb.disabled = True
        kihagyas_gomb.disabled = True
        page.update()

        sikeres = await award_service.save_votes(jatek_id, current_user, {}, skipped = True)

        if sikeres:
            eredmeny_szoveg.value = "Szavazás kihagyva!"
            eredmeny_szoveg.color = ft.Colors.ORANGE
            for dropdown in vote_dropdowns.values():
                dropdown.disabled = True
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_SZAVAZAT)
        else:
            eredmeny_szoveg.value = "Hiba történt a művelet során!"
            eredmeny_szoveg.color = ft.Colors.RED
            bekuldes_gomb.disabled = False
            kihagyas_gomb.disabled = False
        eredmeny_szoveg.visible = True
        page.update()

    async def cancel_skip_click(e):
        page.pop_dialog()
        page.update()

    skip_dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Szavazás kihagyása"),
        content = ft.Text("Biztosan nem szeretnél szavazni? Ezt később nem vonhatod vissza"),
        actions = [
            ft.Button("Igen, kihagyom", on_click = confirm_skip_click, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
            ft.Button("Nem, mégis szavazok", on_click = cancel_skip_click)
        ]
    )

    async def kihagyas_click(e):
        page.show_dialog(skip_dialog)
        page.update()

    bekuldes_gomb.on_click = bekuldes_click
    kihagyas_gomb.on_click = kihagyas_click

    #Adatok betöltése
    async def load_data():
        awards, players = await award_service.get_awards_and_players(jatek_id)

        main_section.controls.clear()
        main_section.controls.append(
            ft.Text("Díjak megszavazása:", size = 30, weight = ft.FontWeight.BOLD)
        )

        if not awards:
            main_section.controls.append(
                ft.Text("Ebben a játékban nem lettek felvéve díjak", color = ft.Colors.ORANGE)
            )
        else:
            #legördülő menü opcióinak elkészítése
            player_options = [
                ft.DropdownOption(key = str(p.id), text = p.felhasznalonev)
                for p in players
            ]

            #minden díjhoz létrehozunk egy legördülő menüt
            for dij in awards:
                dropdown = ft.Dropdown(
                    label = f"Kinek adnád: {dij}?",
                    options = player_options,
                    width = 400
                )
                vote_dropdowns[dij] = dropdown
                main_section.controls.append(ft.Container(content = dropdown, padding = 5))

            #beküldés és kihagyás gombok
            main_section.controls.append(
                ft.Container(
                    content = ft.Row([bekuldes_gomb, kihagyas_gomb], alignment = ft.MainAxisAlignment.CENTER),
                    padding = ft.Padding.only(top = 20)
                )
            )

        main_section.controls.append(eredmeny_szoveg)
        main_section.controls.append(ft.Container(content = vissza_gomb, padding = ft.Padding.only(top = 10)))
        page.update()

    await load_data()

    return ft.View(
        route = f"/award_voting/{jatek_id}",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [main_section]
    )