import allure

from base.base_page import BasePage


class MainMenuLinks(BasePage):
    """Переходы по основным разделам приложения из левого меню."""

    _HOME = "[data-testid='nav-feed']"
    _EXPLORE = "[data-testid='nav-explore']"
    _SEARCH = "[data-testid='nav-search']"
    _MESSAGES = "[data-testid='nav-messages']"
    _NOTIFICATIONS = "[data-testid='nav-notifications']"
    _BOOKMARKS = "[data-testid='nav-bookmarks']"
    _DOCS = "[data-testid='nav-docs']"
    _SETTINGS = "[data-testid='nav-settings']"
    _PROFILE = "[data-testid='nav-profile']"
    _UNREAD_BADGE = "[data-testid='notifications-unread-badge']"

    @allure.step("Меню: переход в ленту")
    def open_feed(self):
        self.click(self._HOME)
        self._wait_loading_page()

    @allure.step("Меню: переход в сообщения")
    def open_messages(self):
        self.click(self._MESSAGES)
        self._wait_loading_page()

    @allure.step("Меню: переход в уведомления")
    def open_notifications(self):
        self.click(self._NOTIFICATIONS)
        self._wait_loading_page()

    @allure.step("Меню: переход в закладки")
    def open_bookmarks(self):
        self.click(self._BOOKMARKS)
        self._wait_loading_page()

    @allure.step("Меню: переход в настройки")
    def open_settings(self):
        self.click(self._SETTINGS)
        self._wait_loading_page()

    @allure.step("Меню: переход в свой профиль")
    def open_profile(self):
        self.click(self._PROFILE)
        self._wait_loading_page()

    def unread_notifications_count(self) -> int:
        """Значение бейджа непрочитанных. 0 — если бейдж скрыт."""
        if not self.is_element_visible(self._UNREAD_BADGE):
            return 0
        text = self.get_text(self._UNREAD_BADGE)
        return int("".join(ch for ch in text if ch.isdigit()) or 0)
