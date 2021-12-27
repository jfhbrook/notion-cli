from io import StringIO
import os
import sys

import click
from notion.block import TodoBlock
from notion.client import NotionClient
from termcolor import colored, cprint


class ConfigurationError(Exception):
    pass


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
    ctx.ensure_object(dict)

    has_token = "NOTION_TOKEN" in os.environ
    has_page = "NOTION_PAGE" in os.environ

    if not has_token:
        if has_page:
            raise ConfigurationError("Missing NOTION_TOKEN")
        else:
            raise ConfigurationError("Missing NOTION_TOKEN and NOTION_PAGE")

    try:
        client = NotionClient(token_v2=os.environ["NOTION_TOKEN"], monitor=False)
    except:
        raise ConfigurationError("Invalid or expired NOTION_TOKEN")

    ctx.obj["CLIENT"] = client
    ctx.obj["PAGE"] = client.get_block(os.environ["NOTION_PAGE"])


@cli.command(help="Print current relevant environment variables")
def config():
    cprint("\n Environment variables: \n", "white", attrs=["underline"])

    for env_var in ["NOTION_TOKEN", "NOTION_PAGE"]:
        cprint(f"{env_var}='{os.environ.get(env_var, '<unset>')}'", "green")


@cli.command(help="List tasks")
@click.pass_context
def list(ctx):
    page = ctx.obj["PAGE"]

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
    page = ctx.obj["PAGE"]

    for task in tasks:
        newchild = page.children.add_new(TodoBlock, title=task)
        newchild.checked = False
        cprint("{} added as a new task".format(task))


@cli.command()
@click.argument("tasks", type=TASKS)
@click.pass_context
def remove(ctx, task):
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
    page = ctx.obj["PAGE"]

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
    page = ctx.obj["PAGE"]

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
