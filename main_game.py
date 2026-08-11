import flet as ft

from services import main_game_service
from game.events import jatek_topic, Uzenet

class ErvKartya(ft.Container):
    def __init__(self, jatekos_nev: str, cimke: str, erv_szoveg: str, ertekeles_atlag: float, ertekeles_lathato: bool):
        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jatekos_nev}", size = 16, weight = ft.FontWeight.BOLD),
                        ft.Text(f" {cimke}", italic = True, size = 14, color = "onSurfaceVariant")
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
                        ft.Text(f"Értékelés: {ertekeles_atlag}", weight = "w500")
                    ],
                    alignment = "end"
                )
            )

        vonal = ft.BorderSide(1, "outline")
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
    erveles = ft.TextField(label = "Ide írd az érvelésed", expand = True)
    reason = ft.TextField(label = "Kérlek indokold meg a szélsőséges értékelést!")

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
        title = ft.Text("Indokold meg az értékelésed"),
        content = ft.Column(
            controls = [
                ft.Text("Az érvet szélsőségesen értékelted, kérlek indokold meg a döntésedet:"),
                ft.Row(controls = [reason, reason_button]),
            ],
            tight = True
        )
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

        kartya = ErvKartya(
            jatekos_nev = soron_levo_jatekos.felhasznalonev,
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

        kuldes_gomb = ft.Button(
            "Küldés",
            disabled = False,
            on_click = on_kuldes_click
        )

        if soron_levo_erv:
            ertekelo_oszlop.controls.append(kartya)
            ertekelo_oszlop.controls.append(
                ft.Row(controls = [pontvalaszto, kuldes_gomb], expand = True)
            )
        else:
            ertekelo_oszlop.controls.append(ft.Text("A soron levő játékos még nem érvelt, kérlek várj..."))
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
            kartyak.controls.append(ft.Text(f"Korábbi érvek a(z) {aktualis_szerep} szerepből:", size = 20, weight = ft.FontWeight.BOLD))

            if not ervek:
                kartyak.controls.append(ft.Text("Ehhez a szerephez még nem érkeztek érvek"))
            else:
                for erv_obj, erv_szerzo in ervek:
                    kartyak.controls.append(ErvKartya(
                        jatekos_nev = erv_szerzo.felhasznalonev,
                        cimke = f"{erv_obj.kor}. kör",
                        erv_szoveg = erv_obj.erv,
                        ertekeles_atlag = erv_obj.ertekeles_atlag,
                        ertekeles_lathato = True
                    ))

            erveles.disabled = mar_ervelt

            korabbi_ervek.controls.append(kartyak)
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

    page.pubsub.subscribe_topic(jatek_topic(jatek_id), handle_pubsub_message)

    #Felület inicializálása
    await betolt_korabbi_ervek()

    async def vissza_kattintas(e):
        await on_back_click()

    #Kezelők, hogy ne csak a küldés gombbal lehessen elküldeni az érvelést/értékelést, hanem az ENTER megnyomására is működjön
    erveles.on_submit = send_argument_click
    reason.on_submit = send_reason_click

    return ft.View(
        route = f"/game/{jatek_id}",
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        vertical_alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Row(
                controls = [korabbi_ervek, ertekelo_oszlop],
                expand = True
            ),
            ft.Row(
                controls = [ft.Button("Vissza a dashboardra", on_click = vissza_kattintas)],
                alignment = ft.MainAxisAlignment.CENTER
            )
        ]
    )