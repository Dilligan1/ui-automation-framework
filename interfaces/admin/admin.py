from pages.admin_page.admin_content_page.admin_content_page import AdminContentPage
from pages.admin_page.admin_dashboard_page.admin_dashboard_page import AdminDashboardPage
from pages.admin_page.admin_users_page.admin_users_page import AdminUsersPage
from pages.common_page.login_page.login_page import LoginPage


class AdminInterface:
    """Страницы администратора: дашборд, пользователи, модерация контента."""

    def __init__(self, driver):
        self.login_page = LoginPage(driver)
        self.dashboard = AdminDashboardPage(driver)
        self.users = AdminUsersPage(driver)
        self.content = AdminContentPage(driver)
