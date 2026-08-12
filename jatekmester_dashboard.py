import flet as ft
from datetime import datetime

from game.events import jatek_topic, Uzenet
from services import gm_dashboard_service

#Érvkártya osztály
class GmErvKartya(ft.Container):
    def __init__(
            self,
            jatekos_nev: str,
            szerep: str,
            kor: int,
            erv_szoveg: str,
            ertekeles_atlag: float,
            bekuldes_ideje: str
    ):
        #A kártya belső felépítése
        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Text(f"{jatekos_nev} |", size = 16, weight = ft.FontWeight.BOLD),
                        ft.Text(f" {szerep}", italic = True, size = 14, color = "onSurfaceVariant"),
                        ft.Text(" |"),
                        ft.Text(f" {kor}. kör", size = 14, weight = ft.FontWeight.W_500),
                    ]
                ),
                ft.Text(f"Beküldve: {bekuldes_ideje}", size = 12, color = ft.Colors.GREY_500),
                ft.Text(f"{erv_szoveg}", text_align = ft.TextAlign.JUSTIFY),
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.STAR, color = "amber", size = 18),
                        ft.Text(f"Értékelés átlaga: {ertekeles_atlag}", weight = "w500")
                    ],
                    alignment = ft.MainAxisAlignment.END
                )
            ]
        )

        vonal = ft.BorderSide(1, "outline")
        keret = ft.Border(top=vonal, right=vonal, bottom=vonal, left=vonal)
        margo = ft.Margin(left=0, bottom=10, right=40, top=0)

        #Szülőosztály inicializálása
        super().__init__(
            content = kartya_tartalom,
            padding = 15,
            border_radius = 8,
            border = keret,
            margin = margo,
            bgcolor = "surfaceVariant"
        )

#Indoklás kártya osztály
class IndoklasKartya(ft.Container):
    def __init__(
            self,
            ertekelo_nev: str,
            ertekelt_nev: str,
            szerep: str,
            kor: int,
            ertekeles: int,
            indoklas_szoveg: str,
            bekuldes_ideje: str
    ):
        szin = ft.Colors.RED_100 if ertekeles == 1 else ft.Colors.GREEN_100

        kartya_tartalom = ft.Column(
            controls = [
                ft.Row(
                    controls = [
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color = ft.Colors.ORANGE),
                        ft.Text(f"{ertekelo_nev} szélsőségesen ({ertekeles} pont) értékelte {ertekelt_nev} ({szerep}) érvét", weight = ft.FontWeight.BOLD),
                        ft.Text(f" | {kor}. kör", size = 14)
                    ]
                ),
                ft.Text(f"Beküldve: {bekuldes_ideje}", size = 12, color = ft.Colors.GREY_700),
                ft.Text(indoklas_szoveg, text_align = ft.TextAlign.JUSTIFY)
            ]
        )

        vonal = ft.BorderSide(1, "outline")
        keret = ft.Border(top=vonal, right=vonal, bottom=vonal, left=vonal)
        margo = ft.Margin(left=40, bottom=10, right=0, top=0) #Kicsi margó bal oldalon, hogy az érvekre adott válasznak tűnjön

        super().__init__(
            content = kartya_tartalom,
            padding = 15,
            border_radius = 8,
            border = keret,
            margin = margo,
            bgcolor = szin
        )

