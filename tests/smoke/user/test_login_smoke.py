import allure
import pytest

from base.base_test import BaseTest


@allure.epic("Smoke")
@allure.feature("Авторизация")
class TestLoginSmoke(BaseTest):
    """Smoke-тесты входа в приложение."""

    @pytest.mark.smoke
    @pytest.mark.critical
    @allure.story("Вход в систему")
    @allure.title("Smoke: вход обычного пользователя")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_user_login(self):
        """
        Шаги:
        1. Открыть страницу входа
        2. Авторизоваться под ролью user

        Ожидаемый результат:
        - отрисован каркас приложения (признак активной сессии)
        - открыта лента
        """
        with allure.step("Авторизация под ролью user"):
            self.user_page().login_page.login("user")

        with allure.step("Проверка успешного входа"):
            assert self.user_page().feed.is_authorized(), (
                "После входа каркас приложения не отрисован — сессия не установлена"
            )

    @pytest.mark.smoke
    @pytest.mark.negative
    @allure.story("Вход в систему")
    @allure.title("Smoke: вход с неверным паролем отклоняется")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_with_wrong_password(self, gen):
        """
        Шаги:
        1. Открыть страницу входа
        2. Ввести несуществующие учётные данные

        Ожидаемый результат:
        - показано сообщение об ошибке
        - вход не выполнен
        """
        login_page = self.user_page().login_page

        with allure.step("Ввод несуществующих учётных данных"):
            login_page.login_with(gen.unique_email(), "wrong-password")

        with allure.step("Проверка сообщения об ошибке"):
            message = login_page.wait_error_message()
            assert message, "Сообщение об ошибке пустое"
            assert not login_page.is_authorized(), (
                "Пользователь авторизован, хотя учётные данные неверны"
            )

    @pytest.mark.smoke
    @allure.story("Выход из системы")
    @allure.title("Smoke: выход из аккаунта возвращает на страницу входа")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout(self):
        """
        Шаги:
        1. Войти под ролью user
        2. Выйти через меню

        Ожидаемый результат: каркас приложения больше не отрисован.
        """
        with allure.step("Авторизация"):
            self.user_page().login_page.login("user")

        with allure.step("Выход из аккаунта"):
            self.menu().logout()

        with allure.step("Проверка выхода"):
            assert not self.user_page().login_page.is_authorized(), (
                "После выхода каркас приложения всё ещё отрисован"
            )
