from dataclasses import dataclass

from notion.client import NotionClient

from notioncli.ctx import Context

ctx = Context()
config = ctx.config
client = ctx.client
