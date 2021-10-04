import bs4.element
import requests
from bs4 import BeautifulSoup


def create_links_dictionary(vehicle_link_tags: list[bs4.element.Tag], sub_link_to_append: str = "") -> dict[str, str]:
    dictionary: dict[str, str] = {}
    for link in vehicle_link_tags:
        line_number = link.text.strip()
        link_to_timetable = sub_link_to_append + link.attrs['href']
        dictionary[line_number] = link_to_timetable
    if len(dictionary) == 0:
        raise Exception("Error, vehicle tag link list is empty")
    return dictionary


def get_page_content(url: str, session: requests.Session = None, verify=True) -> BeautifulSoup:
    if session is None:
        r = requests.get(url, verify=verify)
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
