#AZ ADATBÁZIST DUMMY ADATOKKAL FELTÖLTŐ FILE
from datetime import datetime
import random
from faker import Faker
#Adatbázis tábláinak importálása
from database import (
SessionLocal, init_db, Base, engine, Jatekos, Jatek, JatekosJatek, Szerep, Dijak, DijatKapott,
DijSzavazas, JelenlegiKor, SoronVan, NulladikKor, JatekosSzerep, JatekosErv,
Kerdoiv, JatekosJatek, JatekosValaszolPost, JatekosValaszolPre, ErvRendszer
)

#Faker inicializálása magyar nyelven
fake = Faker('hu_HU')

#Szerepek és díjak definiálása
SZEREPEK = ["Gyilkos", "Nyomozó", "Orvos", "Áldozat", "Testőr", "Polgármester"]
DIJAK = ["Legjobb érvelő", "Legviccesebb", "Legcsendesebb", "Legjobb stratéga", "Legkonstruktívabb"]

#Táblák feltöltése
def seed_all_tables(jatekosok_szama = 15, jatekok_szama = 3):
    #Adatbázis kiürítése
    Base.metadata.drop_all(bind = engine)
    #Adatbázis újboli létrehozása
    init_db()
    db = SessionLocal()
    try:
        print("Az adatbázis teljes feltöltése megkezdődött...")

        #Játékosok
        jatekosok = []
        for _ in range(jatekosok_szama):
            jatekos = Jatekos(
                felhasznalonev = fake.unique.user_name(),
                email = fake.unique.email(),
                jelszo = fake.password(length = 12),
            )
            db.add(jatekos)
            jatekosok.append(jatekos)

        #Fix teszt játékos létrehozása
        test_jatekos = Jatekos(
            felhasznalonev = "test",
            email = "test",
            jelszo = "test"
        )
        db.add(test_jatekos)
        jatekosok.append(test_jatekos)

        db.commit()
        print(f"-> {jatekosok_szama} játékos létrehozva")

        #Játékok
        jatekok = []
        for _ in range(jatekok_szama):
            jatek = Jatek(
                cim = fake.sentence(nb_words = 3).replace(".", " "), #nb_words: hány szóból álljon a mondat
                ismertetes = fake.paragraph(nb_sentences = 4),
                min_kor = 3,
                max_kor = 7,
                lobby_code = fake.unique.bothify(text = '????-####').upper()
            )
            db.add(jatek)
            jatekok.append(jatek)
            db.commit()
            print(f"-> {jatekok_szama} játék létrehozva")

        #Játékokhoz kapcsolódó adatok
        for jatek in jatekok:
            #Jelenlegi kör:
            aktualis_kor = random.randint(1, 4)
            db.add(JelenlegiKor(jatek_id = jatek.id, kor = aktualis_kor))

            #Nulladik kör és javaslatok
            db.add(NulladikKor(
                jatek_id = jatek.id,
                javaslat = fake.word(),
                szerep_dij = random.choice([True, False])
            ))

            #Érvrendszer
            db.add(ErvRendszer(
                jatek_id = jatek.id,
                jatek_cim = jatek.cim,
                erv = fake.sentence(),
                erv_atlag = round(random.uniform(5.0, 10.0), 2)
            ))

            #Szerepek
            kivalasztott_szerepek = random.sample(SZEREPEK, k = random.randint(3, len(SZEREPEK))) #a SZEREPEK listából kiválaszt 3+random darabot ismétlés nélkül
            for szerep_nev in kivalasztott_szerepek:
                db.add(Szerep(jatek_id = jatek.id, szerepkor = szerep_nev))

            #Díjak
            kivalasztott_dijak = random.sample(DIJAK, k = random.randint(2, 4))
            for dij_nev in kivalasztott_dijak:
                db.add(Dijak(jatek_id = jatek.id, dij = dij_nev))

            #Kérdőívek: 2-2 játék előtt és után
            kerdesek = []
            for _ in range(2):
                pre_k = Kerdoiv(jatek_id = jatek.id, kerdes = fake.sentence(nb_words = 6) + "?", jatek_elott_utan = True)
                post_k = Kerdoiv(jatek_id = jatek.id, kerdes = fake.sentence(nb_words = 6) + "?", jatek_elott_utan = False)
                db.add(pre_k)
                db.add(post_k)
                kerdesek.extend([pre_k, post_k])

        db.commit()
        print(f"-> Játék metaadatok (szerepek, díjak, kérdőívek, érvrendszer) generálva")

        #Játékosok részvétele és események
        for jatek in jatekok:
            #Játékosok véletlenszerű kiválasztása a játékhoz
            resztvevok = random.sample(jatekosok, random.randint(4, 8))

            #Szerepek és díjak lekérése
            jatek_szerepek = [sz.szerepkor for sz in db.query(Szerep).filter_by(jatek_id = jatek.id).all()]
            jatek_dijak = [d.dij for d in db.query(Dijak).filter_by(jatek_id = jatek.id).all()]

            # Kérdések lekérése az adott játékhoz
            jatek_pre_kerdesek = db.query(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=True).all()
            jatek_post_kerdesek = db.query(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=False).all()

            jatekmester_kivalasztva = False #Flag, ami azt, jelzi, hogy van-e játékmester résztvevő, a JatekosJatek ciklus 1. lefutása lesz a játékmester

            for jatekos in resztvevok:
                #JatekosJatek
                db.add(JatekosJatek(
                    jatekos_id = jatekos.id,
                    jatek_id = jatek.id,
                    jatekmester = not jatekmester_kivalasztva
                ))
                jatekmester_kivalasztva = True

                #SoronVan
                db.add(SoronVan(
                    jatek_id = jatek.id,
                    jatekos_id = jatekos.id,
                    kor = 1,
                    time = datetime.now()
                ))

                #Szerepek kiosztása
                kiosztott_szerep = random.choice(jatek_szerepek) if jatek_szerepek else "Ismeretlen"
                db.add(JatekosSzerep(
                    jatek_id = jatek.id,
                    jatekos_id = jatekos.id,
                    kor = 1,
                    szerep = kiosztott_szerep
                ))

                #Érvek létrehozása
                db.add(JatekosErv(
                    jatek_id = jatek.id,
                    jatekos_id = jatekos.id,
                    szerep = kiosztott_szerep,
                    kor = 1,
                    erv = fake.text(max_nb_chars=150),
                    ertekeles_atlag = round(random.uniform(1.0, 10.0), 2),
                    time = datetime.now()
                ))

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

                #Díjak és szavazások
                if jatek_dijak:
                    kivalasztott_dij = random.choice(jatek_dijak)
                    #Szavazat leadása
                    db.add(DijSzavazas(
                        jatek_id = jatek.id,
                        jatek_dij = kivalasztott_dij,
                        jatekos_id = jatekos.id,
                        kapott_szavazatok = random.randint(0, 10)
                    ))
                    #Díj kiosztása véletlenszerűen
                    if random.random() > 0.7:
                        #Ellenőrizzük, hogy az adott játékos kapott-e már ilyen díjat az adott játékban
                        meglevo = db.query(DijatKapott).filter_by(jatek_id = jatek.id, jatekos_id = jatekos.id, dij = kivalasztott_dij).first()
                        if not meglevo:
                            db.add(DijatKapott(
                                jatek_id = jatek.id,
                                jatekos_id = jatekos.id,
                                dij = kivalasztott_dij,
                            ))

        db.commit()
        print(f"Játékos interakciók (kapcsolatok, szerepek, érvek, válaszok, díjak) generálva.")
        print("\nSikeresen befejeződött a tesztadatok generálása!")

    except Exception as e:
        db.rollback()
        print(f"{e}\nHiba az adatok generálása során, minden változtatás elvetésre került.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_all_tables()