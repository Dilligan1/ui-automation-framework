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

## Как запустить

### Что понадобится

| | |
|---|---|
| Python | 3.11 или новее (`python3 --version`) |
| Docker | с плагином Compose (`docker compose version`) — нужен, чтобы поднять тестируемое приложение |
| Google Chrome | любой свежей версии. Драйвер скачивать не нужно: Selenium Manager подберёт его сам |
| Git | `git --version` |

### 1. Поднять тестируемое приложение

Тесты работают с [QA Automation Sandbox](https://github.com/manikosto/qa-automation-sandbox) — она поднимается локально, внешний стенд не нужен.

```bash
git clone https://github.com/manikosto/qa-automation-sandbox.git
docker compose -f qa-automation-sandbox/docker-compose.yml up -d --build
```

Первая сборка занимает 2–4 минуты. Готовность проверяется так:

```bash
curl http://localhost:8000/api/health   # {"status":"healthy","database":"connected"}
open http://localhost:3000              # Linux: xdg-open
```

### 2. Поставить зависимости

```bash
git clone https://github.com/Dilligan1/ui-automation-framework.git
cd ui-automation-framework

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Создать `.env`

```bash
cp .env.example .env
```

Заполнять ничего не нужно: учётные данные seed-пользователей песочницы **публичные** (опубликованы в её README) и уже проставлены в примере. Полезные переключатели в этом же файле:

| Переменная | Значение |
|---|---|
| `HEADLESS` | `false` — видеть браузер (удобно при разборе), `true` — без окна |
| `UI_TIMEOUT` | базовый таймаут ожиданий, по умолчанию 20 секунд |
| `SELENIUM_REMOTE_URL` | адрес Selenium Grid; пусто — локальный Chrome |

### 4. Запустить тесты

```bash
pytest                    # всё, что есть — около 35 секунд
```

Отдельные наборы:

```bash
pytest -m smoke           # критичный функционал: вход, публикация, доступ к разделам
pytest -m regress         # регрессия жизненного цикла поста
pytest -m e2e             # сквозной сценарий в двух браузерах одновременно
```

Параллельно и точечно:

```bash
pytest -n 3                                    # 3 браузера одновременно
HEADLESS=false pytest -m smoke                 # смотреть, что происходит на экране
pytest tests/smoke/user/test_feed_smoke.py     # один файл
pytest -k "login"                              # по части имени теста
python runner.py                               # smoke и regress разными процессами сразу
```

### 5. Посмотреть отчёт

```bash
pytest --alluredir=allure-results
allure serve allure-results          # если Allure CLI установлен
```

Без установки Allure CLI — собрать отчёт в контейнере:

```bash
docker compose run --rm report
open allure-report/index.html
```

Если тест упал, в отчёте рядом с шагом лежат скриншот экрана, адрес страницы и её HTML — разбирать падение по одному трейсбеку не придётся.

### Вариант без установки Python

```bash
docker compose run --rm smoke
docker compose run --rm regress
docker compose run --rm e2e
docker compose run --rm report
```

В контейнере браузер всегда headless, а приложение берётся с хоста через `host.docker.internal`.

### Если что-то пошло не так

| Симптом | Причина и что делать |
|---|---|
| Браузер не стартует | Проверьте, что Chrome установлен: `google-chrome --version` (macOS: `/Applications/Google Chrome.app`) |
| `Connection refused` на `localhost:3000` | Приложение не поднялось: `docker compose -f qa-automation-sandbox/docker-compose.yml logs frontend` |
| `port is already allocated` | Порты 3000/8000/5432 заняты — освободите их или измените в compose песочницы и в `.env` |
| `ValueError: Не найдены учётные данные для роли` | Нет `.env` — вернитесь к шагу 3 |
| Вход падает с «Login failed» при `-n` | Известный дефект стенда при одновременном входе, см. [docs/known-issues.md](docs/known-issues.md). Фреймворк его обходит; если столкнулись — удалите папку `storage/` и повторите |
| Клики «проходят», но ничего не происходит | Почти наверняка модальное окно Chrome поверх страницы — разбор в [docs/known-issues.md](docs/known-issues.md) (ENV-001) |
| Данные на стенде «разъехались» | `curl -X POST http://localhost:8000/api/reset` |

Папка `storage/` — это сохранённые сессии ролей, чтобы не логиниться в каждом тесте. Её можно удалять в любой момент: тесты просто войдут заново.

Погасить стенд, когда закончили:

```bash
docker compose -f qa-automation-sandbox/docker-compose.yml down -v
```

### Как это гоняется в CI

GitHub Actions на каждый push, PR и по расписанию ночью сам поднимает приложение на раннере, ждёт готовности, гоняет тесты в 3 браузерах headless и публикует отчёт. Постоянно работающий стенд не нужен — смотрите [`.github/workflows/tests.yml`](.github/workflows/tests.yml).

## Отчётность

Каждый шаг страницы и теста размечен `allure.step`. При падении в отчёт автоматически попадают скриншот, URL и HTML страницы — этого достаточно, чтобы разобрать упавший тест, не воспроизводя его руками. В CI отчёт публикуется на GitHub Pages — [посмотреть последний прогон](https://dilligan1.github.io/ui-automation-framework/).

## Документация

- [docs/architecture.md](docs/architecture.md) — слои, наследование, границы ответственности
- [docs/ui-map.md](docs/ui-map.md) — карта страниц и компонентов
- [docs/test-plan.md](docs/test-plan.md) — уровни тестирования и приоритеты покрытия
- [docs/known-issues.md](docs/known-issues.md) — найденный дефект приложения и особенность Chrome, из-за которой падали клики
- [CONTRIBUTING.md](CONTRIBUTING.md) — правила добавления страниц и тестов
