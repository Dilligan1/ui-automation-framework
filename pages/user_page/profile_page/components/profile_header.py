import allure

from base.base_page import BasePage


class ProfileHeader(BasePage):
    """Шапка профиля: имя, счётчики, кнопки подписки и сообщения."""

    _DISPLAY_NAME = "[data-testid='profile-display-name']"
    _USERNAME = "[data-testid='profile-username']"
    _BIO = "[data-testid='profile-bio']"
    _ROLE = "[data-testid='profile-role']"
    _AVATAR = "[data-testid='profile-avatar']"
    _POSTS_COUNT = "[data-testid='profile-posts-count']"
    _FOLLOWERS_COUNT = "[data-testid='profile-followers-count']"
    _FOLLOWING_COUNT = "[data-testid='profile-following-count']"
    _FOLLOW_BUTTON = "[data-testid='profile-follow-btn']"
    _MESSAGE_BUTTON = "[data-testid='profile-message-btn']"
    _EDIT_BUTTON = "[data-testid='profile-edit-btn']"

    def display_name(self) -> str:
        return self.get_text(self._DISPLAY_NAME)

    def username(self) -> str:
        return self.get_text(self._USERNAME)

    def bio(self) -> str:
        return self.get_text(self._BIO)

    def role(self) -> str:
        return self.get_text(self._ROLE)

    def posts_count(self) -> int:
        return self._digits(self._POSTS_COUNT)

    def followers_count(self) -> int:
        return self._digits(self._FOLLOWERS_COUNT)

    def following_count(self) -> int:
        return self._digits(self._FOLLOWING_COUNT)

    def _digits(self, locator) -> int:
        text = self.get_text(locator)
        return int("".join(ch for ch in text if ch.isdigit()) or 0)

    @allure.step("Подписка / отписка через профиль")
    def toggle_follow(self):
        """
        Нажать кнопку подписки.

        Кнопка переключаемая: её текст (Follow / Requested / Following)
        отражает текущее состояние, поэтому читается до и после клика.
        """
        self.click(self._FOLLOW_BUTTON)
        self._wait_loading_page()
        return self

    def follow_button_text(self) -> str:
        return self.get_text(self._FOLLOW_BUTTON)

    def is_follow_available(self) -> bool:
        """На своём профиле кнопки подписки нет — вместо неё кнопка редактирования."""
        return self.is_element_visible(self._FOLLOW_BUTTON)

    @allure.step("Переход к диалогу с пользователем")
    def open_message(self):
        self.click(self._MESSAGE_BUTTON)
        self._wait_loading_page()
        return self

    @allure.step("Открытие редактирования профиля")
    def open_edit(self):
        self.click(self._EDIT_BUTTON)
        return self
