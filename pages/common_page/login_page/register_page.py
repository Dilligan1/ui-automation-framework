import allure

from base.base_page import BasePage
from config.urls import URLS


class RegisterPage(BasePage):
    """Страница регистрации нового пользователя."""

    _PAGE_URL = URLS.REGISTER

    _EMAIL_FIELD = "[data-testid='auth-email-input']"
    _USERNAME_FIELD = "[data-testid='auth-username-input']"
    _DISPLAY_NAME_FIELD = "[data-testid='auth-display-name-input']"
    _PASSWORD_FIELD = "[data-testid='auth-password-input']"
    _SUBMIT_BUTTON = "[data-testid='auth-register-btn']"
    _ERROR_MESSAGE = "[data-testid='auth-error-message']"

    @allure.step("Регистрация пользователя {username}")
    def register(self, email: str, username: str, display_name: str, password: str):
        """Заполнить форму и отправить. Данные готовит DataGenerator."""
        self.fill(self._EMAIL_FIELD, email)
        self.fill(self._USERNAME_FIELD, username)
        self.fill(self._DISPLAY_NAME_FIELD, display_name)
        self.fill(self._PASSWORD_FIELD, password)
        self.click(self._SUBMIT_BUTTON)
        self._wait_loading_page()
        return self

    def error_message(self) -> str:
        return self.get_text(self._ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        return self.is_element_visible(self._ERROR_MESSAGE)
