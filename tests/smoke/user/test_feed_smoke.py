import allure
import pytest

from base.base_test import BaseTest


@allure.epic("Smoke")
@allure.feature("Лента")
class TestFeedSmoke(BaseTest):
    """Smoke-тесты публикации и отображения постов."""

    @pytest.mark.smoke
    @pytest.mark.critical
    @allure.story("Публикация поста")
    @allure.title("Smoke: пост публикуется и появляется в ленте")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_publish_post(self, gen):
        """
        Шаги:
        1. Войти под ролью user
        2. Опубликовать пост с уникальным текстом
        3. Проверить, что пост появился в ленте
        4. Удалить пост — стенд остаётся чистым

        Ожидаемый результат: карточка поста отрисована, текст совпадает
        с отправленным, счётчики обнулены.
        """
        feed = self.user_page().feed
        text = gen.post_content()

        with allure.step("Авторизация и открытие ленты"):
            self.user_page().login_page.login("user")
            feed.open()

        with allure.step("Публикация поста"):
            post_id = feed.publish_post(text)
            allure.attach(post_id, "post_id", allure.attachment_type.TEXT)

        try:
            with allure.step("Проверка поста в ленте"):
                assert feed.posts.is_visible(post_id), (
                    f"Карточка поста {post_id} не отрисована в ленте"
                )
                assert text in feed.posts.content(post_id), (
                    "Текст опубликованного поста не совпадает с отправленным"
                )
                assert feed.posts.likes_count(post_id) == 0, (
                    "У нового поста не должно быть лайков"
                )
        finally:
            with allure.step("Удаление поста"):
                feed.posts.delete(post_id)

    @pytest.mark.smoke
    @allure.story("Публикация поста")
    @allure.title("Smoke: пустой пост опубликовать нельзя")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_post_cannot_be_published(self):
        """
        Шаги:
        1. Войти и открыть ленту
        2. Не вводя текст, проверить состояние кнопки отправки

        Ожидаемый результат: кнопка публикации неактивна.
        """
        feed = self.user_page().feed

        with allure.step("Авторизация и открытие ленты"):
            self.user_page().login_page.login("user")
            feed.open()

        with allure.step("Проверка кнопки публикации при пустой форме"):
            assert not feed.composer.is_submit_enabled(), (
                "Кнопка публикации активна при пустом тексте поста"
            )

    @pytest.mark.smoke
    @allure.story("Взаимодействие с постом")
    @allure.title("Smoke: лайк поста увеличивает счётчик")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_like_post(self, gen):
        """
        Шаги:
        1. Опубликовать пост
        2. Поставить лайк
        3. Проверить счётчик
        4. Удалить пост

        Ожидаемый результат: счётчик лайков равен 1.
        """
        feed = self.user_page().feed
        text = gen.post_content()

        with allure.step("Авторизация и публикация поста"):
            self.user_page().login_page.login("user")
            feed.open()
            post_id = feed.publish_post(text)

        try:
            with allure.step("Лайк поста"):
                feed.posts.like(post_id)

            with allure.step("Проверка счётчика лайков"):
                self.user_page().feed.waiter.wait_for(
                    lambda: feed.posts.likes_count(post_id) == 1,
                    message="Счётчик лайков не увеличился до 1",
                )
        finally:
            with allure.step("Удаление поста"):
                feed.posts.delete(post_id)
