import flet as ft
from services import award_service

async def create_award_voting_view(page: ft.Page, jatek_id: int, on_back_click):
    current_user = page.session.store.get("current_user")

    #UI elemek inicializálása
    main_section = ft.Column(
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAlignment.CENTER,
        expand = True
    )

    vote_dropdowns = {}

    bekuldes_gomb = ft.Button("Szavazatok beküldése", width = 250)
    vissza_gomb = ft.Button("Vissza a dashboardra", width = 250)

    eredmeny_szoveg = ft.Text(value = "", visible = False, size = 16, weight = ft.FontWeight.BOLD)

    async def vissza_click(e):
        await on_back_click()

    vissza_gomb.on_click = vissza_click

    #Szavazatok beküldése
    async def bekuldes_click(e):
        bekuldes_gomb.disabled = True
        page.update()

        #szavazatok összegyűjtése
        szavazatok = {}
        for dij_nev, dropdown in vote_dropdowns.items():
            if dropdown.value:
                szavazatok[dij_nev] = int(dropdown.value)

        if not szavazatok:
            eredmeny_szoveg.value = "Kérlek szavazz legalább egy díjra!"
            eredmeny_szoveg.color = ft.Colors.RED
            eredmeny_szoveg.visible = True
            bekuldes_gomb.disabled = False
            page.update()
            return

        sikeres = await award_service.save_votes(jatek_id, szavazatok)

        if sikeres:
            eredmeny_szoveg.value = "Szavazatok sikeresen mentve! Köszönjük a rsézvételt!"
            eredmeny_szoveg.color = ft.Colors.GREEN
            for dropdown in vote_dropdowns.values():
                dropdown.disabled = True
        else:
            eredmeny_szoveg.value = "Hiba történt a szavazatok mentésekor"
            eredmeny_szoveg.color = ft.Colors.RED
            bekuldes_gomb.disabled = False

        eredmeny_szoveg.visible = True
        page.update()

    bekuldes_gomb.on_click = bekuldes_click

    #Adatok betöltése
    async def load_data():
        awards, players = await award_service.get_awards_and_players(jatek_id)

        main_section.controls.clear()
        main_section.controls.append(
            ft.Text("Díjak megszavazása:", size = 30, weight = ft.FontWeight.BOLD)
        )

        if not awards:
            main_section.controls.append(
                ft.Text("Ebben a játékban nem lette kfelvéve díjak", color = ft.Colors.ORANGE)
            )
        else:
            #legördülő menü opcióinak elkészítése
            player_options = [
                ft.DropdownOption(key=str(p.id), text=p.felhasznalonev)
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

            main_section.controls.append(ft.Container(content = bekuldes_gomb, padding = ft.Padding_only(top=20)))

        main_section.controls.append(eredmeny_szoveg)
        main_section.controls.append(ft.Container(content = vissza_gomb, padding = ft.Padding_only(top=10)))
        page.update()

    #Adatok betöltése a nézet inicializálásakor
    await load_data()

    #View visszaadása
    return ft.View(
        route = "/award_voting/{jatek_id}",
        horizontal_alignment = ft.CrossAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [main_section]
    )