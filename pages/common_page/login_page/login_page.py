import os

import allure
from filelock import FileLock

from base.base_page import BasePage
from config.credentials import Credentials
from config.urls import URLS
from utils.storage_manager import StorageManager


class LoginPage(BasePage):
    """
    Страница входа.

    Логин выполняется один раз на роль: токены сохраняются в файл и в следующих
    тестах подставляются в localStorage. Это экономит на каждом тесте полный
    проход формы, но остаётся честным — при протухшей сессии происходит
    обычный вход через UI.
    """

    _PAGE_URL = URLS.LOGIN

    _EMAIL_FIELD = "[data-testid='auth-email-input']"
    _PASSWORD_FIELD = "[data-testid='auth-password-input']"
    _SUBMIT_BUTTON = "[data-testid='auth-login-btn']"
    _ERROR_MESSAGE = "[data-testid='auth-error-message']"
    _REGISTER_LINK = "//a[@href='/register']"

    @property
    def _stage(self) -> str:
        return os.getenv("STAGE", "local").lower()

    def _session_path(self, role: str) -> str:
        """
        Файл сессии роли. Общий для всех xdist-worker'ов — доступ к нему
        сериализуется файловой блокировкой в login().
        """
        return f"storage/{self._stage}/{role}.json"

    @allure.step("Авторизация под ролью: {role}")
    def login(self, role: str = "user", force_login: bool = False):
        """
        Войти в приложение.

        role:        admin | moderator | user | private | empty | banned
        force_login: игнорировать сохранённую сессию и пройти форму заново
        """
        session_path = self._session_path(role)
        storage = StorageManager(self.driver, session_path)

        # localStorage доступен только после открытия origin приложения
        self.open()

        # Блокировка на время «прочитать сессию или войти заново»: при
        # параллельном прогоне worker'ы не должны входить одним пользователем
        # одновременно — сервис отвечает на это 500 (BUG-001).
        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        with FileLock(f"{session_path}.lock", timeout=120):
            return self._login_locked(role, storage, force_login)

    def _login_locked(self, role: str, storage: StorageManager, force_login: bool):
        """Тело входа, выполняемое под файловой блокировкой."""
        if not force_login and storage.load():
            self.driver.get(URLS.FEED)
            self._wait_loading_page()
            # Проверять сессию мгновенно нельзя: приложение — SPA, каркас
            # появляется после монтирования React, а не после загрузки документа
            if self.wait_authorized():
                return self
            # Сессия протухла — идём обычным путём
            self.open()

        email, password = Credentials.get(role)
        self.fill(self._EMAIL_FIELD, email)
        self.fill(self._PASSWORD_FIELD, password)
        self.click(self._SUBMIT_BUTTON)
        self._wait_loading_page()
        assert self.wait_authorized(timeout=20), (
            f"Вход под ролью '{role}' не выполнен: каркас приложения не отрисован. "
            f"Сообщение формы: '{self.error_message() if self.is_error_visible() else '—'}'"
        )

        storage.save()
        return self

    @allure.step("Попытка входа с произвольными учётными данными")
    def login_with(self, email: str, password: str):
        """Вход указанными данными без сохранения сессии — для негативных тестов."""
        self.open()
        self.fill(self._EMAIL_FIELD, email)
        self.fill(self._PASSWORD_FIELD, password)
        self.click(self._SUBMIT_BUTTON)
        return self

    @allure.step("Ожидание сообщения об ошибке входа")
    def wait_error_message(self) -> str:
        """
        Дождаться сообщения об ошибке и вернуть его текст.

        Проверять видимость сразу после клика нельзя: форма отправляет запрос
        асинхронно и подставляет текст ошибки только после ответа сервера.
        """
        return self.get_text(self._ERROR_MESSAGE)

    def error_message(self) -> str:
        return self.get_text(self._ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        """Неблокирующая проверка — для случаев, когда ошибки быть не должно."""
        return self.is_element_visible(self._ERROR_MESSAGE)

    @allure.step("Переход к форме регистрации")
    def go_to_register(self):
        self.click(self._REGISTER_LINK)
        self._wait_loading_page()
