def fancy_join(sep: str, items: list[str], final: str = None) -> str:
    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if not final:
        final = sep

    *items, last = items
    return sep.join(items) + final + last
