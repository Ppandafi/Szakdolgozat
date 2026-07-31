#ADATBÁZIST DUMMY ADATOKKAL FELTÖLTŐ FÁJL
from datetime import datetime
import random
from faker import Faker
from sqlalchemy import select

#Adatbázis tábláinak és komponenseinek impotálása
from database import (
SessionLocal, init_db, Base, engine, Jatekos, Jatek, JatekosJatek, Szerep, Dijak, DijatKapott,
DijSzavazas, JelenlegiKor, SoronVan, NulladikKor, JatekosSzerep, JatekosErv,
Kerdoiv, JatekosValaszolPost, JatekosValaszolPre, ErvRendszer
)

#Faker inicializálása magyar nyelven
fake = Faker('hu_HU')

#Szerepek és díjak inicializálása
SZEREPEK = ["Gyilkos", "Nyomozó", "Orvos", "Áldozat", "Testőr", "Polgármester"]
DIJAK = ["Legjobb érvelő", "Legviccesebb", "Legcsendesebb", "Legkonstruktívabb", "Legsegítőkészebb"]

#Táblák feltöltése
async def seed_all_tables(jatekosok_szama = 15, jatekok_szama = 5):
    #Adatbázis kiürítése és újbóli létrehozása
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await init_db()

    async with SessionLocal() as db:
       try:
           print("Az adatbázis feltöltése megkezdődött...")

           # Játékosok létrehozása
           jatekosok = []
           for _ in range(jatekosok_szama):
               jatekos = Jatekos(
                   felhasznalonev=fake.unique.user_name(),
                   email=fake.unique.email(),
                   jelszo=fake.password(length=10)
               )
               db.add(jatekos)
               jatekosok.append(jatekos)
           # fix test játékos létrehozása
           test_jatekos = Jatekos(
               felhasznalonev="test",
               email="test",
               jelszo="test"
           )
           db.add(test_jatekos)
           jatekosok.append(test_jatekos)

           await db.commit()
           print(f"-> {jatekosok_szama + 1} játékos létrehozva")

           # Játékok létrehozása
           jatekok = []
           for i in range(jatekok_szama):
               if i == 0:
                   general_kod = "AAAA-1234"
               else:
                   general_kod = fake.unique.bothify('????-####').upper()
               jatek = Jatek(
                   cim=fake.sentence(nb_words=3).replace(".", " "),
                   ismertetes=fake.paragraph(nb_sentences=4),
                   min_kor=3,
                   max_kor=7,
                   lobby_code=general_kod
               )
               db.add(jatek)
               jatekok.append(jatek)
           await db.commit()
           print(f"-> {jatekok_szama} játék létrehozva")

           # Játékokhoz kapcsolódó metaadatok
           for jatek in jatekok:
               kivalasztott_szerepek = random.sample(SZEREPEK, k=random.randint(3, len(SZEREPEK)))
               for szerep_nev in kivalasztott_szerepek:
                   db.add(Szerep(jatek_id=jatek.id, szerepkor=szerep_nev))

               if jatek == jatekok[0]:
                   aktualis_kor = 0
               else:
                   aktualis_kor = random.randint(1, len(kivalasztott_szerepek))
               db.add(JelenlegiKor(jatek_id=jatek.id, kor=aktualis_kor))

               db.add(NulladikKor(
                   jatek_id=jatek.id,
                   javaslat=fake.word(),
                   szerep_dij=random.choice([True, False])
               ))

               db.add(ErvRendszer(
                   jatek_id=jatek.id,
                   jatek_cim=jatek.cim,
                   erv=fake.sentence(),
                   erv_atlag=round(random.uniform(5.0, 10.0), 2)
               ))

               kivalasztott_dijak = random.sample(DIJAK, k=random.randint(2, 4))
               for dij_nev in kivalasztott_dijak:
                   db.add(Dijak(jatek_id=jatek.id, dij=dij_nev))

               for _ in range(2):
                   pre_k = Kerdoiv(jatek_id=jatek.id, kerdes=fake.sentence(nb_words=6))
                   post_k = Kerdoiv(jatek_id=jatek.id, kerdes=fake.sentence(nb_words=6))
                   db.add(pre_k)
                   db.add(post_k)

           await db.commit()
           print("-> Játék metaadatok (szerepek, díjak, kérdőívek, érvrendszer) generálva")

           # Játékosok részvétele és események szimulációja
           for jatek in jatekok:
               egyeb_jatekosok = [j for j in jatekosok if j.felhasznalonev != "test"]
               resztvevok = random.sample(egyeb_jatekosok, random.randint(4, 7))
               resztvevok.append(test_jatekos)

               # szerepek lekérése
               szerep = await db.execute(select(Szerep).filter_by(jatek_id=jatek.id))
               jatek_szerepek = [sz.szerepkor for sz in szerep.scalars().all()]

               # díjak lekérése
               dij = await db.execute(select(Dijak).filter_by(jatek_id=jatek.id))
               jatek_dijak = [d.dij for d in dij.scalars().all()]

               # játék előtti- és utáni kérdőívek lekérése
               pre_kerdes = await db.execute(select(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=True))
               jatek_pre_kerdesek = pre_kerdes.scalars().all()
               post_kerdes = await db.execute(select(Kerdoiv).filter_by(jatek_id=jatek.id, jatek_elott_utan=False))
               jatek_post_kerdesek = post_kerdes.scalars().all()

               # kör lekérése
               kor = await db.execute(select(JelenlegiKor).filter_by(jatek_id=jatek.id))
               aktualis_kor_obj = kor.scalars().first()
               aktualis_kor_szam = aktualis_kor_obj.kor if aktualis_kor_obj else 1

               jatekmester_kivalasztva = False
               jatekos_kiosztott_szerepek = {j.id: [] for j in resztvevok}

               for jatekos in resztvevok:
                   db.add(JatekosJatek(
                       jatekos_id=jatekos.id,
                       jatek_id=jatek.id,
                       jatekmester=not jatekmester_kivalasztva
                   ))
                   jatekmester_kivalasztva = True

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

                   for kor in range(1, aktualis_kor_szam + 1):
                       #Logika a játékos léptetésének teszteléséhez
                       if kor == aktualis_kor_szam:
                            if jatekos.felhasznalonev == "test":
                               continue #A "test" játékos semmiképp ne legyen soron a legfrissebb körben
                            if random.random() > 0.5:
                                continue #Minden más játékos 50% esélyjel kerül sorra

                       db.add(SoronVan(
                           jatek_id=jatek.id,
                           jatekos_id=jatekos.id,
                           kor=kor,
                           time=datetime.now()
                       ))

                       elerheto_szerepek = [sz for sz in jatek_szerepek if
                                            sz not in jatekos_kiosztott_szerepek[jatekos.id]]
                       kiosztott_szerep = random.choice(elerheto_szerepek) if elerheto_szerepek else "Ismeretlen"
                       jatekos_kiosztott_szerepek[jatekos.id].append(kiosztott_szerep)

                       db.add(JatekosSzerep(
                           jatek_id=jatek.id,
                           jatekos_id=jatekos.id,
                           kor=kor,
                           szerep=kiosztott_szerep
                       ))

                       if jatekos.felhasznalonev == "test":
                           if kor == aktualis_kor_szam:
                               continue
                           else:
                               generalt_erv = f"A 'test' nevű játékos {kor}. körös próbaérve a(z) {kiosztott_szerep} szerepkört képviselve."
                       else:
                           generalt_erv = fake.text(max_nb_chars=400)

                       db.add(JatekosErv(
                           jatek_id=jatek.id,
                           jatekos_id=jatekos.id,
                           szerep=kiosztott_szerep,
                           kor=kor,
                           erv=generalt_erv,
                           ertekeles_atlag=round(random.uniform(1.0, 10.0), 2),
                           time=datetime.now()
                       ))

                   if jatek_dijak:
                       kivalasztott_dij = random.choice(jatek_dijak)
                       db.add(DijSzavazas(
                           jatek_id=jatek.id,
                           jatek_dij=kivalasztott_dij,
                           jatekos_id=jatekos.id,
                           kapott_szavazatok=random.randint(0, 10)
                       ))
                       if random.random() > 0.7:
                           meglevo = await db.execute(
                               select(DijatKapott).filter_by(jatek_id=jatek.id, jatekos_id=jatekos.id,
                                                             dij=kivalasztott_dij)
                           )
                           meglevo = meglevo.scalars().first()
                           if not meglevo:
                               db.add(DijatKapott(
                                   jatek_id=jatek.id,
                                   jatekos_id=jatekos.id,
                                   dij=kivalasztott_dij,
                               ))

           await db.commit()
           print("-> Játékos interakciók (kapcsolatok, szerepek, körönkénti érvek, válaszok, díjak) generálva")
           print("\nSikeresen befejeződött a tesztadatok generálása!")
       except Exception as e:
           await db.rollback()
           print(f"Hiba a tesztadatok generálása során, minden változtatás elvetésre került")
           print(f"\n{e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_all_tables())