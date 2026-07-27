import flet as ft

from services import auth_service

from login import create_login_view
from register import create_register_view

async def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"

    #A jelenleg bejelentkezett felhasználó állapotának tárolása
    #page.client_storage.set("current_user", None)

    #Nézetek váltása (routing)
    async def route_change(route):
        page.views.clear()

        #login
        if page.route == "/login" or page.route == "/":
            page.views.append(
                create_login_view(
                    page,
                    on_login_attempt = handle_login_attempt,
                    on_register_click = lambda: page.push_route("/register")
                )
            )
        #regisztráció
        elif page.route == "/register":
            page.views.append(
                create_register_view(
                    page,
                    on_register_attempt = handle_register_attempt,
                    on_cancel_click = lambda: page.push_route("/login")
                )
            )
        #dashboard
        elif page.route == "/dashboard":
            page.views.append(
                ft.View(
                    route="/dashboard",
                    controls = [ft.Text("Dashboard")]
                )
            )

        page.update()

    #Böngésző vissza gomb kezelése
    async def view_pop(view):
        page.views.clear()
        top_view = page.views[-1]
        page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    #Adatbázis logika
    async def handle_login_attempt(email, password):
        success, result = auth_service.authenticate_user(email, password)
        if success:
            #page.client_storage.set("current_user", result)
            page.push_route("/dashboard")
        return success, result

    async def handle_register_attempt(email, username, password):
        return auth_service.register_user(email, username, password)

    #Alkalmazás indítása alapból a login felületen
    page.push_route("/login")

if __name__ == "__main__":
    ft.run(main, view = ft.AppView.WEB_BROWSER)