from urllib import parse

import requests
from bs4 import BeautifulSoup

from settings import GITHUB
from stores.classes import (
    Developer,
    Price,
    PrivacyCard,
    Rating,
)
from utils import fancy_join
from .appsliced import AppSliced
from .helpers import find_by_attr, find_all_by_attr

TEMPLATE = """
## [**{title}**]({url})  
 > by [{dev_name}]({dev_url})  
  
{subtitle}  
  
____  
  
### ℹ️ **App Info**  
**Category**: {category}.  

**Last Update**: {last_update}.
  
**Platforms**: {platforms}.
  
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
  
^[github]({github})  
  
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

        self.app_sliced = AppSliced(app_id=response.url.split("/")[-1])
        self.soup = BeautifulSoup(response.content, features="html.parser")

    @property
    def age(self) -> str:
        tag = find_by_attr(self.soup, "span", "data-test-product-rating")
        return tag.text.strip() if tag else None

    @property
    def category(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-category")
        return tag.text.strip() if tag else None

    @property
    def compatibility(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-compatibility")
        return tag.text.strip().split(". ")[0] if tag else None

    @property
    def description(self) -> list[str]:
        tag = find_by_attr(self.soup, "div", "data-test-description")
        return [str(p) for p in tag.find("p") if str(p) != "<br/>"]

    @property
    def developer(self) -> Developer:
        tag = find_by_attr(self.soup, "a", "data-test-developer-link")
        return Developer(name=tag.text.strip(), url=tag["href"])

    @property
    def iaps(self) -> list[Price]:
        tags = find_all_by_attr(self.soup, "li", "data-test-app-info-iap")

        iaps = []

        for li in tags:
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
    def platforms(self) -> list[str]:
        tags = list(find_all_by_attr(self.soup, "a", "data-test-app-platform-link"))

        if not tags:
            tags = list(find_all_by_attr(self.soup, "h2", "data-test-app-screenshots-title"))

        return [a.text.strip().replace(" Screenshots", "") for a in tags]

    @property
    def price(self) -> str:
        tag = self.soup.find("li", class_="app-header__list__item--price")
        return tag.text.strip()

    @property
    def price_history(self) -> list[str]:
        return self.app_sliced.price_history

    @property
    def privacy_cards(self) -> list[PrivacyCard]:
        tags = self.soup.find_all("div", class_="ember-view app-privacy__card")

        cards = []
        for tag in tags:
            spans = tag.find_all(
                "span",
                class_="privacy-type__grid-content privacy-type__data-category-heading",
            )

            cards.append(
                PrivacyCard(
                    title=tag.find("h3", class_="privacy-type__heading").text,
                    items=list(map(lambda span: span.text.strip(), spans)),
                )
            )

        return cards

    @property
    def privacy_policy(self) -> str:
        tag = find_by_attr(self.soup, "a", "data-test-app-info-links-privacy")
        return tag["href"] if tag else None

    @property
    def rating(self) -> Rating:
        tag = find_by_attr(self.soup, "div", "data-test-average-rating")
        score = tag.text if tag else None

        tag = find_by_attr(self.soup, "p", "data-test-rating-count")
        count = tag.text.lower() if tag else None

        if not score or not count:
            return Rating("n/a", "not enough ratings")

        return Rating(score, count)

    @property
    def size(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-size")
        return tag.text if tag else None

    @property
    def subtitle(self) -> str:
        tag = find_by_attr(self.soup, "h2", "data-test-product-subtitle")
        return tag.text.strip() if tag else None

    @property
    def title(self) -> str:
        tag = find_by_attr(self.soup, "h1", "data-test-product-name")
        return tag.find(text=True).strip()

    @property
    def url(self) -> str:
        return self.soup.find("link", rel="canonical")["href"]

    def __str__(self) -> str:
        developer = self.developer
        iaps = self.iaps
        platforms = self.platforms
        price_history = self.price_history[:5]
        privacy_cards = self.privacy_cards
        subtitle = self.subtitle

        # == Platforms ====================================
        platforms_str = fancy_join(", ", platforms, " & ")

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
            price_history_str = "\n".join(["  "] + [f"  * {item}  " for item in price_history])

        # == Privacy Cards ================================
        if len(privacy_cards) == 1 and len(privacy_cards[0].items) == 0:
            privacy_cards_str = f"{privacy_cards[0].title}  "
        else:
            privacy_cards_str = "\n".join(["  "] + [f"  * {card}  " for card in privacy_cards])

        return TEMPLATE.format(
            title=self.title,
            url=self.url,
            subtitle=subtitle_str,
            dev_name=developer.name,
            dev_url=developer.url,
            age=self.age,
            category=self.category,
            last_update=self.last_update,
            platforms=platforms_str,
            rating_value=self.rating.value,
            rating_count=self.rating.count,
            size=self.size,
            price=self.price,
            price_history=price_history_str,
            iaps=iaps_str,
            privacy_policy=self.privacy_policy,
            privacy_cards=privacy_cards_str,
            github=GITHUB,
        )
