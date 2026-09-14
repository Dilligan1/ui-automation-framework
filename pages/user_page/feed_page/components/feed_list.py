from base_components.lists.base_list_handler import BaseListHandler


class FeedList(BaseListHandler):
    """Лента постов как коллекция карточек."""

    _ROW_LOCATOR = "[data-testid^='post-card-']"

    _FIELDS = {
        "author": ".//*[starts-with(@data-testid,'post-author-')]",
        "content": ".//*[starts-with(@data-testid,'post-content-')]",
        "likes": ".//*[starts-with(@data-testid,'post-likes-count-')]",
        "comments": ".//*[starts-with(@data-testid,'post-comments-count-')]",
    }

    def _row_testid(self, entity_id: str) -> str:
        return f"post-card-{entity_id}"
