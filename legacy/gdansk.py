import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

JSON_FILE_NAME = "gdansk.json"

MAIN_LINK = "https://ztm.gda.pl/rozklady/"


def gdansk():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Gdańsk",
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
    _filtered_links = filter_links_of_class_main_route_number_block(_all_links)
    _tram_timetable_links = filter_vehicle_type_links("Tram", _filtered_links)
    _bus_timetable_links = filter_vehicle_type_links("bus", _filtered_links)

    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def filter_vehicle_type_links(vehicle_type, links):
    _result = []
    for link in links:
        parent = link.parent
        img = parent.contents[0]
        try:
            img_alt = img.attrs['alt']
            is_img_alt_vehicle_type = vehicle_type in img_alt
            if is_img_alt_vehicle_type:
                _result.append(link)
        except KeyError:
            print()
    return _result


def get_main_page_content():
    _r = requests.get(MAIN_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filter_links_of_class_main_route_number_block(all_links):
    _result = []
    for link in all_links:
        try:
            a_class = link.attrs['class']
            is_class_matching = a_class == ['main-route-number', 'block']
            if is_class_matching:
                _result.append(link)
        except KeyError:
            print()
    return _result


def create_dict(timetable_links):
    _dict = {}
    for link in timetable_links:
        line_number = link.text.strip()
        link_to_timetable = link.attrs['href']
        _dict[line_number] = MAIN_LINK + link_to_timetable
    return _dict


def get_vehicle_data(vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])

        if len(_directions_for_subpage) == 0:
            print("Error: sub-page is empty for:" + vehicle_data_dict[key])
            continue

        _number = key
        for direction in _directions_for_subpage:
            _row = {VEHICLE_NUMBER_ATTR: _number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(_row)
            print(_row)
    return _vehicle_data


def get_directions_for_subpage(url_to_subpage):
    _sub_page_content = get_sub_page_content(url_to_subpage)
    _all_tds = _sub_page_content.find_all('td')
    _filtered_tds = filtered_td_of_class_text_center_bg_light_gray(_all_tds)
    _result = []
    for filtered_td in _filtered_tds:
        direction = get_direction(filtered_td)
        _result.append(direction)
    return _result


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_td_of_class_text_center_bg_light_gray(all_tds):
    _result = []
    for td in all_tds:
        try:
            a_class = td.attrs['class']
            is_class_matching = a_class == ['text-center', 'bg-lightgray']
            if is_class_matching:
                _result.append(td)
        except KeyError:
            print()
    return _result


def get_direction(td):
    _direction = td.contents[1].contents[0]
    return _direction


if __name__ == '__main__':
    gdansk()
