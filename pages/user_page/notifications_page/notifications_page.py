import allure

from base_components.lists.base_list_handler import BaseListHandler
from config.urls import URLS


class NotificationsPage(BaseListHandler):
    """
    Страница уведомлений.

    Сама является коллекцией, поэтому наследуется от BaseListHandler напрямую,
    без отдельного компонента списка.
    """

    _PAGE_URL = URLS.NOTIFICATIONS

    _ROW_LOCATOR = "[data-testid^='notification-']"

    _FILTER_ALL = "[data-testid='notifications-filter-all']"
    _FILTER_UNREAD = "[data-testid='notifications-filter-unread']"
    _MARK_ALL_BUTTON = "[data-testid='notifications-mark-all-btn']"
    _UNREAD_BADGE = "[data-testid='notifications-unread-badge']"

    def _row_testid(self, entity_id: str) -> str:
        return f"notification-{entity_id}"

    @allure.step("Фильтр: только непрочитанные")
    def filter_unread(self):
        self.click(self._FILTER_UNREAD)
        self._wait_loading_page()
        return self

    @allure.step("Фильтр: все уведомления")
    def filter_all(self):
        self.click(self._FILTER_ALL)
        self._wait_loading_page()
        return self

    @allure.step("Отметить все уведомления прочитанными")
    def mark_all_read(self):
        self.click(self._MARK_ALL_BUTTON)
        self._wait_loading_page()
        return self

    @allure.step("Отметить уведомление {notification_id} прочитанным")
    def mark_read(self, notification_id: str):
        self.click(
            ("css selector", f"[data-testid='notification-mark-read-btn-{notification_id}']")
        )
        return self

    @allure.step("Ожидание появления уведомлений")
    def wait_any(self, timeout: int = 20):
        """
        Дождаться хотя бы одного уведомления.

        Уведомление создаётся побочным эффектом чужого действия и приезжает
        отдельным запросом — проверять список сразу после открытия страницы
        рано.
        """
        self.waiter.wait_for(
            lambda: not self.is_empty(),
            timeout=timeout,
            message="Уведомления не появились",
        )
        return self

    def unread_count(self) -> int:
        """Значение бейджа непрочитанных. 0 — если бейдж скрыт."""
        if not self.is_element_visible(self._UNREAD_BADGE):
            return 0
        return int("".join(ch for ch in self.get_text(self._UNREAD_BADGE) if ch.isdigit()) or 0)
