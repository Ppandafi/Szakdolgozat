import flet as ft
from flet.controls import keys

from database import SessionLocal, Jatek, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost, JatekosJatek, Jatekos


def show_answer_page(page:ft.Page, jatek_id, current_user,on_back_click):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.update()

    def back_clicked(e):
        on_back_click()

    #Javaslat ablak
    #beviteli lehetőségek
    proposal_input = ft.TextField(label = "Javaslat")
    proposal_dropdown = ft.Dropdown(
        options = [
            ft.DropdownOption(key = "dij", text = "Díj"),
            ft.DropdownOption(key = "szerep", text = "Szerep"),
        ],
        label = "Kérlek válassz..."
    )

    #Javaslat mentése:
    def submit_proposal(e):
        if proposal_input.value and proposal_dropdown.value:
            print("Javaslat mentése...")
        else:
            proposal_column.controls.append(ft.Text("Kérlek tölts ki minden mezőt!", color = ft.Colors.RED))

    proposal_column = ft.Column(
            controls = [
                ft.Row(
                    controls=[
                        proposal_input,
                        proposal_dropdown,
                        ft.Button("Küldés", on_click=submit_proposal),
                        ft.Button("Mégse", on_click=page.pop_dialog)
                    ], tight = True
                )
            ],
        tight = True
        )

    proposal_dialog = ft.AlertDialog(
        modal = True,
        title = "Javaslat",
        content = proposal_column
    )

    #Állapotváltozók a válaszok mentéséhez
    csuszkak = {}
    aktualis_fazis = None

    #Beküldés gomb külön deklarálva, hogy késbb letiltható legyen
    bekuldes_gomb = ft.Button("Beküldés", width = 210)

    #Többi játékos kiírása
    jatekosok = ft.Column()

    #Gombok
    gombok = ft.Column(
        controls = [
            bekuldes_gomb,
            ft.Button("Javaslattétel", width = 210, on_click = lambda: page.show_dialog(proposal_dialog)),
            ft.Button("Vissza", width = 210, on_click = back_clicked)
        ]
    )

    #Oldalsó sáv
    sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = gombok, padding = ft.Padding.only(left = 20, top = 10)),
                ft.Text("Játékosok:", weight = ft.FontWeight.BOLD),
                ft.Container(content = jatekosok),
            ]
        ),
        expand = 1,
        #bgcolor = ft.Colors.LIGHT_BLUE,
    )

    #Fő szekció
    main_section = ft.Column(
        expand = 3,
        alignment = ft.MainAxisAlignment.CENTER,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
    )

    #Csatlakozott játékosok lekérése
    def update_csatlakozott_jatekosok():
        db = SessionLocal()
        try:
            #Felhasználónevek lekérése
            resztvevok = db.query(Jatekos.felhasznalonev).join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id).filter(JatekosJatek.jatek_id == jatek_id).all()
            #Csatlakozók lista kiürítése
            jatekosok.controls.clear()

            #Az aktuális felhasználó nevének lekérése
            aktualis_felhasznalo = db.query(Jatekos.felhasznalonev).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
            aktualis_nev = aktualis_felhasznalo[0] if aktualis_felhasznalo else ""

            #Lista feltöltése a nevekkel
            for (nev,) in resztvevok:
                if nev == aktualis_nev:
                    jatekosok.controls.append(ft.Text(f"- {nev} (Ön)"))
                else:
                    jatekosok.controls.append(ft.Text(f"- {nev}"))
            page.update()

        except Exception as e:
            print(f"Hiba a játékosok frissíése folyamán: {e}")
        finally:
            db.close()

    #Kérdések betöltése
    def betolt_kerdesek(message):
        nonlocal aktualis_fazis #hozzáférés külső változóhoz
        db = SessionLocal()
        try:
            #Kérdések lekérése a kapott üzenet alapján:
            if message == "kerdoivek_pre":
                aktualis_fazis = "pre" #fázis beállítása
                #Csak a játék előtti kérdések lekérése
                kerdesek = db.query(Kerdoiv).filter(Kerdoiv.jatek_id == jatek_id, Kerdoiv.jatek_elott_utan == True).all()
            elif message == "kerdoivek_post":
                aktualis_fazis = "post" #fázis beállítása
                #Minden kérdés lekérése
                kerdesek = db.query(Kerdoiv).filter(Kerdoiv.jatek_id == jatek_id).all()

            #Felület kiürítése és kérdések betöltése
            main_section.controls.clear()
            csuszkak.clear()
            main_section.alignment = ft.MainAxisAlignment.START

            main_section.controls.append(ft.Text("Kérlek a következő kérdéseket pontozd 1-től 10-ig, hogy mennyire értesz egyet velük"))

            if not kerdesek:
                main_section.controls.append(ft.Text("Nincsenek megjeleníthető kérdések"))
            else:
                for kerdes in kerdesek:
                    uj_csuszka = ft.Slider(min = 1, max = 10, divisions = 9, label = "{value} pont")
                    csuszkak[kerdes.kerdes_id] = uj_csuszka #a csúszka értékét eltároljuk a szótárban

                    main_section.controls.append(
                        ft.Column([
                            ft.Text(kerdes.kerdes, size = 15),
                            uj_csuszka
                        ])
                    )
            bekuldes_gomb.disabled = False
            page.update()

        except Exception as e:
            print(f"Hiba a kérdések betöltése során: {e}")
            main_section.controls.append(ft.Text("Hiba az adatok betöltésekor"))
            page.update()
        finally:
            db.close()

    def handle_pubsub_message(topic, message):
        #Ellenőrzés: a kérdőívek kiírásáról szól-e az üzenet
        if message in ["kerdoivek_pre", "kerdoivek_post"]:
            betolt_kerdesek(message)
        elif message == "uj_jatekos":
            update_csatlakozott_jatekosok()

    page.pubsub.subscribe_topic(f"jatek_{jatek_id}", handle_pubsub_message)

    #Logika, ami eldönti, hogy várakoztató szöveggel, vagy rögtön a kérdések megjelenítésével kezdünk
    db = SessionLocal()
    try:
        #Aktuális játék lekérése
        aktualis_jatek = db.query(Jatek).filter(Jatek.id == jatek_id).first()
        if aktualis_jatek and aktualis_jatek.kerdoivek_kikuldve:
            #Ha már ki lettek küldve a kérdőívek
            betolt_kerdesek("kerdoivek_pre")
        else:
            #Még nincsenek a kérdések kiküldve, várakozó szöveg
            main_section.controls.append(
                ft.Text("Kérlek várj, amíg a játékmester kiküldi a kérdőíveket...", size = 30, weight = ft.FontWeight.BOLD)
            )
    except Exception as e:
        print(f"Hiba a játék állapotának lekérésekor: {e}")
        main_section.controls.append(ft.Text("Hiba az adatok betöltésekor"))
        page.update()
    finally:
        db.close()

    #Válaszok mentése
    def bekuldes_click(e):
        if not aktualis_fazis or not csuszkak:
            #Ha nincsenek kérdések, nem csinál semmit
            return

        db = SessionLocal()
        try:
            #Játékos id lekérése
            felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
            if not felhasznalo:
                return

            #Végigmegyünk az eltárolt csúszkákon
            for kerdes_id, csuszka in csuszkak.items():
                valasz_ertek = int(csuszka.value)

                if aktualis_fazis == "pre":
                    #Ellenőrzés: ne mentsünk duplán, ha a játékos kétszer kattint
                    meglevo = db.query(JatekosValaszolPre).filter_by(jatek_id = jatek_id, jatekos_id = felhasznalo.id, kerdes_id = kerdes_id).first()
                    if meglevo:
                        meglevo.valasz = valasz_ertek
                    else:
                        uj_valasz = JatekosValaszolPre(jatek_id = jatek_id, jatekos_id = felhasznalo.id, kerdes_id = kerdes_id, valasz = valasz_ertek)
                        db.add(uj_valasz)

                elif aktualis_fazis == "post":
                    # Ellenőrzés: ne mentsünk duplán, ha a játékos kétszer kattint
                    meglevo = db.query(JatekosValaszolPost).filter_by(jatek_id = jatek_id, jatekos_id = felhasznalo.id, kerdes_id = kerdes_id).first()
                    if meglevo:
                        meglevo.valasz = valasz_ertek
                    else:
                        uj_valasz = JatekosValaszolPost(jatek_id = jatek_id, jatekos_id = felhasznalo.id, kerdes_id = kerdes_id, valasz = valasz_ertek)
                        db.add(uj_valasz)

            db.commit()

            #Beküldés gomb letiltása
            bekuldes_gomb.disabled = True
            main_section.controls.append(ft.Text("Válaszok sikeresen mentve!", color = ft.Colors.GREEN))
            page.update()
        except Exception as e:
            print(f"Hiba az adatok mentése során: {e}")
            main_section.controls.append(ft.Text("Hiba a válaszok mentése során", color = ft.Colors.RED))
        finally:
            db.close()

    #Funkció hozzárendelése a gombhoz
    bekuldes_gomb.on_click = bekuldes_click

    #Játékos lista feltöltése
    update_csatlakozott_jatekosok()

    page.add(
        ft.Row(
            controls = [
                sidebar,
                main_section
            ],
            expand = True,
        )
    )
    page.update()