from base.base_page import BasePage
from config.urls import URLS
from pages.user_page.feed_page.components.feed_list import FeedList
from pages.user_page.feed_page.components.post_card import PostCard


class BookmarksPage(BasePage):
    """Сохранённые посты. Отрисовываются теми же карточками, что и лента."""

    _PAGE_URL = URLS.BOOKMARKS

    def __init__(self, driver):
        super().__init__(driver)
        self.posts = PostCard(driver)
        self.list = FeedList(driver)

    def is_empty(self) -> bool:
        return self.list.is_empty()
