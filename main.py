import flet as ft

from services import auth_service
from login import create_login_view
from register import create_register_view
from dashboard import create_dashboard_view
from profile_page import create_profile_view
from create_game import create_game_view
from answer import create_answer_view
from main_game import create_main_game_view
from jatekmester_dashboard import create_gm_dashboard_view
from award_voting import create_award_voting_view

async def main(page: ft.Page):
    page.title = "Társadalmi vitajáték"

    async def route_change(route):
        page.views.clear()

        #Navigációs segédfüggvények
        async def go_register(e=None):
            await page.push_route("/register")

        async def go_login(e=None):
            if page.session.store.contains_key("current_user"):
                page.session.store.remove("current_user")
            await page.push_route("/login")

        async def go_create(email, jatek_id):
            await page.push_route(f"/create/{jatek_id}")

        async def go_answer(jatek_id):
            await page.push_route(f"/answer/{jatek_id}")

        async def go_main_game(jatek_id):
            await page.push_route(f"/game/{jatek_id}")

        async def go_profile(e=None):
            await page.push_route(f"/profile")

        async def go_dashboard(e=None):
            await page.push_route(f"/dashboard")

        async def go_gm_dashboard(jatek_id):
            await page.push_route(f"/gm_dashboard/{jatek_id}")

        async def go_award_voting(jatek_id):
            await page.push_route(f"/award_voting/{jatek_id}")

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
                on_profile_click = go_profile,
                on_connect_click = None,
                on_create_click = go_create,
                on_answer_click = go_answer,
                on_main_game_click = go_main_game,
                on_gm_dashboard_click = go_gm_dashboard,
            )
            page.views.append(dashboard_view)
        #profile page
        elif page.route == "/profile":
            current_user = page.session.store.get("current_user")
            profile_view = await create_profile_view(
                page,
                current_user = current_user,
                on_password_change_attempt = handle_password_change,
                on_logout_click = go_login,
                on_dashboard_click = go_dashboard,
            )
            page.views.append(profile_view)
        #create game
        elif page.route.startswith("/create/"):
            #az útvonal febontása, hogy kinyerjük belőle az uj_id-t
            path_parts = page.route.split("/")
            if len(path_parts) == 3:
                uj_id = int(path_parts[2])

            create_view = await create_game_view(
                page,
                uj_id = uj_id,
                on_cancel = go_dashboard,
                on_gm_click = lambda: go_gm_dashboard(uj_id),
            )
            page.views.append(create_view)
        #answer
        elif page.route.startswith("/answer/"):
            #az útvonal felbontása, hogy kinyerjük belőle a jatek_id-t
            path_parts = page.route.split("/")
            if len(path_parts) == 3:
                jatek_id = int(path_parts[2])
        #award_vote
        elif page.route.startswith("/award_voting"):
            path_parts = page.route.split("/")
            if len(path_parts) == 3:
                jatek_id = int(path_parts[2])

            award_view = await create_award_voting_view(
                page,
                jatek_id = jatek_id,
                on_back_click = go_dashboard
            )
            page.views.append(award_view)

            answer_view = await create_answer_view(
                page,
                jatek_id = jatek_id,
                on_back_click = go_dashboard,
                on_start_game_click = go_main_game
            )
            page.views.append(answer_view)
        #main game
        elif page.route.startswith("/game/"):
            #az útvonal felbontása, hogy kinyerjük belőle a jatek_id-t
            path_parts = page.route.split("/")
            if len(path_parts) == 3:
                jatek_id = int(path_parts[2])

            main_game_view = await create_main_game_view(
                page,
                jatek_id = jatek_id,
                on_back_click = go_dashboard,
                on_answer_redirect = lambda: go_answer(jatek_id)
            )
            page.views.append(main_game_view)
        #játékmester dashboard
        elif page.route.startswith("/gm_dashboard/"):
            #az útvonal felbontása, hogy kinyerjük belőle a jatek_id-t
            path_parts = page.route.split("/")
            if len(path_parts) == 3:
                jatek_id = int(path_parts[2])

            gm_dashboard_view = await create_gm_dashboard_view(
                page,
                jatek_id
            )
            page.views.append(gm_dashboard_view)

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

    async def handle_password_change(email_vagy_nev, uj_jelszo):
        return await auth_service.change_password(email_vagy_nev, uj_jelszo)

    #Alkalmazás indítása alapból a login felületen
    await page.push_route("/login")

if __name__ == "__main__":
    ft.run(main, view = ft.AppView.WEB_BROWSER)