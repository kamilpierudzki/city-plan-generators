import datetime
import json

import requests
from bs4 import BeautifulSoup

from commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "lublin.json"

MAIN_LINK = "https://www.ztm.lublin.eu/pl/zaplanuj-podroz/mapy-i-schematy"
SUB_LINK = "https://www.ztm.lublin.eu"


def lublin():
    bus_dict = get_vehicle_types_dicts()
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Lublin",
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
    _filtered_divs = filter_fiv_class_col_xs_12_autobusy(_all_divs)
    _bus_timetable_links = get_all_links(_filtered_divs)
    _bus_dict = create_dict(_bus_timetable_links)
    return _bus_dict


def get_all_links(divs):
    _links = []
    for div in divs:
        all_links_in_div = div.find_all('a')
        _links.append(all_links_in_div)

    _flatten_links = [item for sublist in _links for item in sublist]
    return _flatten_links


def get_main_page_content():
    _r = requests.get(MAIN_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filter_fiv_class_col_xs_12_autobusy(all_divs):
    _filtered = []
    for div in all_divs:
        try:
            a_class = div.attrs['class']
            is_class_matching = a_class == ['col-xs-12', 'autobusy']
            if is_class_matching:
                _filtered.append(div)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("class \'col-xs-12 autobusy\' not found")
    return _filtered


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = SUB_LINK + link.attrs['href']
        _dict[line_number] = link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        try:
            _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])
        except Exception:
            print("Error: " + vehicle_data_dict[key] + "is broken")
            continue

        _number = key
        for direction in _directions_for_subpage:
            _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(_row)
            print(_row)
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_spans = _sub_page_content.find_all('span')
    _filtered_spans = filtered_span_class_icon_wheel(_all_spans)
    _directions = []
    for span in _filtered_spans:
        direction = filtered_span_direction(span)
        _directions.append(direction)
    if len(_directions) == 0:
        raise Exception("Error: directions not found")
    return _directions


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_span_class_icon_wheel(all_spans):
    _filtered = []
    for span in all_spans:
        try:
            a_class = span.attrs['class']
            is_class_matching = a_class == ['icon-wheel']
            if is_class_matching:
                _filtered.append(span)
        except KeyError:
            print()
    if len(_filtered) == 0:
        raise Exception("Error: class=icon-wheel not found")
    return _filtered


def filtered_span_direction(span):
    _direction = span.find_next('span').text
    return _direction


if __name__ == '__main__':
    lublin()
