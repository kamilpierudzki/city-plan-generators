import datetime
import json

import requests
from bs4 import BeautifulSoup

from legacy.commons import VEHICLE_NUMBER_ATTR, VEHICLE_DESTINATION_ATTR, CITY_ATTR, TIMESTAMP_ATTR, READABLE_TIME_ATTR, \
    APP_VERSION_ATTR, TRAMS_ATTR, BUSES_ATTR, create_json_file

MAIN_PAGE_URL = "https://rozklady.mpk.krakow.pl"

TRAM_SEARCH_KEY = "tram"
BUS_SEARCH_KEY = "auto"

JSON_FILE_NAME = "krakow.json"


def krakow():
    tram_dict, bus_dict = get_vehicle_types_dicts()

    session = requests.Session()
    enable_mobile_version_of_sub_page(session)

    trams = get_vehicle_data(session, tram_dict)
    buses = get_vehicle_data(session, bus_dict)

    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp())
    formatted_date = current_time.strftime("%d-%m-%Y")

    json_dict = {
        CITY_ATTR: "Kraków",
        TIMESTAMP_ATTR: timestamp,
        READABLE_TIME_ATTR: formatted_date,
        APP_VERSION_ATTR: 1,
        TRAMS_ATTR: trams,
        BUSES_ATTR: buses
    }

    raw_json = json.dumps(json_dict, ensure_ascii=False)
    create_json_file(raw_json, JSON_FILE_NAME)
    pass


def get_vehicle_data(session, vehicle_data_dict):
    _vehicle_data = []
    for key in vehicle_data_dict:
        sub_page_content = get_sub_page_content(session, vehicle_data_dict[key])
        directions = get_directions(sub_page_content)
        number = key
        for direction in directions:
            row = {VEHICLE_NUMBER_ATTR: number, VEHICLE_DESTINATION_ATTR: direction}
            _vehicle_data.append(row)
            print(row)
    return _vehicle_data


def get_directions(sub_page_content):
    _all_p_elements = get_all_p_elements(sub_page_content)
    _filtered_p_elements_with_directions = filtered_style_text_align_left(_all_p_elements)
    _directions = strip_direction_texts(_filtered_p_elements_with_directions)
    return _directions


def strip_direction_texts(p_elements_with_directions):
    key_to_filter_1 = "Od:"
    key_to_filter_2 = "Do:"
    _directions = []
    for p in p_elements_with_directions:
        raw_text = p.text
        raw_text = raw_text.strip()
        raw_text = raw_text.replace(key_to_filter_1, '')
        raw_text = raw_text.replace(key_to_filter_2, '')
        raw_text = raw_text.strip()
        _directions.append(raw_text)
    return _directions


def filtered_style_text_align_left(all_p_elements):
    _filtered = []
    for p in all_p_elements:
        try:
            a_style = p.attrs['style']
            is_style_matching = a_style == ' text-align: left; '
            if is_style_matching:
                _filtered.append(p)
        except KeyError:
            print()
    return _filtered


def get_all_p_elements(sub_page_content):
    _all_p_elements = sub_page_content.find_all('p')
    return _all_p_elements


def enable_mobile_version_of_sub_page(session):
    _r1 = session.get(MAIN_PAGE_URL)
    _r2 = session.get(MAIN_PAGE_URL + '/?akcja=telefon')
    print()


def get_sub_page_content(session, url):
    _r = session.get(url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def get_vehicle_types_dicts():
    _main_page_content = get_main_page_content(MAIN_PAGE_URL)

    _all_tds = _main_page_content.find_all('td')
    _filtered_tds_tuples = filtered_linia_table_left_and_vehicle_types(_all_tds)

    _td_trams = get_td_vehicle_types(TRAM_SEARCH_KEY, _filtered_tds_tuples)
    _all_links_for_trams = get_all_links_for_vehicle_type(_td_trams)
    _tram_dict = create_dict_number_link_for_vehicle_type(_all_links_for_trams)

    _td_buses = get_td_vehicle_types(BUS_SEARCH_KEY, _filtered_tds_tuples)
    _all_links_for_buses = get_all_links_for_vehicle_type(_td_buses)
    _bus_dict = create_dict_number_link_for_vehicle_type(_all_links_for_buses)
    return _tram_dict, _bus_dict


def get_main_page_content(main_page_url):
    _r = requests.get(main_page_url)
    _raw_content = _r.content
    _content = BeautifulSoup(_raw_content, 'html.parser')
    return _content


def filtered_linia_table_left_and_vehicle_types(all_tds):
    _filtered = []
    for td in all_tds:
        try:
            a_class = td.attrs['class']
            is_class_matching = a_class == ['linia_table_left']
            if is_class_matching:
                vehicle_type = td.parent.previous_sibling.previous_sibling.contents[1].text.strip()
                _filtered.append((vehicle_type, td))
        except KeyError:
            print()
    return _filtered


def get_td_vehicle_types(vehicle_type_search_key, filtered_tds_tuples):
    _td_vehicle_type_tuples = filtered_vehicle_types_tuples(vehicle_type_search_key, filtered_tds_tuples)
    _td_vehicle_types = strip_tuples(_td_vehicle_type_tuples)
    return _td_vehicle_types


def filtered_vehicle_types_tuples(vehicle_type_key, tds_tuples):
    _filtered = []
    for td_tuple in tds_tuples:
        raw_vehicle_type = td_tuple[0]
        is_vehicle_type = raw_vehicle_type.find(vehicle_type_key) >= 0
        if is_vehicle_type:
            _filtered.append(td_tuple)
    return _filtered


def strip_tuples(td_vehicle_type_tuples):
    _list = []
    for _tuple in td_vehicle_type_tuples:
        _list.append(_tuple[1])
    return _list


def get_all_links_for_vehicle_type(td_vehicle_types):
    _all_links = []
    for td_vehicle_type in td_vehicle_types:
        a_list = get_a_list_for_vehicle_type(td_vehicle_type)
        _all_links = _all_links + a_list
    return _all_links


def create_dict_number_link_for_vehicle_type(_all_links_for_vehicle_types):
    _dict = {}
    for link_for_vehicle_type in _all_links_for_vehicle_types:
        number = link_for_vehicle_type.text.strip()
        link = find_link_to_sub_page(link_for_vehicle_type)
        _dict[number] = link
    return _dict


def find_link_to_sub_page(link_for_vehicle_type):
    _link = MAIN_PAGE_URL + link_for_vehicle_type.attrs['href']
    return _link


def get_a_list_for_vehicle_type(td_vehicle_type):
    _all_a_for_td = td_vehicle_type.find_all('a')
    return _all_a_for_td


if __name__ == '__main__':
    krakow()
