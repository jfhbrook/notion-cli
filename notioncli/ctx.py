from dataclasses import dataclass

from notion.client import NotionClient

from notioncli.config import Config


@dataclass
class SubHeader:
    title: str


@dataclass
class Task:
    id: int
    title: str
    checked: bool


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

    def set_config(self, **kwargs):
        self.config = self.config.set(**kwargs)
