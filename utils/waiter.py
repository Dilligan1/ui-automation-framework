"""
Waiter — утилиты ожидания условий (polling).
НИКОГДА не использовать time.sleep() в тестах: ожидание всегда по условию.
"""

import time
from typing import Callable, Optional

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from metaclasses.meta_locators import MetaLocator


def _norm(locator):
    """Нормализация локатора: строка → кортеж (тот же разбор, что в MetaLocator)."""
    if isinstance(locator, str):
        if locator.startswith(("//", ".//", "(//")):
            return ("xpath", locator)
        if locator.startswith((".", "#", "[")):
            return ("css selector", locator)
    return locator


class Waiter(metaclass=MetaLocator):
    """Вызывается через инстанс: Waiter(driver).wait_for_element_visible(...)"""

    DEFAULT_TIMEOUT = 20.0
    POLL_INTERVAL = 0.5

    # Индикаторы загрузки SPA
    _SPINNER = "[data-testid='loading-spinner']"
    _TOAST = "[role='status']"

    def __init__(self, driver: WebDriver):
        self.driver = driver

    @allure.step("Ожидание условия (timeout={timeout}s)")
    def wait_for(
        self,
        condition: Callable[[], bool],
        timeout: float = DEFAULT_TIMEOUT,
        poll_interval: float = POLL_INTERVAL,
        message: Optional[str] = None,
    ) -> None:
        """Ждать, пока условие не вернёт True."""
        deadline = time.time() + timeout
        last_error = None
        attempts = 0

        while time.time() < deadline:
            attempts += 1
            try:
                if condition():
                    return
            except Exception as e:
                last_error = e
            time.sleep(poll_interval)

        error_message = message or f"Условие не выполнено за {timeout}s"
        if last_error:
            error_message += f". Последняя ошибка: {type(last_error).__name__}: {last_error}"
        error_message += f" (попыток: {attempts})"
        raise TimeoutError(error_message)

    @allure.step("Ожидание видимости элемента (timeout={timeout}s)")
    def wait_for_element_visible(self, locator, timeout: float = DEFAULT_TIMEOUT):
        locator = _norm(locator)
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            raise TimeoutError(f"Элемент {locator} не появился за {timeout}s")

    @allure.step("Ожидание кликабельности элемента (timeout={timeout}s)")
    def wait_for_element_clickable(self, locator, timeout: float = DEFAULT_TIMEOUT):
        locator = _norm(locator)
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            raise TimeoutError(f"Элемент {locator} не стал кликабельным за {timeout}s")

    @allure.step("Ожидание исчезновения элемента (timeout={timeout}s)")
    def wait_for_element_invisible(self, locator, timeout: float = DEFAULT_TIMEOUT):
        locator = _norm(locator)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
        except TimeoutException:
            raise TimeoutError(f"Элемент {locator} всё ещё виден после {timeout}s")

    @allure.step("Ожидание количества элементов (count={count}, timeout={timeout}s)")
    def wait_for_element_count(
        self, locator, count: int, timeout: float = DEFAULT_TIMEOUT, min_count: bool = False
    ):
        locator = _norm(locator)
        try:
            if min_count:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(d.find_elements(*locator)) >= count
                )
            else:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: len(d.find_elements(*locator)) == count
                )
        except TimeoutException:
            actual = len(self.driver.find_elements(*locator))
            raise TimeoutError(
                f"Ожидалось {'хотя бы ' if min_count else ''}{count} элементов, "
                f"найдено {actual} после {timeout}s"
            )

    @allure.step("Ожидание текста в элементе (timeout={timeout}s)")
    def wait_for_text_in_element(
        self, locator, text: str, timeout: float = DEFAULT_TIMEOUT, partial: bool = True
    ):
        locator = _norm(locator)
        try:
            if partial:
                WebDriverWait(self.driver, timeout).until(
                    EC.text_to_be_present_in_element(locator, text)
                )
            else:
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.find_element(*locator).text == text
                )
        except TimeoutException:
            actual = self.driver.find_element(*locator).text
            raise TimeoutError(
                f"Текст '{text}' не найден в элементе {locator} после {timeout}s. "
                f"Фактический текст: '{actual}'"
            )

    @allure.step("Ожидание значения атрибута (timeout={timeout}s)")
    def wait_for_attribute(
        self, locator, attribute: str, value: str, timeout: float = DEFAULT_TIMEOUT
    ):
        locator = _norm(locator)

        def check():
            actual = self.driver.find_element(*locator).get_attribute(attribute)
            return value in (actual or "")

        self.wait_for(
            check,
            timeout=timeout,
            message=f"Атрибут '{attribute}'='{value}' не найден после {timeout}s",
        )

    @allure.step("Ожидание загрузки страницы (timeout={timeout}s)")
    def wait_for_page_load(self, timeout: float = DEFAULT_TIMEOUT):
        self.wait_for(
            lambda: self.driver.execute_script("return document.readyState") == "complete",
            timeout=timeout,
            message=f"Страница не загрузилась за {timeout}s",
        )

    @allure.step("Ожидание завершения фоновых запросов SPA (timeout={timeout}s)")
    def wait_for_spa_idle(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Приложение — SPA: document.readyState становится complete задолго до того,
        как отрисованы данные. Поэтому дополнительно ждём исчезновения спиннера.
        Спиннера может не быть вовсе (мгновенный ответ) — это не ошибка.
        """
        self.wait_for_page_load(timeout=timeout)
        spinners = self.driver.find_elements(*_norm(self._SPINNER))
        if spinners:
            self.wait_for_element_invisible(self._SPINNER, timeout=timeout)
