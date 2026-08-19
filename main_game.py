import flet as ft
from flet.controls import border, border_radius

from services import main_game_service
from game.events import jatek_topic, Uzenet

class ErvKartya(ft.Container):
    def __init__(self, jatekos_nev: str, cimke: str, erv_szoveg: str, ertekeles_atlag: float, ertekeles_lathato: bool):
        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jatekos_nev}", size = 16, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY),
                        ft.Text(f" {cimke}", italic = True, size = 14, color = ft.Colors.ON_SURFACE_VARIANT)
                    ]
                ),
                ft.Text(erv_szoveg, text_align = "justify"),
            ]
        )

        if ertekeles_lathato:
            kartya_tartalom.controls.append(
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.STAR, color = "amber", size = 18),
                        ft.Text(f"Értékelés: {ertekeles_atlag}", weight = ft.FontWeight.W_500)
                    ],
                    alignment = ft.MainAxisAlignment.END
                )
            )

        vonal = ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)
        keret = ft.Border(top=vonal, right=vonal, bottom=vonal, left=vonal)
        margo = ft.Margin(left=0, bottom=0, right=0, top=0)

        super().__init__(
            content = kartya_tartalom,
            padding = 15,
            border_radius = 8,
            border = keret,
            margin = margo,
            bgcolor = "surfaceVariant"
        )

