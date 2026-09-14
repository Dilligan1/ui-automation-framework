import allure

from base_components.lists.base_list_handler import BaseListHandler


class MessageThread(BaseListHandler):
    """Переписка внутри диалога."""

    _ROW_LOCATOR = "[data-testid^='message-']"

    _INPUT = "[data-testid='message-input']"
    _SEND_BUTTON = "[data-testid='message-send-btn']"

    def _row_testid(self, entity_id: str) -> str:
        return f"message-{entity_id}"

    @allure.step("Отправка сообщения")
    def send(self, text: str):
        """Отправить сообщение и дождаться его появления в переписке."""
        self.fill(self._INPUT, text)
        self.click(self._SEND_BUTTON)
        self.wait_row_with_text(text)
        return self

    def last_message_text(self) -> str:
        rows = self.rows()
        assert rows, "Переписка пуста — сообщений нет"
        return rows[-1].text.strip()
