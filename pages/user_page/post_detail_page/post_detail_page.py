import allure

from base.base_page import BasePage
from config.urls import URLS
from pages.user_page.feed_page.components.post_card import PostCard
from pages.user_page.post_detail_page.components.comment_section import CommentSection


class PostDetailPage(BasePage):
    """Страница отдельного поста: карточка поста и блок комментариев."""

    def __init__(self, driver):
        super().__init__(driver)
        self.post = PostCard(driver)
        self.comments = CommentSection(driver)

    @allure.step("Открытие страницы поста по UUID")
    def open_post(self, post_uuid: str):
        """
        Открыть пост по прямому адресу.

        Принимает ПОЛНЫЙ UUID — такой есть, когда пост подготовлен через API
        или БД. Идентификатор из data-testid карточки сюда не подходит: он
        сокращён (см. PostCard). Для перехода из списка используйте
        open_from_card().
        """
        self.driver.get(URLS.post(post_uuid))
        self._wait_loading_page()
        return self

    @allure.step("Переход на страницу поста {post_id} из списка")
    def open_from_card(self, post_id: str):
        """Открыть пост кликом по его карточке в текущем списке."""
        self.post.open(post_id)
        return self
