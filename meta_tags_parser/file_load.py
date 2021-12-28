"""Load from file."""
import pathlib
import typing

from aiofile import async_open


def read_file_sync(file_path: typing.Union[str, pathlib.Path]) -> str:
    """Sync file read."""
    return (
        file_path if isinstance(file_path, pathlib.Path) else pathlib.Path(file_path)
    ).read_text()


async def read_file_async(file_path: typing.Union[str, pathlib.Path]) -> str:
    """Sync file read."""
    async with async_open(
        str(file_path) if isinstance(file_path, pathlib.Path) else file_path, "r"
    ) as afp:
        return await afp.read()


__all__ = [
    'read_file_async',
    'read_file_sync'
]
