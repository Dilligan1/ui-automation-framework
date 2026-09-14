from base.base_page import BasePage
from base_components.menu.components.admin_menu import AdminMenuLinks
from base_components.menu.components.main_menu import MainMenuLinks


class Menu(BasePage):
    """
    Навигация приложения — общий компонент всех страниц.

    Разбита на подкомпоненты: основное меню доступно всем, админское —
    только привилегированным ролям.
    """

    def __init__(self, driver):
        super().__init__(driver)
        self.main = MainMenuLinks(driver)
        self.admin = AdminMenuLinks(driver)

    def logout(self):
        """Выход из аккаунта через сайдбар."""
        self.click(self._LOGOUT_BUTTON)
        self.wait_logged_out()
