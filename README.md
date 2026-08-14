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
- <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#1f1f1f"><path d="M287-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM80-160v-112q0-33 17-62t47-44q51-26 115-44t141-18h14q6 0 12 2-8 18-13.5 37.5T404-360h-4q-71 0-127.5 18T180-306q-9 5-14.5 14t-5.5 20v32h252q6 21 16 41.5t22 38.5H80Zm560 40-12-60q-12-5-22.5-10.5T584-204l-58 18-40-68 46-40q-2-14-2-26t2-26l-46-40 40-68 58 18q11-8 21.5-13.5T628-460l12-60h80l12 60q12 5 22.5 11t21.5 15l58-20 40 70-46 40q2 12 2 25t-2 25l46 40-40 68-58-18q-11 8-21.5 13.5T732-180l-12 60h-80Zm96.5-143.5Q760-287 760-320t-23.5-56.5Q713-400 680-400t-56.5 23.5Q600-353 600-320t23.5 56.5Q647-240 680-240t56.5-23.5Zm-280-320Q480-607 480-640t-23.5-56.5Q433-720 400-720t-56.5 23.5Q320-673 320-640t23.5 56.5Q367-560 400-560t56.5-23.5ZM400-640Zm12 400Z"/></svg>
A játékos az adott játék játékmestere
- <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#1f1f1f"><path d="M280-120v-80h160v-124q-49-11-87.5-41.5T296-442q-75-9-125.5-65.5T120-640v-40q0-33 23.5-56.5T200-760h80v-80h400v80h80q33 0 56.5 23.5T840-680v40q0 76-50.5 132.5T664-442q-18 46-56.5 76.5T520-324v124h160v80H280Zm0-408v-152h-80v40q0 38 22 68.5t58 43.5Zm285 93q35-35 35-85v-240H360v240q0 50 35 85t85 35q50 0 85-35Zm115-93q36-13 58-43.5t22-68.5v-40h-80v152Zm-200-52Z"/></svg>
A játékot lezárták és az eredményeket összegezték, megtekinthető az érvrendszer
- <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#1f1f1f"><path d="M268-240 42-466l57-56 170 170 56 56-57 56Zm226 0L268-466l56-57 170 170 368-368 56 57-424 424Zm0-226-57-56 198-198 57 56-198 198Z"/></svg>
A játékot lezárták, de az eredményeket még nem összegezték, kitölthető a játék utáni kérdőív