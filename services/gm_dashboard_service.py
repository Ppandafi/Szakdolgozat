from sqlalchemy import select, func
from database import(
    SessionLocal, Jatek, Jatekos, JatekosJatek, JatekosSzerep, JelenlegiKor, JatekosErv, ErtekeltekMar, ErveltekMar,
    SoronVan, ErvRendszer
)

#Cache változó, hogy elég legyen csak egyszer lekérni a csatlakozott játékosok számát
jatekosok_szama_cache = {}

#Játék lekérdezése
async def get_game_by_id(jatek_id: int):
    async with SessionLocal() as db:
        result =  await db.execute(select(Jatek).where(Jatek.id == jatek_id))
        return result.scalars().first()

#Jelenlegi és max kör lekérdezése
async def get_rounds(jatek_id: int):
    async with SessionLocal() as db:
        stmt = (
            select(JelenlegiKor.kor, Jatek.max_kor)
            .join(Jatek, JelenlegiKor.jatek_id == jatek_id)
            .where(Jatek.id == jatek_id)
        )
        result = await db.execute(stmt)
        return result.first()


#Játékmester adatainak lekérdezése
async def get_user(email_vagy_nev: str):
    async with SessionLocal() as db:
        stmt = select(Jatekos).where(
            (Jatekos.email == email_vagy_nev) |
            (Jatekos.felhasznalonev == email_vagy_nev)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

#Csatlakozott játékosok és szerepeinek lekérése
async def get_joined_players(jatek_id: int):
    async with SessionLocal() as db:
        #Jelenlegi kör lekérése
        stmt_kor = select(JelenlegiKor.kor).where(JelenlegiKor.jatek_id == jatek_id)
        aktualis_kor = db.scalar(stmt_kor)

        #Soron levő játékos lekérése
        stmt_soron_van = select(SoronVan.jatekos_id).where(
            (SoronVan.jatek_id == jatek_id) &
            (SoronVan.kor == aktualis_kor)
        ).order_by(SoronVan.time.desc())
        soron_levo_id = await db.scalar(stmt_soron_van)

        #Játékosok és szerepeik lekérése
        stmt = (
            select(
                Jatekos.felhasznalonev,
                JatekosSzerep.szerep,
                (Jatekos.id == soron_levo_id).label("soron_van") #Dinamikus logikai oszlop
            )
            .join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id)
            .outerjoin(
                JatekosSzerep,
                (Jatekos.id == JatekosSzerep.jatekos_id) &
                (JatekosSzerep.jatek_id == jatek_id) &
                (JatekosSzerep.kor == aktualis_kor)
            )
            .where(
                (JatekosJatek.jatek_id == jatek_id) &
                (JatekosJatek.jatekmester == False)
            )
        )

        result = await db.execute(stmt)
        resztvevok = result.all()

        #Játékosok száma mentése a cache-be
        jatekosok_szama_cache[jatek_id] = len(resztvevok)

        return resztvevok

#Összes érv lekérése
async def get_all_arguments(jatek_id: int):
    async with SessionLocal() as db:
        stmt =(
            select(JatekosErv, Jatekos)
            .join(Jatekos, JatekosErv.jatekos_id == Jatekos.id)
            .where(JatekosErv.jatek_id == jatek_id)
            .order_by(JatekosErv.kor.desc())
        )
        result = await db.execute(stmt)
        return result.all()

#Érveltek már lekérdezése
async def get_erveltek_mar(jatek_id: int, kor:int):
    async with SessionLocal() as db:
        try:
            stmt = select(ErveltekMar.erveltek).where(
                ErveltekMar.jatek_id == jatek_id,
                ErveltekMar.kor == kor
            )
            result = await db.execute(stmt)
            erveltek_mar = result.scalar_one_or_none()

            return erveltek_mar if erveltek_mar is not None else 0
        except Exception as ex:
            print(f"Hiba a már érvelt játékosok lekérése során: {ex}")
            return 0

#Értékeltek már lekérdezése
async def get_ertekeltek_mar(jatek_id: int, erv_szerzo_id: int, szerep: str):
    async with SessionLocal() as db:
        try:
            stmt = select(func.max(ErtekeltekMar.ertekeltek)).where(
                ErtekeltekMar.jatek_id == jatek_id,
                ErtekeltekMar.erv_szerzo_id == erv_szerzo_id,
                ErtekeltekMar.szerep == szerep
            )
            result = await db.execute(stmt)
            mar_ertekeltek = result.scalar_one_or_none()

            return mar_ertekeltek if mar_ertekeltek is not None else 0
        except Exception as ex:
            print(f"Hiba a már értékeltek számának lekérésekor: {ex}")
            return 0