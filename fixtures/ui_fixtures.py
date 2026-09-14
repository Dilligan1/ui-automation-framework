import os
import threading

import pytest
from faker import Faker
from selenium import webdriver

from utils.data_generator import DataGenerator

# Режим без окна браузера — включается в CI и в контейнере
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# Удалённый Selenium Grid / standalone-контейнер; пусто — локальный Chrome
REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL", "")

# Потокобезопасное хранилище драйвера — нужно при параллельном прогоне
_local = threading.local()


def _chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()

    # === HEADLESS ===
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    # === Базовые настройки ===
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    # /dev/shm в контейнере мал — без этого флага Chrome падает на тяжёлых страницах
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")

    # === Убираем признаки автоматизации ===
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # === Отключаем встроенные диалоги Chrome ===
    # Тестовые пароли seed-пользователей («alice123» и т.п.) числятся в утечках,
    # и после входа Chrome показывает модальное окно «Смените пароль». Оно
    # перехватывает клики по странице: следующий клик теста формально проходит,
    # но до приложения не доходит — тест падает в непредсказуемом месте.
    options.add_argument("--disable-features=PasswordLeakDetection,AutofillServerCommunication")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            # Уведомления браузера поверх страницы — та же проблема
            "profile.default_content_setting_values.notifications": 2,
        },
    )

    return options


def get_driver():
    """Создать драйвер: локальный Chrome или удалённый (Grid/контейнер)."""
    options = _chrome_options()

    if REMOTE_URL:
        driver = webdriver.Remote(command_executor=REMOTE_URL, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    # Прячем navigator.webdriver — часть фронтов меняет поведение, увидев его
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """
        },
    )
    driver.set_page_load_timeout(60)
    return driver


@pytest.fixture(autouse=True)
def driver(request):
    """
    Драйвер на каждый тест.

    Пишется и в thread-local (для параллельного прогона), и в request.cls.driver —
    последнее нужно, чтобы тест-классы обращались к нему как self.driver,
    а хук создания скриншота в conftest.py мог достать драйвер упавшего теста.
    """
    driver = get_driver()
    _local.driver = driver
    request.cls.driver = driver
    yield driver
    driver.quit()


@pytest.fixture
def second_driver():
    """
    Второй независимый браузер.

    Нужен сценариям с двумя пользователями одновременно: автор публикует пост
    в одном окне, читатель реагирует в другом.
    """
    driver = get_driver()
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def fake():
    return Faker("en_US")


@pytest.fixture
def gen() -> DataGenerator:
    """Фабрика тестовых данных — доступна тесту напрямую."""
    return DataGenerator()


@pytest.fixture
def authorized_user(request, driver):
    """
    Тест начинается с уже авторизованного пользователя.

    Роль задаётся маркером: @pytest.mark.role("admin"). По умолчанию — user.
    """
    from interfaces.user.user import UserInterface

    marker = request.node.get_closest_marker("role")
    role = marker.args[0] if marker else "user"

    UserInterface(driver).login_page.login(role)
    return role
