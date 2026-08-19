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

## A játék fő szakaszai
Az inrányított vitajáték 3 fő szakaszból áll, ezekből ténylegges érvelés/vita csak a fő szakaszban zajlik, a többi szakasz a játékosok véleményének rögzítéséről szól:

- **0. Kör:**
  - A játékmester (az adott játék létrehozója) ebben a körben veszi fel a játék adatait
  - A játékhoz csak ebben a fázisban tud új játékos csatlakozni
  - Miután a játékmester felvett minden adatot, a játékosok kitöltik a játék előtti kérdőívet, és lehetőségük van javaslatot tenni új szerepek / díjak bevezetésére
  

- **Számozott körök: (Fő szakasz)**
  - Az egyes körök elején minden játékos véletlenszerűen kap egy olyan szerepet, amilyet még nem töltött be az előző körök folyamán
  - A játékosok egymás után kerülnek sorra érveik kifejtésére, amiket az éppen nem érvelő játékosok értékelnek, hogy mennyire értenek egyet az érvelővel
  - Egy körnek akkor van vége, amikor mindenki érvelt és minden érvet értékelt mindenki, vagy a játékmester manuálisan lezárta a kört
  - A fő szakasznak akkor van vége,  
    -amikor a játékmester lezárja a játékot,  
    -amikor a játszott körök száma eléri a játék létrehozásakor megadott *Max. kör* értéket


- **Játék lezárása utáni szakasz:**
  - A játék lezárása után a játékosok kitöltik a játék utáni kérdőívet. Ez a kérdőív tartalmazza a játék előtti kérdőív kérdéseit és opcionálisan bónusz kérdéseket is
  - A kérdőívek kitöltése után a játékosoknak lehetőségük van szavazni, hogy melyik, a játékhoz tartozó díjat melyik játékos érdemli szerintük a legjobban
  - Miután minden játékos leadta szavazatát (vagy a játékmester manuálisan elindította), a rendszer összesíti a szavazatokat és kiállítja a játék érvrendszerét  

### Az érvrendszer
A játékosok akkor tekinthetik meg egy játék érvrendszerét, amikor egy összesített játékba akarnak belépni. Az érvrendszer a következőket tartalmazza:

- A játékos véleményének alakulása = a játék előtti- és utáni kérdőívekre adott válaszai
- A játékban kiosztott díjak és a díjazottak listája
- A játékosok által pozitívnak értékelt érvek: Azok az érvek, amik 5-nél jobb értékelést kaptak átlagosan

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
**1. Függőségek telepítése:**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`pip install` parancs segítségével, pl: `pip install flet[all]`  
**2. Tesztadatok generálása:**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`seed.py`script futtatása `python seed.py` paranccsal. Ez a script feltölti az adatbázist 16 db játékossal, 1 db 0. körben tartó, 4 db folyaamatban levő és 1 db lezárt játékkal
és miden hozzájuk tartozó adattal (játékosok részvétele, szerepek, díjak, kérdőívek, érvelések, értékelések/indoklások, stb.)  
**3. Alkalmazás indítása:**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A program a `main.py` fájl indításával futtatható, amely alapértelmezetten a böngészőben indítja el a programot

## Mérföldkő commitok
- [Core funkciók kész (#d32ae4e)](https://github.com/Ppandafi/Szakdolgozat/commit/d32ae4e1f16e6deb42e9a01c46cae0d749754904), innentől
 a core funkciókat késznek tekintjük és a fő fókusz átkerül egy esztétikusabb UI elkészítésére, hibajavításokra, esetleges
bővítési lehetőségek megvalósítására és a projekt webes élesítésére
- [Új UI design kész (#3725810)](https://github.com/Ppandafi/Szakdolgozat/commit/37258105be90248eee6f62f8fdba3a3536ac0fda), elkészült
 a projekt frissített, átláthatóbb UI designja 

## Dashboard jelmagyarázat
A fő képernyőn a saját játékoknál a játék státuszait különböző ikonok jelölik. Ezek az ikonok:  
- <img src="assets/icons/manage_accounts.svg" width="20" height="20"> A játékos az adott játék játékmestere
- <img src="assets/icons/trophy.svg" width="20" height="20"> A játékot lezárták és az eredményeket összegezték, megtekinthető az érvrendszer
- <img src="assets/icons/done_all.svg" width="20" height="20"> A játékot lezárták, de az eredményeket még nem összegezték, kitölthető a játék utáni kérdőív  
