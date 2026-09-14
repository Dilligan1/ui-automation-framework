import allure

from base_components.lists.base_list_handler import BaseListHandler


class AdminPostsList(BaseListHandler):
    """Таблица постов в админке — модераторское удаление контента."""

    _CONTAINER_LOCATOR = "[data-testid='admin-posts-table']"
    _ROW_LOCATOR = "[data-testid^='admin-post-row-']"

    _SEARCH_INPUT = "[data-testid='admin-search-input']"

    def _row_testid(self, entity_id: str) -> str:
        return f"admin-post-row-{entity_id}"

    @allure.step("Поиск поста: {query}")
    def search(self, query: str):
        field = self.fill(self._SEARCH_INPUT, query)
        field.submit()
        self._wait_loading_page()
        return self

    @allure.step("Модераторское удаление поста {post_id}")
    def delete_post(self, post_id: str):
        self.click(("css selector", f"[data-testid='admin-delete-post-btn-{post_id}']"))
        self.wait_toast()
        return self
