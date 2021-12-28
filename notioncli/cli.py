from dataclasses import fields
import os
import sys

import click
from notion.block import TodoBlock
from notion.client import NotionClient
from pygments import highlight
from pygments.lexers import MarkdownLexer
from pygments.formatters import Terminal256Formatter
from termcolor import colored, cprint

from notioncli.config import Config
from notioncli.ctx import Context


def pprint_md(obj):
    print(highlight(obj._repr_markdown_(), MarkdownLexer(), Terminal256Formatter()))


class TasksType(click.ParamType):
    name = "task"

    def convert(self, value, param, ctx):
        try:
            return [int(task) for task in value.split(",")]
        except ValueError:
            self.fail(f"{value!r} not a comma-separated list of integers", param, ctx)


TASKS = TasksType()


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
    token = click.prompt(
        "Notion API token (from the browser cookie)", default=ctx.obj.config.token or "<unset>"
    )
    page = click.prompt(
        "Notion page (from the browser location bar)",
        default=ctx.obj.config.page or "https://notion.so/<page>",
    )

    ctx.obj.set_config(token=token, page=page)

    cprint(f"Configuration written to {config.config_file}")


@config.command(help="Show the current configuration")
@click.pass_context
def show(ctx):
    pprint_md(ctx.obj.config)


@config.command(help="Set a configuration field")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    ctx.obj.set_config(**{key: value})
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
