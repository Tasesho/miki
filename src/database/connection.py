from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any


class AsyncCursor:
    def __init__(self, connection: AsyncConnection, cursor: sqlite3.Cursor):
        self._connection = connection
        self._cursor = cursor

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    async def fetchone(self):
        return await self._connection._run(self._cursor.fetchone)

    async def fetchall(self):
        return await self._connection._run(self._cursor.fetchall)

    async def close(self) -> None:
        await self._connection._run(self._cursor.close)

    async def __aenter__(self) -> AsyncCursor:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


class _ExecuteResult:
    def __init__(
        self,
        connection: AsyncConnection,
        operation: Callable[[], sqlite3.Cursor],
    ):
        self._connection = connection
        self._operation = operation

    async def _execute(self) -> AsyncCursor:
        cursor = await self._connection._run(self._operation)
        return AsyncCursor(self._connection, cursor)

    def __await__(self):
        return self._execute().__await__()

    async def __aenter__(self) -> AsyncCursor:
        return await self._execute()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None


class AsyncConnection:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._lock = asyncio.Lock()

    async def _run(self, function: Callable[[], Any]):
        async with self._lock:
            return function()

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> _ExecuteResult:
        return _ExecuteResult(
            self,
            lambda: self._connection.execute(sql, parameters),
        )

    async def executemany(self, sql: str, parameters: Any) -> AsyncCursor:
        cursor = await self._run(lambda: self._connection.executemany(sql, parameters))
        return AsyncCursor(self, cursor)

    async def executescript(self, script: str) -> None:
        await self._run(lambda: self._connection.executescript(script))

    async def commit(self) -> None:
        await self._run(self._connection.commit)

    async def rollback(self) -> None:
        await self._run(self._connection.rollback)

    async def close(self) -> None:
        await self._run(self._connection.close)


class Database:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        db = AsyncConnection(sqlite3.connect(self.path, timeout=30))
        try:
            await db.execute("PRAGMA foreign_keys = ON")
            await db.execute("PRAGMA journal_mode = WAL")
            await db.execute("PRAGMA busy_timeout = 5000")
            yield db
        finally:
            await db.close()
