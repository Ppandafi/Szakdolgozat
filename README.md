## Megjegyzés
A 2026.07.29. előtti commitok a projekt egy korábbi verziójának refaktorálása  
A refaktorálás fő okai:  
- Az eredeti kód átláthatatlanná vált
- Áttérés aszinkron fejlesztésre -> egyszerűbb volt a kódot nulláról újra írni, mint a szinkron logikát aszinkron logikára konvertálni  

## Függőségek
- [flet](https://flet.dev/)
- [sqlalchemy](https://flet.dev/)
- [faker](https://pypi.org/project/Faker/)
- [aiosqlite](https://pypi.org/project/aiosqlite/)  

**Függőségek telepítése:** `pip install` *csomag neve*  
Pl.: `pip install flet[all]`

## Mérföldkő commit
[Mérföldkő commit](https://github.com/Ppandafi/Szakdolgozat/commit/d32ae4e1f16e6deb42e9a01c46cae0d749754904), innentől
 a core funkciókat késznek tekintjük és a fő fókusz átkerül egy esztétikusabb UI elkészítésére, hibajavításokra, esetleges
bővítési lehetőségek megvalósítására és a projekt webes élesítésére

## Dashboard jelmagyarázat
A fő képernyőn a saját játékoknál a játék státuszait különböző ikonok jelölik. Ezek az ikonok:  
- A játékos az adott játék játékmestere
- A játékot lezárták és az eredményeket összegezték, megtekinthető az érvrendszer
- A játékot lezárták, de az eredményeket még nem összegezték, kitölthető a játék utáni kérdőív