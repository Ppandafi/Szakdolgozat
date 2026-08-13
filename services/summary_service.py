from sqlalchemy import select
from database import(
SessionLocal, Jatekos, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost,
DijatKapott, ErvRendszer, JatekosJatek
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
                return None,[],[],[], False

            #Játékmester jogosultság ellenőrzése
            stmt_gm = select(JatekosJatek.jatekmester).where(
                JatekosJatek.jatek_id == jatek_id,
                JatekosJatek.jatekos_id == user.id
            )
            is_gm = await db.scalar(stmt_gm)

            #Kérdések és válaszok lekérése
            stmt_questions = select(Kerdoiv).where(Kerdoiv.jatek_id == jatek_id)
            questions = (await db.execute(stmt_questions)).scalars().all()

            question_data = []

            #ha játékmester, lekérjük az összes játékos válaszait
            if is_gm:
                stmt_players = select(Jatekos).join(
                    JatekosJatek, Jatekos.id == JatekosJatek.jatekos_id
                ).where(
                    JatekosJatek.jatek_id == jatek_id,
                    JatekosJatek.jatekmester == False
                )
                players = (await db.execute(stmt_players)).scalars().all()

                for q in questions:
                    q_dict = {"kerdes": q.kerdes, "valaszok": []}
                    for p in players:
                        stmt_pre = select(JatekosValaszolPre.valasz).where(
                            JatekosValaszolPre.jatek_id == jatek_id,
                            JatekosValaszolPre.jatekos_id == p.id,
                            JatekosValaszolPre.kerdes_id == q.kerdes_id
                        )
                        pre_val = await db.scalar(stmt_pre)

                        stmt_post = select(JatekosValaszolPost.valasz).where(
                            JatekosValaszolPost.jatek_id == jatek_id,
                            JatekosValaszolPost.jatekos_id == p.id,
                            JatekosValaszolPost.kerdes_id == q.kerdes_id
                        )
                        post_val = await db.scalar(stmt_post)

                        q_dict["valaszok"].append({
                            "jatekos": p.felhasznalonev,
                            "pre": pre_val if pre_val is not None else "-",
                            "post": post_val if post_val is not None else "-",
                        })
                    question_data.append(q_dict)
            else:
                #Normál játékosnál csak a saját válaszait kérjük le
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
                        "valaszok": [{
                            "jatekos": user.felhasznalonev,
                            "pre": pre_val if pre_val is not None else "-",
                            "post": post_val if post_val is not None else "-",
                        }]
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

            return user, question_data, awards, ervrendszer, is_gm
        except Exception as e:
            print(f"Hiba az összesítési adatok lekérése során: {e}")
            return None, [],[],[], False