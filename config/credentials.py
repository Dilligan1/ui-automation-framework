import os

from dotenv import load_dotenv

load_dotenv()


class Credentials:
    """
    Учётные данные seed-пользователей по стендам.

    Роли приложения: admin, moderator, user. Дополнительно выделены
    состояния обычного пользователя, у которых своё поведение в UI:
    приватный аккаунт, пустой аккаунт, забаненный.
    """

    STAGE = os.getenv("STAGE", "local")

    @staticmethod
    def _pair(role: str) -> tuple[str | None, str | None]:
        prefix = Credentials.STAGE.upper()
        return (
            os.getenv(f"{prefix}_{role}_EMAIL"),
            os.getenv(f"{prefix}_{role}_PASSWORD"),
        )

    @staticmethod
    def get(role: str) -> tuple[str, str]:
        """
        Пара (email, password) для роли в текущем стенде.

        role: admin | moderator | user | private | empty | banned
        """
        email, password = Credentials._pair(role.upper())
        if not email or not password:
            raise ValueError(
                f"Не найдены учётные данные для роли '{role}' "
                f"(стенд: {Credentials.STAGE}). Проверьте .env — см. .env.example"
            )
        return email, password


class Usernames:
    """Хэндлы seed-пользователей — нужны для URL профилей."""

    ADMIN = os.getenv("USERNAME_ADMIN", "admin")
    MODERATOR = os.getenv("USERNAME_MODERATOR", "moderator")
    USER = os.getenv("USERNAME_USER", "alice_dev")
    MEDIA = os.getenv("USERNAME_MEDIA", "bob_photo")
    PRIVATE = os.getenv("USERNAME_PRIVATE", "dave_quiet")
    EMPTY = os.getenv("USERNAME_EMPTY", "eve_new")
    BANNED = os.getenv("USERNAME_BANNED", "frank_banned")
