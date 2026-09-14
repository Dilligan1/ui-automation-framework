import allure

from base.base_page import BasePage
from config.urls import URLS
from pages.user_page.messages_page.components.conversation_list import ConversationList
from pages.user_page.messages_page.components.message_thread import MessageThread


class MessagesPage(BasePage):
    """Раздел сообщений: список диалогов слева, переписка справа."""

    _PAGE_URL = URLS.MESSAGES

    def __init__(self, driver):
        super().__init__(driver)
        self.conversations = ConversationList(driver)
        self.thread = MessageThread(driver)

    @allure.step("Отправка сообщения пользователю @{username}")
    def send_message_to(self, username: str, text: str):
        """Сквозной сценарий: открыть раздел → создать диалог → отправить."""
        self.open()
        self.conversations.start_conversation(username)
        self.thread.send(text)
        return self
