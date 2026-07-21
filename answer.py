import flet as ft
from database import SessionLocal, Jatek, Kerdoiv, JatekosValaszolPre, JatekosValaszolPost, JatekosJatek

pre_post_flag = "both" #ez a flag adja meg, hogy éppen játék előtti vagy utáni kérdőív kerül kitöltésre (both = előtt / post = után)

def show_answer_page(page:ft.Page, jatek_id):
    page.add(ft.Text("Ez lesz a kérdőív kitöltő mező"))
    page.update()