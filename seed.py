#ADATBÁZIST DUMMY ADATOKKAL FELTÖLTŐ KÓD
from datetime import datetime, timedelta
import random
from faker import Faker
from sqlalchemy import select

#Adatbázis tábláinak és komponenseinek importálása
from database import (
    SessionLocal, Base, engine, Jatekos, JatekosJatek, Jatek, Szerep, Dijak, DijatKapott,
    DijSzavazas, JelenlegiKor, SoronVan, NulladikKor, JatekosSzerep, JatekosErv,
    Kerdoiv, JatekosValaszolPre, JatekosValaszolPost, ErvRendszer, ErveltekMar,
    ErtekeltekMar, ErtekelesIndoklas, init_db
)

#Faker inicializálása magyar nyelven
fake = Faker('hu_HU')

#Szerepek és díjak inicializálása
SZEREPEK = [
    "Gyilkos", "Nyomozó", "Orvos", "Áldozat", "Testőr", "Polgármester",
    "Újságíró", "Bíró", "Ügyvéd", "Tüntető", "Rendőr", "Politikus",
    "Tanár", "Vállalkozó", "Diák", "Nyugdíjas", "Aktivista", "Munkás"
]
DIJAK = ["Legjobb érvelő", "Legviccesebb", "Legcsendesebb", "Legkonstruktívabb", "Legsegítőkészebb"]

