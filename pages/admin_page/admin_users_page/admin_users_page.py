from base.base_page import BasePage
from config.urls import URLS
from pages.admin_page.admin_users_page.components.admin_users_list import AdminUsersList


class AdminUsersPage(BasePage):
    """Управление пользователями: роли, бан, верификация."""

    _PAGE_URL = URLS.ADMIN_USERS

    _TITLE = "//h1"

    def __init__(self, driver):
        super().__init__(driver)
        self.users = AdminUsersList(driver)
