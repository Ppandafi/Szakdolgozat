# AZ ADATBÁZIST DUMMY ADATOKKAL FELTÖLTŐ FILE
from datetime import datetime
import random
from faker import Faker
# Adatbázis tábláinak importálása
from database import (
    SessionLocal, init_db, Base, engine, Jatekos, Jatek, JatekosJatek, Szerep, Dijak, DijatKapott,
    DijSzavazas, JelenlegiKor, SoronVan, NulladikKor, JatekosSzerep, JatekosErv,
    Kerdoiv, JatekosValaszolPost, JatekosValaszolPre, ErvRendszer
)

# Faker inicializálása magyar nyelven
fake = Faker('hu_HU')

# Szerepek és díjak definiálása
SZEREPEK = ["Gyilkos", "Nyomozó", "Orvos", "Áldozat", "Testőr", "Polgármester"]
DIJAK = ["Legjobb érvelő", "Legviccesebb", "Legcsendesebb", "Legjobb stratéga", "Legkonstruktívabb"]

# Táblák feltöltése
def seed_all_tables(jatekosok_szama = 15, jatekok_szama = 5):
    # Adatbázis kiürítése
    Base.metadata.drop_all(bind = engine)
    # Adatbázis újbóli létrehozása
    init_db()
    db = SessionLocal()
    try:
        print("Az adatbázis teljes feltöltése megkezdődött...")

        # Játékosok
        jatekosok = []
        for _ in range(jatekosok_szama):
            jatekos = Jatekos(
                felhasznalonev = fake.unique.user_name(),
                email = fake.unique.email(),
                jelszo = fake.password(length = 12),
            )
            db.add(jatekos)
            jatekosok.append(jatekos)

        # Fix teszt játékos létrehozása
        test_jatekos = Jatekos(
            felhasznalonev = "test",
            email = "test@test",
            jelszo = "test"
        )
        db.add(test_jatekos)
        jatekosok.append(test_jatekos)

        db.commit()
        print(f"-> {jatekosok_szama + 1} játékos létrehozva")

        # Játékok
        jatekok = []
        for i in range(jatekok_szama):
            if i == 0:
                general_kod = "AAAA-1234"
            else:
                general_kod = fake.unique.bothify(text = '????-####').upper()
            jatek = Jatek(
                cim = fake.sentence(nb_words = 3).replace(".", " "),
                ismertetes = fake.paragraph(nb_sentences = 4),
                min_kor = 3,
                max_kor = 7,
                lobby_code = general_kod
            )
            db.add(jatek)
            jatekok.append(jatek)
            db.commit()
            print(f"-> {jatekok_szama} játék létrehozva")

        # Játékokhoz kapcsolódó adatok
        for jatek in jatekok:
            # Szerepek (a körök száma nem lehet nagyobb, mint az elérhető szerepek)
            kivalasztott_szerepek = random.sample(SZEREPEK, k = random.randint(3, len(SZEREPEK)))
            for szerep_nev in kivalasztott_szerepek:
                db.add(Szerep(jatek_id = jatek.id, szerepkor = szerep_nev))

            # Jelenlegi kör (melyik játék épp hányadik körben tart)
            #Garantáljuk, hogy az első generált játék a 0. körben legyen
            if jatek == jatekok[0]:
                aktualis_kor = 0
            else:
                aktualis_kor = random.randint(1, len(kivalasztott_szerepek))
            db.add(JelenlegiKor(jatek_id = jatek.id, kor = aktualis_kor))

            # Nulladik kör és javaslatok
            db.add(NulladikKor(
                jatek_id = jatek.id,
                javaslat = fake.word(),
                szerep_dij = random.choice([True, False])
            ))

            # Érvrendszer
            db.add(ErvRendszer(
                jatek_id = jatek.id,
                jatek_cim = jatek.cim,
                erv = fake.sentence(),
                erv_atlag = round(random.uniform(5.0, 10.0), 2)
            ))

            # Díjak
            kivalasztott_dijak = random.sample(DIJAK, k = random.randint(2, 4))
            for dij_nev in kivalasztott_dijak:
                db.add(Dijak(jatek_id = jatek.id, dij = dij_nev))

            # Kérdőívek: 2-2 játék előtt és után
            kerdesek = []
            for _ in range(2):
                pre_k = Kerdoiv(jatek_id = jatek.id, kerdes = fake.sentence(nb_words = 6) + "?", jatek_elott_utan = True)
                post_k = Kerdoiv(jatek_id = jatek.id, kerdes = fake.sentence(nb_words = 6) + "?", jatek_elott_utan = False)
                db.add(pre_k)
                db.add(post_k)
                kerdesek.extend([pre_k, post_k])

        db.commit()
        print("-> Játék metaadatok (szerepek, díjak, kérdőívek, érvrendszer) generálva")

        # Játékosok részvétele és események szimulációja körökön keresztül
        for jatek in jatekok:
            # Játékosok kiválasztása, test felhasználó fix hozzáadása
            egyeb_jatekosok = [j for j in jatekosok if j.felhasznalonev != "test"]
            resztvevok = random.sample(egyeb_jatekosok, random.randint(4, 7))
            resztvevok.append(test_jatekos)

            # Szerepek és díjak lekérése az adott játékhoz
            jatek_szerepek = [sz.szerepkor for sz in db.query(Szerep).filter_by(jatek_id = jatek.id).all()]
            jatek_dijak = [d.dij for d in db.query(Dijak).filter_by(jatek_id = jatek.id).all()]

            # Kérdések lekérése
            jatek_pre_kerdesek = db.query(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=True).all()
            jatek_post_kerdesek = db.query(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=False).all()
            aktualis_kor_obj = db.query(JelenlegiKor).filter_by(jatek_id=jatek.id).first()
            aktualis_kor_szam = aktualis_kor_obj.kor if aktualis_kor_obj else 1

            jatekmester_kivalasztva = False

            # Nyilvántartjuk, hogy melyik játékos milyen szerepeket kapott már az adott játékban
            jatekos_kiosztott_szerepek = {j.id: [] for j in resztvevok}

            for jatekos in resztvevok:
                # JatekosJatek kapcsolat létrehozása
                db.add(JatekosJatek(
                    jatekos_id = jatekos.id,
                    jatek_id = jatek.id,
                    jatekmester = not jatekmester_kivalasztva
                ))
                jatekmester_kivalasztva = True

                # Kérdőív válaszok
                for kerdes in jatek_pre_kerdesek:
                    db.add(JatekosValaszolPre(
                        jatek_id=jatek.id,
                        jatekos_id=jatekos.id,
                        kerdes_id=kerdes.kerdes_id,
                        valasz=random.randint(1, 10)
                    ))
                for kerdes in jatek_post_kerdesek:
                    db.add(JatekosValaszolPost(
                        jatek_id=jatek.id,
                        jatekos_id=jatekos.id,
                        kerdes_id=kerdes.kerdes_id,
                        valasz=random.randint(1, 10)
                    ))

                # KÖRÖK SZIMULÁLÁSA (1-től az aktuális körig)
                for kor in range(1, aktualis_kor_szam + 1):
                    db.add(SoronVan(
                        jatek_id = jatek.id,
                        jatekos_id = jatekos.id,
                        kor = kor,
                        time = datetime.now()
                    ))

                    # Olyan szerep kiosztása, amit a játékos még nem kapott
                    elerheto_szerepek = [sz for sz in jatek_szerepek if sz not in jatekos_kiosztott_szerepek[jatekos.id]]
                    kiosztott_szerep = random.choice(elerheto_szerepek) if elerheto_szerepek else "Ismeretlen"
                    jatekos_kiosztott_szerepek[jatekos.id].append(kiosztott_szerep)

                    db.add(JatekosSzerep(
                        jatek_id = jatek.id,
                        jatekos_id = jatekos.id,
                        kor = kor,
                        szerep = kiosztott_szerep
                    ))

                    # Érvek létrehozása (a "test" kapjon felismerhető szöveget)
                    if jatekos.felhasznalonev == "test":
                        generalt_erv = f"A 'test' nevű játékos {kor}. körös próbaérve a(z) {kiosztott_szerep} szerepkört képviselve."
                    else:
                        generalt_erv = fake.text(max_nb_chars = 400)

                    db.add(JatekosErv(
                        jatek_id = jatek.id,
                        jatekos_id = jatekos.id,
                        szerep = kiosztott_szerep,
                        kor = kor,
                        erv = generalt_erv,
                        ertekeles_atlag = round(random.uniform(1.0, 10.0), 2),
                        time = datetime.now()
                    ))

                # Díjak és szavazások szimulációja (csak ha a játék véget ért, de tesztadatként mehet)
                if jatek_dijak:
                    kivalasztott_dij = random.choice(jatek_dijak)
                    db.add(DijSzavazas(
                        jatek_id = jatek.id,
                        jatek_dij = kivalasztott_dij,
                        jatekos_id = jatekos.id,
                        kapott_szavazatok = random.randint(0, 10)
                    ))
                    if random.random() > 0.7:
                        meglevo = db.query(DijatKapott).filter_by(jatek_id = jatek.id, jatekos_id = jatekos.id, dij = kivalasztott_dij).first()
                        if not meglevo:
                            db.add(DijatKapott(
                                jatek_id = jatek.id,
                                jatekos_id = jatekos.id,
                                dij = kivalasztott_dij,
                            ))

        db.commit()
        print("-> Játékos interakciók (kapcsolatok, szerepek, körönkénti érvek, válaszok, díjak) generálva.")
        print("\nSikeresen befejeződött a tesztadatok generálása!")

    except Exception as e:
        db.rollback()
        print(f"{e}\nHiba az adatok generálása során, minden változtatás elvetésre került.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_all_tables()