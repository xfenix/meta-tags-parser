"""Bunch of public methods."""
from . import download, parse, structs


def parse_tags_from_url(web_url: str) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(download.download_page_sync(web_url))


async def parse_tags_from_url_async(web_url: str) -> structs.TagsGroup:
    """Stupid and low quality helper."""
    return parse.parse_meta_tags_from_source(await download.download_page_async(web_url))


__all__ = ["parse_tags_from_url", "parse_tags_from_url_async"]
