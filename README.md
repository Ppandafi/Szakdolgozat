## Megjegyzés
A *2026.07.29.* előtti commitok a projekt egy korábbi verziójának refaktorálása  
A refaktorálás fő okai:  
- Az eredeti kód átláthatatlanná vált
- Áttérés aszinkron fejlesztésre -> egyszerűbb volt a kódot nulláról újra írni, mint a szinkron logikát aszinkron logikára konvertálni  

## A projekt célja
- A szoftver egy online platform, ami keretet és szabályrendszert biztosít egy irányított, körökre osztott vitajáték lefolytatására.  
- A játék fő céljai a résztvevők véleményének árnyalása és empátiájának javítása azáltal, hogy a vita témáját a játék minden körében egy eltérő társadalmi csoport szemszögéből kell megvizsgálniuk.  
- A rendszer a játékosok véleményét (és annak változását) 1-től 10-ig terjedő pontozás segítségével számszerűsítve rögzíti.  
- Az egyes körök folyamán a játékosoknak lehetőségük van társaik érveit pontozni az alapján, hogy mennyire értenek egyet az érvelővel,
 a szélsőséges pontozást (1 vagy 10) pedig meg is kell indokolniuk.  

## Architektúra
**Felépítés:**  
- <img src="https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54" height="20"> <img src="https://img.shields.io/badge/Flet-101010?style=flat&logo=flutter&logoColor=45D1FD" height="20"> Python Flet keretrendszer: Sajátossága, hogy nincs elkülönített front- és backend, hanem a logika és a UI egy helyen futnak, a kliensek WebSockets segítségével kommunikálnak a szerverrel
**Adatbázis:**  
- <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat" height="20"> Adatbázis kezelés (ORM)
- <img src="https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white" height="20">Fejlesztési / tesztelési szakasz
- <img src="https://img.shields.io/badge/postgresql-4169E1?style=flat&logo=postgresql&logoColor=white" height="20">Éles, webes környezet  

**Navigáció:**  
A projekt belépési és irányítási pontja a `main.py`, ez felel az útválasztásért. A program egyes felületei külön `.py` fájlokban kerültek megvalósítása

## Függőségek
- [flet](https://flet.dev/)
- [sqlalchemy](https://flet.dev/)
- [faker](https://pypi.org/project/Faker/)
- [aiosqlite](https://pypi.org/project/aiosqlite/)  

## Futtatás és tesztelés
**1. Függőségek telepítése:** `pip install` parancs segítségével, pl: `pip install flet[all]`  
**2. Tesztadatok generálása:**  `seed.py`script futtatása `python seed.py` paranccsal. Ez a script feltölti az adatbázist 16 játékossal, 1 0. körben tartó, 4 folyaamatban levő és 1 lezárt játékkal  
**3. Alkalmazás indítása:** A program a `main.py` fájl indításával futtatható, amely alapértelmezetten a böngészőben indítja el a programot

## Mérföldkő commit
[Mérföldkő commit](https://github.com/Ppandafi/Szakdolgozat/commit/d32ae4e1f16e6deb42e9a01c46cae0d749754904), innentől
 a core funkciókat késznek tekintjük és a fő fókusz átkerül egy esztétikusabb UI elkészítésére, hibajavításokra, esetleges
bővítési lehetőségek megvalósítására és a projekt webes élesítésére

## Dashboard jelmagyarázat
A fő képernyőn a saját játékoknál a játék státuszait különböző ikonok jelölik. Ezek az ikonok:  
- <img src="assets/icons/manage_accounts.svg" width="20" height="20"> A játékos az adott játék játékmestere
- <img src="assets/icons/trophy.svg" width="20" height="20"> A játékot lezárták és az eredményeket összegezték, megtekinthető az érvrendszer
- <img src="assets/icons/done_all.svg" width="20" height="20"> A játékot lezárták, de az eredményeket még nem összegezték, kitölthető a játék utáni kérdőív