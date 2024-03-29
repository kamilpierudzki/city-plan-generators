import base64
from typing import Callable

import bs4.element
import requests
from bs4 import BeautifulSoup


def create_links_dictionary(
        vehicle_link_tags: list[bs4.element.Tag],
        sub_link_to_append: str = "",
        line_number_processor: Callable[[bs4.element.Tag], str] = lambda link_tag: link_tag.text.strip(),
        link_processor: Callable[[bs4.element.Tag, str], str] = lambda link_tag,
                                                                       sub_link_to_append: sub_link_to_append +
                                                                                           link_tag.attrs['href'],
) -> dict[str, str]:
    dictionary: dict[str, str] = {}
    for link_tag in vehicle_link_tags:
        line_number = line_number_processor(link_tag)
        link_to_timetable = link_processor(link_tag, sub_link_to_append)
        dictionary[line_number] = link_to_timetable
    if len(dictionary) == 0:
        raise Exception("Error, vehicle tag link list is empty")
    return dictionary


def get_page_content(url: str, session: requests.Session = None, verify=True, headers=None) -> BeautifulSoup:
    if headers is None:
        headers = {}
    if session is None:
        r = requests.get(url, verify=verify, headers=headers)
        raw_content = r.content
    else:
        r = session.get(url)
        raw_content = r.content

    content = BeautifulSoup(raw_content, 'html.parser')
    return content


def print_generation_results(transit_agency: str, elements: list[str]):
    print(transit_agency)
    for e in elements:
        print(e)


def encrypt_json(raw_json: str) -> str:
    encoded_json = raw_json.encode("utf-8")
    encoded_base64_bytes_before_shift = base64.b64encode(encoded_json)
    encoded_base64_bytes_shifted: list[int] = []
    for byte in encoded_base64_bytes_before_shift:
        encoded_base64_bytes_shifted.append(byte + 1)
    encoded_base64_bytes_after_shift = bytes(encoded_base64_bytes_shifted)
    encrypted_json = encoded_base64_bytes_after_shift.decode("utf-8")
    return encrypted_json
