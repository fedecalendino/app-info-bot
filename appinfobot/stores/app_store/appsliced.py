import requests
from bs4 import BeautifulSoup


URL = "https://appsliced.co/apps?search={app_id}"


class AppSliced:

    def __init__(self, app_id: str):
        url = URL.format(app_id=app_id)
        response = requests.get(url)

        soup = BeautifulSoup(response.content, features="html.parser")

        div = soup.find("div", class_="10u title")
        a = div.find("a")

        response = requests.get(a.attrs["href"])
        self.soup = BeautifulSoup(response.content, features="html.parser")

    @property
    def price_history(self) -> list[str]:
        ul = self.soup.find("ul", class_="price_changes")

        price_history = []

        if ul:
            for li in ul.find_all("li"):
                string = str(li)

                icon = ""

                if "more_recent_expand" in string:
                    continue

                if "more_recent_collapse" in string:
                    continue

                if "history" in string:
                    icon = "⏺️"
                elif "down" in string:
                    icon = "⬇️"
                elif "up" in string:
                    icon = "⬆️"

                price_history.append(f"{icon} {li.text.strip()}")

        return price_history
