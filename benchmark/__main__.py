import os

from meta_tags_parser.parse import parse_meta_tags_from_source

from ._payload import PAYLOAD_DATA


def test_my_code():
    result = parse_meta_tags_from_source(PAYLOAD_DATA)
    for one_attr in [one_attr for one_attr in dir(result) if not one_attr.startswith("_")]:
        print(one_attr, getattr(result, one_attr))


if __name__ == "__main__":
    import timeit

    print(timeit.timeit("test_my_code()", globals=locals(), number=int(os.getenv("COUNTS", 1))))


__all__ = ["test_my_code"]
