from appinfobot.utils import fancy_join


class Developer:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url


class Price:
    def __init__(self, name: str, price: str):
        self.name = name
        self.price = price


class PrivacyCard:
    def __init__(self, title: str, items: list[str]):
        self.title = title
        self.items = items

    def __repr__(self):
        return f"{self.title}: {fancy_join(', ', self.items, ' & ')}."


class Rating:
    def __init__(self, value: str, count: str):
        self.value = value
        self.count = count
