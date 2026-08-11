from sqlalchemy import select
from database import SessionLocal, Dijak, Jatekos, JatekosJatek, DijSzavazas

async def get_awards_and_players(jatek_id: int):
    #Lekéri a játékhoz tartozó díjakat és játékosokat (játékmester kivételével)
    async with SessionLocal() as db:
        try:
            #díjak lekérése
            stmt_awards = select(Dijak.dij).where(Dijak.jatek_id == jatek_id)
            awards = (await db.execute(stmt_awards)).scalars().all()

            #játékosok lekérése
            stmt_players = select(Jatekos).join(JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekmester == False
            )
            players = (await db.execute(stmt_players)).scalars().all()

            return awards, players
        except Exception as e:
            print(f"Hiba a díjak és játékosok lekérése során: {e}")
            return [], []

async def save_votes(jatek_id: int, votes_dict:dict):
    #elmenti a szavazatokat az adatbázisba
    async with SessionLocal() as db:
        try:
            for dij_nev, jatekos_id in votes_dict.items():
                if jatekos_id is None:
                    continue #ha a játékos nem szavazott valamilyen díjra

                #megnézzük, kapott-e már szavazatot a játékos erre a díjra
                stmt_szavazas = select(DijSzavazas).where(
                    DijSzavazas.jatek_id == jate_id,
                    DijSzavazas.jatek_dij == dij_nev,
                    DijSzavazas.jatekos_id == jatekos_id
                )
                szavazas = (await db.execute(stmt_szavazas)).scalars().first()

                if szavazas:
                    szavazas.kapott_szavazatok += 1
                else:
                    uj_szavazas = DijSzavazas(
                        jatek_id=jatek_id,
                        jatek_dij=dij_nev,
                        jatekos_id=jatekos_id,
                        kapott_szavazatok=1
                    )
                    db.add(uj_szavazas)

            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            print(f"Hiba a szavazás mentése során: {e}")
            return False