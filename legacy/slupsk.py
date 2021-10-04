import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "slupsk.json"
MAIN_PAGE_LINK = "https://rozklad.zimslupsk.pl/"


def slupsk():
    bus_dict = get_vehicle_types_dicts()
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Słupsk",
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
    _all_links = _main_page_content.find_all('a')
    _bus_timetable_links = filter_links_class_stretched_link_p_3_text_center_badge_badge_primary_d_block(_all_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _bus_dict


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filter_links_class_stretched_link_p_3_text_center_badge_badge_primary_d_block(all_links):
    _filtered = []
    for link in all_links:
        try:
            a_class = link.attrs['class']
            is_class_matching = a_class == ['stretched-link', 'p-3', 'text-center', 'badge', 'badge-primary', 'd-block']
            if is_class_matching:
                _filtered.append(link)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("Error: class did not find")
    return _filtered


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = MAIN_PAGE_LINK + link.attrs['href']
        _dict[line_number] = link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        try:
            _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])
            _number = key
            for direction in _directions_for_subpage:
                _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
                _vehicle_data.append(_row)
                print(_row)
        except Exception:
            print("Error: link " + vehicle_data_dict[key] + " is broken")
            continue
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_is = _sub_page_content.find_all('i')
    _i = find_first_i_class_bi_bi_arrow_right_short_mr_2(_all_is)
    _directions = get_directions(_i)
    if len(_directions) == 0:
        raise Exception("Error: did not find directions")
    return _directions


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_first_i_class_bi_bi_arrow_right_short_mr_2(all_is):
    for i in all_is:
        try:
            a_class = i.attrs['class']
            is_class_matching = a_class == ['bi', 'bi-arrow-right-short', 'mr-2']
            if is_class_matching:
                return i
        except KeyError:
            print()
    return None


def get_directions(i):
    _next_i = i.find_next('a')
    _raw_text = _next_i.text
    _directions = _raw_text.split(' - ')
    return _directions


if __name__ == '__main__':
    slupsk()
