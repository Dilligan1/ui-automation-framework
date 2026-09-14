# Карта интерфейса

## Страницы и их классы

| Раздел | URL | Класс | Компоненты |
|---|---|---|---|
| Вход | `/login` | `LoginPage` | — |
| Регистрация | `/register` | `RegisterPage` | — |
| Лента | `/` | `FeedPage` | `PostComposer`, `PostCard`, `FeedList` |
| Пост | `/post/:id` | `PostDetailPage` | `PostCard`, `CommentSection` |
| Профиль | `/profile/:username` | `ProfilePage` | `ProfileHeader`, `FeedList`, `PostCard` |
| Сообщения | `/messages` | `MessagesPage` | `ConversationList`, `MessageThread` |
| Уведомления | `/notifications` | `NotificationsPage` | сама является списком |
| Закладки | `/bookmarks` | `BookmarksPage` | `FeedList`, `PostCard` |
| Поиск | `/search` | `SearchPage` | — |
| Настройки | `/settings` | `SettingsPage` | — |
| Дашборд админа | `/admin` | `AdminDashboardPage` | — |
| Пользователи | `/admin/users` | `AdminUsersPage` | `AdminUsersList` |
| Модерация | `/admin/content` | `AdminContentPage` | `AdminPostsList` |

## Доступ по ролям

| Раздел | user | moderator | admin |
|---|:---:|:---:|:---:|
| Лента, профиль, сообщения, закладки | ✅ | ✅ | ✅ |
| Дашборд администратора | ❌ | ✅ | ✅ |
| Модерация контента | ❌ | ✅ | ✅ |
| Управление пользователями (роли, бан) | ❌ | ❌ | ✅ |

Отсутствие раздела у роли — такая же проверка, как и его наличие: `test_admin_menu_hidden_for_user`.

## Соглашение по локаторам

Приложение размечено атрибутами `data-testid`, поэтому локаторы не завязаны ни на классы стилей, ни на структуру вёрстки:

| Шаблон | Пример | Где используется |
|---|---|---|
| Статический | `auth-login-btn` | кнопки, поля форм, контейнеры |
| С идентификатором | `post-card-<id>` | строки коллекций |
| Действие над сущностью | `post-like-btn-<id>` | кнопки внутри строки |

Элементы, у которых `data-testid` нет (вкладки, ссылки навигации), адресуются XPath по тексту или по `href` — это оговорено в коде комментарием.

## Как найти id сущности, созданной через UI

Интерфейс не показывает идентификаторы. Когда тест создал пост или комментарий и должен работать с ним дальше, id достаётся из `data-testid` карточки, найденной по уникальному тексту:

```python
text = gen.post_content()          # текст содержит уникальный хэштег
post_id = feed.publish_post(text)  # внутри: найти карточку по тексту → достать id
```

Именно поэтому `DataGenerator.post_content()` всегда добавляет к тексту уникальный хэштег.
