"""
StorageManager — переиспользование авторизации между тестами.

Приложение хранит JWT в localStorage (access_token / refresh_token), поэтому
логин можно не прогонять через форму в каждом тесте: первый тест логинится,
токены сохраняются в файл, остальные тесты подставляют их в localStorage.

Файл сессии один на роль и общий для всех xdist-worker'ов: доступ к нему
сериализуется файловой блокировкой, поэтому за прогон происходит ровно один
вход на роль. Это не только быстрее — на стенде есть дефект BUG-001
(см. docs/known-issues.md): два одновременных входа одного пользователя
в пределах секунды приводят к 500 на стороне сервиса.
"""

import json
import os
from pathlib import Path

import allure
from selenium.webdriver.remote.webdriver import WebDriver

ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"


class StorageManager:
    def __init__(self, driver: WebDriver, relative_path: str):
        self.driver = driver
        self.path = Path(relative_path)

    @allure.step("Сохранение сессии в файл")
    def save(self) -> None:
        """Выгрузить токены из localStorage в файл."""
        tokens = {
            ACCESS_TOKEN_KEY: self.driver.execute_script(
                f"return window.localStorage.getItem('{ACCESS_TOKEN_KEY}');"
            ),
            REFRESH_TOKEN_KEY: self.driver.execute_script(
                f"return window.localStorage.getItem('{REFRESH_TOKEN_KEY}');"
            ),
        }
        if not tokens[ACCESS_TOKEN_KEY]:
            return  # сохранять нечего — логин не состоялся
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(tokens))

    @allure.step("Восстановление сессии из файла")
    def load(self) -> bool:
        """
        Подставить сохранённые токены в localStorage.

        Возвращает False, если файла нет или он пуст — вызывающий код делает
        обычный логин через форму.
        Важно: перед записью в localStorage должен быть открыт origin приложения,
        иначе браузер запишет данные в about:blank.
        """
        if not self.path.exists():
            return False
        try:
            tokens = json.loads(self.path.read_text())
        except (ValueError, OSError):
            return False
        if not tokens.get(ACCESS_TOKEN_KEY):
            return False

        for key, value in tokens.items():
            if value:
                self.driver.execute_script(
                    "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
                )
        return True

    def clear(self) -> None:
        """Сбросить сессию в браузере (не трогая файл) — для тестов на разлогин."""
        self.driver.execute_script("window.localStorage.clear();")
