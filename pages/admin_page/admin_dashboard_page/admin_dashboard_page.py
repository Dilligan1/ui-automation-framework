from base.base_page import BasePage
from config.urls import URLS


class AdminDashboardPage(BasePage):
    """Дашборд администратора со сводной статистикой."""

    _PAGE_URL = URLS.ADMIN_DASHBOARD

    _USERS_COUNT = "[data-testid='admin-stats-users-count']"
    _POSTS_COUNT = "[data-testid='admin-stats-posts-count']"

    def users_count(self) -> int:
        return self._digits(self._USERS_COUNT)

    def posts_count(self) -> int:
        return self._digits(self._POSTS_COUNT)

    def _digits(self, locator) -> int:
        text = self.get_text(locator)
        return int("".join(ch for ch in text if ch.isdigit()) or 0)
