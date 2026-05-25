# Readme

Dreamy is an admin for therapists. It solves some core problems for most private practitioners: Setting up client info,
sessions, and coordinating rooms.

It is a sort of CRM, and in the future, more features in that direction could be added. I wanted to create a core system
of sessions that shared the information with the room system.

It is running on:

[Dreamy](https://dreamy.crea-therapy.com/en/)

## Features

- Client info
- Sessions booking and payment tracking
- Room sharing and managing

## Stack

- Python
- Django
- HTMX + hyperscript
- Bootstrap CSS
- PostgrSQL/SQLite

## Installation

First, I recommend getting UV to manage Python packages. UV and Python run in Windows, Mac, Linux and Android.

[Installation | uv](https://docs.astral.sh/uv/getting-started/installation/)

### I recommend

- creating a folder.

```bash
mk dir dreamy
```

- then run ‘UV init’ inside it on your terminal.

```bash
uv init
```

- an then run the next two commands.

```bash
uv add dreamy-admin
```

```bash
uv run dreamy
```

For a quick try, you can also run:

```bash
uvx --from dreamy-admin dreamy
```

## Contribute

This project is open source, and you are welcome to write in the issues and conversations. You can also send PRs with
bug fixes afterwards.

New features are welcome, but I would prefer coming from people using the app and actively engaging in the repository.

You can also contribute financially to the project so I can keep working on it and maintain the server version.

I will need to find a way to charge for the hosted version at some point, but the community's use of it is my priority.
If Dreamy can be maintained by donations and open-source contributions, that would be my preferred way.