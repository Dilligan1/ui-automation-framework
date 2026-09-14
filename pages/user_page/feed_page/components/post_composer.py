import allure

from base.base_page import BasePage


class PostComposer(BasePage):
    """
    Форма публикации поста в ленте.

    Вынесена в отдельный компонент: она встречается на нескольких страницах
    и содержит собственную логику работы с вложением.
    """

    _COMPOSER = "[data-testid='post-composer']"
    _INPUT = "[data-testid='post-composer-input']"
    _SUBMIT = "[data-testid='post-composer-submit']"
    _IMAGE_BUTTON = "[data-testid='post-composer-image-btn']"
    _FILE_INPUT = "[data-testid='post-composer-file-input']"
    _IMAGE_PREVIEW = "[data-testid='post-composer-image-preview']"
    _IMAGE_REMOVE = "[data-testid='post-composer-image-remove']"

    @allure.step("Ввод текста поста")
    def type_content(self, text: str):
        self.fill(self._INPUT, text)
        return self

    @allure.step("Прикрепление изображения: {file_path}")
    def attach_image(self, file_path: str):
        """
        Прикрепить изображение.

        Сам input[type=file] скрыт за кастомной кнопкой, поэтому файл
        передаётся send_keys напрямую в input, без клика по кнопке.
        """
        self.upload_file(self._FILE_INPUT, file_path)
        self.wait_for_visibility(self._IMAGE_PREVIEW)
        return self

    @allure.step("Удаление прикреплённого изображения")
    def remove_image(self):
        self.click(self._IMAGE_REMOVE)
        self.wait_for_invisibility(self._IMAGE_PREVIEW)
        return self

    @allure.step("Отправка поста")
    def submit(self):
        self.click(self._SUBMIT)
        self._wait_loading_page()
        return self

    @allure.step("Публикация поста")
    def publish(self, text: str, image_path: str | None = None):
        """Полный сценарий публикации: текст → (вложение) → отправка."""
        self.type_content(text)
        if image_path:
            self.attach_image(image_path)
        self.submit()
        return self

    def is_submit_enabled(self) -> bool:
        """Активна ли кнопка отправки — пустой пост публиковать нельзя."""
        return self.find(self._SUBMIT).is_enabled()

    def is_image_attached(self) -> bool:
        return self.is_element_visible(self._IMAGE_PREVIEW)
