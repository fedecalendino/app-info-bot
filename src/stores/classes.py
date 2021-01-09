from collections import namedtuple

Developer = namedtuple("Developer", ("name", "url"))
Price = namedtuple("Price", ("name", "price"))
PrivacyCard = namedtuple("PrivacyCard", ("title", "items"))
Rating = namedtuple("Rating", ("value", "count"))
