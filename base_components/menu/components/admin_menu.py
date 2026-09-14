import allure

from base.base_page import BasePage


class AdminMenuLinks(BasePage):
    """
    Пункты меню администратора.

    Видны только ролям admin и moderator — факт их отсутствия у обычного
    пользователя сам по себе является проверкой разграничения прав.
    """

    _ADMIN = "[data-testid='nav-admin']"
    # Подразделы админки собственных data-testid не имеют — адресуются по href
    _ADMIN_USERS = "//a[@href='/admin/users']"
    _ADMIN_CONTENT = "//a[@href='/admin/content']"

    @allure.step("Меню: переход в админ-панель")
    def open_dashboard(self):
        self.click(self._ADMIN)
        self._wait_loading_page()

    @allure.step("Меню: переход к управлению пользователями")
    def open_users(self):
        self.click(self._ADMIN_USERS)
        self._wait_loading_page()

    @allure.step("Меню: переход к модерации контента")
    def open_content(self):
        self.click(self._ADMIN_CONTENT)
        self._wait_loading_page()

    def is_available(self) -> bool:
        """Доступен ли раздел администрирования текущему пользователю."""
        return self.is_element_visible(self._ADMIN)
