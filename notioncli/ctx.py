from notion.client import NotionClient

from notioncli.config import Config


class Context:
    def __init__(self):
        self.config = Config.from_file()
        self._client = None
        self._page = None

    @property
    def client(self):
        if not self._client:
            self.config.validate()
            self._client = NotionClient(token_v2=self.config.token, monitor=False)
        return self._client

    @property
    def page(self):
        if not self._page:
            self._page = self.client.get_block(self.config.page)
        return self._page
