import flet as ft

from game.events import jatek_topic, Uzenet
from services import gm_dashboard_service

async def create_gm_dashboard_view(page: ft.Page, jatek_id: int):
    #Felhasználó lekérése a session-ből
    current_user = page.session.store.get("current_user")

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
                erveltek_container,
                ertekeltek_container
            ]
        ),
        expand=1
    )

    #Fő szekció
    main_section = ft.Container(
        ft.Column(
            controls = [
                ft.Text("Itt lesz felsorolva MINDEN érv"),
                ft.Row(
                    controls = [
                        ft.Button("Következő játékos"),
                        ft.Button("Következő kör"),
                        ft.Button("Játék lezárása")
                    ],
                    expand = True
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

    #PubSub üzenetkezelő
    async def handle_pubsub_message(topic, message):
        #Ha változott e jelenlegi kör
        if message == Uzenet.KOR_VALTOZOTT:
            await update_jelenlegi_kor()
        #Ha új érv érkezett
        elif message == Uzenet.UJ_ERVELES:
            await update_erveltek_mar()
            await update_soron_levo_cache()
            await update_ertekeltek_mar()
        #Ha új értékelés érkezett
        elif message == Uzenet.UJ_ERTEKELES:
            await update_ertekeltek_mar()

    #Feliratkozás az eseményekre
    page.pubsub.subscribe_topic(jatek_topic(jatek_id), handle_pubsub_message)

    #Indításkori lekérések
    await update_soron_levo_cache()
    await update_csatlakozott_jatekosok()
    await update_jelenlegi_kor()
    await update_erveltek_mar()
    await update_ertekeltek_mar()

    return ft.View(
        route = f"/gm_dashboard/{jatek_id}",
        controls = [
            ft.Row(
                controls = [l_sidebar, main_section, r_sidebar],
                expand = True
            )
        ]
    )