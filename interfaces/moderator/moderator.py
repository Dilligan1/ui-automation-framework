from pages.admin_page.admin_content_page.admin_content_page import AdminContentPage
from pages.admin_page.admin_dashboard_page.admin_dashboard_page import AdminDashboardPage
from pages.common_page.login_page.login_page import LoginPage


class ModeratorInterface:
    """
    Страницы модератора.

    Отличается от администратора набором доступных разделов: модерация контента
    есть, управления ролями пользователей нет. Отдельный интерфейс нужен именно
    для того, чтобы это ограничение было видно в коде, а не только в тестах.
    """

    def __init__(self, driver):
        self.login_page = LoginPage(driver)
        self.dashboard = AdminDashboardPage(driver)
        self.content = AdminContentPage(driver)
