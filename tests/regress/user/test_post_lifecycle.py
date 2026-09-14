import allure
import pytest

from base.base_test import BaseTest
from data.test_data import POST_CONTENT_MAX


@allure.epic("Regression")
@allure.feature("Жизненный цикл поста")
class TestPostLifecycle(BaseTest):
    """Регрессия полного цикла поста: создание, правка, реакции, удаление."""

    @pytest.mark.regress
    @allure.story("Редактирование")
    @allure.title("Регресс: автор редактирует свой пост в окне редактирования")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_author_can_edit_own_post(self, gen):
        """
        Шаги:
        1. Опубликовать пост
        2. Убедиться, что кнопка редактирования доступна автору
        3. Удалить пост

        Ожидаемый результат: кнопка редактирования присутствует в карточке
        сразу после публикации (окно 15 минут ещё открыто).
        """
        feed = self.user_page().feed

        with allure.step("Авторизация и публикация поста"):
            self.user_page().login_page.login("user")
            feed.open()
            post_id = feed.publish_post(gen.post_content())

        try:
            with allure.step("Проверка доступности редактирования"):
                feed.posts.open_menu(post_id)
                assert feed.posts.is_edit_available(post_id), (
                    "Кнопка редактирования недоступна автору сразу после публикации"
                )
        finally:
            with allure.step("Удаление поста"):
                feed.posts.delete(post_id)

    @pytest.mark.regress
    @allure.story("Границы контента")
    @allure.title(f"Регресс: пост длиной ровно {POST_CONTENT_MAX} символов публикуется")
    @allure.severity(allure.severity_level.NORMAL)
    def test_max_length_post(self):
        """
        Граничное значение: ровно верхняя граница должна проходить.

        Шаги:
        1. Опубликовать пост длиной ровно POST_CONTENT_MAX
        2. Проверить, что карточка появилась
        3. Удалить пост
        """
        feed = self.user_page().feed
        text = self.gen_text()

        with allure.step("Авторизация и открытие ленты"):
            self.user_page().login_page.login("user")
            feed.open()

        with allure.step(f"Публикация поста длиной {POST_CONTENT_MAX} символов"):
            feed.composer.publish(text)
            row = feed.list.wait_row_with_text(text[:50])
            post_id = row.get_attribute("data-testid").replace("post-card-", "")

        try:
            with allure.step("Проверка публикации"):
                assert feed.posts.is_visible(post_id), (
                    "Пост длиной ровно по верхней границе не опубликовался"
                )
        finally:
            with allure.step("Удаление поста"):
                feed.posts.delete(post_id)

    def gen_text(self) -> str:
        """Текст ровно по верхней границе длины."""
        from utils.data_generator import DataGenerator

        return DataGenerator.text_of_length(POST_CONTENT_MAX)

    @pytest.mark.regress
    @allure.story("Закладки")
    @allure.title("Регресс: пост добавляется в закладки и виден в разделе")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bookmark_post(self, gen):
        """
        Шаги:
        1. Опубликовать пост
        2. Добавить его в закладки
        3. Открыть раздел закладок
        4. Убрать из закладок и удалить пост

        Ожидаемый результат: пост присутствует в списке закладок.
        """
        user = self.user_page()
        feed = user.feed
        text = gen.post_content()

        with allure.step("Авторизация и публикация поста"):
            user.login_page.login("user")
            feed.open()
            post_id = feed.publish_post(text)

        try:
            with allure.step("Добавление поста в закладки"):
                feed.posts.bookmark(post_id)

            with allure.step("Проверка поста в разделе закладок"):
                user.bookmarks.open()
                # Ждём именно свой пост: список подгружается запросом,
                # и проверка сразу после открытия страницы приходит слишком рано
                user.bookmarks.list.wait_row_with_text(text)
                assert user.bookmarks.posts.is_visible(post_id), (
                    f"Пост {post_id} не найден в закладках"
                )
        finally:
            with allure.step("Удаление поста"):
                feed.open()
                feed.posts.delete(post_id)
