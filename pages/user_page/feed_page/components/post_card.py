import allure
from selenium.webdriver.remote.webelement import WebElement

from base.base_page import BasePage


class PostCard(BasePage):
    """
    Карточка поста — самый переиспользуемый компонент приложения.

    Встречается в ленте, в профиле, в закладках, на странице поста и в админке.
    Все действия параметризованы id поста, поэтому компонент работает в любом
    из этих контекстов, а не только в ленте.

    ВАЖНО: в data-testid лежит СОКРАЩЁННЫЙ идентификатор, а не UUID —
    фронт обрезает его до последних 12 hex-символов и убирает ведущие нули
    (`10000000-0000-0000-0000-000000000025` → `25`). Поэтому значение,
    полученное из карточки, годится только для адресации элементов UI,
    но не для сборки URL вида /post/<uuid> и не для запросов к API.
    Чтобы открыть пост, используйте open() — переход по самой карточке.
    """

    def _testid(self, prefix: str, post_id: str) -> tuple[str, str]:
        return ("css selector", f"[data-testid='{prefix}-{post_id}']")

    # === Элементы карточки ===

    def card(self, post_id: str) -> WebElement:
        return self.find(self._testid("post-card", post_id))

    def content(self, post_id: str) -> str:
        return self.get_text(self._testid("post-content", post_id))

    def author(self, post_id: str) -> str:
        return self.get_text(self._testid("post-author", post_id))

    def likes_count(self, post_id: str) -> int:
        return self._count(self._testid("post-likes-count", post_id))

    def comments_count(self, post_id: str) -> int:
        return self._count(self._testid("post-comments-count", post_id))

    def _count(self, locator) -> int:
        """Счётчик в карточке. Пустой или отсутствующий счётчик — это 0."""
        if not self.is_element_visible(locator):
            return 0
        text = self.get_text(locator)
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits or 0)

    # === Действия ===

    @allure.step("Лайк поста {post_id}")
    def like(self, post_id: str):
        """
        Поставить реакцию и дождаться, пока счётчик её отразит.

        Ждать обязательно: после реакции приложение перезагружает список,
        и следующее действие по этой же карточке иначе попадёт в узел,
        который React уже заменил.
        """
        before = self.likes_count(post_id)
        self.click_until(
            self._testid("post-like-btn", post_id),
            lambda: self.likes_count(post_id) != before,
            message=f"Счётчик лайков поста {post_id} не изменился после клика",
        )
        return self

    @allure.step("Добавление поста {post_id} в закладки")
    def bookmark(self, post_id: str):
        self.click(self._testid("post-bookmark-btn", post_id))
        return self

    @allure.step("Открытие комментариев поста {post_id}")
    def open_comments(self, post_id: str):
        """Комментарии живут на странице поста — это тот же переход, что и open()."""
        return self.open(post_id)

    @allure.step("Репост поста {post_id}")
    def repost(self, post_id: str):
        self.click(self._testid("post-repost-btn", post_id))
        return self

    @allure.step("Открытие поста {post_id}")
    def open(self, post_id: str):
        """
        Перейти на страницу поста.

        Ссылкой на страницу поста служит кнопка комментариев — сам текст поста
        в карточке кликабельным не является. Переходим кликом, а не по URL:
        в data-testid лежит сокращённый id, из которого адрес /post/<uuid>
        не собрать.

        Клик с проверкой адреса: список мог перерисоваться после предыдущего
        действия, и одиночный клик тогда уходит в заменённый узел.
        """
        self.click_until(
            self._testid("post-comment-btn", post_id),
            lambda: "/post/" in self.driver.current_url,
            message=f"Переход на страницу поста {post_id} не состоялся",
        )
        self._wait_loading_page()
        return self

    @allure.step("Открытие меню поста {post_id}")
    def open_menu(self, post_id: str):
        """
        Раскрыть меню карточки и дождаться его пунктов.

        Идемпотентно: кнопка меню — переключатель, поэтому повторный вызов
        на уже раскрытом меню закрыл бы его, и следующий шаг теста упал бы
        на пропавшем пункте.
        """
        if self.is_menu_open(post_id):
            return self
        self.click_until(
            self._testid("post-menu-btn", post_id),
            lambda: self.is_menu_open(post_id),
            message=f"Меню поста {post_id} не раскрылось",
        )
        return self

    def is_menu_open(self, post_id: str) -> bool:
        """Раскрыто ли меню карточки — пункты меню рендерятся только открытыми."""
        return self.is_element_visible(self._testid("post-delete-btn", post_id))

    @allure.step("Редактирование поста {post_id}")
    def edit(self, post_id: str):
        """
        Открыть редактирование. Кнопка доступна автору и только в течение
        15 минут после публикации — за пределами окна её в DOM нет.
        """
        self.open_menu(post_id)
        self.click(self._testid("post-edit-btn", post_id))
        return self

    @allure.step("Удаление поста {post_id}")
    def delete(self, post_id: str):
        """
        Удалить пост.

        Приложение спрашивает подтверждение нативным window.confirm —
        его нужно принять, иначе удаление не произойдёт, а следующее
        действие упадёт на незакрытом диалоге.
        """
        self.open_menu(post_id)
        self.click(self._testid("post-delete-btn", post_id))
        self.accept_alert()
        self.waiter.wait_for(
            lambda: not self.is_visible(post_id),
            message=f"Карточка поста {post_id} осталась в списке после удаления",
        )
        return self

    # === Состояние ===

    def is_visible(self, post_id: str) -> bool:
        return self.is_element_visible(self._testid("post-card", post_id))

    def is_edit_available(self, post_id: str) -> bool:
        """
        Доступно ли редактирование. Проверяется при раскрытом меню карточки:
        у чужого поста и за пределами 15-минутного окна пункта в меню нет.
        """
        return self.is_element_visible(self._testid("post-edit-btn", post_id))

    def post_id_by_text(self, text: str) -> str:
        """
        Найти идентификатор карточки поста по его тексту.

        Пост, созданный через UI, своего id не возвращает — он достаётся из
        data-testid карточки, найденной по уникальному хэштегу. Возвращается
        сокращённый id (см. докстринг класса): для адресации элементов UI.
        """
        cards = self.find_all("[data-testid^='post-card-']", wait=True)
        for card in cards:
            if text in card.text:
                return card.get_attribute("data-testid").replace("post-card-", "")
        raise AssertionError(f"Пост с текстом '{text}' не найден в списке карточек")
