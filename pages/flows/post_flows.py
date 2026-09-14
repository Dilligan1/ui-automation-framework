"""
Флоу — многошаговые сценарии, которые повторяются в разных тестах.

Флоу живёт отдельно от страниц: страница знает про свои элементы, флоу — про
последовательность действий между страницами. Так сценарий «опубликовать пост,
прокомментировать и убедиться в счётчиках» не дублируется в каждом тесте.
"""

import allure

from interfaces.user.user import UserInterface
from utils.data_generator import DataGenerator


class PostFlows:
    def __init__(self, driver):
        self.driver = driver
        self.user = UserInterface(driver)
        self.gen = DataGenerator()

    @allure.step("Флоу: публикация поста")
    def publish_post(self, text: str | None = None) -> tuple[str, str]:
        """
        Опубликовать пост в ленте.

        Возвращает (post_id, text): текст нужен тесту, чтобы найти пост
        в других разделах, id — чтобы адресно кликать по его кнопкам.
        """
        text = text or self.gen.post_content()
        self.user.feed.open()
        post_id = self.user.feed.publish_post(text)
        return post_id, text

    @allure.step("Флоу: публикация поста с изображением")
    def publish_post_with_image(self, image_path: str, text: str | None = None) -> tuple[str, str]:
        text = text or self.gen.post_content()
        self.user.feed.open()
        post_id = self.user.feed.publish_post(text, image_path=image_path)
        return post_id, text

    @allure.step("Флоу: комментирование поста")
    def comment_post(self, post_id: str, text: str | None = None) -> str:
        text = text or self.gen.comment_text()
        self.user.post.open_post(post_id)
        self.user.post.comments.add(text)
        return text

    @allure.step("Флоу: удаление поста")
    def delete_post(self, post_id: str):
        """Убрать за собой. Вызывается в teardown теста, а не в конце шагов."""
        self.user.feed.open()
        self.user.feed.posts.delete(post_id)
