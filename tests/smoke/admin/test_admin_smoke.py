import allure
import pytest

from base.base_test import BaseTest


@allure.epic("Smoke")
@allure.feature("Администрирование")
class TestAdminSmoke(BaseTest):
    """Smoke-тесты админ-панели."""

    @pytest.mark.smoke
    @pytest.mark.critical
    @allure.story("Доступ к админ-панели")
    @allure.title("Smoke: администратору доступен раздел управления пользователями")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_admin_users_page_available(self):
        """
        Шаги:
        1. Войти под ролью admin
        2. Открыть раздел управления пользователями

        Ожидаемый результат: таблица пользователей отрисована и не пуста.
        """
        admin = self.admin_page()

        with allure.step("Авторизация под ролью admin"):
            admin.login_page.login("admin")

        with allure.step("Открытие раздела управления пользователями"):
            admin.users.open()
            admin.users.users.wait_list_ready()

        with allure.step("Проверка содержимого таблицы"):
            assert not admin.users.users.is_empty(), (
                "Таблица пользователей пуста — данные не загрузились"
            )

    @pytest.mark.smoke
    @pytest.mark.critical
    @allure.story("Разграничение прав")
    @allure.title("Smoke: обычному пользователю раздел администрирования недоступен")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_admin_menu_hidden_for_user(self):
        """
        Шаги:
        1. Войти под ролью user
        2. Проверить наличие пункта меню «Администрирование»

        Ожидаемый результат: пункт меню не отображается.
        """
        with allure.step("Авторизация под ролью user"):
            self.user_page().login_page.login("user")
            self.user_page().feed.open()

        with allure.step("Проверка отсутствия админского меню"):
            assert not self.menu().admin.is_available(), (
                "Раздел администрирования виден обычному пользователю"
            )

    @pytest.mark.smoke
    @allure.story("Дашборд")
    @allure.title("Smoke: дашборд администратора показывает статистику")
    @allure.severity(allure.severity_level.NORMAL)
    def test_dashboard_shows_stats(self):
        """
        Шаги:
        1. Войти под ролью admin
        2. Открыть дашборд

        Ожидаемый результат: счётчики пользователей и постов больше нуля.
        """
        admin = self.admin_page()

        with allure.step("Авторизация и открытие дашборда"):
            admin.login_page.login("admin")
            admin.dashboard.open()

        with allure.step("Проверка счётчиков"):
            assert admin.dashboard.users_count() > 0, "Счётчик пользователей равен нулю"
            assert admin.dashboard.posts_count() > 0, "Счётчик постов равен нулю"