async def create_main_game_view(page: ft.Page, jatek_id: int, on_back_click, on_answer_redirect=None):
    #A felhasználó lekérése a session-ből
    current_user = page.session.store.get("current_user")

    #Felület oszlopai
    ertekelo_oszlop = ft.Column(
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
    )
    korabbi_ervek = ft.Column(expand = True)
    kartyak = ft.Column(scroll = ft.ScrollMode.AUTO, expand = True)

    #Beviteli mezők
    erveles = ft.TextField(
        label = "Ide írd az érvelésed",
        expand = True,
        border_radius = 8,
        prefix_icon = ft.Icons.COMMENT
    )
    reason = ft.TextField(
        label = "Kérlek indokold meg a szélsőséges értékelést",
        border_radius = 8,
        filled = True,
        multiline = True,
    )

    ertekelo_adatok = {}

    async def send_argument_click(e):
        felhasznalo, aktualis_kor, aktualis_szerep = await main_game_service.get_current_user_context(jatek_id, current_user)
        if not felhasznalo: return

        sikeres = await main_game_service.save_argument(jatek_id, felhasznalo.id, aktualis_szerep, aktualis_kor, erveles.value)
        if sikeres:
            erveles.value = ""
            erveles.disabled = True
            e.control.disabled = True
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_ERVELES)
        else:
            print("Hiba az érv elküldése során")
        page.update()

    async def send_reason_click(e):
        if not ertekelo_adatok.get('ervelo_id'): return

        sikeres = await main_game_service.save_reason(
            jatek_id = jatek_id,
            ertekelo_id = ertekelo_adatok['ertekelo_id'],
            ervelo_id = ertekelo_adatok['ervelo_id'],
            ervelo_szerep = ertekelo_adatok['ervelo_szerep'],
            aktualis_kor = ertekelo_adatok['aktualis_kor'],
            indoklas_szoveg = reason.value,
            ertek = ertekelo_adatok['ertek']
        )
        if sikeres:
            reason.value = ""
            page.pop_dialog()
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_ERTEKELES)
            page.update()

    reason_button = ft.Button("Küldés", on_click = send_reason_click)

    indok_dialog = ft.AlertDialog(
        modal = True,
        shape = ft.RoundedRectangleBorder(radius = 12),
        title = ft.Row(
            controls = [
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color = ft.Colors.ORANGE),
                ft.Text("Indokold meg az értékelésed!", weight = ft.FontWeight.BOLD, color = ft.Colors.ORANGE)
            ]
        ),
        content = ft.Column(
            controls = [
                ft.Text("Az érvet szélsőségesen értékelted (1 vagy 10). Kérlek indokold meg a döntésed!",size = 14, color = ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height = 5),
                reason
            ],
            tight = True,
            width = 400
        ),
        actions = [
            ft.FilledButton("küldés", icon = ft.Icons.SEND, on_click = send_reason_click)
        ],
        actions_padding = ft.Padding(right = 20, left = 20, bottom = 20, top = 10),
        content_padding = ft.Padding(left = 24, right = 24, bottom = 10, top = 10),
    )

    async def send_point_click(e, ertek, ertekelt_id, ertekelt_szerep, ertekelo_id, aktualis_kor):
        sikeres = await main_game_service.save_evaluation(jatek_id, int(ertek[0]), ertekelt_id, ertekelt_szerep, ertekelo_id)
        if sikeres:
            e.control.disabled = True

            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.UJ_ERTEKELES)

            if int(ertek[0]) == 1 or int(ertek[0]) == 10:
                ertekelo_adatok.update({
                    'ertekelo_id': ertekelo_id,
                    'ervelo_id': ertekelt_id,
                    'ervelo_szerep': ertekelt_szerep,
                    'aktualis_kor': aktualis_kor,
                    'ertek': int(ertek[0])
                })
                page.show_dialog(indok_dialog)
        page.update()

    async def ertekelo_felulet_betoltese():
        felhasznalo, aktualis_kor, aktualis_szerep = await main_game_service.get_current_user_context(jatek_id, current_user)
        if not felhasznalo: return

        soron_levo_jatekos, soron_levo_szerep, soron_levo_erv = await main_game_service.get_evaluation_context(jatek_id, felhasznalo.id, aktualis_kor)

        ertekelo_oszlop.controls.clear()

        #Ha maga a játékos van soron vagy nincs érv
        if not soron_levo_jatekos:
            page.update()
            return

        #Játékos nevének elrejtése, ha törölte a profilját
        megjelenitendo_nev = soron_levo_jatekos.felhasznalonev if getattr(soron_levo_jatekos, 'active', True) else "Törölt felhasználó"

        kartya = ErvKartya(
            jatekos_nev = megjelenitendo_nev,
            cimke = soron_levo_szerep,
            erv_szoveg = soron_levo_erv,
            ertekeles_atlag = 0,
            ertekeles_lathato = False
        )

        pontvalaszto = ft.SegmentedButton(
            segments = [ft.Segment(value = str(i), label = ft.Text(str(i))) for i in range(1, 11)],
            allow_multiple_selection = False,
            selected = ["5"],
            expand = True,
        )

        #Burkoló eseménykezelő, hogy a kuldes_gomb on_click-nek ne egy lambda függvényt kelljen meghívnia
        async def on_kuldes_click(e):
            await send_point_click(
                e,
                list(pontvalaszto.selected),
                soron_levo_jatekos.id,
                soron_levo_szerep,
                felhasznalo.id,
                aktualis_kor
            )

        kuldes_gomb = ft.FilledButton(
            "Küldés",
            icon = ft.Icons.SEND,
            disabled = False,
            on_click = on_kuldes_click
        )

        if soron_levo_erv:
            ertekelo_oszlop.controls.append(
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.STAR_RATE, color = ft.Colors.PRIMARY, size = 28),
                        ft.Text("Értékeld a soron levő játékos érvelését", size = 24, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY)
                    ],
                    alignment = ft.MainAxisAlignment.CENTER
                )
            )
            ertekelo_oszlop.controls.append(ft.Divider(height = 20))
            ertekelo_oszlop.controls.append(kartya)
            ertekelo_oszlop.controls.append(ft.Divider(height = 10))
            ertekelo_oszlop.controls.append(
                ft.Row(controls = [pontvalaszto, kuldes_gomb], alignment = ft.MainAxisAlignment.CENTER),
            )
        else:
            ertekelo_oszlop.controls.append(
                ft.Column(
                    controls = [
                        ft.Icon(ft.Icons.HOURGLASS_EMPTY, size = 60, color = ft.Colors.PRIMARY),
                        ft.Text("A soron levő játékos még nem érvelt, kérlek várj...", size = 18, weight = ft.FontWeight.BOLD, text_align = ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    alignment = ft.MainAxisAlignment.CENTER
                )
            )
        page.update()

    async def betolt_korabbi_ervek():
        felhasznalo, aktualis_kor, aktualis_szerep = await main_game_service.get_current_user_context(jatek_id, current_user)
        if not felhasznalo: return

        ervek, soron_van, mar_ervelt = await main_game_service.get_previous_arguments_and_turn_status(jatek_id, felhasznalo.id, aktualis_szerep, aktualis_kor)

        send_button = ft.IconButton(
            icon = ft.Icons.SEND,
            on_click = send_argument_click,
            disabled = mar_ervelt
        )

        korabbi_ervek.controls.clear()
        ertekelo_oszlop.controls.clear()
        kartyak.controls.clear()

        if soron_van:
            korabbi_ervek.visible = True
            ertekelo_oszlop.visible = False
            kartyak.controls.append(
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.HISTORY, color = ft.Colors.PRIMARY, size = 28),
                        ft.Text(f"Korábbi érvek a(z) {aktualis_szerep} szerepből:", size = 24, weight = ft.FontWeight.BOLD, color = ft.Colors.PRIMARY)
                    ]
                )
            )
            kartyak.controls.append(ft.Divider(height = 20))

            if not ervek:
                kartyak.controls.append(ft.Text("Ehhez a szerephez még nem érkeztek érvek", italic = True))
            else:
                for erv_obj, erv_szerzo in ervek:
                    # Játékos nevének elrejtése, ha törölte a profilját
                    megjelenitendo_nev = erv_szerzo.felhasznalonev if getattr(erv_szerzo, 'active', True) else "Törölt felhasználó"

                    kartyak.controls.append(ErvKartya(
                        jatekos_nev = megjelenitendo_nev,
                        cimke = f"{erv_obj.kor}. kör",
                        erv_szoveg = erv_obj.erv,
                        ertekeles_atlag = erv_obj.ertekeles_atlag,
                        ertekeles_lathato = True
                    ))

            erveles.disabled = mar_ervelt

            korabbi_ervek.controls.append(kartyak)
            korabbi_ervek.controls.append(ft.Container(height = 10))
            korabbi_ervek.controls.append(ft.Row(controls = [erveles, send_button]))
        else:
            korabbi_ervek.visible = False
            ertekelo_oszlop.visible = True
            await ertekelo_felulet_betoltese()

        page.update()

    async def handle_pubsub_message(topic, message):
        if message == Uzenet.UJ_ERVELES:
            await ertekelo_felulet_betoltese()
        elif message == Uzenet.KERDOIVEK_POST:
            if on_answer_redirect:
                    await on_answer_redirect()
        elif message in [Uzenet.KOR_VALTOZOTT, Uzenet.KOVETKEZO_JATEKOS]:
            await betolt_korabbi_ervek()
        elif message == Uzenet.JATEKOS_TOROLVE:
            #Ha valakit törölnek, frissítjük a nevét a kártyákben
            await betolt_korabbi_ervek()
            await ertekelo_felulet_betoltese()

    page.pubsub.subscribe_topic(jatek_topic(jatek_id), handle_pubsub_message)

    #Felület inicializálása
    await betolt_korabbi_ervek()

    async def vissza_kattintas(e):
        await on_back_click()

    #Kezelők, hogy ne csak a küldés gombbal lehessen elküldeni az érvelést/értékelést, hanem az ENTER megnyomására is működjön
    erveles.on_submit = send_argument_click
    reason.on_submit = send_reason_click

    korabbi_ervek.col = {"xs": 12, "lg": 6}
    ertekelo_oszlop.col = {"xs": 12, "lg": 6}

    #Fő szekció kártyába csomagolva
    main_card = ft.Card(
        elevation = 4,
        expand = True,
        content = ft.Container(
            padding = 30,
            content = ft.ResponsiveRow(
                controls = [
                    korabbi_ervek,
                    ertekelo_oszlop
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.CENTER
            )
        )
    )

    return ft.View(
        route = f"/game/{jatek_id}",
        #scroll=ft.ScrollMode.AUTO,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Container(
                content = ft.Column(
                    controls = [
                        main_card,
                        ft.Container(height = 10),
                        ft.Row(
                            controls = [ft.OutlinedButton("Vissza a kezdőképernyőre", icon = ft.Icons.ARROW_BACK, on_click = vissza_kattintas)],
                            alignment = ft.MainAxisAlignment.CENTER
                        )
                    ],
                    expand = True,
                ),
                padding = 20,
                expand = True
            )
        ]
    )