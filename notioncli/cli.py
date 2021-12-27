from dataclasses import fields
import os
import sys

import click
from notion.block import TodoBlock
from notion.client import NotionClient
from termcolor import colored, cprint

from notioncli.config import Config


class TasksType(click.ParamType):
    name = "task"

    def convert(self, value, param, ctx):
        try:
            return [int(task) for task in value.split(",")]
        except ValueError:
            self.fail(f"{value!r} not a comma-separated list of integers", param, ctx)


TASKS = TasksType()


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


@click.group(help="A Notion.so CLI focused on simple task management")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(Context)


@cli.group(help="Show or set the current configuration")
def config():
    pass


@config.command(help="Initialize the configuration")
@click.pass_context
def init(ctx):
    config = ctx.obj.config

    token = click.prompt(
        "Notion API token (from the browser cookie)", default=config.token or "<unset>"
    )
    page = click.prompt(
        "Notion page (from the browser location bar)",
        default=config.page or "https://notion.so/<page>",
    )

    config = config.set(token=token, page=page)
    ctx.obj["CONFIG"] = config

    cprint(f"Configuration written to {config.config_file}")


@config.command(help="Show the current configuration")
@click.pass_context
def show(ctx):
    config = ctx.obj.config

    cprint("\n Configuration: \n", "white", attrs=["underline"])

    for field in fields(config):
        cprint(f"{field.name}: {getattr(config, field.name) or '<unset>'}", "green")


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    ctx.obj.config = ctx.obj.config.set(key, value)
    cprint(f"{key}='{value}'", "green")


@cli.command(help="List tasks")
@click.pass_context
def list(ctx):
    page = ctx.obj.page

    n = 0
    cprint("\n\n{}\n".format(page.title), "white", attrs=["bold"])
    cprint("  # Status Description", "white", attrs=["underline"])
    for child in page.children:
        if child.type == "sub_header":
            cprint("[{}]".format(child.title), "green")
        elif child.type == "to_do":
            n += 1
            if child.checked:
                check = "[*]"
            else:
                check = "[ ]"
            cprint("  {}  {}  {}.".format(n, check, child.title), "green")
        else:
            pass

    cprint("\n{} total tasks".format(n), "white", attrs=["bold"])


@cli.command()
@click.argument("tasks", type=TASKS)
@click.pass_context
def add(ctx, tasks):
    page = ctx.obj.page

    for task in tasks:
        newchild = page.children.add_new(TodoBlock, title=task)
        newchild.checked = False
        cprint("{} added as a new task".format(task))


@cli.command()
@click.argument("tasks", type=TASKS)
@click.pass_context
def remove(ctx, task):
    page = ctx.obj.page

    n = 0
    for child in page.children:
        if child.type == "to_do":
            n += 1
            for task in tasks:
                if n == task:
                    child.remove()
        else:
            pass  # not a task
    cprint("{} removed.".format(taskn), "white", attrs=["bold"])


@cli.command()
@click.argument("tasks", type=TASKS)
@click.pass_context
def check(ctx, tasks):
    page = ctx.obj.page

    n = 0
    for child in page.children:
        if child.type == "to_do":
            n += 1
            for task in tasks:
                if n == task:
                    child.checked = True
        else:
            pass  # not a task
    cprint("{} marked as completed".format(taskn), "white", attrs=["bold"])


@cli.command()
@click.argument("tasks", type=TASKS)
@click.pass_context
def uncheck(ctx, tasks):
    page = ctx.obj.page

    n = 0
    for child in page.children:
        n += 1
        try:
            for task in tasks:
                if n == task:
                    child.checked = False
        except:
            pass  # not a task
    cprint("{} marked as incomplete".format(taskn), "white", attrs=["bold"])


if __name__ == "__main__":
    cli()
