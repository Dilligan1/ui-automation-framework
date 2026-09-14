import allure

from base.base_page import BasePage
from config.urls import URLS
from pages.user_page.feed_page.components.feed_list import FeedList
from pages.user_page.feed_page.components.post_card import PostCard
from pages.user_page.feed_page.components.post_composer import PostComposer


class FeedPage(BasePage):
    """
    Главная страница — лента подписок.

    Страница собирает компоненты: форму публикации, список постов и карточку
    поста. Сама отвечает только за открытие и за сценарии уровня страницы.
    """

    _PAGE_URL = URLS.FEED

    _TAB_FOR_YOU = "//button[normalize-space()='For you']"
    _TAB_FOLLOWING = "//button[normalize-space()='Following']"

    def __init__(self, driver):
        super().__init__(driver)
        self.composer = PostComposer(driver)
        self.posts = PostCard(driver)
        self.list = FeedList(driver)

    @allure.step("Публикация поста через ленту")
    def publish_post(self, text: str, image_path: str | None = None) -> str:
        """
        Опубликовать пост и вернуть его id.

        Текст должен содержать уникальный хэштег (см. DataGenerator.post_content) —
        по нему пост опознаётся в общей ленте.
        """
        self.composer.publish(text, image_path)
        self.list.wait_row_with_text(text)
        return self.posts.post_id_by_text(text)

    def is_feed_empty(self) -> bool:
        """Пустая лента. Отдельной заглушки с data-testid у приложения нет."""
        return self.list.is_empty()
