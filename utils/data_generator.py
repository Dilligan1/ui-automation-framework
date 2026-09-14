"""
DataGenerator — фабрика тестовых данных.
НИКОГДА не хардкодить тексты, email и имена в тестах: параллельный прогон
и повторный запуск на том же стенде должны быть безопасны.
"""

from typing import Any

from faker import Faker

fake = Faker("en_US")


class DataGenerator:
    """Factory for generating test data. NEVER hardcode values in tests."""

    # === Пользователи ===

    @staticmethod
    def user(**overrides) -> dict[str, Any]:
        """Данные для формы регистрации."""
        data = {
            "email": DataGenerator.unique_email(),
            "username": DataGenerator.unique_username(),
            "password": fake.password(length=12),
            "display_name": fake.name(),
        }
        data.update(overrides)
        return data

    @staticmethod
    def unique_email(prefix: str = "qa", domain: str = "example.com") -> str:
        return f"{prefix}+{fake.uuid4()[:8]}@{domain}"

    @staticmethod
    def unique_username(prefix: str = "qa") -> str:
        """Ограничение фронта: ^[a-zA-Z0-9_]+$, 3–30 символов."""
        return f"{prefix}_{fake.uuid4()[:8]}"

    # === Контент ===

    @staticmethod
    def post_content(words: int = 10, hashtag: bool = True) -> str:
        """
        Текст поста с уникальным хэштегом.

        Хэштег уникален намеренно: по нему тест находит собственный пост
        в общей ленте, не завязываясь на порядок элементов.
        """
        text = fake.sentence(nb_words=words)
        if not hashtag:
            return text
        return f"{text} #{DataGenerator.unique_hashtag()}"

    @staticmethod
    def unique_hashtag(prefix: str = "qa") -> str:
        return f"{prefix}{fake.random_number(digits=8, fix_len=True)}"

    @staticmethod
    def text_of_length(length: int) -> str:
        """Строка ровно заданной длины — для проверки границ (2000 символов)."""
        return fake.pystr(min_chars=length, max_chars=length)

    @staticmethod
    def comment_text() -> str:
        return fake.sentence(nb_words=7)

    @staticmethod
    def message_text() -> str:
        return fake.sentence(nb_words=6)

    @staticmethod
    def bio() -> str:
        """Описание профиля — до 500 символов."""
        return fake.sentence(nb_words=12)
