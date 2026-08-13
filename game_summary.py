import flet as ft
from services import summary_service

async def create_game_summary_view(page: ft.Page, jatek_id: int, on_back_click):
    current_user = page.session.store.get("current_user")

    user, question_data, awards, ervrendszer, is_gm = await summary_service.get_player_summary_data(jatek_id, current_user)

    #Vissza gomb
    async def back_click(e):
        await on_back_click()

    #Fő tartalom
    main_column = ft.Column(
        scroll = ft.ScrollMode.AUTO,
        expand = True,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
    )

    main_column.controls.append(
        ft.Text("Játék végi összefoglaló", size = 32, weight = ft.FontWeight.BOLD)
    )

    #Vélemény alakulása
    cim_szoveg = "1. Játékosok véleményének alakulása" if is_gm else "1. Véleményed alauklása"
    main_column.controls.append(ft.Text(cim_szoveg, size = 24, weight = ft.FontWeight.BOLD))

    if not question_data:
        main_column.controls.append(ft.Text("Nincsenek kérdőív adatok ehhez a játékhoz", italic = True))
    else:
        for q in question_data:
            valaszok_ui = [] #lista a válasz sorok felépítéséhez

            for v in q["valaszok"]:
                prefix = f"{v['jatekos']}: " if is_gm else "" #Ha a játékmester nézi, akkor legyen kiírva a játékos neve is

                valaszok_ui.append(
                    ft.Row([
                        ft.Text(f"{prefix}Játék előtt adott válasz: {v['pre']}"),
                        ft.Text("|", weight = ft.FontWeight.BOLD),
                        ft.Text(f"Játék után adott válasz: {v['post']}"),
                    ])
                )

            main_column.controls.append(
                ft.Container(
                    content = ft.Column([
                        ft.Text(f"Kérdés: {q['kerdes']}", weight = ft.FontWeight.W_600),
                        *valaszok_ui,
                    ]),
                    padding = 10,
                    border = ft.Border.all(1, "outline"),
                    border_radius = 8,
                    bgcolor = "surfaceVariant",
                    margin = ft.Margin(bottom = 5, top = 5, left = 0, right = 0)
                )
            )

    main_column.controls.append(ft.Divider(height = 20, thickness = 2))

    #Kiosztott díjak
    main_column.controls.append(ft.Text("2. A játékban kiosztott díjak", size = 24, weight = ft.FontWeight.BOLD))
    if not awards:
        main_column.controls.append(ft.Text("Ebben a játékban nem osztottak ki díjakat", italic = True))
    else:
        for award in awards:
            main_column.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.MILITARY_TECH, color = ft.Colors.AMBER, size = 24),
                    ft.Text(f"{award['dij']}: ", weight = ft.FontWeight.BOLD, size = 18),
                    ft.Text(f"{award['nyertes']}", size = 18, italic = True)
                ])
            )

    main_column.controls.append(ft.Divider(height = 20, thickness = 2))

    #Érvrendszer
    main_column.controls.append(ft.Text("3. A játék végén elkészült érvrendszer", size = 24, weight = ft.FontWeight.BOLD))
    if not ervrendszer:
        main_column.controls.append(ft.Text("Még nem jött létre érvrendszer ehhez a játékhoz", italic = True))
    else:
        for erv in ervrendszer:
            main_column.controls.append(
                ft.Container(
                    content = ft.Column([
                        ft.Text(erv.erv, text_align = ft.TextAlign.JUSTIFY, size = 16),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color = ft.Colors.AMBER, size = 16),
                            ft.Text(f"Értékelés átlaga: {erv.erv_atlag}", weight = ft.FontWeight.W_500)
                        ],alignment = ft.MainAxisAlignment.END)
                    ]),
                    padding = 15,
                    border = ft.Border.all(1, "outline"),
                    border_radius = 8,
                    bgcolor = "surfaceVariant",
                    margin = ft.Margin(bottom = 5, top = 5, left = 0, right = 0)
                )
            )

    #Vissza gomb
    main_column.controls.append(
        ft.Container(
            content = ft.Button("Vissza a kezdőképernyőre", on_click = back_click, width = 250),
            padding = ft.Padding(top = 20, left = 0, right = 0, bottom = 20)
        )
    )

    return ft.View(
        route = f"/summary/{jatek_id}",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [main_column]
    )