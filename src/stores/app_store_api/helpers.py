import requests

URL = "https://amp-api.apps.apple.com/v1/catalog/US/apps/{app_id}"

EXTEND = [
    "description",
    "developerInfo",
    "distributionKind",
    "editorialVideo",
    "fileSizeByDevice",
    "messagesScreenshots",
    "platformAttributes",
    "privacy",
    "privacyPolicyUrl",
    "privacyPolicyText",
    "promotionalText",
    "screenshotsByType",
    "supportURLForLanguage",
    "versionHistory",
    "videoPreviewsByType",
    "websiteUrl",
]
INCLUDE = [
    "genres",
    "developer",
    "reviews",
    "merchandised-in-apps",
    "customers-also-bought-apps",
    "developer-other-apps",
    "app-bundles",
    "top-in-apps",
]

PLATFORMS = ["appletv", "ipad", "iphone", "mac", "watch"]


PARAMS = {
    "platform": "web",
    "additionalPlatforms": ",".join(PLATFORMS),
    "extend": ",".join(EXTEND),
    "include": ",".join(INCLUDE),
    "l": "en-us",
    "limit[merchandised-in-apps]": 20,
}

HEADERS = {
    "authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNSRjVITkJHUFEifQ.eyJpc3MiOiI4Q1UyNk1LTFM0IiwiaWF0IjoxNjA4MTYzMDk0LCJleHAiOjE2MTExODcwOTR9.FSD4K4vZZy1ouVlyS-vXLQavXuXVo5kbWQGnYIgoWq8Am5DwP7tJlLjkLxeZ0k3D2XDH0F6fAN4FwfUYCIqXGw",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0)",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://apps.apple.com",
    "referer": "https://apps.apple.com/",
}


def get_data(app_id: str) -> dict:
    url = URL.format(app_id=app_id)
    response = requests.get(url, headers=HEADERS, params=PARAMS)
    return response.json()["data"][0]
