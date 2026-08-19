import flet as ft
from flet import RoundedRectangleBorder
from flet.controls import border_radius

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

    bekuldes_gomb = ft.FilledButton("Szavazatok beküldése", width = 250, icon = ft.Icons.SEND)
    kihagyas_gomb = ft.FilledButton("Nem szeretnék szavazni", width = 250, icon = ft.Icons.SKIP_NEXT, style = ft.ButtonStyle(bgcolor = ft.Colors.RED, color = ft.Colors.WHITE))
    vissza_gomb = ft.OutlinedButton("Vissza a kezdőképernyőre", width = 250, icon = ft.Icons.ARROW_BACK)

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
        shape = RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color = ft.Colors.ERROR),
                ft.Text("Szavazás kihagyása", weight = ft.FontWeight.BOLD, color = ft.Colors.ERROR)
            ]
        ),
        content = ft.Text("Biztosan nem szeretnél szavazni? Ezt később nem vonhatod vissza"),
        actions = [
            ft.TextButton("Nem, mégis szavazok", on_click = cancel_skip_click),
            ft.FilledButton("Igen, kihagyom", on_click = confirm_skip_click, style = ft.ButtonStyle(bgcolor = ft.Colors.ERROR, color = ft.Colors.WHITE))
        ],
        actions_padding = ft.Padding(right = 20, left = 20, bottom = 20, top = 10),
        content_padding = ft.Padding(left = 24, right = 24, top = 10, bottom = 10)
    )

    async def kihagyas_click(e):
        page.show_dialog(skip_dialog)
        page.update()

    bekuldes_gomb.on_click = bekuldes_click
    kihagyas_gomb.on_click = kihagyas_click

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
                    ft.Container(
                        content = ft.Column(
                            controls = [bekuldes_gomb, kihagyas_gomb, vissza_gomb],
                            spacing = 15,
                            horizontal_alignment = ft.CrossAxisAlignment.CENTER
                        ),
                        alignment = ft.Alignment.CENTER
                    )
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

    main_card = ft.Card(
        elevation = 4,
        margin = ft.Margin(10, 0, 0, 0),
        content = ft.Container(
            padding = 30,
            content = main_section,
        ),
        expand = 3
    )

    #Adatok betöltése
    async def load_data():
        awards, players = await award_service.get_awards_and_players(jatek_id)

        main_section.controls.clear()
        main_section.controls.append(
            ft.Row(
                controls = [
                    ft.Icon(ft.Icons.MILITARY_TECH, color=ft.Colors.PRIMARY, size=32),
                    ft.Text("Díjak megszavazása", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
                ],
                alignment = ft.MainAxisAlignment.CENTER
            )
        )
        main_section.controls.append(ft.Divider(height = 20))

        if not awards:
            main_section.controls.append(
                ft.Text("Ebben a játékban nem lettek felvéve díjak", color = ft.Colors.ORANGE, size = 16)
            )
            bekuldes_gomb.disabled = True
            kihagyas_gomb.disabled = True
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
                    width = 400,
                    border_radius = 8,
                    filled = True
                )
                vote_dropdowns[dij] = dropdown
                main_section.controls.append(ft.Container(content = dropdown, padding = 5))


        main_section.controls.append(ft.Container(height = 10))
        main_section.controls.append(eredmeny_szoveg)
        page.update()

    await load_data()

    sidebar.col = {"xs": 12, "md": 4, "lg": 3}
    main_card.col = {"xs": 12, "md": 8, "lg": 9}

    award_view =  ft.View(
        route = f"/award_voting/{jatek_id}",
        controls = [
            ft.ResponsiveRow(
                controls = [
                    sidebar,
                    main_card
                ],
                expand = True
            )
        ]
    )

    def page_resize(e=None):
        if page.route != f"/award_voting/{jatek_id}":
            return

        is_mobile = page.width < 768

        if is_mobile:
            award_view.scroll = ft.ScrollMode.AUTO
            sidebar.expand = False
            main_card.expand = False
            #sidebar.height = 300
            #main_card.height = 700
        else:
            award_view.scroll = None
            sidebar.expand = 1
            main_card.expand = 3
            sidebar.height = None
            main_card.height = None
        page.update()

    page.on_resize = page_resize
    page_resize()

    return award_view