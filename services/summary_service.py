from sqlalchemy import select
from database import(
SessionLocal, Jatekos, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost,
DijatKapott, ErvRendszer
)

async def get_player_summary_data(jatek_id: int, current_user: str):
    async with SessionLocal() as db:
        try:
            #Játékos azonosítása
            stmt_user = select(Jatekos).where(
                (Jatekos.email == current_user) |
                (Jatekos.felhasznalonev == current_user)
            )
            user = (await db.execute(stmt_user)).scalars().first()
            if not user:
                return None,[],[],[]

            #Kérdések és válaszok lekérése
            stmt_questions = select(Kerdoiv).where(Kerdoiv.jatek_id == jatek_id)
            questions = (await db.execute(stmt_questions)).scalars().all()

            question_data = []
            for q in questions:
                stmt_pre = select(JatekosValaszolPre.valasz).where(
                    JatekosValaszolPre.jatek_id == jatek_id,
                    JatekosValaszolPre.jatekos_id == user.id,
                    JatekosValaszolPre.kerdes_id == q.kerdes_id
                )
                pre_val = await db.scalar(stmt_pre)

                stmt_post = select(JatekosValaszolPost.valasz).where(
                    JatekosValaszolPost.jatek_id == jatek_id,
                    JatekosValaszolPost.jatekos_id == user.id,
                    JatekosValaszolPost.kerdes_id == q.kerdes_id
                )
                post_val = await db.scalar(stmt_post)

                question_data.append({
                    "kerdes": q.kerdes,
                    "pre": pre_val if pre_val is not None else "-",
                    "post": post_val if post_val is not None else "-",
                })

            #Díjak és nyerteseik lekérése
            stmt_awards = select(DijatKapott.dij, Jatekos.felhasznalonev).join(
                Jatekos, DijatKapott.jatekos_id == Jatekos.id
            ).where(DijatKapott.jatek_id == jatek_id)
            awards_raw = (await db.execute(stmt_awards)).all()

            awards = [{"dij": a[0], "nyertes": a[1]} for a in awards_raw]

            #Érvrendszer lekérése
            stmt_erv = select(ErvRendszer).where(ErvRendszer.jatek_id == jatek_id)
            ervrendszer = (await db.execute(stmt_erv)).scalars().all()

            return user, question_data, awards, ervrendszer
        except Exception as e:
            print(f"Hiba az összesítési adatok lekérése során: {e}")
            return None, [],[],[]