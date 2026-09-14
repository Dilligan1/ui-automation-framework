import allure

from base.base_page import BasePage
from config.urls import URLS


class SettingsPage(BasePage):
    """
    Настройки аккаунта.

    Из всей страницы приложение размечает data-testid только переключатель
    языка и кнопку сброса стенда. Форма профиля разметки не имеет, поэтому
    её поля здесь не объявлены: выдуманный локатор хуже отсутствующего —
    он падает не там, где сломалось приложение.

    Кнопка сброса стенда намеренно НЕ используется в тестах: она уничтожает
    данные всех пользователей и уронила бы параллельный прогон. Сброс делается
    из conftest до старта worker'ов.
    """

    _PAGE_URL = URLS.SETTINGS

    _LANG_EN = "[data-testid='lang-en']"
    _LANG_RU = "[data-testid='lang-ru']"
    _RESET_DATABASE_BUTTON = "[data-testid='reset-database-btn']"

    @allure.step("Переключение языка интерфейса на {lang}")
    def switch_language(self, lang: str = "en"):
        self.click(self._LANG_EN if lang == "en" else self._LANG_RU)
        self._wait_loading_page()
        return self

    def is_reset_available(self) -> bool:
        """Доступна ли кнопка сброса стенда (проверяется, но не нажимается)."""
        return self.is_element_visible(self._RESET_DATABASE_BUTTON)
