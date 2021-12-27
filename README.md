# Notion CLI

This project is a heavily refactored fork of
[kris-hansen/notion-cli](https://github.com/kris-hansen/notion-cli). It's very
much a work in progress - it's not useful right now - but I'm working on it
slowly during lunch breaks.

Notion doesn't actually have an API, as far as I can tell. Instead, this tool
uses [notion-py](https://github.com/jamalex/notion-py)
to make calls to Notion and munge returned HTML.

## Install

### pip

You can install from git with pip:

```sh
pip install --user git+https://github.com/kris-hansen/notion-cli@latest
```

### git + virtualenv

First, make sure you have a recent Python 3 in your path. Ubuntu and other Linux
distributions should already have it installed. On MacOS, you can run
`brew install python`. For Windows, you're on your own.

I'm using <https://github.com/casey/just> for task execution. You can install
it through `cargo install just`, or through your system package manager of
choice.

Anyway: to set up the virtualenv, run `just setup`.

To source the virtualenv after it's built, run `source ./venv/bin/activate` in
bash.

## Configuration

This tool stores its configuration in `~/.local/notion/cli.toml`. To create
a new one, run `notion config init`.

It will prompt you for two configuration parameters:

- `token` - This is the API token for the Notion client
- `page` - This is the URL for the page (ex: https://notion.so/my-page)

To get the `token`, you'll need to:

- Log into notion in your web browser
- Crack open the dev console
- Dig through your browser cookies
- Copy-paste it on out

See the notion-py documentation for more details.

## Run

To run the tool, ensure that the virtualenv is set up (if applicable):

```bash
source ./venv/bin/activate
```

then go to town:

```bash
notion --help
```

For convenience, you may want to put a shim in your path:

```bash
#!/usr/bin/env bash

source "${HOME}/notion-cli/venv/bin/activate"

exec notion "$@"
```

A good location for this script may be `~/.local/bin/notion`.

```bash
$ notion --help
Usage: notion [OPTIONS] COMMAND [ARGS]...

  A Notion.so CLI focused on simple task management

Options:
  --help  Show this message and exit.

Commands:
  add
  check
  config   Show or set the current configuration
  list     List tasks
  remove
  uncheck
```

## Known Issues

- The tool only supports one page right now.
- I haven't actually gotten the tool to output anything meaningful. I suspect
  that Notion has changed since the original commands were written.
