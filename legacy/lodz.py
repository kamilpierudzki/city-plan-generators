import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

MAIN_LINK = "https://www.mpk.lodz.pl/rozklady/linie.jsp"
LINK_TO_EACH = "https://www.mpk.lodz.pl/rozklady/"

JSON_FILE_NAME = "lodz.json"


def lodz():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Łódź",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: trams,
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)


def get_vehicle_types_dicts():
    _main_page_content = get_main_page_content()
    _all_links = _main_page_content.find_all('a')
    _tram_link = find_vehicle_type_link('Tramwaje', _all_links)
    _bus_link = find_vehicle_type_link('Autobusy', _all_links)

    _trams_td_with_links = find_td_with_links_for_vehicle_type(_tram_link)
    _buses_td_with_links = find_td_with_links_for_vehicle_type(_bus_link)

    _tram_timetable_links = find_all_links_for_td(_trams_td_with_links)
    _bus_timetable_links = find_all_links_for_td(_buses_td_with_links)

    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def find_all_links_for_td(td_with_links):
    _all_links = td_with_links.find_all('a')
    return _all_links


def find_td_with_links_for_vehicle_type(vehicle_type_link):
    _td = vehicle_type_link.parent.nextSibling
    return _td


def get_main_page_content():
    _r = requests.get(MAIN_LINK, verify=False)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_vehicle_type_link(vehicle_type, all_links):
    for link in all_links:
        try:
            name = link.attrs['name']
            is_name_matching = name == vehicle_type
            if is_name_matching:
                return link
        except KeyError:
            print()
    return None


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = link.attrs['href']
        _dict[line_number] = LINK_TO_EACH + link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])

        if len(_directions_for_subpage) == 0:
            print("ERROR: " + vehicle_data_dict[key])
            continue

        _number = key
        for direction in _directions_for_subpage:
            _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(_row)
            print(_row)
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_divs = _sub_page_content.find_all('div')
    _filtered_divs = filtered_divs_head_sign_class(_all_divs)
    _directions = []
    for filtered_div in _filtered_divs:
        _direction_from_div = get_direction_from_div(filtered_div)
        _directions.append(_direction_from_div)
    return _directions


def get_direction_from_div(filtered_div):
    _direction = filtered_div.contents[0]
    return _direction


def get_sub_page_content(url):
    _r = requests.get(url, verify=False)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_divs_head_sign_class(all_divs):
    _result = []
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['headSign']
            if is_class_matching:
                _result.append(div)
        except KeyError:
            print()
    return _result


if __name__ == '__main__':
    lodz()
