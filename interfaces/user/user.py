from pages.common_page.login_page.login_page import LoginPage
from pages.common_page.login_page.register_page import RegisterPage
from pages.user_page.bookmarks_page.bookmarks_page import BookmarksPage
from pages.user_page.feed_page.feed_page import FeedPage
from pages.user_page.messages_page.messages_page import MessagesPage
from pages.user_page.notifications_page.notifications_page import NotificationsPage
from pages.user_page.post_detail_page.post_detail_page import PostDetailPage
from pages.user_page.profile_page.profile_page import ProfilePage
from pages.user_page.search_page.search_page import SearchPage
from pages.user_page.settings_page.settings_page import SettingsPage


class UserInterface:
    """
    Все страницы, доступные обычному пользователю.

    Точка входа теста: self.user_page().feed.publish_post(...).
    Тест не импортирует классы страниц напрямую — он работает с ролью.
    """

    def __init__(self, driver):
        self.login_page = LoginPage(driver)
        self.register_page = RegisterPage(driver)
        self.feed = FeedPage(driver)
        self.post = PostDetailPage(driver)
        self.profile = ProfilePage(driver)
        self.messages = MessagesPage(driver)
        self.notifications = NotificationsPage(driver)
        self.bookmarks = BookmarksPage(driver)
        self.search = SearchPage(driver)
        self.settings = SettingsPage(driver)
