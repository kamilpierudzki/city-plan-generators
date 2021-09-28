import bs4.element
import requests
from bs4 import BeautifulSoup


def create_links_dictionary(vehicle_tag_links: list[bs4.element.Tag], sub_link_to_append: str = "") -> dict[str, str]:
    _dictionary: dict[str, str] = {}
    for link in vehicle_tag_links:
        line_number = link.text.strip()
        link_to_timetable = sub_link_to_append + link.attrs['href']
        _dictionary[line_number] = link_to_timetable
    if len(_dictionary) == 0:
        raise Exception("Error, vehicle tag link list is empty")
    return _dictionary


def get_page_content(link: str) -> BeautifulSoup:
    _r = requests.get(link)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def print_list(transit_agency: str, elements: list[str]):
    print(transit_agency)
    for e in elements:
        print(e)
