from typing import List, Any, Dict
import redis
from redis_lru import RedisLRU
from models import Author, Quote

client = redis.StrictRedis(host='localhost', port=6379, password=None)
cache = RedisLRU(client)


@cache
def find_by_tag(tag: str) -> list[str | None]:
    print(f"Find by {tag}")
    quotes = Quote.objects(tags__iregex=tag)
    result = [q.quote for q in quotes]
    return result


@cache
def find_by_author(author: str) -> dict[Any, list[Any]]:
    print(f"Find by {author}")
    authors = Author.objects(fullname__iregex=author)
    result = {}
    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]
    return result


@cache
def find_by_tags(tags: list[str]) -> list[str | None]:
    quotes = Quote.objects(tags__in=tags)
    return [q.quote for q in quotes]


if __name__ == '__main__':
    while True:
        command = input("Enter command: ")
        if command == "exit":
            break

        cmd, value = command.split(':', 1)
        value = value.strip()

        if cmd == "name":
            print(find_by_author(value))
        elif cmd == "tag":
            print(find_by_tag(value))
        elif cmd == "tags":
            tags = value.split(',')
            results = find_by_tags(tags)
            print(results)
        else:
            print("Unknown command")
