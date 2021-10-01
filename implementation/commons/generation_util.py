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


def get_page_content(url: str, session: requests.Session = None) -> BeautifulSoup:
    if session is None:
        r = requests.get(url)
        raw_content = r.content
    else:
        r = session.get(url)
        raw_content = r.content

    content = BeautifulSoup(raw_content, 'html.parser')
    return content


def print_list_str(transit_agency: str, elements: list[str]):
    print(transit_agency)
    for e in elements:
        print(e)
