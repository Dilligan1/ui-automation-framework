# UI Automation Framework

[![UI tests](https://github.com/Dilligan1/ui-automation-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/Dilligan1/ui-automation-framework/actions/workflows/tests.yml)
[![Allure report](https://img.shields.io/badge/Allure-отчёт-blue)](https://dilligan1.github.io/ui-automation-framework/)

Фреймворк UI-автотестов на **Python + Selenium + pytest**, построенный по Page Object Model с разделением на интерфейсы ролей, компоненты и флоу.

Тестируемая система (SUT) — [QA Automation Sandbox](https://github.com/manikosto/qa-automation-sandbox): социальная сеть на React + FastAPI с ролевым доступом, лентой, комментариями, загрузкой изображений и админ-панелью. Поднимается локально одной командой — прогон не зависит от доступности чужих демо-стендов.

> API-автотесты на ту же систему — в репозитории [api-automation-framework](https://github.com/Dilligan1/api-automation-framework).

---

## Что демонстрирует проект

| Задача | Решение в коде |
|---|---|
| Локаторы без визуального шума | `metaclasses/meta_locators.py` — метакласс превращает строку `"[data-testid='x']"` в кортеж Selenium автоматически |
| Ни одного `time.sleep` | `utils/waiter.py` — ожидания по условию, включая ожидание «тишины» SPA после навигации |
| Устойчивость к перерисовке React | `utils/ui_helper.py` — клик переживает `StaleElementReference` и перехват клика тостом |
| Один логин на роль за прогон | `utils/storage_manager.py` + `FileLock` — JWT сохраняется из `localStorage` в файл и переиспользуется всеми worker'ами, включая параллельный прогон |
| Работа со списками без привязки к позиции | `base_components/lists/base_list_handler.py` — поиск строки по id или тексту, чтение полей по имени, дамп содержимого в отчёт при падении |
| Тест на языке роли | `interfaces/{admin,moderator,user}` — `self.user_page().feed.publish_post(...)`, без импорта классов страниц в тест |
| Разбор упавшего теста | `conftest.py` — скриншот, URL и HTML страницы прикрепляются в Allure автоматически |
| Два уровня параллелизма | `runner.py` — наборы тестов в `ProcessPoolExecutor`, тесты внутри набора в `pytest-xdist` |

## Архитектура

```
conftest.py                  хуки: скриншот при падении, environment.properties
runner.py                    параллельный запуск наборов (процессы + xdist)
metaclasses/meta_locators.py преобразование строковых локаторов
base/
  base_page.py               общий предок страниц: open, тосты, каркас приложения
  base_test.py               общий предок тестов: доступ к ролям и меню
base_components/
  menu/navbar.py             навигация (основная + админская)
  lists/base_list_handler.py базовый обработчик коллекций
interfaces/
  admin | moderator | user   наборы страниц, доступные роли
pages/
  common_page/login_page/    вход и регистрация
  user_page/<page>/          страница + components/ для сложных блоков
  admin_page/<page>/         админ-панель
  flows/                     многошаговые сценарии между страницами
utils/
  ui_helper.py               обёртка над WebDriver
  waiter.py                  ожидания по условию
  storage_manager.py         переиспользование сессии
  data_generator.py          фабрика тестовых данных
  db_helper.py               подготовка состояний через БД
config/                      URL, учётные данные, параметры БД по стендам
fixtures/ui_fixtures.py      драйвер, второй браузер, авторизованный пользователь
tests/
  smoke/{admin,user}         критичный функционал
  regress/user               регрессия
  e2e                        сквозные сценарии, в том числе в двух браузерах
```

Цепочка наследования: `UIHelper → BasePage → конкретная страница`, а списки — `BasePage → BaseListHandler → конкретный список`. Тест не вызывает Selenium напрямую ни в одной точке.

## Быстрый старт

```bash
# 1. Поднять тестируемое приложение
git clone https://github.com/manikosto/qa-automation-sandbox.git
docker compose -f qa-automation-sandbox/docker-compose.yml up -d

# 2. Настроить окружение
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # заполнить учётные данные seed-пользователей

# 3. Прогон
pytest -m smoke
```

### Полезные команды

```bash
pytest -m smoke                   # критичный функционал
pytest -m regress                 # регрессия
pytest -m e2e                     # сквозные сценарии
pytest -n 3                       # параллельно, 3 браузера
HEADLESS=true pytest -m smoke     # без окна браузера
python runner.py                  # smoke и regress одновременно, разными процессами

docker compose run --rm smoke     # прогон в контейнере
docker compose run --rm report    # HTML-отчёт Allure
```

## Отчётность

Каждый шаг страницы и теста размечен `allure.step`. При падении в отчёт автоматически попадают скриншот, URL и HTML страницы — этого достаточно, чтобы разобрать упавший тест, не воспроизводя его руками. В CI отчёт публикуется на GitHub Pages — [посмотреть последний прогон](https://dilligan1.github.io/ui-automation-framework/).

## Документация

- [docs/architecture.md](docs/architecture.md) — слои, наследование, границы ответственности
- [docs/ui-map.md](docs/ui-map.md) — карта страниц и компонентов
- [docs/test-plan.md](docs/test-plan.md) — уровни тестирования и приоритеты покрытия
- [docs/known-issues.md](docs/known-issues.md) — найденный дефект приложения и особенность Chrome, из-за которой падали клики
- [CONTRIBUTING.md](CONTRIBUTING.md) — правила добавления страниц и тестов
