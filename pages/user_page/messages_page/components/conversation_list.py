import allure

from base_components.lists.base_list_handler import BaseListHandler


class ConversationList(BaseListHandler):
    """Список диалогов и создание нового."""

    _ROW_LOCATOR = "[data-testid^='conversation-']"

    _NEW_CONVERSATION_BUTTON = "[data-testid='new-conversation-btn']"
    _NEW_CONVERSATION_MODAL = "[data-testid='new-conversation-modal']"
    _NEW_CONVERSATION_SEARCH = "[data-testid='new-conversation-search']"

    def _row_testid(self, entity_id: str) -> str:
        return f"conversation-{entity_id}"

    @allure.step("Создание диалога с пользователем")
    def start_conversation(self, username: str):
        """Открыть модалку, найти пользователя и начать с ним диалог."""
        self.click(self._NEW_CONVERSATION_BUTTON)
        self.wait_for_visibility(self._NEW_CONVERSATION_MODAL)
        self.fill(self._NEW_CONVERSATION_SEARCH, username)
        self.click(("xpath", f"//*[starts-with(@data-testid,'new-conversation-user-')][.//text()[contains(.,'{username}')]]"))
        self._wait_loading_page()
        return self

    @allure.step("Открытие диалога {conversation_id}")
    def open_conversation(self, conversation_id: str):
        self.row_by_id(conversation_id).click()
        self._wait_loading_page()
        return self
