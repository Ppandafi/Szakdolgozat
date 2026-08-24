from fpdf import FPDF
import os
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
                        #Játékos nevének elrejtése, ha törölte a profilját
                        megjelenitendo_nev = p.felhasznalonev if p.active else "Törölt felhasználó"

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
                            "jatekos": megjelenitendo_nev,
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
            stmt_awards = select(DijatKapott.dij, Jatekos.felhasznalonev, Jatekos.active).join(
                Jatekos, DijatKapott.jatekos_id == Jatekos.id
            ).where(DijatKapott.jatek_id == jatek_id)
            awards_raw = (await db.execute(stmt_awards)).all()

            awards = [{"dij": a[0], "nyertes": a[1] if a[2] else "Törölt felhasználó"} for a in awards_raw]

            #Érvrendszer lekérése
            stmt_erv = select(ErvRendszer).where(ErvRendszer.jatek_id == jatek_id)
            ervrendszer = (await db.execute(stmt_erv)).scalars().all()

            return user, question_data, awards, ervrendszer, is_gm
        except Exception as e:
            print(f"Hiba az összesítési adatok lekérése során: {e}")
            return None, [],[],[], False

def generate_ervrendszer_pdf(jatek_cim: str, ervrednszer_lista: list) -> str:
    #Egyedi pdf osztály definiálása, hogy testre lehessen szabni a fejlécet
    class PDF(FPDF):
        def header(self):
            self.set_font('Unicodefont', 'B', 16)
            self.set_text_color(26, 35, 126)
            self.cell(0, 10, 'Érvrendszer export', border = False, ln = True, align = 'C')

            self.set_font('Unicodefont', '', 12)
            self.set_text_color(51, 51, 51)
            self.cell(0, 10, f'{jatek_cim}', border = False, ln = True, align = 'C')

            self.line(10, 30, 200, 30)
            self.ln(10)

    pdf = PDF()

    font_path = os.path.join("assets", "Roboto-Regular.ttf")
    font_bold_path = os.path.join("assets", "Roboto-Bold.ttf")

    if os.path.exists(font_path):
        pdf.add_font('UnicodeFont', '', font_path)
        if os.path.exists(font_bold_path):
            pdf.add_font('UnicodeFont', 'B', font_bold_path)
        else:
            pdf.add_font('UnicodeFont', 'B', font_path)
    else:
        pdf.add_font('Unicodefont', '', 'helvetica')
        pdf.add_font('Unicodefont', 'B', 'helvetica')

    pdf.add_page()

    for erv in ervrednszer_lista:
        pdf.set_font('Unicodefont', '', 11)
        pdf.set_text_color(51, 51, 51)
        pdf.multi_cell(0, 8, txt = erv.erv)

        pdf.set_font('Unicodefont', 'B', 10)
        pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 8, txt=f"Értékelés átlaga: {erv.erv_atlag}", ln = True, align = 'R')
        pdf.ln(5)

    biztonsagos_cim = jatek_cim.replace(" ", "-")
    kimeneti_utvonal = f"assets/ervrendszer_export_{biztonsagos_cim}.pdf"
    os.makedirs("assets", exist_ok = True)
    pdf.output(kimeneti_utvonal)

    return kimeneti_utvonal