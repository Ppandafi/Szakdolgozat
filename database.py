import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import (
Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base

#ENVIRONMENT meghatározása, ha nincs külön beállítva, alapértelmezetten "development"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

#Adatbázsis beállítása az ENVIRONMENT-től függően
#"production" -> posgreSQL // "development" -> local SQLite
if ENVIRONMENT == "production":
    DATABASE_URL = ""
    #Kapcsolódás az adatbázishoz
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    DATABASE_URL = "sqlite+aiosqlite:///dev.database.db"
    #Kapcsolódás az adatbázishoz
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

#Session létrehozása kommunikációhoz
SessionLocal = async_sessionmaker(
    bind = engine,
    class_= AsyncSession,
    autocommit = False,
    autoflush = False,
    expire_on_commit = False,
)
Base = declarative_base()


#MODELLEK DEFINIÁLÁSA
#Játékos
class Jatekos(Base):
    __tablename__ = "jatekos"
    id = Column(Integer, primary_key = True, index = True)
    felhasznalonev = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    jelszo = Column(String, nullable = False)
    active = Column(Boolean, default = True)

#Játék
class Jatek(Base):
    __tablename__ = "jatek"
    id = Column(Integer, primary_key = True, index = True)
    cim = Column(String, nullable = False)
    ismertetes = Column(Text)
    min_kor = Column(Integer)
    max_kor = Column(Integer)
    lobby_code = Column(String, unique = True)
    kerdoivek_kikuldve = Column(Boolean, default = False) #Játék szerkesztése gombjainak letiltásához kell
    jatek_lezarva = Column(Boolean, default = False)
    eredmenyek_osszesitve = Column(Boolean, default = False)

#Játékos_Játék -> az adott játékban ki vesz részt
class JatekosJatek(Base):
    __tablename__ = "jatekos_jatek"
    jatekos_id = Column(Integer,ForeignKey('jatekos.id'), primary_key = True)
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekmester = Column(Boolean, default = False)

#Szerep -> az adott játékban milyen szerepkörök lettek létrehozva
class Szerep(Base):
    __tablename__ = "szerep"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    szerepkor = Column(String, primary_key = True)

#Díjak -> az adott játékban milyen díjak lettek létrehozva
class Dijak(Base):
    __tablename__ = "dijak"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    dij = Column(String, primary_key = True)

#Díjat kapott
class DijatKapott(Base):
    __tablename__ = "dijat_kapott"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    dij = Column(String, primary_key = True)

#Díj szavazás
class DijSzavazas(Base):
    __tablename__ = "dij_szavazas"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatek_dij = Column(String, primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    kapott_szavazatok = Column(Integer, default = 0)

#Jelenlegi kör -> melyik játék hányadik körnél tart
class JelenlegiKor(Base):
    __tablename__ = "jelenlegi_kor"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    kor = Column(Integer)

#Soron van -> az adott játék adott körében melyik játékos van soron érvelésre
class SoronVan(Base):
    __tablename__ = "soron_van"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    kor = Column(Integer, primary_key = True)
    soron_van = Column(Boolean, default = False)
    time = Column(DateTime) #ahhoz kell, hogy tudjuk melyik a legfrissebb rekord

#Nulladik kör -> játék indítása előtti javaslatok új szerepekhez/díjakhoz
class NulladikKor(Base):
    __tablename__ = "nulladik_kor"
    javaslat_id = Column(Integer, primary_key = True, autoincrement = True)
    jatek_id = Column(Integer, ForeignKey('jatek.id'))
    javaslat = Column(Text)
    szerep_dij = Column(Boolean) #1-szerep / 0-díj

#Játékos szerep -> az adott játék adott körében ki milyen szerepet tölt be
class JatekosSzerep(Base):
    __tablename__ = "jatekos_szerep"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    kor = Column(Integer, primary_key = True)
    szerep = Column(String)

#Játékos érv
class JatekosErv(Base):
    __tablename__ = "jatekos_erv"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    szerep = Column(String, primary_key = True)
    kor = Column(Integer)
    erv = Column(Text)
    ertekeles_atlag = Column(Float) #Ide kerül be a többi játékos által adott pont (átlag=pontok/játékosok száma-1)
    time = Column(DateTime) #ahhoz kell, hogy tudjuk melyik a legfrissebb rekord

#Szélsőséges értékelés indoklása
class ErtekelesIndoklas(Base):
    __tablename__ = "ertekeles_indoklas"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    ertekelo_jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True) #Aki szélsőségesen értékelte az érvelést
    erv_szerzo_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True) #Aki az érvet írta
    kor = Column(Integer, primary_key = True) #Melyik körben írt érvet értékelték szélsőségesen
    szerep = Column(String)
    ertek = Column(Integer)
    indoklas = Column(Text, nullable = False)
    time = Column(DateTime)

#Érveltek - azt követi, hogy az adott játék adott körében hányan érveltek
class ErveltekMar(Base):
    __tablename__ = "erveltek_mar"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    kor = Column(Integer, primary_key = True)
    erveltek = Column(Integer, default = 0)

#Értékeltek - azt követi, hogy az adott érvet hányan értékelték
class ErtekeltekMar(Base):
    __tablename__ = "ertekeltek_mar"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    ertekelo_jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    erv_szerzo_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    szerep = Column(String, primary_key = True)
    ertekeltek = Column(Integer, default = 0)

#Szavaztak - azt követi, hogy a játék végén hányan adtak le szavazatot a díj szavazáson
class SzavaztakMar(Base):
    __tablename__ = "szavaztak_mar"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)

#Kérdőívek
class Kerdoiv(Base):
    __tablename__ = "kerdoiv"
    jatek_id = Column(Integer, ForeignKey('jatek.id'))
    kerdes_id = Column(Integer, primary_key = True, autoincrement = True)
    kerdes = Column(Text, nullable = False)
    jatek_elott_utan = Column(Boolean) #True=előtt / False=után

#Játékos válaszol játék előtt
class JatekosValaszolPre(Base):
    __tablename__ = "jatekos_valaszol_pre"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    kerdes_id = Column(Integer, ForeignKey('kerdoiv.kerdes_id'), primary_key = True)
    valasz = Column(Integer)

#Játékos válaszol játék után
class JatekosValaszolPost(Base):
    __tablename__ = "jatekos_valaszol_post"
    jatek_id = Column(Integer, ForeignKey('jatek.id'), primary_key = True)
    jatekos_id = Column(Integer, ForeignKey('jatekos.id'), primary_key = True)
    kerdes_id = Column(Integer, ForeignKey('kerdoiv.kerdes_id'), primary_key = True)
    valasz = Column(Integer)

#Érvrendszer -> kigyűjtünk minden olyan érvet, ami a játék folyamán 5.0-nál jobb átlag értékelést kapott
class ErvRendszer(Base):
    __tablename__ = "ervrendszer"
    id = Column(Integer, primary_key = True, autoincrement = True)
    jatek_id = Column(Integer, ForeignKey('jatek.id'))
    jatek_cim = Column(String)
    erv = Column(Text)
    erv_atlag = Column(Float)

#Táblák létrehozása az adatbázisban
async def init_db():
    #Aszinkron kapcsolat megnyitása a metadata.create_all futtatásához
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)