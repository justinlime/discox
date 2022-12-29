import discord
import asyncio
import aiosqlite
import re

from abc import ABC, abstractmethod

from typing import Optional, List, Tuple

from .logger import Logger
from .manager import Manager


class Command(ABC):
    """ Base abstrct class for all commands. """

    name: Optional[str] = None
    usage: Optional[str] = None
    description: Optional[str] = None
    hidden: Optional[bool] = False
    category: Optional[str] = None 

    db: Optional[aiosqlite.Connection] = None
    logger = Logger()

    def __init__(self, bot: discord.Client, manager: Manager, db: aiosqlite.Connection) -> None:
        """ Initialize the command. """

        self.bot = bot
        self.manager = manager
        self.db = db

        if not self.name:
            raise ValueError("Command name is required")

        if not self.description:
            raise ValueError("Command description is required")

        if not self.usage:
            raise ValueError("Command usage is required")
        else:
            args: List[Tuple[str,str]] = re.findall(f'\[([^\[\]]+)\]|\<([^\<\>]+)\>', self.usage)
            args: List[str] = [f"<{i[1]}>" if i[1] else f"[{i[0]}]" for i in args]

            # Verify the integredy of the usage arguments
            last_arg = "< "
            for arg in args:
                if arg[0] == "<" and last_arg[0] == "[":
                    raise ValueError("Cannot have a positional argument after an optional argument.")
                if last_arg[1] == "*":
                    raise ValueError("Cannot have a command argument after a *arg.")
                last_arg = arg

        if not asyncio.iscoroutinefunction(self.execute):
            raise TypeError("Command execute() method must be a coroutine")

    @abstractmethod
    async def execute(self, arguments: List[str], message: discord.Message) -> None:
        """ Execute the command. """
        raise NotImplementedError("Command execute method is required")


class Event(ABC):
    """ Base abstrct class for all events. """

    name: Optional[str] = None

    db: Optional[aiosqlite.Connection] = None
    logger = Logger()

    def __init__(self, bot: discord.Client, manager: Manager, db: aiosqlite.Connection) -> None:
        """ Initialize the command. """

        self.bot = bot
        self.manager = manager
        self.db = db

        if not self.name:
            raise ValueError("Command name is required")

    @abstractmethod
    async def execute(self) -> None:
        """ Execute the event. """
        raise NotImplementedError("Event execute method is required")
