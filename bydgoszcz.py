import datetime
import json

import requests
from bs4 import BeautifulSoup

from commons import CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, \
    VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, create_json_file

# UPDATE THIS INFORMATION
TRAM_LINE_RANGE_BEGIN = 1
TRAM_LINE_RANGE_END = 11
# ------------------------

MAIN_PAGE_LINK = "http://www.zdmikp.bydgoszcz.pl/rozklady/paczka/linie.htm"

JSON_FILE_NAME = "bydgoszcz.json"
SUB_PAGE_LINK = "http://www.zdmikp.bydgoszcz.pl/rozklady/paczka/"


def bydgoszcz():
    tram_dict, bus_dict = get_vehicle_types_dicts()
    trams = get_vehicle_data(tram_dict)
    buses = get_vehicle_data(bus_dict)
    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Bydgoszcz",
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
    _all_linksa = _main_page_content.find_all('a')
    _tram_timetable_links, _bus_timetable_links = find_tram_and_bus_links(_all_linksa)
    _tram_dict = create_dict(_tram_timetable_links)
    _bus_dict = create_dict(_bus_timetable_links)
    return _tram_dict, _bus_dict


def get_main_page_content():
    _r = requests.get(MAIN_PAGE_LINK)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def find_tram_and_bus_links(all_links):
    _tram_timetable_links = []
    _bus_timetable_links = []
    for link in all_links:
        link_text = get_link_text(link)
        if len(link_text) == 0:
            continue

        try:
            link_number = int(link_text)
            is_tram_number = link_number in range(TRAM_LINE_RANGE_BEGIN, TRAM_LINE_RANGE_END + 1)
            if is_tram_number:
                _tram_timetable_links.append(link)
            else:
                _bus_timetable_links.append(link)
        except ValueError:
            _bus_timetable_links.append(link)

    return _tram_timetable_links, _bus_timetable_links


def get_link_text(link):
    _text = link.text
    return _text


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
        _directions_for_subpage = get_directions_for_subpage(vehicle_data_dict[key])

        if _directions_for_subpage is None:
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
    _filtered_td2 = filtered_h2_class_kierunki(_all_tds)
    _result = []
    for filtered_td in _filtered_td2:
        direction = get_direction_from_td(filtered_td)
        _result.append(direction)

    return _result


def get_sub_page_content(url):
    _r = requests.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_h2_class_kierunki(all_tds):
    _result = []
    for td in all_tds:
        try:
            a_class = td.attrs['class']
            is_class_matching = a_class == ['kierunki']
            if is_class_matching:
                _result.append(td)
        except KeyError:
            print()
    return _result


def get_direction_from_td(td):
    _direction = td.contents[2].text
    return _direction


if __name__ == '__main__':
    bydgoszcz()
