# Как добавлять код в проект

## Новая страница

1. Создать `pages/<role>_page/<page_name>/<page_name>.py`, унаследовать от `BasePage`.
2. Объявить `_PAGE_URL` и локаторы — строками, без кортежей: их преобразует `MetaLocator`.
3. Сложные блоки вынести в `components/` рядом со страницей.
4. Добавить страницу в интерфейс соответствующей роли (`interfaces/`).

```python
class BookmarksPage(BasePage):
    _PAGE_URL = URLS.BOOKMARKS
    _EMPTY_STATE = "[data-testid='empty-state']"

    def __init__(self, driver):
        super().__init__(driver)
        self.posts = PostCard(driver)
```

## Новый список

Унаследовать от `BaseListHandler`, объявить контейнер, строку, шаблон `data-testid` строки и — при необходимости — карту полей:

```python
class FeedList(BaseListHandler):
    _CONTAINER_LOCATOR = "[data-testid='feed-list']"
    _ROW_LOCATOR = "[data-testid^='post-card-']"
    _FIELDS = {"author": ".//*[starts-with(@data-testid,'post-author-')]"}

    def _row_testid(self, entity_id: str) -> str:
        return f"post-card-{entity_id}"
```

Поиск строки, ожидания её появления и исчезновения, чтение полей и дамп содержимого достаются от базового класса.

## Новый тест

- Класс наследуется от `BaseTest`, метод начинается с `test_`.
- Разметка обязательна: `@allure.epic`, `@allure.feature`, `@allure.story`, `@allure.title`, `@allure.severity` и маркер уровня.
- Докстринг содержит шаги и ожидаемый результат.
- Данные — только из `DataGenerator`.
- Созданные сущности удаляются в `finally`.

```python
@pytest.mark.smoke
@allure.title("Smoke: пост публикуется и появляется в ленте")
def test_publish_post(self, gen):
    """
    Шаги:
    1. ...
    Ожидаемый результат: ...
    """
```

## Чего делать нельзя

| Запрещено | Почему | Что вместо |
|---|---|---|
| `time.sleep()` | Либо замедляет прогон, либо всё равно флакует | `Waiter` / ожидания в `UIHelper` |
| Локаторы в тесте | Тест ломается от любой правки вёрстки | Локатор живёт в странице или компоненте |
| `driver.find_element` в тесте | Обход всех ожиданий и обработки ошибок | Методы `UIHelper` |
| Клик без проверки результата в перерисовываемом списке | React заменяет узел, клик уходит в никуда, падение случается позже и в другом месте | `UIHelper.click_until` |
| Хардкод текстов, email, паролей | Повторный и параллельный прогон перестают быть безопасными | `DataGenerator`, `.env` |
| Обращение к `reset-database-btn` | Уничтожает данные всех пользователей и роняет параллельный прогон | Сброс из `conftest` до старта worker'ов |
| Зависимость между тестами | Рушится при параллельном прогоне и при запуске одного теста | Каждый тест готовит своё состояние |
