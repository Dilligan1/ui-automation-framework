import allure

from base.base_page import BasePage
from config.urls import URLS
from pages.user_page.feed_page.components.feed_list import FeedList
from pages.user_page.feed_page.components.post_card import PostCard
from pages.user_page.profile_page.components.profile_header import ProfileHeader


class ProfilePage(BasePage):
    """Профиль пользователя: шапка с данными и лента его постов."""

    def __init__(self, driver):
        super().__init__(driver)
        self.header = ProfileHeader(driver)
        self.posts = PostCard(driver)
        self.list = FeedList(driver)

    @allure.step("Открытие профиля @{username}")
    def open_profile(self, username: str):
        self.driver.get(URLS.profile(username))
        self._wait_loading_page()
        return self

    @allure.step("Открытие списка подписчиков @{username}")
    def open_followers(self, username: str):
        self.driver.get(URLS.followers(username))
        self._wait_loading_page()
        return self

    @allure.step("Открытие списка подписок @{username}")
    def open_following(self, username: str):
        self.driver.get(URLS.following(username))
        self._wait_loading_page()
        return self

    def is_content_hidden(self) -> bool:
        """
        Скрыт ли контент приватного аккаунта от неподписанного пользователя.

        Отдельной заглушки с data-testid приложение не рисует, поэтому
        признак — отсутствие постов в профиле при ненулевом счётчике постов
        в шапке: посты есть, но не показаны.
        """
        return self.list.is_empty() and self.header.posts_count() > 0
