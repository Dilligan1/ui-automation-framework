from base.base_page import BasePage
from config.urls import URLS
from pages.admin_page.admin_content_page.components.admin_posts_list import AdminPostsList


class AdminContentPage(BasePage):
    """Модерация контента: просмотр и удаление постов."""

    _PAGE_URL = URLS.ADMIN_CONTENT

    def __init__(self, driver):
        super().__init__(driver)
        self.posts = AdminPostsList(driver)
