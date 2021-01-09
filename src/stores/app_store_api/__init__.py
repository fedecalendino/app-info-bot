from settings import GITHUB

from stores.classes import (
    Developer,
    PlatformAttr,
    Price,
    PrivacyCard,
    Rating,
)
from utils import fancy_join

from . import helpers


TEMPLATE = """
## [**{title}**]({url})  
 > by [{dev_name}]({dev_url})  

____
  
#### ℹ️ **App Info**  
**Age**: {age}.  
**Category**: {category}.  
**Platforms**: {platforms}.  
**Rating**: {rating_value} stars ({rating_count} ratings).  
**Size**: {size}.  
#### 💸 **Pricing**  
**Prices**: {prices}  
**In-App Purchases**: {iap_count}  
{iaps}  
#### 🔒️ **Privacy**  
**Policy**: {privacy_policy}  
**Specification**:  
{privacy_cards}
  
---  
  
^[github]({github})
"""


class AppStoreApplication:
    store = "App Store"

    def __init__(self, url: str):
        data = helpers.get_data(app_id=url.split("/")[-1].replace("id", ""))

        self.attributes = data["attributes"]
        self.relationships = data["relationships"]

    @property
    def age(self) -> str:
        return self.attributes["contentRatingsBySystem"]["appsApple"]["name"]

    @property
    def category(self) -> str:
        return self.attributes["genreDisplayName"]

    @property
    def developer(self) -> Developer:
        dev = self.relationships["developer"]["data"][0]["attributes"]
        return Developer(name=dev["name"], url=dev["url"])

    @property
    def description(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform,
                    name="description",
                    value=data["description"]["standard"],
                ),
            )

        return attrs

    @property
    def iaps(self) -> list[Price]:
        iaps = []

        for data in self.relationships["top-in-apps"]["data"]:
            iaps.append(
                Price(
                    name=data["attributes"]["name"],
                    price=data["attributes"]["offers"][0]["priceFormatted"],
                )
            )

        return iaps

    @property
    def platforms(self) -> list[str]:
        return self.attributes["deviceFamilies"]

    @property
    def prices(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            for offer in data["offers"]:
                if offer["type"] != "get":
                    continue

                attrs.append(
                    PlatformAttr(
                        platform=platform,
                        name="price",
                        value=offer["priceFormatted"] if offer["price"] else "Free",
                    ),
                )

        return attrs

    @property
    def privacy_cards(self) -> list[PrivacyCard]:
        cards = []

        for data in self.attributes["privacy"]["privacyTypes"]:
            cards.append(
                PrivacyCard(
                    title=data["privacyType"],
                    items=list(
                        map(
                            lambda category: category["dataCategory"],
                            data["dataCategories"],
                        )
                    ),
                )
            )

        return cards

    @property
    def privacy_policy(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform, name="policy", value=data["privacyPolicyUrl"]
                ),
            )

        return attrs

    @property
    def rating(self) -> Rating:
        user_rating = self.attributes["userRating"]
        return Rating(user_rating["ariaLabelForRatings"], user_rating["ratingCount"])

    @property
    def size(self) -> str:
        values = self.attributes["fileSizeByDevice"].values()
        return f"{(sum(values)/len(values)) // 1024 // 1024} MB"

    @property
    def subtitle(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform, name="subtitle", value=data["subtitle"]
                ),
            )

        return attrs

    @property
    def title(self) -> str:
        return self.attributes["name"]

    @property
    def url(self) -> str:
        return self.attributes["url"]

    def __str__(self) -> str:
        price_list = [""]

        for price in self.prices:
            price_list.append(f" * {price.platform}: {price.value}  ")

        iaps = self.iaps

        if len(iaps) > 5:
            iap_count = "5+"
        elif len(iaps) == 0:
            iap_count = "None"
        else:
            iap_count = str(len(iaps))

        iap_list = []

        for iap in iaps[:5]:
            iap_list.append(f" * {iap.name}: {iap.price}")

        privacy_cards_list = []

        for card in self.privacy_cards:
            if card.items:
                privacy_cards_list.append(f" * {card.title}: {fancy_join(', ', card.items, ' & ')}.")
            else:
                privacy_cards_list.append(f" * {card.title}.")

        return TEMPLATE.format(
            title=self.title,
            url=self.url,
            dev_name=self.developer.name,
            dev_url=self.developer.url,
            age=self.age,
            category=self.category,
            platforms=fancy_join(", ", self.platforms, " & "),
            rating_value=self.rating.value,
            rating_count=self.rating.count,
            size=self.size,
            prices="\n".join(price_list),
            iap_count=iap_count,
            iaps="\n".join(iap_list),
            privacy_policy=self.privacy_policy[0].value,
            privacy_cards="\n".join(privacy_cards_list),
            github=GITHUB,
        )