async def create_gm_dashboard_view(page: ft.Page, jatek_id: int):
    #Felhasználó lekérése a session-ből
    current_user = page.session.store.get("current_user")

    soron_voltak_szoveg = ft.Text("Eddig soron voltak: 0/0", weight = ft.FontWeight.BOLD, size = 16)

    #Soron levő játékos cache, hogy ne kelljen lekéregetni
    soron_levo_cache = {
        "jatekos_id": None,
        "szerep": None
    }

    #Fő UI elemek
    #Játékosok lista
    jatekosok_lista = ft.Column()
    csatlakozott_jatekosok = ft.Container(
        content = jatekosok_lista,
        expand = True
    )

    #Aktuális kör
    kor_szoveg = ft.Text("", weight = ft.FontWeight.BOLD)

    #Érveltek már progress-bar
    erveltek_progress = ft.ProgressRing(value = 0.0, stroke_width = 10, width = 150, height = 150)
    erveltek_szoveg = ft.Text("", weight = ft.FontWeight.BOLD, size = 35, text_align = ft.TextAlign.CENTER)

    progress_container = ft.Container(
        content = ft.Stack( #Ahhoz kell, hogy az erveltek_szoveget és erveltek_progresst egymással lehessen overlapelni
            controls = [
                ft.Container(
                    content = erveltek_progress,
                    alignment = ft.Alignment.CENTER,
                ),
                ft.Container(
                    content = erveltek_szoveg,
                    alignment = ft.Alignment.CENTER,
                )
            ]
        ),
        width = 150,
        height = 150,
        alignment = ft.Alignment.CENTER,
    )
    erveltek_container = ft.Column(
        controls = [
            ft.Text("Érveltek a körben: ", weight = ft.FontWeight.BOLD),
            ft.Container(
                content =  progress_container,
                alignment = ft.Alignment.CENTER,
            )
        ]
    )

    #Értékeltek már progress-bar
    ertekeltek_progress = ft.ProgressRing(value = 0.0, stroke_width = 10, width = 150, height = 150)
    ertekeltek_szoveg = ft.Text("", weight = ft.FontWeight.BOLD, size = 35, text_align = ft.TextAlign.CENTER)

    progressRing_container = ft.Container(
        content = ft.Stack(
            controls = [
                ft.Container(
                    content = ertekeltek_progress,
                    alignment = ft.Alignment.CENTER
                ),
                ft.Container(
                    content = ertekeltek_szoveg,
                    alignment =ft.Alignment.CENTER
                )
            ]
        ),
        width = 150,
        height = 150,
        alignment = ft.Alignment.CENTER
    )
    ertekeltek_container = ft.Column(
        controls = [
            ft.Text("Értékelték a soron levő érvelését: ", weight = ft.FontWeight.BOLD),
            ft.Container(
                content = progressRing_container,
                alignment = ft.Alignment.CENTER
            )
        ]
    )

    #Szavaztak már progress-bar
    szavaztak_progress = ft.ProgressRing(value = 0.0, stroke_width = 10, width = 150, height = 150)
    szavaztak_szoveg = ft.Text("0/0", weight = ft.FontWeight.BOLD, size = 35, text_align = ft.TextAlign.CENTER)

    szavaztak_progressring_container = ft.Container(
        content = ft.Stack(
            controls = [
                ft.Container(
                    content = szavaztak_progress,
                    alignment = ft.Alignment.CENTER
                ),
                ft.Container(
                    content = szavaztak_szoveg,
                    alignment = ft.Alignment.CENTER
                )
            ]
        ),
        width = 150,
        height = 150,
        alignment = ft.Alignment.CENTER
    )

    szavaztak_container = ft.Column(
        controls = [
            ft.Text("Szavaztak a díjakra: ", weight = ft.FontWeight.BOLD),
            ft.Container(
                content = szavaztak_progressring_container,
                alignment = ft.Alignment.CENTER
            )
        ],
        visible = False
    )
    
    #Érvek oszlop
    ervek_oszlop = ft.Column(
        scroll = ft.ScrollMode.AUTO,
        expand = True
    )

    #Bal oldali menüsáv
    l_sidebar = ft.Container(
        ft.Column(
            controls = [
                kor_szoveg,
                csatlakozott_jatekosok,
            ]
        ),
        expand=1
    )

    #Jobb oldali szekció
    r_sidebar = ft.Container(
        ft.Column(
            controls = [
                soron_voltak_szoveg,
                erveltek_container,
                ertekeltek_container,
                szavaztak_container
            ]
        ),
        expand=1
    )

    #Gombok
    next_player_button = ft.Button("Következő játékos")
    next_round_button = ft.Button("Következő kör")
    end_game_button = ft.Button("Játék lezárása")

    #Fő szekció
    main_section = ft.Container(
        ft.Column(
            controls = [
                ervek_oszlop,
                ft.Row(
                    controls = [
                        next_player_button,
                        next_round_button,
                        end_game_button,
                    ],
                    #expand = True
                )
            ]
        ),
        expand=3
    )

    #Csatlakozott játékosok lista feltöltése
    async def update_csatlakozott_jatekosok(topic=None, message=None):
        resztvevok = await gm_dashboard_service.get_joined_players(jatek_id)

        jatekosok_lista.controls.clear()
        jatekosok_lista.controls.append(ft.Text("Csatlakozott játékosok:", weight = ft.FontWeight.BOLD))

        for nev, szerep, soron_van in resztvevok:
            szerep_szoveg = f" - {szerep}" if szerep else " - Még nincs szerep"
            soron_van_szoveg = " (soron van)" if soron_van else ""

            jatekosok_lista.controls.append(
                ft.Text(f"{nev}{szerep_szoveg}{soron_van_szoveg}")
            )
        page.update()

    #Jelenlegi kör frissítése
    async def update_jelenlegi_kor():
        korok = await gm_dashboard_service.get_rounds(jatek_id)
        if korok:
            jelenlegi_kor = korok[0]
            max_kor = korok[1]
            kor_szoveg.value = f"Jelenlegi kör: {jelenlegi_kor}/{max_kor}"
            page.update()

    #Soron levő játékos mentése a cache-be
    async def update_soron_levo_cache():
        soron_adatok = await gm_dashboard_service.get_soron_levo(jatek_id)
        if soron_adatok and soron_adatok[0]:
            soron_levo_cache["jatekos_id"] = soron_adatok[0]
            soron_levo_cache["szerep"] = soron_adatok[1]
        else:
            soron_levo_cache["jatekos_id"] = None
            soron_levo_cache["szerep"] = None

    #Érveltek progress-bar frissítése
    async def update_erveltek_mar():
        korok = await gm_dashboard_service.get_rounds(jatek_id)
        if not korok:
            return
        jelenlegi_kor = korok[0]

        #Már érveltek és cache változó lekérése
        erveltek_szama = await gm_dashboard_service.get_erveltek_mar(jatek_id, jelenlegi_kor)
        max_jatekosok = gm_dashboard_service.jatekosok_szama_cache.get(jatek_id, 1)

        #Biztonsági ellenőrzés, ha valamiért 0 lenne a max_jatekosok
        if max_jatekosok == 0:
            max_jatekosok = 1

        arany = erveltek_szama / max_jatekosok

        #UI elemek frissítése
        erveltek_progress.value = arany
        erveltek_szoveg.value = f"{erveltek_szama} / {max_jatekosok}"

        page.update()

    #Értékeltek progress-bar frissítése
    async def update_ertekeltek_mar():
        erv_szerzo_id = soron_levo_cache["jatekos_id"]
        szerep = soron_levo_cache["szerep"]

        ertekeltek_szama = await gm_dashboard_service.get_ertekeltek_mar(jatek_id, erv_szerzo_id, szerep)

        max_jatekosok = gm_dashboard_service.jatekosok_szama_cache.get(jatek_id, 1)
        max_ertekelok = max_jatekosok - 1

        if max_ertekelok <= 0:
            max_ertekelok = 1

        arany = ertekeltek_szama / max_ertekelok

        #UI elemek frissítése
        ertekeltek_progress.value = arany
        ertekeltek_szoveg.value = f"{ertekeltek_szama} / {max_ertekelok}"

        page.update()

    #Szavaztak már frissítése
    async def update_szavaztak_mar():
        szavaztak_szama = await gm_dashboard_service.get_szavaztak_mar(jatek_id)
        max_jatekosok = gm_dashboard_service.jatekosok_szama_cache.get(jatek_id, 1)

        #Biztonsáig ellenőrzés
        if max_jatekosok <= 0:
            max_jatekosok = 1

        arany = szavaztak_szama / max_jatekosok

        #UI elemek frissítése
        szavaztak_progress.value = arany
        szavaztak_szoveg.value = f"{szavaztak_szama} / {max_jatekosok}"
        page.update()

    #Érvek frissítése
    async def update_ervek():
        ervek = await gm_dashboard_service.get_all_arguments(jatek_id)
        indoklasok = await gm_dashboard_service.get_extreme_evaluations(jatek_id)

        ervek_oszlop.controls.clear()

        if not ervek and not indoklasok:
            ervek_oszlop.controls.append(ft.Text("Még nem érkeztek érvek ebben a játékban...", italic = True))
        else:
            kombinalt_lista = []

            for erv_obj, jatekos_obj in ervek:
                kombinalt_lista.append({
                    "tipus": "erv",
                    "time": erv_obj.time,
                    "obj": erv_obj,
                    "jatekos": jatekos_obj
                })
            for indoklas in indoklasok:
                kombinalt_lista.append({
                    "tipus": "indoklas",
                    "time": indoklas.time,
                    "adatok": indoklas
                })

            #Sorbarendezés idő szerint csökkenő sorrendben
            kombinalt_lista.sort(key = lambda x: x["time"] if x["time"] else datetime.min, reverse=True)

            for item in kombinalt_lista:
                if item["tipus"] == "erv":
                    erv_obj = item["obj"]
                    jatekos_obj = item["jatekos"]
                    ido_szoveg = erv_obj.time.strftime("%Y. %m. %d %H:%M:%S") if erv_obj.time else "Ismeretlen időpont"
                    atlag = erv_obj.ertekeles_atlag if erv_obj.ertekeles_atlag is not None else 0.0

                    kartya = GmErvKartya(
                        jatekos_nev = jatekos_obj.felhasznalonev,
                        szerep = erv_obj.szerep,
                        kor = erv_obj.kor,
                        erv_szoveg = erv_obj.erv,
                        ertekeles_atlag = atlag,
                        bekuldes_ideje = ido_szoveg
                    )
                    ervek_oszlop.controls.append(kartya)

                elif item["tipus"] == "indoklas":
                    adatok = item["adatok"]
                    ido_szoveg = adatok.time.strftime("%Y. %m. %d %H:%M:%S") if adatok.time else "Ismeretlen időpont"
                    indoklas_kartya = IndoklasKartya(
                        ertekelo_nev = adatok.ertekelo_nev,
                        ertekelt_nev = adatok.ertekelt_jatekos_nev,
                        szerep = adatok.ertekelt_jatekos_szerep,
                        kor = adatok.kor,
                        ertekeles = adatok.ertekeles_erteke,
                        indoklas_szoveg = adatok.indoklas,
                        bekuldes_ideje = ido_szoveg
                    )
                    ervek_oszlop.controls.append(indoklas_kartya)

        page.update()

    async def next_player_click(e):
        e.control.disabled = True
        page.update()

        sikeres, msg = await gm_dashboard_service.set_next_player(jatek_id)

        if sikeres:
            await update_soron_levo_cache()
            await update_csatlakozott_jatekosok()
            await update_ertekeltek_mar()
            await update_soron_voltak()

            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.KOVETKEZO_JATEKOS)
        else:
            print(f"Hiba: {msg}")

        e.control.disabled = False
        page.update()

    #AlertDialog gombkezelő események
    async def confirm_end(e):
        page.pop_dialog()
        await gm_dashboard_service.set_game_ended(jatek_id)
        page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.KERDOIVEK_POST)
        page.update()
        print("Igen, lezárom a játékot")

    async def cancel_end(e):
        page.pop_dialog()
        end_game_button.disabled = False
        page.update()
        print("Mégse")

    #AlertDialog definiálása
    end_game_dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Figyelmeztetés!"),
        content = ft.Text("A játék lezárási feltételei még nem teljesültek (nem az utolsó körben jár a játék, vagy az utolsó körben még nem érvelt/értékelt mindenki). Biztos le akarod zárni a játékot?"),
        actions = [
            ft.Button("Igen, lezárom", on_click = confirm_end, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
            ft.Button("Mégse", on_click = cancel_end)
        ]
    )

    async def end_click(e):
        e.control.disabled = True
        page.update()

        #Ellenőrzés: teljesültek-e a lezárási feltételek?
        feltetelek_tlejesultek = await gm_dashboard_service.check_ready_to_end(jatek_id)

        if feltetelek_tlejesultek:
            await gm_dashboard_service.set_game_ended(jatek_id)
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.KERDOIVEK_POST)
        else:
            #Ha valamelyik feltétel nem teljesült (nem az utolsó körben tart a játék vagy az utolsó körben nem érvelt/értékelt mindenki)
            page.show_dialog(end_game_dialog)
            page.update()

    #AlertDialog a kör léptetése megerősítéséhez
    async def confirm_nect_round(e):
        page.pop_dialog()

        sikeres, msg = await gm_dashboard_service.start_next_round(jatek_id)

        if sikeres:
            await gm_dashboard_service.set_next_player(jatek_id)
            await update_jelenlegi_kor()
            await update_soron_levo_cache()
            await update_csatlakozott_jatekosok()
            await update_ertekeltek_mar()
            await update_erveltek_mar()
            await update_soron_voltak()
            page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.KOR_VALTOZOTT)
        else:
            print(f"Hiba: {msg}")

        next_round_button.disabled = False
        page.update()

    async def cancel_next_round(e):
        page.pop_dialog()
        next_round_button.disabled = False
        page.update()

    next_round_dialog = ft.AlertDialog(
        modal = True,
        title = ft.Text("Figyelmeztés!"),
        content = ft.Text("A jelenlegi körben még nem érvelt mindenki, vagy az utolsó érvelőt még nem értékelte mindenki. Biztosan el szeretnéd indítani a következő kört?"),
        actions = [
            ft.Button("Igen, indítom", on_click = confirm_nect_round, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
            ft.Button("Mégse", on_click = cancel_next_round)
        ]
    )

    async def next_round_click(e):
        e.control.disabled = True
        page.update()

        soron_volt_arany = soron_voltak_szoveg.data if hasattr(soron_voltak_szoveg, "data") else 0.0

        if soron_volt_arany >=0.99 and ertekeltek_progress.value >= 0.99:
            sikeres, msg = await gm_dashboard_service.start_next_round(jatek_id)

            if sikeres:
                await gm_dashboard_service.set_next_player(jatek_id)
                await update_jelenlegi_kor()
                await update_soron_levo_cache()
                await update_csatlakozott_jatekosok()
                await update_ertekeltek_mar()
                await update_erveltek_mar()
                await update_soron_voltak()
                page.pubsub.send_all_on_topic(jatek_topic(jatek_id), Uzenet.KOR_VALTOZOTT)

            else:
                print(f"Hiba: {msg}")
            e.control.disabled = False
            page.update()

        else:
            page.show_dialog(next_round_dialog)
            page.update()

    #Soron voltak frissítése
    async def update_soron_voltak():
        korok = await gm_dashboard_service.get_rounds(jatek_id)
        if not korok:
            return
        jelenlegi_kor = korok[0]

        #lekérjük, hányan voltak már soron
        soron_voltak = await gm_dashboard_service.get_soron_voltak_szama(jatek_id, jelenlegi_kor)
        max_jatekosok = gm_dashboard_service.jatekosok_szama_cache.get(jatek_id, 1)

        if max_jatekosok == 0:
            max_jatekosok = 1

        soron_voltak_szoveg.value = f"Eddig soron voltak: {soron_voltak} / {max_jatekosok}"

        soron_voltak_szoveg.data = soron_voltak / max_jatekosok
        page.update()

    #PubSub üzenetkezelő
    async def handle_pubsub_message(topic, message):
        #Ha változott e jelenlegi kör
        if message == Uzenet.KOR_VALTOZOTT:
            await update_jelenlegi_kor()
            await update_soron_levo_cache()
        #Ha új érv érkezett
        elif message == Uzenet.UJ_ERVELES:
            await update_erveltek_mar()
            await update_soron_levo_cache()
            await update_ertekeltek_mar()
            await update_ervek()
        #Ha új értékelés érkezett
        elif message == Uzenet.UJ_ERTEKELES:
            await update_ertekeltek_mar()
            await update_ervek()
        #Soron levő játékos léptetésekor
        elif message == Uzenet.KOVETKEZO_JATEKOS:
            await update_soron_levo_cache()
            await update_ertekeltek_mar()
            await update_soron_voltak()
        #Játék lezárásakor
        elif message == Uzenet.KERDOIVEK_POST:
            szavaztak_container.visible = True
            await update_szavaztak_mar()
            page.update()
        #Ha egy játékos leadta a játék végi díj szavazatát
        elif message == Uzenet.UJ_SZAVAZAT:
            await update_szavaztak_mar()

    #Feliratkozás az eseményekre
    page.pubsub.subscribe_topic(jatek_topic(jatek_id), handle_pubsub_message)

    #Indításkori lekérések
    await update_ervek()
    await update_soron_levo_cache()
    await update_csatlakozott_jatekosok()
    await update_jelenlegi_kor()
    await update_erveltek_mar()
    await update_ertekeltek_mar()
    await update_soron_voltak()

    next_player_button.on_click = next_player_click
    end_game_button.on_click = end_click
    next_round_button.on_click = next_round_click

    return ft.View(
        route = f"/gm_dashboard/{jatek_id}",
        controls = [
            ft.Row(
                controls = [l_sidebar, main_section, r_sidebar],
                expand = True
            )
        ]
    )