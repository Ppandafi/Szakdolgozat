import flet as ft
from services import dashboard_service
from game.events import jatek_topic, Uzenet

async def create_profile_view(
        page: ft.Page, current_user: str, on_password_change_attempt,
        on_logout_click, on_dashboard_click
):
    #Felhasználó adatainak lekérése
    felhasznalo = await dashboard_service.get_user(current_user)

    if not felhasznalo:
        return ft.View(
            route = "/profile",
            controls = [ft.Text("Hiba történt a felhasználó betöltésekor")]
        )

    #Statisztikák - globális átlag és díjak - lekérése
    global_avg = await dashboard_service.get_user_global_average(felhasznalo.id)
    awards = await dashboard_service.get_user_awards(felhasznalo.id)

    uj_jelszo = ft.TextField(
        label = "Új jelszó",
        width = 300,
        password = True,
        can_reveal_password = True
    )

    error_text = ft.Text(value = "", color = ft.Colors.RED, size = 15, visible = False)
    success_text = ft.Text(value = "", color = ft.Colors.GREEN, size = 15, visible = False)

    async def jelszot_valtoztat(e):
        if not uj_jelszo.value:
            error_text.value = "Kérlek töltsd ki az új jelszó mezőt!"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        success, msg = await on_password_change_attempt(current_user, uj_jelszo.value)

        if success:
            success_text.value = msg
            success_text.visible = True
            error_text.visible = False
            uj_jelszo.value = ""
        else:
            error_text.value = msg
            error_text.visible = True
            success_text.visible = False
        page.update()

    uj_jelszo.on_submit = jelszot_valtoztat

    #Profil törlése
    async def confirm_delete_profile(e):
        page.pop_dialog()
        #Lekérjük a felhasználó játékait
        jatekaim = await dashboard_service.get_user_games(felhasznalo.id)

        sikeres = await dashboard_service.deactivate_user(felhasznalo.id)
        if sikeres:
            #Végigmegyünk a játékokon, és minden szobába kiküldjük a "játékos törölve" üzenetet
            if jatekaim:
                for jatek, kor, jatekmester in jatekaim:
                    page.pubsub.send_all_on_topic(jatek_topic(jatek.id), Uzenet.JATEKOS_TOROLVE)

            #Ha sikeres a törlés, kijelentkeztetjük
            await on_logout_click(e)
        else:
            error_text.value = "Hiba történt a profil törlése során"
            error_text.visible = True
            page.update()

    async def cancel_delete_profile(e):
        page.pop_dialog()
        page.update()

    async def on_delete_click(e):
        page.show_dialog(delete_dialog)
        page.update()

    #Jelszó megváltoztatása kártya
    password_card = ft.Card(
        elevation = 4,
        content = ft.Container(
            padding = 30,
            content = ft.Column(
                controls = [
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size = 60, color = ft.Colors.PRIMARY),
                    ft.Text(f"{felhasznalo.felhasznalonev}", weight = ft.FontWeight.BOLD, size = 32),
                    ft.Divider(height = 20),
                    ft.Text("Jelszó megváltoztatása", size = 18, weight = ft.FontWeight.BOLD),
                    uj_jelszo,
                    error_text,
                    success_text,
                    ft.FilledButton("Jelszó megváltoztatása", icon = ft.Icons.SAVE)
                ],
                horizontal_alignment = ft.CrossAxisAlignment.CENTER
            )
        )
    )

    #Globális érv-átlag kártya
    progress_value = global_avg / 10.0 if global_avg else 0.0

    average_card = ft.Card(
        elevation = 4,
        expand = True,
        content = ft.Container(
            padding = 30,
            content = ft.Column(
                controls = [
                    ft.Text("Globális érv-átlagod", size = 20, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    ft.Container(
                        content = ft.Stack(
                            controls = [
                                ft.Container(
                                    content =  ft.ProgressRing(value = progress_value, stroke_width = 12, width = 150, height = 150, color = ft.Colors.PRIMARY),
                                    alignment = ft.Alignment.CENTER
                                ),
                                ft.Container(
                                    content = ft.Text(f"{global_avg}", weight = ft.FontWeight.BOLD, size = 35),
                                    alignment = ft.Alignment.CENTER
                                )
                            ]
                        ),
                        width = 150,
                        height = 150,
                        alignment = ft.Alignment.CENTER
                    )
                ],
                horizontal_alignment = ft.CrossAxisAlignment.CENTER
            )
        )
    )

    #Kapott díjak listája
    dijak_lista = ft.ListView(spacing = 10, expand = True)

    if not awards:
        dijak_lista.controls.append(
            ft.Text("Még nem szereztél díjat egy játékban sem", italic = True, color = ft.Colors.ON_SURFACE_VARIANT)
        )
    else:
        for dij, jatek_cim in awards:
            dijak_lista.controls.append(
                ft.ListTile(
                    leading = ft.Icon(ft.Icons.MILITARY_TECH, color = ft.Colors.AMBER, size = 32),
                    title = ft.Text(dij, weight = ft.FontWeight.BOLD),
                    subtitle = ft.Text(f"Játék: {jatek_cim}", italic = True)
                )
            )

    award_card = ft.Card(
        elevation = 4,
        expand = True,
        content = ft.Container(
            expand = True,
            padding = 30,
            #height = 300,
            content = ft.Column(
                controls = [
                    ft.Text("Megszerzett díjak", size = 20, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                    ft.Divider(height = 20),
                    dijak_lista
                ],
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                expand = True
            )
        )
    )

    #Alsó sor - globális átlag és díjak
    stats_row = ft.Row(
        controls = [average_card, award_card],
        alignment = ft.MainAxisAlignment.CENTER,
        vertical_alignment = ft.CrossAxisAlignment.STRETCH,
        spacing = 20,
        expand = True
    )

    #Profil törlése AlertDialog
    delete_dialog = ft.AlertDialog(
        modal = False,
        shape = ft.RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color = ft.Colors.ERROR),
                ft.Text("Profil törlése", weight = ft.FontWeight.BOLD, color = ft.Colors.ERROR),
            ]
        ),
        content = ft.Text("Biztosan törölni szeretnéd a profilodat? A törlés végleges"),
        actions = [
            ft.TextButton("Mégse", on_click = cancel_delete_profile),
            ft.FilledButton("Igen, törlöm", on_click = confirm_delete_profile, style = ft.ButtonStyle(bgcolor = ft.Colors.ERROR, color = ft.Colors.WHITE))
        ],
        actions_padding = ft.Padding(right = 20, left = 20, bottom = 20, top = 10),
        content_padding = ft.Padding(right = 24, left = 24, bottom = 10, top = 10),
    )

    #Fő szekció
    main_section = ft.Column(
        controls = [
            password_card,
            stats_row
        ],
        horizontal_alignment = ft.CrossAxisAlignment.STRETCH,
        spacing = 20,
        expand = True,
    )

    #UI felépítése
    return ft.View(
        route = "/profile",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Container(
                content = ft.Column(
                    controls = [
                        main_section,
                        ft.Container(height = 20),
                        ft.Row(
                            controls = [
                                ft.OutlinedButton("Vissza a kezdőképernyőre", icon = ft.Icons.ARROW_BACK, on_click = on_dashboard_click),
                                ft.FilledButton("Kijelentkezés", icon = ft.Icons.LOGOUT, style = ft.ButtonStyle(bgcolor = ft.Colors.ERROR, color = ft.Colors.WHITE), on_click = on_logout_click),
                                ft.FilledButton("Profil törlése", icon = ft.Icons.DELETE_FOREVER, style = ft.ButtonStyle(bgcolor = ft.Colors.RED, color = ft.Colors.WHITE), on_click = on_delete_click)
                            ],
                            alignment = ft.MainAxisAlignment.CENTER,
                        )
                    ],
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    expand = True,
                ),
                padding = 20,
                width = 1000,
                expand = True
            )
        ]
    )