from base_components.menu.navbar import Menu
from interfaces.admin.admin import AdminInterface
from interfaces.moderator.moderator import ModeratorInterface
from interfaces.user.user import UserInterface


class BaseTest:
    """
    Общий предок всех тест-классов.

    Страницы доступны через интерфейсы ролей, а не напрямую: тест пишется
    на языке роли — self.user_page().feed.publish(...), а не через импорт
    десятка классов страниц в каждый файл.

    Интерфейсы создаются лениво (lambda), потому что драйвер появляется
    в фикстуре уже после инстанцирования класса.
    """

    def setup_method(self):
        # роли
        self.admin_page = lambda driver=None: AdminInterface(driver or self.driver)
        self.moderator_page = lambda driver=None: ModeratorInterface(driver or self.driver)
        self.user_page = lambda driver=None: UserInterface(driver or self.driver)

        # компоненты, общие для всех ролей
        self.menu = lambda driver=None: Menu(driver or self.driver)
