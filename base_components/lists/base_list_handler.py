import allure
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


class BaseListHandler(BasePage):
    """
    Базовый обработчик списков-коллекций приложения.

    Ленты, списки диалогов, уведомлений, таблица пользователей в админке — всё
    это однотипные коллекции карточек: контейнер, строки, поля внутри строки.
    Логика поиска строки, ожидания её появления/исчезновения и чтения полей
    общая, поэтому живёт здесь, а наследники объявляют только локаторы.

    Дочерний класс обязан переопределить:
        _ROW_LOCATOR — строка/карточка коллекции
    и может объявить:
        _CONTAINER_LOCATOR — корень коллекции,
        _FIELDS            — карту «имя поля → относительный локатор»,
                             чтобы читать содержимое строки по имени, а не по индексу.

    Контейнер по умолчанию — <main> страницы: приложение не размечает
    контейнеры списков атрибутом data-testid, размечены только сами строки
    (post-card-<id>, comment-<id>, admin-user-row-<id> и т.д.). Привязка к
    <main> устойчивее, чем к классам вёрстки, и не зависит от Tailwind-стилей.
    """

    _CONTAINER_LOCATOR = "//main"
    _ROW_LOCATOR = None

    # Карта полей строки: {"author": ".//*[starts-with(@data-testid,'post-author-')]"}
    _FIELDS: dict[str, str] = {}

    # === Контейнер и строки ===

    @property
    def _container(self) -> WebElement:
        return self.find(self._CONTAINER_LOCATOR)

    @allure.step("Ожидание готовности списка")
    def wait_list_ready(self, timeout: int | None = None):
        """
        Дождаться, пока список отрисован.

        Пустой список — валидное состояние (аккаунт без постов, пустые закладки),
        поэтому ждём именно контейнер, а не первую строку.
        """
        self._wait_loading_page(timeout)
        self.wait_for_visibility(self._CONTAINER_LOCATOR)
        return self

    def rows(self) -> list[WebElement]:
        """Все строки коллекции. Пустой список — не ошибка."""
        return self.find_all(self._ROW_LOCATOR, wait=False)

    def rows_count(self) -> int:
        return len(self.rows())

    def is_empty(self) -> bool:
        """
        Пуста ли коллекция.

        Отдельного пустого состояния с data-testid у приложения нет,
        поэтому признак пустоты — отсутствие строк.
        """
        return self.rows_count() == 0

    # === Поиск строки ===

    def row_by_id(self, entity_id: str) -> WebElement:
        """
        Строка по идентификатору сущности.

        Фронт проставляет data-testid вида `post-card-<id>`, `admin-user-row-<id>`,
        поэтому поиск по id — самый устойчивый способ: он не зависит ни от
        порядка элементов, ни от текста.
        """
        locator = ("css selector", f"[data-testid='{self._row_testid(entity_id)}']")
        try:
            return self.find(locator)
        except Exception:
            raise NoSuchElementException(
                f"Строка с id '{entity_id}' не найдена в списке.\n"
                f"Всего строк: {self.rows_count()}"
            )

    def _row_testid(self, entity_id: str) -> str:
        """Шаблон data-testid строки. Переопределяется наследником."""
        raise NotImplementedError(
            f"{type(self).__name__} не описал шаблон data-testid строки"
        )

    def row_by_text(self, text: str) -> WebElement:
        """
        Первая строка, содержащая указанный текст.

        Применяется, когда id заранее неизвестен — например, пост только что
        создан через UI и опознаётся по своему уникальному хэштегу.
        """
        for row in self.rows():
            try:
                if text in row.text:
                    return row
            except StaleElementReferenceException:
                continue  # React перерисовал список — пропускаем узел
        raise NoSuchElementException(
            f"Строка с текстом '{text}' не найдена.\n{self.dump_rows()}"
        )

    def has_row_with_text(self, text: str) -> bool:
        try:
            self.row_by_text(text)
            return True
        except NoSuchElementException:
            return False

    # === Чтение полей строки ===

    def field(self, row: WebElement, name: str) -> str:
        """
        Текст поля строки по имени из _FIELDS.

        Чтение по имени, а не по индексу: когда фронт добавляет колонку или
        меняет порядок элементов в карточке, тесты не разъезжаются.
        """
        if name not in self._FIELDS:
            raise KeyError(
                f"Поле '{name}' не описано в {type(self).__name__}._FIELDS. "
                f"Доступны: {list(self._FIELDS)}"
            )
        return row.find_element("xpath", self._FIELDS[name]).text.strip()

    def row_as_dict(self, row: WebElement) -> dict[str, str]:
        """Строка целиком как словарь — удобно для ассерта одним сравнением."""
        return {name: self.field(row, name) for name in self._FIELDS}

    # === Отладка ===

    def dump_rows(self, limit: int = 10) -> str:
        """
        Печатает первые строки списка и прикладывает их в отчёт.

        Нужен, когда тест не нашёл ожидаемую строку: из отчёта сразу видно,
        что в списке было на самом деле.
        """
        rows = self.rows()
        lines = [f"Всего строк: {len(rows)}"]
        for index, row in enumerate(rows[:limit]):
            try:
                text = " | ".join(row.text.split("\n"))
            except StaleElementReferenceException:
                text = "<элемент устарел>"
            lines.append(f"{index:>3}: {text}")
        dump = "\n".join(lines)
        allure.attach(dump, name="Содержимое списка", attachment_type=allure.attachment_type.TEXT)
        return dump

    # === Ожидания изменения списка ===

    @allure.step("Ожидание появления строки с текстом: {text}")
    def wait_row_with_text(self, text: str, timeout: int = 20):
        self.waiter.wait_for(
            lambda: self.has_row_with_text(text),
            timeout=timeout,
            message=f"Строка с текстом '{text}' не появилась в списке",
        )
        return self.row_by_text(text)

    @allure.step("Ожидание исчезновения строки с текстом: {text}")
    def wait_row_gone(self, text: str, timeout: int = 20):
        self.waiter.wait_for(
            lambda: not self.has_row_with_text(text),
            timeout=timeout,
            message=f"Строка с текстом '{text}' осталась в списке",
        )
