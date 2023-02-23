import requests
import os
from bs4 import BeautifulSoup


URL = "https://appsliced.co/apps?search={app_id}"

EMAIL = os.getenv("APPSLICED_EMAIL")
PASSWORD = os.getenv("APPSLICED_PASSWORD")


class AppSliced:
    def __init__(self, app_id: str):
        with requests.Session() as session:
            url = "https://appsliced.co/f/f-login.php"

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://appsliced.co",
                "Pragma": "no-cache",
                "Referer": "https://appsliced.co/login",
            }

            body = {
                "email": EMAIL,
                "password": PASSWORD,
                "rememberme": "1",
                "type": "1",
            }

            session.cookies.update(
                {
                    "loc": "US",
                    "refurl": f"%252Fapps%253Fsearch%253D{app_id}",
                    "cstatus": "1",
                    "UISstate": "3939313032",
                }
            )

            response = session.post(
                url,
                headers=headers,
                data=body,
                allow_redirects=True,
            )

            soup = BeautifulSoup(response.content, features="html.parser")

        div = soup.find("div", class_="10u title")
        a = div.find("a")

        response = requests.get(a.attrs["href"])
        self.soup = BeautifulSoup(response.content, features="html.parser")

    @property
    def price_history(self) -> list[str]:
        ul = self.soup.find("ul", class_="price_changes")

        if not ul:
            return []

        price_history = []

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
