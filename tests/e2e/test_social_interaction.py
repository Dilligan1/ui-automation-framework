"""
E2E: взаимодействие двух пользователей.

Единственный сценарий, который требует двух браузеров одновременно: автор
публикует пост в одном окне, читатель реагирует в другом, автор видит
уведомление. Разбивать его на отдельные тесты нельзя — они потеряют смысл.
"""

import allure
import pytest

from base.base_test import BaseTest
from config.credentials import Usernames
from interfaces.user.user import UserInterface


@allure.epic("E2E")
@allure.feature("Социальное взаимодействие")
class TestSocialInteraction(BaseTest):

    @pytest.mark.e2e
    @pytest.mark.critical
    @pytest.mark.slow
    @allure.story("Пост → реакция → комментарий → уведомление")
    @allure.title("E2E: автор получает уведомление о реакции другого пользователя")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_post_reaction_notification_flow(self, second_driver, gen):
        """
        Шаги:
        1. Автор (user) публикует пост
        2. Читатель (media) в отдельном браузере открывает профиль автора,
           находит пост по его уникальному хэштегу и ставит лайк
        3. Читатель комментирует пост на его странице
        4. Автор видит обновлённые счётчики на своём посте
        5. Автор видит уведомление о взаимодействии
        6. Автор удаляет пост — стенд остаётся чистым

        Ожидаемый результат: счётчики и уведомления соответствуют действиям
        читателя, оба браузера работают с одним и тем же постом.
        """
        author = self.user_page()
        reader = UserInterface(second_driver)
        text = gen.post_content()

        with allure.step("1. Автор публикует пост"):
            author.login_page.login("user")
            author.feed.open()
            post_id = author.feed.publish_post(text)
            allure.attach(post_id, "post_id", allure.attachment_type.TEXT)

        try:
            with allure.step("2. Читатель находит пост в профиле автора и лайкает"):
                reader.login_page.login("media")
                reader.profile.open_profile(Usernames.USER)
                reader.profile.list.wait_row_with_text(text)
                reader.profile.posts.like(post_id)
                assert reader.profile.posts.likes_count(post_id) == 1, (
                    "Лайк читателя не отразился в карточке поста"
                )

            with allure.step("3. Читатель комментирует пост на его странице"):
                reader.profile.posts.open(post_id)
                reader.post.comments.add(gen.comment_text())

            with allure.step("4. Автор видит обновлённые счётчики"):
                author.feed.open()
                author.feed.list.wait_row_with_text(text)
                author.feed.waiter.wait_for(
                    lambda: author.feed.posts.likes_count(post_id) == 1,
                    message="Счётчик лайков у автора не обновился до 1",
                )
                assert author.feed.posts.comments_count(post_id) == 1, (
                    "Счётчик комментариев не обновился"
                )

            with allure.step("5. Автор видит уведомление о взаимодействии"):
                author.notifications.open()
                author.notifications.wait_any()
                assert not author.notifications.is_empty(), (
                    "Уведомлений о лайке и комментарии нет"
                )
        finally:
            with allure.step("6. Автор удаляет пост"):
                author.feed.open()
                author.feed.posts.delete(post_id)
