"""
Константы и границы приложения.

Тесты ссылаются на них, а не на магические числа: когда бэкенд меняет лимит,
правится одна строка, а не десяток ассертов.
"""

# Ограничения форм
POST_CONTENT_MAX = 2000        # символов в теле поста
BIO_MAX = 500                  # символов в описании профиля
COMMENT_DEPTH_MAX = 3          # уровней вложенности ответов
POST_EDIT_WINDOW_MINUTES = 15  # окно, в течение которого доступно редактирование

# Загрузка изображений
UPLOAD_MAX_BYTES = 5 * 1024 * 1024
UPLOAD_ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# Реакции на пост
REACTIONS = ("like", "love", "laugh", "wow", "sad", "angry")

# Роли в выпадающем списке админки
ROLES = ("user", "moderator", "admin")

# Тексты интерфейса, используемые в ассертах
TOAST_ROLE_UPDATED = "Role updated"
TOAST_USER_BANNED = "User banned"
TOAST_USER_ACTIVATED = "User activated"