#Táblák feltöltése
async def seed_all_tables(jatekosok_szama = 15, jatekok_szama = 5):
    #DB kiürítése és újból létrehozása
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()

    async with SessionLocal() as db:
        try:
            print("Az adatbázis feltöltése megkezdődött...")

            #Játékosok létrehozása
            jatekosok = []
            for _ in range(jatekosok_szama):
                jatekos = Jatekos(
                    felhasznalonev = fake.unique.user_name(),
                    email = fake.unique.email(),
                    jelszo = fake.password(length=10)
                )
                db.add(jatekos)
                jatekosok.append(jatekos)
            #Fix test játékos létrehozása
            test_jatekos = Jatekos(
                felhasznalonev = "test",
                email = "test",
                jelszo = "test"
            )
            db.add(test_jatekos)
            jatekosok.append(test_jatekos)

            await db.commit()
            print(f"-> {jatekosok_szama + 1} játékos létrehozva")

            #Játékok létrehozása
            jatekok = []
            for i in range(jatekok_szama):
                if i == 0:
                    general_kod = "AAAA-1234"
                else:
                    general_kod = fake.unique.bothify('????-####').upper()

                general_max_kor = random.randint(5, 10)

                jatek = Jatek(
                    cim = fake.sentence(nb_words = 3).replace(".", " "),
                    ismertetes = fake.paragraph(nb_sentences = 3),
                    min_kor = 3,
                    max_kor = general_max_kor,
                    lobby_code = general_kod,
                )
                db.add(jatek)
                jatekok.append(jatek)
            await db.commit()
            print(f"-> {jatekok_szama} játék létrehozva")

            #Játékokhoz kapcsolódó metaadatok
            for jatek in jatekok:
                kivalasztott_szerepek =  random.sample(SZEREPEK, k = random.randint(8, 12))
                for szerep_nev in kivalasztott_szerepek:
                    db.add(Szerep(jatek_id=jatek.id, szerepkor=szerep_nev))

                if jatek == jatekok[0]:
                    aktualis_kor = 0
                else:
                    #Biztosítjuk, hogy legfeljebb annyi kör legyen létrehozva, amennyi a max kör
                    felso_korlat = min(len(kivalasztott_szerepek), jatek.max_kor)
                    aktualis_kor =  random.randint(1, felso_korlat)
                db.add(JelenlegiKor(jatek_id=jatek.id, kor=aktualis_kor))

                db.add(NulladikKor(
                    jatek_id = jatek.id,
                    javaslat = fake.word(),
                    szerep_dij = random.choice([True, False])
                ))

                db.add(ErvRendszer(
                    jatek_id = jatek.id,
                    jatek_cim = jatek.cim,
                    erv = fake.sentence(),
                    erv_atlag = round(random.uniform(5.0, 10.0), 2),
                ))

                kivalasztott_dijak = random.sample(DIJAK, k = random.randint(2, 4))
                for dij_nev in kivalasztott_dijak:
                    db.add(Dijak(jatek_id=jatek.id, dij=dij_nev))

                for _ in range(2):
                    pre_k = Kerdoiv(jatek_id=jatek.id, kerdes=fake.sentence(nb_words = 6), jatek_elott_utan=True)
                    post_k = Kerdoiv(jatek_id=jatek.id, kerdes=fake.sentence(nb_words = 6), jatek_elott_utan=False)
                    db.add(pre_k)
                    db.add(post_k)

            await db.commit()
            print(r"-> Játékokhoz tartozó metaadatok (szerepek, díjak, kérdőívek, érvrendszer) generálva")

            #Játékosok részvétele és események szimulációja
            for jatek in jatekok:
                egyeb_jatekosok = [j for j in jatekosok if j.felhasznalonev != "test"]
                resztvevok = random.sample(egyeb_jatekosok, k = random.randint(4, 7))
                resztvevok.append(test_jatekos)

                erveltek_szamlalo = {}

                #szerepek lekérése
                szerep = await db.execute(select(Szerep).filter_by(jatek_id = jatek.id))
                jatek_szerepek = [sz.szerepkor for sz in szerep.scalars().all()]

                #díjak lekérése
                dij = await db.execute(select(Dijak).filter_by(jatek_id = jatek.id))
                jatek_dijak = [d.dij for d in dij.scalars().all()]

                #játék előtti és utáni kérdőívek lekérése
                pre_kerdes = await db.execute(select(Kerdoiv).filter_by(jatek_id = jatek.id, jatek_elott_utan = True))
                jatek_pre_kerdesek = pre_kerdes.scalars().all()
                post_kerdesek = await db.execute(select(Kerdoiv).filter_by(jatek_id = jatek.id, jatek_elott_utan = False))
                jatek_post_kerdesek = post_kerdesek.scalars().all()

                #kör lekérése
                kor = await db.execute(select(JelenlegiKor).filter_by(jatek_id = jatek.id))
                aktualis_kor_obj = kor.scalars().first()
                aktualis_kor_szam = aktualis_kor_obj.kor if aktualis_kor_obj else 1

                jatekmester_kivalasztva = False
                jatekos_kiosztott_szerepek = {j.id: [] for j in resztvevok}
                jatekmester_id = resztvevok[0].id

                #aktív játékos kiválasztása
                valaszthato_aktivak = [j for j in resztvevok if j.id != jatekmester_id and j.felhasznalonev != "test"]
                aktiv_jatekos_id = random.choice(valaszthato_aktivak).id if valaszthato_aktivak else None

                for jatekos in resztvevok:
                    is_jatekmester = not jatekmester_kivalasztva
                    db.add(JatekosJatek(
                        jatekos_id = jatekos.id,
                        jatek_id = jatek.id,
                        jatekmester =  not jatekmester_kivalasztva
                    ))
                    jatekmester_kivalasztva = True

                    if is_jatekmester:
                        continue

                    #Kérdések feltöltése játék előtt és után
                    for kerdes in jatek_pre_kerdesek:
                        db.add(JatekosValaszolPre(
                            jatek_id = jatek.id,
                            jatekos_id = jatekos.id,
                            kerdes_id = kerdes.kerdes_id,
                            valasz = random.randint(1, 10)
                        ))
                    for kerds in jatek_post_kerdesek:
                        db.add(JatekosValaszolPost(
                            jatek_id = jatek.id,
                            jatekos_id = jatekos.id,
                            kerdes_id = kerds.kerdes_id,
                            valasz = random.randint(1, 10)
                        ))

                    for kor in range(1, aktualis_kor_szam + 1):
                        #szerep kiosztása
                        elerheto_szerek = [sz for sz in jatek_szerepek if sz not in jatekos_kiosztott_szerepek[jatekos.id]]
                        kiosztott_szerep = random.choice(elerheto_szerek) if elerheto_szerek else "Ismeretlen"
                        jatekos_kiosztott_szerepek[jatekos.id].append(kiosztott_szerep)

                        #JátékosSzerep rögzítése
                        db.add(JatekosSzerep(
                            jatek_id = jatek.id,
                            jatekos_id = jatekos.id,
                            kor = kor,
                            szerep = kiosztott_szerep
                        ))
                        #Logika a játékos léptetéséhez az aktuális körben
                        if kor == aktualis_kor_szam:
                            if jatekos.felhasznalonev == "test":
                                continue #a "test" játékos semmiképp ne kerüljön sorra
                            #A többieket 50% eséllyel kiszűrjük, de az aktív játékost soha
                            if jatekos.id != aktiv_jatekos_id and random.random() > 0.5:
                                continue

                        #SoronVan időbélyeg manipuláció, hogy biztosan az aktív játékos legyen az utolsó
                        soron_van_ido = datetime.now()
                        if kor == aktualis_kor_szam and jatekos.id == aktiv_jatekos_id:
                            soron_van_ido += timedelta(minutes=10)

                        db.add(SoronVan(
                            jatek_id = jatek.id,
                            jatekos_id = jatekos.id,
                            kor = kor,
                            time = soron_van_ido
                        ))

                        #Ha ő az aktív játékos, kilépünk a ciklusból érv generálása nélkül
                        if kor == aktualis_kor_szam and jatekos.id == aktiv_jatekos_id:
                            continue

                        #Érv generálása
                        if jatekos.felhasznalonev == "test":
                            generalt_erv = f"A 'test' játékos {kor}. körös érve a(z) {kiosztott_szerep} szerepet betöltve"
                        else:
                            generalt_erv = fake.text(max_nb_chars = 400)

                        #Értékelések generálása
                        ertekelok = [j for j in resztvevok if j.id != jatekmester_id and j.id != jatekos.id]
                        osszes_pont = 0
                        ertekeltek_szama = 0

                        for ertekelo in ertekelok:
                            pont = random.randint(1, 10)
                            osszes_pont += pont
                            ertekeltek_szama += 1

                            db.add(ErtekeltekMar(
                                jatek_id = jatek.id,
                                ertekelo_jatekos_id = ertekelo.id,
                                erv_szerzo_id = jatekos.id,
                                szerep = kiosztott_szerep,
                                ertekeltek = ertekeltek_szama,
                            ))

                            #indoklás hozzáadása a szélsőséges értékelésekhez
                            if pont == 1 or pont == 10:
                                db.add(ErtekelesIndoklas(
                                    jatek_id = jatek.id,
                                    ertekelo_jatekos_id = ertekelo.id,
                                    erv_szerzo_id = jatekos.id,
                                    kor = kor,
                                    szerep = kiosztott_szerep,
                                    ertek = pont,
                                    indoklas = fake.sentence(nb_words = 8),
                                    time = datetime.now()
                                ))

                        atlag = 0.0
                        if len(ertekelok) > 0:
                            atlag = round(osszes_pont / len(ertekelok), 2)

                        db.add(JatekosErv(
                            jatek_id = jatek.id,
                            jatekos_id = jatekos.id,
                            szerep = kiosztott_szerep,
                            kor = kor,
                            erv = generalt_erv,
                            ertekeles_atlag = atlag,
                            time = datetime.now()
                        ))

                        erveltek_szamlalo[kor] = erveltek_szamlalo.get(kor, 0) + 1

                    if jatek_dijak:
                        kivalasztott_dij = random.choice(jatek_dijak)
                        db.add(DijSzavazas(
                            jatek_id = jatek.id,
                            jatek_dij = kivalasztott_dij,
                            jatekos_id = jatekos.id,
                            kapott_szavazatok = random.randint(0, 10)
                        ))
                        if random.random() > 0.7:
                            meglevo = await db.execute(
                                select(DijatKapott).filter_by(jatek_id = jatek.id, jatekos_id=jatekos.id, dij=kivalasztott_dij)
                            )
                            meglevo = meglevo.scalars().first()
                            if not meglevo:
                                db.add(DijatKapott(
                                    jatek_id = jatek.id,
                                    jatekos_id = jatekos.id,
                                    dij = kivalasztott_dij
                                ))

                for kor_szam, erv_darab in erveltek_szamlalo.items():
                    db.add(ErveltekMar(
                        jatek_id = jatek.id,
                        kor = kor_szam,
                        erveltek = erv_darab
                    ))

            await db.commit()
            print("-> játékos interakciók (kapcsolatok, szerepek, körönkénti érvek, értékelések, válaszok, díjak) generálva")
            print("\nSikeresen befejeződött a tesztadatok generálása!")
        except Exception as e:
            await db.rollback()
            print(f"Hiba a tesztadatok generálása során, minden változtatás elvetésre került")
            print(f"\n{e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_all_tables())