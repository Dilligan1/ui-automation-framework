import allure

from base_components.lists.base_list_handler import BaseListHandler


class CommentSection(BaseListHandler):
    """
    Блок комментариев под постом.

    Комментарии — тоже коллекция, поэтому наследуется от BaseListHandler:
    поиск по тексту, ожидание появления и дамп содержимого достаются бесплатно.
    Вложенность ответов ограничена тремя уровнями.
    """

    _ROW_LOCATOR = "[data-testid^='comment-']"

    _INPUT = "[data-testid='comment-input']"
    _SUBMIT = "[data-testid='comment-submit-btn']"

    _FIELDS = {
        "author": ".//*[starts-with(@data-testid,'comment-author-')]",
        "content": ".//*[starts-with(@data-testid,'comment-content-')]",
    }

    def _row_testid(self, entity_id: str) -> str:
        return f"comment-{entity_id}"

    @allure.step("Добавление комментария")
    def add(self, text: str):
        """Оставить комментарий и дождаться его появления в списке."""
        self.fill(self._INPUT, text)
        self.click(self._SUBMIT)
        self.wait_row_with_text(text)
        return self

    @allure.step("Ответ на комментарий {comment_id}")
    def reply(self, comment_id: str, text: str):
        """Ответить на комментарий — форма ответа раскрывается по кнопке."""
        self.click(("css selector", f"[data-testid='comment-reply-btn-{comment_id}']"))
        self.fill(self._INPUT, text)
        self.click(self._SUBMIT)
        self.wait_row_with_text(text)
        return self

    @allure.step("Лайк комментария {comment_id}")
    def like(self, comment_id: str):
        self.click(("css selector", f"[data-testid='comment-like-btn-{comment_id}']"))
        return self

    def comment_id_by_text(self, text: str) -> str:
        """id комментария по его тексту — комментарий создаётся через UI без id."""
        row = self.row_by_text(text)
        return row.get_attribute("data-testid").replace("comment-", "")
