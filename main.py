import flet as ft
from services import auth_service
from login import create_login_view
from register import create_register_view
from dashboard import create_dashboard_view

async def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"

    async def route_change(route):
        page.views.clear()

        #Navigációs segédfüggvények
        async def go_register(e=None):
            await page.push_route("/register")

        async def go_login(e=None):
            await page.push_route("/login")

        async def go_connect(e=None):
            await page.push_route("/connect")

        async def go_create(email, jatek_id):
            await page.push_route(f"/create/{jatek_id}")

        async def go_answer(jatek_id):
            await page.push_route(f"/answer/{jatek_id}")

        async def go_main_game(jatek_id):
            await page.push_route(f"/game/{jatek_id}")

        #Login
        if page.route == "/login" or page.route == "/":
            page.views.append(
                create_login_view(
                    page,
                    on_login_attempt = handle_login_attempt,
                    on_register_click = go_register,
                )
            )
        #regisztráció
        elif page.route == "/register":
            page.views.append(
                create_register_view(
                    page,
                    on_register_attempt = handle_register_attempt,
                    on_cancel_click = go_login,
                )
            )
        #dashboard
        elif page.route == "/dashboard":
            current_user = page.session.store.get("current_user")
            dashboard_view = await create_dashboard_view(
                page,
                current_user = current_user,
                on_logout = go_login,
                on_profile_click = go_connect,
                on_connect_click = go_connect,
                on_create_click = go_create,
                on_answer_click = go_answer,
                on_main_game_click = go_main_game
            )
            page.views.append(dashboard_view)

        page.update()

    async def view_pop(view):
        page.views.clear()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    #Adatbázis logika
    async def handle_login_attempt(email, password):
        success, result = await auth_service.authenticate_user(email, password)
        if success:
            page.session.store.set("current_user", result)
            await page.push_route("/dashboard")
        return success, result

    async def handle_register_attempt(email, username, password):
        return await auth_service.register_user(email, username, password)

    #Alkalmazás indítása alapból a login felületen
    await page.push_route("/login")

if __name__ == "__main__":
    ft.run(main, view = ft.AppView.WEB_BROWSER)