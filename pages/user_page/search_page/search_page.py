import allure

from base.base_page import BasePage
from config.urls import URLS


class SearchPage(BasePage):
    """Поиск по пользователям, постам и хэштегам."""

    _PAGE_URL = URLS.SEARCH

    _SEARCH_INPUT = "[data-testid='nav-search-input']"
    _TAB_USERS = "//button[normalize-space()='Users']"
    _TAB_POSTS = "//button[normalize-space()='Posts']"
    _TAB_HASHTAGS = "//button[normalize-space()='Hashtags']"
    # Контейнера результатов с data-testid нет — якорем служит <main> страницы
    _RESULTS = "//main"

    @allure.step("Поиск по запросу: {query}")
    def search(self, query: str):
        """Ввести запрос и дождаться отрисовки результатов."""
        self.fill(self._SEARCH_INPUT, query)
        self.find(self._SEARCH_INPUT).submit()
        self._wait_loading_page()
        return self

    @allure.step("Вкладка результатов: пользователи")
    def open_users_tab(self):
        self.click(self._TAB_USERS)
        self._wait_loading_page()
        return self

    @allure.step("Вкладка результатов: посты")
    def open_posts_tab(self):
        self.click(self._TAB_POSTS)
        self._wait_loading_page()
        return self

    @allure.step("Вкладка результатов: хэштеги")
    def open_hashtags_tab(self):
        self.click(self._TAB_HASHTAGS)
        self._wait_loading_page()
        return self

    def results_text(self) -> str:
        """Текст блока результатов — проверяется вхождение искомого значения."""
        return self.get_text(self._RESULTS)

    def has_result_with(self, text: str) -> bool:
        return text in self.results_text()
