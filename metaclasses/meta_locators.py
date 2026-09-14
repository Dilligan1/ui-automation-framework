class MetaLocator(type):
    """
    Метакласс, преобразующий строковые локаторы в кортежи Selenium.

    Позволяет объявлять локаторы в странице как обычные строки:

        _LOGIN_BUTTON = "[data-testid='auth-login-btn']"
        _ERROR_TEXT   = "//div[@data-testid='auth-error-message']"

    и не писать ("css selector", ...) / ("xpath", ...) руками в каждом атрибуте.
    Тип селектора определяется по первому символу строки.
    """

    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if isinstance(value, str):
                if value.startswith(("//", ".//", "(//")):
                    # XPath
                    attrs[key] = ("xpath", value)
                elif value.startswith((".", "#", "[")):
                    # CSS-селектор, включая атрибутный [data-testid='...']
                    attrs[key] = ("css selector", value)
        return type.__new__(cls, name, bases, attrs)
