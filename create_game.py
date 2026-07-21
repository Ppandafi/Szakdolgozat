import flet as ft
from pygments.lexers import sieve, automation

from database import SessionLocal, Jatek, Jatekos, JatekosJatek, Kerdoiv, Szerep, Dijak, NulladikKor, JelenlegiKor

def show_create_page(page:ft.Page, current_user, uj_id, on_cancel):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    #Szerkesztett játék lekérése
    db = SessionLocal()
    try:
        szerkesztett_jatek = db.query(Jatek).filter(Jatek.id == uj_id).first()
        print(f"Szerkesztett játék betöltve")
    except Exception as e:
        print(f"Hiba a játék betöltése során: {e}")
    finally:
        db.close()

    #Játékmester adatainak lekérése
    db = SessionLocal()
    try:
        felhasznalo = db.query(Jatekos).filter((Jatekos.email == current_user) | (Jatekos.felhasznalonev == current_user)).first()
        print(f"Játékmester: {felhasznalo.__dict__}")
    except Exception as e:
        print(e)
    finally:
        db.close()

    def cancel_click(e):
        page.show_dialog(backdialog)

    #Dashboardra visszalépés
    def confirm_cancel(e):
        #Játék és adatainak törlése az adatbázisból
        db = SessionLocal()
        try:
            #Adatok törlése
            db.query(NulladikKor).filter(NulladikKor.jatek_id == uj_id).delete()
            db.query(JelenlegiKor).filter(JelenlegiKor.jatek_id == uj_id).delete()
            db.query(JatekosJatek).filter(JatekosJatek.jatek_id == uj_id).delete()
            db.query(Szerep).filter(Szerep.jatek_id == uj_id).delete()
            db.query(Dijak).filter(Dijak.jatek_id == uj_id).delete()
            db.query(Kerdoiv).filter(Kerdoiv.jatek_id == uj_id).delete()

            #Játék törlése:
            db.query(Jatek).filter(Jatek.id == uj_id).delete()

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Törlés hiba: {e}")
        finally:
            db.close()
        page.pop_dialog()
        on_cancel()

    #Mégse - folytatódik a kitöltés
    def decline_cancel(e):
        page.pop_dialog()

    backdialog = ft.AlertDialog(
        modal = True,
        title = "FIGYELEM",
        content = ft.Column(
            controls = [
                ft.Text(f"A főképernyőre való visszalépéssel a játék törlődik!")
            ],
            tight = True
        ),
        actions = [
            ft.Button("Igen, visszalépek", on_click = confirm_cancel, color = ft.Colors.WHITE, bgcolor = ft.Colors.RED),
            ft.Button("Nem, folytatom a kitöltést", on_click = decline_cancel)
        ]
    )

    #Csatlakozott játékosok
    csatlakozok_lista = ft.Column()

    def update_csatlakozott_jatekosok(topic = None, uzenet = None):
        db = SessionLocal()
        try:
            #Felhasználónevek lekérése
            resztvevok = db.query(Jatekos.felhasznalonev).join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id).filter(JatekosJatek.jatek_id == uj_id).all()
            #Csatlakozók lista kiürítése és újraépítése
            csatlakozok_lista.controls.clear()
            csatlakozok_lista.controls.append(
                ft.Text("Csatlakozott játékosok: ", weight = ft.FontWeight.BOLD, size = 20)
            )
            for (nev), in resztvevok:
                if nev == felhasznalo.felhasznalonev:
                    csatlakozok_lista.controls.append(ft.Text(f"- {nev} (Ön)"))
                else:
                    csatlakozok_lista.controls.append(ft.Text(f"- {nev}"))
            page.update()
        except Exception as e:
            print(f"Hiba a csatlakozott játékosok frissítésekor: {e}")
        finally:
            db.close()

    #Feliratkozás az aktuális játék eseményeire
    page.pubsub.subscribe_topic(f"jatek_{uj_id}", update_csatlakozott_jatekosok)
    update_csatlakozott_jatekosok()

    #Javaslatok
    javaslatok = ft.Text("Itt lesznek a díj/szerep javaslatok")

    #Csatlakozott játékok és javaslatok
    l_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Container(content = csatlakozok_lista),
                ft.Container(content = javaslatok),
            ],
            width = 300,
            scroll = ft.ScrollMode.AUTO,
        ),
        #bgcolor = ft.Colors.CYAN_700
    )

    #Eddig felvett adatok (cím, szerepek, díjak, kérdések)
    cim_info = ft.Text("Új játék (szerkesztés alatt)")
    szerep_info = ft.Column()
    dij_info = ft.Column()
    kerdes_info = ft.Column()
    min_info = ft.Text("")
    max_info = ft.Text("")

    #A sidebar felépítése
    r_sidebar = ft.Container(
        ft.Column(
            controls = [
                ft.Text(f"Játék adatai:", weight = ft.FontWeight.BOLD, size = 20),
                ft.Text(f"SZOBAKÓD: {szerkesztett_jatek.lobby_code}", weight = ft.FontWeight.BOLD, size = 20),
                ft.Text("- Cím:", weight = ft.FontWeight.BOLD),
                cim_info,
                ft.Row(
                    controls = [
                        ft.Text("Min. kör: ", weight = ft.FontWeight.BOLD),
                        min_info,
                        ft.Text("   Max. kör: ", weight = ft.FontWeight.BOLD),
                        max_info
                    ]
                ),
                ft.Text("- Szerepek:", weight = ft.FontWeight.BOLD),
                szerep_info,
                ft.Text("- Díjak:", weight = ft.FontWeight.BOLD),
                dij_info,
                ft.Text("- Kérdések:", weight = ft.FontWeight.BOLD),
                kerdes_info,
            ],
            width = 300,
            scroll = ft.ScrollMode.AUTO,
        ),
        #bgcolor = ft.Colors.CYAN_700
    )

    #BEVITELI MEZŐK
    #Cím
    title_input = ft.TextField(expand = True)

    #Ismertetés
    description_input = ft.TextField(expand = True, multiline = True)

    #Szerepek
    positions_input = ft.TextField(expand = True)

    #Díjak
    awards_input = ft.TextField(expand = True)

    #Minimum kör
    min_round_input = ft.TextField(expand = True)

    #Maximum kör
    max_round_input = ft.TextField()

    #Kérdések
    questions_input = ft.TextField()
    elott_utan = ft.Dropdown(
        options=[
            ft.DropdownOption(key="post", text="Csak játék utáni"),
            ft.DropdownOption(key="both", text="Játék előtti és utáni")
        ],
        label="Kérlek válassz...",
    )

    #Értesítő szöveg konstruktor
    def create_alert_text():
        return ft.Text(value = "", color = ft.Colors.RED, visible = False)

    #Külön értesítő szöveg minden beviteli mezőhöz
    title_alert = create_alert_text()
    description_alert = create_alert_text()
    positions_alert = create_alert_text()
    award_alert = create_alert_text()
    questions_alert = create_alert_text()
    min_round_alert = create_alert_text()
    max_round_alert = create_alert_text()

    #BEÍRT ADATOK MENTÉSE
    #cím
    def title_save(e):
        #Ellenőrzés, hogy ki van-e töltve a cím
        if not title_input.value:
            title_alert.value = "Kérlek add meg a játék címét!"
            title_alert.color = ft.Colors.RED
        else:
            # Új cím mentése
            try:
                db = SessionLocal()
                if szerkesztett_jatek:
                    aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                    aktualis_jatek.cim = title_input.value
                    db.commit()
                    cim_info.value = title_input.value
                    title_input.value = ""

                    title_alert.value = "Cím sikeresen mentve!"
                    title_alert.color = ft.Colors.GREEN
            except Exception as e:
                db.rollback()
                print(f"Hiba a játék címének mentése során: {e}")
                title_alert.value = "Hiba az adatbázis mentése során!"
                title_alert.color = ft.Colors.RED
                title_input.value = ""
            finally:
                db.close()

        title_alert.visible = True
        page.update()


    #ismertetés
    def description_save(e):
        #Ellenőrzés, hogy ki van-e töltve az ismertetés
        if not description_input.value:
            description_alert.value = "Kérlek add meg a játék az ismertetést!"
            description_alert.color = ft.Colors.RED
        else:
            #Ismertetés mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                aktualis_jatek.ismertetes = description_input.value
                db.commit()
                description_input.value = ""

                description_alert.value = "Ismertetés sikeresen mentve!"
                description_alert.color = ft.Colors.GREEN
            except Exception as e:
                db.rollback()
                print(f"Hiba a játék ismertetésének mentése során: {e}")
                description_alert.value = "Hiba az adatbázis mentése során!"
                description_alert.color = ft.Colors.RED
                description_input.value = ""
            finally:
                db.close()

        description_alert.visible = True
        page.update()

    #szerepek
    def add_position(e):
        #Ellenőrzés, hogy van-e beírva szerep
        if not positions_input.value:
            positions_alert.value = "Kérlek add meg a szerepet!"
            positions_alert.color = ft.Colors.RED
        else:
            #Szerep mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                #a felsorolt szerepek felbontása a vesszők mentén
                szerepek = positions_input.value.split(',')
                #szóközök és üres elemek eltávolítása
                tisztitott_szerepek = [szerep.strip() for szerep in szerepek if szerep.strip()]

                #Ha a tisztítás után nem maradt érvényes szerep
                if not tisztitott_szerepek:
                    positions_alert.value = "Kérlek érvényes formátumban (vesszővel elválasztva) add meg a szerepeket!"
                    positions_input.color = ft.Colors.RED
                else:
                    #duplikátumok kiszűrése
                    egyedi_szerepek = list(dict.fromkeys(tisztitott_szerepek))
                    #meglévő szerepek lekérése
                    meglevo_szerepek_query = db.query(Szerep.szerepkor).filter(Szerep.jatek_id == aktualis_jatek.id).all()
                    meglevo_szerepek = [sz[0] for sz in meglevo_szerepek_query]

                    hozzaadott = 0 #csak UX javításhoz kell, hogy kiíjuk, hány új szerep lett hozzáadva

                    for uj_szerep_nev in egyedi_szerepek:
                        if uj_szerep_nev not in meglevo_szerepek:
                            uj_szerep = Szerep(jatek_id = aktualis_jatek.id, szerepkor = uj_szerep_nev)
                            db.add(uj_szerep)
                            hozzaadott += 1
                            szerep_info.controls.append(ft.Text(f"{uj_szerep_nev}"))

                    db.commit()

                    if hozzaadott > 0:
                        positions_alert.value = f"{hozzaadott} új szerep hozzáadva!"
                        positions_alert.color = ft.Colors.GREEN
                        positions_input.value = ""
                    else:
                        positions_alert.value = "A megadott szerep(ek) már szerepel(nek) a játékban!"
                        positions_alert.color = ft.Colors.RED
                        positions_input.value = ""

            except Exception as e:
                db.rollback()
                print(f"Hiba a szerep(ek) mentése során: {e}")
                positions_alert.value = "Hiba az adatbázis mentése során"
                positions_alert.color = ft.Colors.RED
                positions_input.value = ""
            finally:
                db.close()

        positions_alert.visible = True
        page.update()


    #díjak
    def add_award(e):
        #Ellenőrzés, hogy van-e beírva díj
        if not awards_input.value:
            award_alert.value = "Kérlek add meg a díjat!"
            award_alert.color = ft.Colors.RED
        else:
            #Díjak mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                #a felsorolt díjak felbontása vesszők mentén
                dijak = awards_input.value.split(',')
                #szóközök és üres elemek eltávolítása
                dijak_tisztitott = [dij.strip() for dij in dijak if dij.strip()]

                #Ha a tisztítás után nem maradt érvényes díj
                if not dijak_tisztitott:
                    award_alert.value = "Kérlek érvényes formátumban (vesszővel elválasztva) add meg a díjakat!"
                    award_alert.color = ft.Colors.RED
                else:
                    #duplikátumok kiszűrése
                    egyedi_dijak = list(dict.fromkeys(dijak_tisztitott))
                    #meglévő díjak lekérdezése
                    meglevo_dijak_query = db.query(Dijak.dij).filter(Dijak.jatek_id == aktualis_jatek.id).all()
                    meglevo_dijak = [d[0] for d in meglevo_dijak_query]

                    hozzaadott = 0 #csak UX javításhoz kell, hogy kiíjuk, hány új díj lett hozzáadva

                    for uj_dij_nev in egyedi_dijak:
                        if uj_dij_nev not in meglevo_dijak:
                            uj_dij = Dijak(jatek_id = aktualis_jatek.id, dij = uj_dij_nev)
                            db.add(uj_dij)
                            hozzaadott += 1
                            dij_info.controls.append(ft.Text(f"{uj_dij_nev}"))

                    db.commit()

                    if hozzaadott > 0:
                        award_alert.value = f"{hozzaadott} új díj hozzáadva!"
                        award_alert.color = ft.Colors.GREEN
                        awards_input.value = ""
                    else:
                        award_alert.value = "A megadott díj(ak) már szerepel(nek) a játékban!"
                        award_alert.color = ft.Colors.RED
                        awards_input.value = ""

            except Exception as e:
                db.rollback()
                print(f"Hiba a díj(ak) mentése során: {e}")
                award_alert.value = "Hiba az adatbázis mentése során!"
                award_alert.color = ft.Colors.RED
                awards_input.value = ""
            finally:
                db.close()

            award_alert.visible = True
            page.update()


    #kérdések
    def add_question(e):
        #Ellenőrzés: ki van-e töltve a kérdés és a dropdown is
        if not questions_input.value:
            questions_alert.value = "Kérlek add meg a kérdést!"
            questions_alert.color = ft.Colors.RED
            questions_alert.visible = True
            page.update()
        elif not elott_utan.value:
            questions_alert.value = "Kérlek válassz a legördülő menüből!"
            questions_alert.visible = True
            page.update()
        else:
            #Kérdés mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolűsa a jelenlegi db seesionhöz
                if elott_utan.value == "post":
                    uj_kerdes = Kerdoiv(jatek_id = aktualis_jatek.id, kerdes = questions_input.value, jatek_elott_utan = False)
                    db.add(uj_kerdes)
                elif elott_utan.value == "both":
                    uj_kerdes = Kerdoiv(jatek_id = aktualis_jatek.id, kerdes = questions_input.value, jatek_elott_utan = True)
                    db.add(uj_kerdes)

                questions_alert.value = "Kérdés sikeresen felvéve!"
                questions_alert.color = ft.Colors.GREEN
                if elott_utan.value == "post":
                    kerdes_info.controls.append(ft.Text(f"{questions_input.value} - Csak játék után"))
                else:
                    kerdes_info.controls.append(ft.Text(f"{questions_input.value} - Játék előtt és után"))
                questions_input.value = ""
                elott_utan.value = ""
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Hiba a kérdés mentése során: {e}")
                questions_alert.value = "Hiba az adatbázis mentése során!"
                questions_alert.color = ft.Colors.RED
                questions_input.value = ""
                elott_utan.value = ""
            finally:
                db.close()

            questions_alert.visible = True
            page.update()

    #minimum kör
    def save_min(e):
        #Ellenőrzés, hogy ki van-e töltve a minimum kör
        if not min_round_input.value or not min_round_input.value.isdigit():
            min_round_alert.value = "Kérlek add meg, hogy legalább hány kör legyen!"
            min_round_alert.color = ft.Colors.RED
        else:
            #Minimum kör mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                aktualis_jatek.min_kor = min_round_input.value
                db.commit()
                min_info.value = min_round_input.value
                min_round_input.value = ""

                min_round_alert.value = "Minimum kör sikeresen mentve!"
                min_round_alert.color = ft.Colors.GREEN
            except Exception as e:
                db.rollback()
                print(f"Hiba a min kör mentése során: {e}")
                min_round_alert.value = "Hiba az adatbázis mentése során!"
                min_round_alert.color = ft.Colors.RED
                min_round_input.value = ""
            finally:
                db.close()

        min_round_alert.visible = True
        page.update()

    #maximum kör
    def save_max(e):
        #Ellenőrzés, hogy ki van-e töltve a maximum kör
        if not max_round_input.value or not max_round_input.value.isdigit():
            max_round_alert.value = "Kérlek add meg, hogy legfeljebb hány kör legyen!"
            max_round_alert.color = ft.Colors.RED
        else:
            #Maximum kör mentése
            try:
                db = SessionLocal()
                aktualis_jatek = db.merge(szerkesztett_jatek) #szerkesztett_jatek változó csatolása a jelenlegi db Sessionhöz
                aktualis_jatek.max_kor = max_round_input.value
                db.commit()
                max_info.value = max_round_input.value
                max_round_input.value = ""

                max_round_alert.vlaue = "Maximum kör sikeresen mentve!"
                max_round_alert.color = ft.Colors.GREEN
            except Exception as e:
                db.rollback()
                print(f"Hiba a max mentése során: {e}")
                max_round_alert.value = "Hiba az adatbázis mentése során!"
                max_round_alert.color = ft.Colors.RED
                max_round_input.value = ""
            finally:
                db.close()

        max_round_alert.visible = True
        page.update()

    #Fő szekció
    main_section = ft.Column(
        controls = [
            ft.Text("Kérlek add meg a játék adatait", weight = ft.FontWeight.BOLD, size = 30, text_align = ft.TextAlign.CENTER),
            ft.Text(
                "FIGYELEM: A 'Véglegesít' gombra csak akkor kattints, ha már mindent hozzáadtál a játékhoz, amit szeretnél. A véglegesítés előtt a 'Hozzáad' gombbal tudod menteni a hozzáadott adatokat",
                color = ft.Colors.RED
                ),
            ft.Column(
                controls = [
                    #cím
                    ft.Column(
                        controls = [
                            ft.Text("Cím:"),
                            ft.Row(
                                controls = [
                                    title_input,
                                    ft.Button("Mentés", on_click = title_save)
                                ]
                            ),
                            title_alert
                        ]
                    ),
                    #ismertetés
                    ft.Column(
                        controls = [
                            ft.Text("Ismertetés:"),
                            ft.Row(
                                controls = [
                                    description_input,
                                    ft.Button("Mentés", on_click = description_save)
                                ]
                            ),
                            description_alert
                        ]
                    ),
                    #minimum és maximum körök száma
                    ft.Column(
                        controls = [
                            ft.Row(
                                controls = [
                                    #minimum kör
                                    ft.Column(
                                        controls = [
                                            ft.Text("Minimum kör:"),
                                            ft.Row(
                                                controls = [
                                                    min_round_input,
                                                    ft.Button("Mentés", on_click = save_min)
                                                ]
                                            ),
                                            min_round_alert
                                        ],
                                        expand = True
                                    ),
                                    #maximum kör
                                    ft.Column(
                                        controls = [
                                            ft.Text("Maximum kör:"),
                                            ft.Row(
                                                controls = [
                                                    max_round_input,
                                                    ft.Button("Mentés", on_click = save_max)
                                                ]
                                            ),
                                            max_round_alert
                                        ],
                                        expand = True
                                    )
                                ]
                            )
                        ]
                    ),
                    #szerepek
                    ft.Column(
                        controls = [
                            ft.Text("Szerepek:"),
                            ft.Row(
                                controls = [
                                    positions_input,
                                    ft.Button("Hozzáad", on_click = add_position)
                                ]
                            ),
                            positions_alert
                        ]
                    ),
                    #díjak
                    ft.Column(
                        controls = [
                          ft.Text("Díjak"),
                          ft.Row(
                              controls = [
                                  awards_input,
                                  ft.Button("Hozzáad", on_click = add_award)
                              ]
                          ),
                            award_alert
                      ]
                    ),
                    #kérdések
                    ft.Column(
                        controls = [
                            ft.Text("Kérdőív kérdés:"),
                            ft.Row(
                                controls = [
                                    questions_input,
                                    elott_utan,
                                    ft.Button("Hozzáad", on_click = add_question)
                                ]
                            ),
                            questions_alert
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Button("Mégse", on_click = cancel_click),
                            ft.Button("Véglegesít", color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE)
                        ]
                    )
                ]
            )
        ],
        scroll = ft.ScrollMode.AUTO,
        expand = True,
    )
    page.add(
        ft.Row(
            controls = [
                l_sidebar,
                main_section,
                r_sidebar
            ],
            expand = True,
        )
    )
    page.update()