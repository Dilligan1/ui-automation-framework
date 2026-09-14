import allure

from base_components.lists.base_list_handler import BaseListHandler
from data.test_data import ROLES


class AdminUsersList(BaseListHandler):
    """
    Таблица пользователей в админке.

    Строка идентифицируется по data-testid `admin-user-row-<id>`, а действия
    (смена роли, бан, верификация) — по такому же шаблону с тем же id.
    Поэтому все операции параметризованы id, а не позицией строки: список
    пересортировывается после каждого действия.
    """

    _CONTAINER_LOCATOR = "[data-testid='admin-users-table']"
    _ROW_LOCATOR = "[data-testid^='admin-user-row-']"

    _SEARCH_INPUT = "[data-testid='admin-search-input']"

    _FIELDS = {
        "name": ".//p[contains(@class,'font-medium')]",
        "meta": ".//p[contains(@class,'text-xs')]",
    }

    def _row_testid(self, entity_id: str) -> str:
        return f"admin-user-row-{entity_id}"

    @allure.step("Поиск пользователя: {query}")
    def search(self, query: str):
        """Фильтрация списка. Поиск применяется по Enter."""
        field = self.fill(self._SEARCH_INPUT, query)
        field.submit()
        self._wait_loading_page()
        return self

    @allure.step("Смена роли пользователя {user_id} на {role}")
    def set_role(self, user_id: str, role: str):
        """Выбрать роль в выпадающем списке строки."""
        assert role in ROLES, f"Недопустимая роль '{role}'. Доступны: {ROLES}"
        from selenium.webdriver.support.ui import Select

        select = Select(self.find(("css selector", f"[data-testid='admin-role-select-{user_id}']")))
        select.select_by_value(role)
        self.wait_toast()
        return self

    def role_of(self, user_id: str) -> str:
        """Текущая роль пользователя — значение селекта в его строке."""
        element = self.find(("css selector", f"[data-testid='admin-role-select-{user_id}']"))
        return element.get_attribute("value")

    @allure.step("Переключение бана пользователя {user_id}")
    def toggle_ban(self, user_id: str):
        """
        Нажать кнопку бана/разбана.

        Кнопка переключаемая: её текст отражает действие, которое произойдёт
        при клике (Ban у активного, Unban у забаненного).
        """
        self.click(("css selector", f"[data-testid='admin-ban-btn-{user_id}']"))
        self.wait_toast()
        return self

    def ban_button_text(self, user_id: str) -> str:
        return self.get_text(("css selector", f"[data-testid='admin-ban-btn-{user_id}']"))

    @allure.step("Переключение верификации пользователя {user_id}")
    def toggle_verify(self, user_id: str):
        self.click(("css selector", f"[data-testid='admin-verify-btn-{user_id}']"))
        self.wait_toast()
        return self

    def is_banned(self, user_id: str) -> bool:
        """Признак бана — метка [BANNED] в строке пользователя."""
        return "[BANNED]" in self.row_by_id(user_id).text

    def user_id_by_username(self, username: str) -> str:
        """id пользователя по его хэндлу — в UI id нигде не показан явно."""
        row = self.row_by_text(f"@{username}")
        return row.get_attribute("data-testid").replace("admin-user-row-", "")
