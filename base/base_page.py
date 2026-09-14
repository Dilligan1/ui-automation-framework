import allure
from selenium.webdriver.support import expected_conditions as EC

from utils.ui_helper import UIHelper


class BasePage(UIHelper):
    """
    Общий предок всех страниц.

    Держит элементы, присутствующие на каждой странице приложения (шапка,
    навигация, тосты), и базовые операции открытия/проверки страницы.
    Конкретная страница объявляет свой _PAGE_URL и свои локаторы.
    """

    _PAGE_URL = None

    # Постоянные элементы каркаса приложения
    _LOGO = "[data-testid='nav-logo']"
    _NAV_PROFILE = "[data-testid='nav-profile']"
    _NAV_SETTINGS = "[data-testid='nav-settings']"
    _NAV_ADMIN = "[data-testid='nav-admin']"
    _NAV_SEARCH_INPUT = "[data-testid='nav-search-input']"
    _LOGOUT_BUTTON = "[data-testid='auth-logout-btn']"

    # Тост-уведомления (react-hot-toast)
    _TOAST = "[role='status']"

    @allure.step("Открытие страницы")
    def open(self):
        """Открыть страницу по её _PAGE_URL и дождаться готовности SPA."""
        if not self._PAGE_URL:
            raise NotImplementedError(
                f"{type(self).__name__} не объявил _PAGE_URL — открывать нечего"
            )
        self.driver.get(self._PAGE_URL)
        self._wait_loading_page()
        return self

    def is_opened(self) -> bool:
        """Совпадает ли текущий URL с URL страницы."""
        try:
            self.wait.until(EC.url_to_be(self._PAGE_URL))
            return True
        except Exception:
            return False

    def is_authorized(self) -> bool:
        """Отрисован ли каркас приложения — признак активной сессии."""
        return self.is_element_visible(self._LOGO)

    def wait_authorized(self, timeout: int = 10) -> bool:
        """
        Дождаться отрисовки каркаса приложения.

        Возвращает True/False вместо исключения: вызывающий код решает, что
        делать с неудачей — например, войти через форму, если восстановленная
        сессия оказалась протухшей.
        """
        try:
            self.waiter.wait_for(self.is_authorized, timeout=timeout)
            return True
        except TimeoutError:
            return False

    @allure.step("Ожидание выхода из аккаунта")
    def wait_logged_out(self, timeout: int = 20):
        """
        Дождаться, пока каркас приложения исчезнет.

        После выхода приложение редиректит на /login, и проверять сессию
        сразу после клика рано: сайдбар ещё в DOM.
        """
        self.waiter.wait_for(
            lambda: not self.is_authorized(),
            timeout=timeout,
            message="Каркас приложения не исчез после выхода из аккаунта",
        )

    # === Тосты ===

    @allure.step("Ожидание тоста")
    def wait_toast(self):
        return self.wait_for_visibility(self._TOAST)

    def toast_text(self) -> str:
        """Текст всплывающего уведомления — часто это единственный отклик UI."""
        return self.get_text(self._TOAST)

    def wait_toast_gone(self):
        """
        Дождаться исчезновения тоста.

        Нужен перед кликом по элементу под ним: тост перекрывает кнопки
        и ловит клик на себя.
        """
        self.wait_for_invisibility(self._TOAST)
