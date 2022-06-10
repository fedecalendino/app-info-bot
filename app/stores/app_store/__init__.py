import html
from json import loads
from urllib import parse

import requests
from bs4 import BeautifulSoup

from app import config
from app.stores.classes import (
    Developer,
    Price,
    PrivacyCard,
    Rating,
)
from .appsliced import AppSliced
from .helpers import find_by_attr, find_all_by_attr

TEMPLATE = """
## [**{title}**]({url})  
 > by [{dev_name}]({dev_url})  
  
{subtitle}  
  
____  
  
### ℹ️ **App Info**  
**Category**: {category}.  

**Release**: {release}.  

**Last Update**: {last_update}.  
  
**Platforms**: {compatibility}  
  
**Rating**: {rating_value} ({rating_count}).  
  
**Size**: {size}.  


### 💸 **Pricing (in USD)**
**Current**: {price}  

**History**: {price_history}  

**IAPs**: {iaps}  

### 🔒️ **Privacy**  
**Policy**: {privacy_policy}  

**Specification**: {privacy_cards}  
  
---  
  
^[dev]({dev}) ^| ^[github]({github})   

"""


class AppStoreApplication:
    store = "App Store"

    @staticmethod
    def us_store(url: str) -> str:
        url = parse.urlsplit(url)
        path = url.path

        if not path.startswith("/app"):
            path = url.path.split("/", 2)[-1]

        return f"https://{url.hostname}/{path}"

    def __init__(self, url: str, use_us_store: bool = True):
        if use_us_store:
            url = self.us_store(url)

        response = requests.get(url)

        self.soup = BeautifulSoup(response.content, features="html.parser")
        self.json = loads(
            html.unescape(
                self.soup.find(
                    "script",
                    attrs={"name": "schema:software-application"},
                ).string
            )
        )

        try:
            self.app_sliced = AppSliced(app_id=response.url.split("/")[-1])
        except:
            self.app_sliced = None

    @property
    def age(self) -> str:
        tag = self.soup.find("span", class_="badge badge--product-title")
        return tag.text.strip() if tag else None

    @property
    def category(self) -> str:
        tag = self.soup.find("dt", text="Category")

        if tag:
            tag = tag.parent.find("dd")

        if not tag:
            return None

        return tag.text.strip()

    @property
    def compatibility(self) -> str:
        tag = self.soup.find("dt", text="Compatibility")

        if tag:
            tag = tag.parent.find("dd")

        if not tag:
            return None

        items = []

        for item in tag.find_all(
            "dl", class_="information-list__item__definition__item"
        ):
            items.append(item.text.strip().replace("\n                \n", ": "))

        return "; ".join(sorted(items)) if items else tag.text.strip()

    @property
    def description(self) -> list[str]:
        return self.json.get("description")

    @property
    def description_short(self) -> str:
        return self.soup.find("meta", attrs={"name": "twitter:description"})["content"]

    @property
    def developer(self) -> Developer:
        return Developer(
            name=self.json["author"]["name"],
            url=self.json["author"]["url"],
        )

    @property
    def iaps(self) -> list[Price]:
        tag = self.soup.find("dt", text="In-App Purchases")

        if not tag:
            return []

        iaps = []

        for li in tag.parent.find_all("li"):
            split = li.text.strip().split("\n")

            if len(split) == 2:
                iaps.append(Price(split[0], split[1]))
            elif len(split) == 1:
                iaps.append(Price(split[0], ""))

        return iaps

    @property
    def last_update(self) -> str:
        tag = find_by_attr(self.soup, "time", "data-test-we-datetime")
        return tag.text if tag else None

    @property
    def price(self) -> str:
        return self.soup.find("li", class_="app-header__list__item--price").text

    @property
    def price_history(self) -> list[str]:
        if self.app_sliced:
            return self.app_sliced.price_history
        else:
            return []

    @property
    def privacy_cards(self) -> list[PrivacyCard]:
        cards = []

        for tag in self.soup.find_all("div", class_="app-privacy__card"):
            spans = tag.find_all("span", class_="privacy-type__data-category-heading")

            cards.append(
                PrivacyCard(
                    title=tag.find("h3", class_="privacy-type__heading").text,
                    items=list(map(lambda span: span.text.strip(), spans)),
                )
            )

        return cards

    @property
    def privacy_policy(self) -> str:
        tag = self.soup.find(
            "a",
            attrs={
                "data-metrics-click": '{"actionType":"navigate","targetType":"link","targetId":"LinkToPrivacyPolicy"}'
            },
        )
        return tag["href"] if tag else None

    @property
    def rating(self) -> Rating:
        tag = self.soup.find("div", class_="we-customer-ratings__averages")
        score = tag.text if tag else None

        tag = self.soup.find("p", class_="we-customer-ratings__count")
        count = tag.text.lower() if tag else None

        if not score or not count:
            return Rating("n/a", "not enough ratings")

        return Rating(score, count)

    @property
    def release(self) -> str:
        return self.json.get("datePublished")

    @property
    def size(self) -> str:
        tag = self.soup.find("dt", text="Size")
        if tag:
            tag = tag.parent.find("dd")

        return tag.text if tag else None

    @property
    def subtitle(self) -> str:
        tag = self.soup.find(
            "h2", class_="product-header__subtitle app-header__subtitle"
        )
        return tag.text.strip() if tag else None

    @property
    def title(self) -> str:
        return self.json.get("name")

    @property
    def url(self) -> str:
        return self.soup.find("link", rel="canonical")["href"]

    def __str__(self) -> str:
        developer = self.developer
        iaps = self.iaps
        price_history = self.price_history[:5]
        privacy_cards = self.privacy_cards
        subtitle = self.subtitle

        # == Subtitle =====================================
        if subtitle:
            subtitle_str = f"{subtitle}."
        else:
            subtitle_str = ""

        # == IAPs =========================================
        if len(iaps) == 3:
            iap_count = "3+  "
        elif len(iaps) == 0:
            iap_count = "None  "
        else:
            iap_count = f"{len(iaps)}  "

        iap_list = []

        for iap in iaps:
            if iap.price:
                iap_list.append(f"{iap.name}: {iap.price}  ")
            else:
                iap_list.append(f"{iap.name}: Free  ")

        iaps_str = "\n".join([iap_count] + [f"  * {item}  " for item in iap_list])

        # == Price History ================================
        if not price_history:
            price_history_str = "n/a"
        else:
            price_history_str = "\n".join(
                ["  "] + [f"  * {item}  " for item in price_history]
            )

        # == Privacy Cards ================================
        if len(privacy_cards) == 1 and len(privacy_cards[0].items) == 0:
            privacy_cards_str = f"{privacy_cards[0].title}  "
        else:
            privacy_cards_str = "\n".join(
                ["  "] + [f"  * {card}  " for card in privacy_cards]
            )

        return TEMPLATE.format(
            title=self.title,
            url=self.url,
            subtitle=subtitle_str,
            dev_name=developer.name,
            dev_url=developer.url,
            age=self.age,
            category=self.category,
            release=self.release,
            last_update=self.last_update,
            compatibility=self.compatibility,
            rating_value=self.rating.value,
            rating_count=self.rating.count,
            size=self.size,
            price=self.price,
            price_history=price_history_str,
            iaps=iaps_str,
            privacy_policy=self.privacy_policy,
            privacy_cards=privacy_cards_str,
            github=config.URL_GITHUB_REPOSITORY,
            dev=config.URL_REDDIT_DEV,
        )
