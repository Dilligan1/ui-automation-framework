import os
import sys
from pathlib import Path

import allure
import pytest

from fixtures.ui_fixtures import *  # noqa: F401,F403 — фикстуры регистрируются импортом


def pytest_configure(config: pytest.Config) -> None:
    """
    Подготовка прогона. Выполняется только мастер-процессом (не xdist worker'ами).

    Опциональный сброс стенда: POST /api/reset возвращает песочницу к seed-данным.
    Вызывается до старта worker'ов — из теста этого делать нельзя, иначе
    параллельные тесты потеряют свои данные.
    """
    if hasattr(config, "workerinput"):
        return

    if os.getenv("RESET_BEFORE_RUN", "false").lower() == "true":
        import requests

        from config.urls import URLS

        requests.post(URLS.API_RESET, timeout=60)


def pytest_sessionfinish(session, exitstatus):
    """Сформировать environment.properties для отчёта Allure."""
    allure_dir = session.config.getoption("--alluredir", default=None)
    if not allure_dir:
        return

    env_file = Path(allure_dir) / "environment.properties"
    env_file.write_text(
        f"Environment={os.getenv('STAGE', 'local')}\n"
        f"Headless={os.getenv('HEADLESS', 'false')}\n"
        f"Browser=chrome\n"
        f"Python={sys.version.split()[0]}\n"
        f"pytest={pytest.__version__}\n"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Скриншот и URL страницы при падении теста.

    Без этого разбор упавшего UI-теста сводится к догадкам: по одному только
    стектрейсу не видно, что было на экране в момент падения.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = getattr(getattr(item, "cls", None), "driver", None)
    if driver is None:
        return

    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"Скриншот падения: {item.name}",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            driver.current_url, name="URL страницы", attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(
            driver.page_source, name="HTML страницы", attachment_type=allure.attachment_type.HTML
        )
    except Exception:
        pass  # сбор диагностики не должен ломать отчёт
