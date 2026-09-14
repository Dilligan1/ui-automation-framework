"""
UIHelper — обёртка над Selenium WebDriver.

Единственный слой, который напрямую дёргает find_element/click/send_keys.
Все страницы наследуются от него через BasePage и работают только этими методами:
это даёт одинаковые ожидания, одинаковое логирование и одну точку правки,
когда поведение фронта меняется.
"""

import os

import allure
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from metaclasses.meta_locators import MetaLocator
from utils.waiter import Waiter, _norm


class UIHelper(metaclass=MetaLocator):
    DEFAULT_TIMEOUT = int(os.getenv("UI_TIMEOUT", "20"))

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)
        self.waiter = Waiter(driver)

    # === Поиск ===

    def find(self, locator: tuple | WebElement, message: str = "", wait: bool = True) -> WebElement:
        """Найти элемент. wait=True — дождаться присутствия в DOM."""
        if isinstance(locator, WebElement):
            return locator
        locator = _norm(locator)
        if not wait:
            return self.driver.find_element(*locator)
        try:
            return self.wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            raise TimeoutException(
                message or f"Элемент не найден за {self.DEFAULT_TIMEOUT}s: {locator}"
            )

    def find_all(self, locator: tuple, message: str = "", wait: bool = True) -> list[WebElement]:
        """
        Найти все элементы. Пустой список — валидный результат
        (лента без постов, профиль без подписчиков), поэтому исключения нет.
        """
        locator = _norm(locator)
        if wait:
            try:
                self.wait.until(EC.presence_of_element_located(locator))
            except TimeoutException:
                return []
        return self.driver.find_elements(*locator)

    # === Действия ===

    @allure.step("Ввод текста: {text}")
    def fill(self, locator, text: str, force_clear: bool = False):
        """Ввести текст в поле. force_clear — очистить через JS, если clear() не сработал."""
        element = self.wait.until(EC.element_to_be_clickable(_norm(locator)))
        if force_clear:
            self.driver.execute_script("arguments[0].value = '';", element)
        else:
            element.clear()
        element.send_keys(text)
        return element

    @allure.step("Клик по элементу")
    def click(self, locator, message: str = ""):
        """
        Клик с двумя страховками:
          - StaleElementReferenceException — React перерисовал узел между поиском
            и кликом, повторяем поиск;
          - ElementClickInterceptedException — элемент перекрыт тостом или модалкой,
            кликаем через JS.
        """
        locator = _norm(locator)
        try:
            element = self.waiter.wait_for_element_clickable(locator)
            element.click()
        except StaleElementReferenceException:
            element = self.waiter.wait_for_element_clickable(locator)
            element.click()
        except ElementClickInterceptedException:
            element = self.find(locator)
            self.driver.execute_script("arguments[0].click();", element)
        except TimeoutError:
            raise TimeoutException(message or f"Элемент некликабелен: {locator}")

    @allure.step("Клик с проверкой результата")
    def click_until(
        self,
        locator,
        condition,
        attempts: int = 3,
        timeout: float = 5.0,
        message: str = "",
    ):
        """
        Кликать, пока клик не даст нужный эффект.

        Нужен там, где список перерисовывается после действия пользователя:
        React заменяет узел между поиском и кликом, событие уходит в никуда,
        а элемент в DOM остаётся — обычный click() отрабатывает «успешно»,
        но ничего не происходит. Проверяется не факт клика, а его результат:
        раскрылось меню, сменился адрес, появился элемент.

        condition: функция без аргументов, возвращающая True при успехе.
        """
        for attempt in range(1, attempts + 1):
            self.click(locator)
            try:
                self.waiter.wait_for(condition, timeout=timeout)
                return self
            except TimeoutError:
                if attempt == attempts:
                    raise TimeoutException(
                        message
                        or f"Клик по {locator} не дал результата за {attempts} попыток"
                    )
        return self

    @allure.step("Скриншот: {name}")
    def screenshot(self, name: str = "screenshot"):
        """Приложить скриншот к текущему шагу отчёта."""
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

    # === Состояние элементов ===

    def wait_for_visibility(self, locator, message: str = "") -> WebElement:
        return self.waiter.wait_for_element_visible(locator)

    def wait_for_invisibility(self, locator, message: str = "") -> None:
        self.waiter.wait_for_element_invisible(locator)

    def is_element_visible(self, locator) -> bool:
        """Видим ли элемент. Не бросает исключение — предназначен для ассертов."""
        try:
            return self.find(locator, wait=False).is_displayed()
        except Exception:
            return False

    def get_text(self, locator) -> str:
        return self.wait_for_visibility(locator).text.strip()

    # === Скроллинг ===

    def scroll_by(self, x: int, y: int):
        self.driver.execute_script(f"window.scrollBy({x}, {y});")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_to_element(self, locator):
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element
        )
        return element

    # === Загрузка страницы и файлов ===

    def _wait_loading_page(self, timeout: int | None = None):
        """Дождаться готовности SPA: DOM загружен и спиннер исчез."""
        self.waiter.wait_for_spa_idle(timeout=timeout or self.DEFAULT_TIMEOUT)

    @allure.step("Загрузка файла: {file_path}")
    def upload_file(self, file_input, file_path: str):
        """
        Загрузка файла через send_keys в <input type="file">.
        Сам input обычно скрыт (кликается кастомная кнопка), поэтому ищем
        без ожидания видимости и передаём абсолютный путь.
        """
        absolute_path = os.path.abspath(file_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"Файл для загрузки не найден: {absolute_path}")
        element = self.find(file_input, wait=True)
        element.send_keys(absolute_path)

    # === Нативные диалоги браузера ===

    @allure.step("Подтверждение системного диалога")
    def accept_alert(self, timeout: int = 10):
        """
        Принять нативный confirm/alert.

        Приложение подтверждает удаление поста через window.confirm — обычными
        локаторами такой диалог не виден, и любой следующий клик упадёт с
        UnexpectedAlertPresentException, пока диалог открыт.
        """
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text

    @allure.step("Отмена системного диалога")
    def dismiss_alert(self, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.dismiss()
        return text

    def wait_for_new_tab(self, timeout: int = 10):
        """Дождаться открытия новой вкладки и переключиться на неё."""
        initial = len(self.driver.window_handles)
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.window_handles) > initial
        )
        self.driver.switch_to.window(self.driver.window_handles[-1])
