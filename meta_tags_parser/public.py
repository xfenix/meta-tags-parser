"""Bunch of public methods."""
import pathlib
import typing

from . import download, file_load, parse, structs


def parse_tags_from_url(web_url: str) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(download.download_page_sync(web_url))


async def parse_tags_from_url_async(web_url: str) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(await download.download_page_async(web_url))


def parse_tags_from_file(file_path: typing.Union[str, pathlib.Path]) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(file_load.read_file_sync(file_path))


async def parse_tags_from_file_async(file_path: typing.Union[str, pathlib.Path]) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(await file_load.read_file_async(file_path))


__all__ = [
    'parse_tags_from_file',
    'parse_tags_from_file_async',
    'parse_tags_from_url',
    'parse_tags_from_url_async'
]
