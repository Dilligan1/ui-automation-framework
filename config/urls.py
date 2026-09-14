import os

from dotenv import load_dotenv

load_dotenv()

# Конфигурация стендов
stages = {
    "local": "http://localhost:3000",
    "ci": "http://frontend:3000",
}

STAGE = os.getenv("STAGE", "local")
HOST = os.getenv(f"UI_HOST_{STAGE.upper()}", stages[STAGE])

# Хост API — используется для подготовки данных и сброса стенда,
# а не для проверок: UI-тест проверяет интерфейс.
API_HOST = os.getenv(f"API_HOST_{STAGE.upper()}", HOST.replace(":3000", ":8000"))


class URLS:
    """URL-адреса страниц приложения."""

    """ --- Общие страницы --- """

    LOGIN = f"{HOST}/login"
    REGISTER = f"{HOST}/register"

    """ --- Страницы пользователя --- """

    FEED = f"{HOST}/"
    EXPLORE = f"{HOST}/explore"
    SEARCH = f"{HOST}/search"
    MESSAGES = f"{HOST}/messages"
    NOTIFICATIONS = f"{HOST}/notifications"
    BOOKMARKS = f"{HOST}/bookmarks"
    SETTINGS = f"{HOST}/settings"

    @staticmethod
    def post(post_id: str) -> str:
        return f"{HOST}/post/{post_id}"

    @staticmethod
    def profile(username: str) -> str:
        return f"{HOST}/profile/{username}"

    @staticmethod
    def followers(username: str) -> str:
        return f"{HOST}/profile/{username}/followers"

    @staticmethod
    def following(username: str) -> str:
        return f"{HOST}/profile/{username}/following"

    """ --- Страницы администратора --- """

    ADMIN_DASHBOARD = f"{HOST}/admin"
    ADMIN_USERS = f"{HOST}/admin/users"
    ADMIN_CONTENT = f"{HOST}/admin/content"

    """ --- Служебное --- """

    API_RESET = f"{API_HOST}/api/reset"
