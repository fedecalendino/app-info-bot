from bs4 import BeautifulSoup


def find_all_by_attr(soup: BeautifulSoup, tag_name: str, attr_name: str):
    for tag in soup.find_all(tag_name):
        if attr_name in tag.attrs:
            yield tag


def find_by_attr(soup: BeautifulSoup, tag_name: str, attr_name: str):
    try:
        return next(find_all_by_attr(soup, tag_name, attr_name))
    except StopIteration:
        return None
