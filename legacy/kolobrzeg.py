import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "kolobrzeg.json"
MAIN_PAGE_LINK = "http://www.km.kolobrzeg.pl/rozklad-jazdy"
SUB_PAGE_LINK = "http://www.km.kolobrzeg.pl"


def kolobrzeg():
    bus_dict = get_vehicle_types_dicts()
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Kołobrzeg",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: [],
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)


def get_vehicle_types_dicts():
    _main_page_content = get_main_page_content()
    _all_divs = _main_page_content.find_all('div')
    _filtered_divs = filter_div_class_jm_module_content_clearfix(_all_divs)
    _div_containing_lines = find_div_class_dj_megamenu_wrapper(_filtered_divs)
    _ul_containing_lines = _div_containing_lines.find_next('ul')
    _bus_timetable_links = _ul_containing_lines.find_all('a')
    _bus_timetable_links_without_first = _bus_timetable_links[1:]
    _bus_dict = create_dict(_bus_timetable_links_without_first)
    return _bus_dict


def find_div_class_dj_megamenu_wrapper(all_divs):
    for div in all_divs:
        try:
            nested_div = div.find_next('div')
            a_class = nested_div.attrs['class']
            is_class_matching = a_class == ['dj-megamenu-wrapper']
            if is_class_matching:
                return nested_div
        except KeyError:
            print()
    raise Exception("Error: div class=\'dj-megamenu-wrapper\' not found")


def filter_div_class_jm_module_content_clearfix(all_divs):
    _filtered = []
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['jm-module-content', 'clearfix']
            if is_class_matching:
                _filtered.append(div)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("Error: div class=\'jm-module-content clearfix\' not found")
    return _filtered


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = SUB_PAGE_LINK + link.attrs['href']
        _dict[line_number] = link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        number = get_line_from_key(key)
        directions = get_directions_from_key(key)
        for direction in directions:
            _row = {VEHICLE_NUMBER_ATTR: number, VEHICLE_DESTINATION_ATTR: direction}
            if _row not in _vehicle_data:
                _vehicle_data.append(_row)
                print(_row)
    return _vehicle_data


def get_line_from_key(key):
    _split = key.split(":")
    _line = _split[0]
    return _line


def get_directions_from_key(key):
    _split_1 = key.split(": ")
    _split_2 = _split_1[1].split(" - ")
    return _split_2


if __name__ == '__main__':
    kolobrzeg()
