import bs4
import requests

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error


def _filtered_vehicle_type_td_tags(
        search_key: str,
        type_td_tags_pairs: list[tuple[str, bs4.element.Tag]]
) -> list[bs4.element.Tag]:
    filtered: list[bs4.element.Tag] = []
    for type_td_tags in type_td_tags_pairs:
        vehicle_type = type_td_tags[0]
        if search_key in vehicle_type:
            td_tags = type_td_tags[1]
            filtered.append(td_tags)
    if len(filtered) == 0:
        raise Exception("Error, _filtered_vehicle_type_td_tags did not filter any element.")
    return filtered


def _get_link_tags_from_td_tags(vehicle_type_td_tags: list[bs4.element.Tag]) -> list[bs4.element.Tag]:
    link_tags: list[bs4.element.Tag] = []
    for td_tag in vehicle_type_td_tags:
        td_link_tags = td_tag.find_all('a')
        link_tags = link_tags + td_link_tags
    if len(link_tags) == 0:
        raise Exception("Error, _get_link_tags_from_td_tags did not find any element")
    return link_tags


def _enable_mobile_version_of_sub_page(url: str, session: requests.Session):
    _r1 = session.get(url)
    _r2 = session.get(url + '/?akcja=telefon')
    print()


def _read_directions(p_tags: list[bs4.element.Tag]) -> list[str]:
    key_to_filter_1 = "Od:"
    key_to_filter_2 = "Do:"
    directions: list[str] = []
    for p_tag in p_tags:
        direction = p_tag.text.strip()
        direction = direction.replace(key_to_filter_1, "")
        direction = direction.replace(key_to_filter_2, "")
        direction = direction.strip()
        directions.append(direction)
    if len(directions) == 0:
        raise Exception("Error, _read_directions did not find eny direction")
    return directions


class MpkKrakow(TransitAgency):
    _MAIN_PAGE_LINK = "https://rozklady.mpk.krakow.pl"
    _TRAM_SEARCH_KEY = "tram"
    _BUS_SEARCH_KEY = "auto"
    _OTHER_SEARCH_KEY = "Linie aglomeracyjne nocne"

    _main_page_content: bs4.BeautifulSoup = None
    _vehicle_type_td_tags_pairs: list[tuple[str, bs4.element.Tag]] = []
    _session: requests.Session = None

    def __init__(self):
        super().__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_td_tags = self._main_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["linia_table_left"]
        )
        for td_tag in filtered_td_tags:
            vehicle_type = td_tag.parent.previous_sibling.previous_sibling.text.strip()
            self._vehicle_type_td_tags_pairs.append((vehicle_type, td_tag))
        self._session = requests.Session()
        _enable_mobile_version_of_sub_page(self._MAIN_PAGE_LINK, self._session)

    def get_transit_agency_name(self) -> str:
        return "MPK Kraków"

    def _get_line_direction_json_file_name(self) -> str:
        return "mpk_krakow.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "mpk_krakow-stops.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_td_tags = _filtered_vehicle_type_td_tags(self._TRAM_SEARCH_KEY, self._vehicle_type_td_tags_pairs)
        link_tags = _get_link_tags_from_td_tags(tram_td_tags)
        return create_links_dictionary(link_tags, self._MAIN_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_td_tags = _filtered_vehicle_type_td_tags(self._BUS_SEARCH_KEY, self._vehicle_type_td_tags_pairs)
        bus_link_tags = _get_link_tags_from_td_tags(bus_td_tags)

        other_td_tags = _filtered_vehicle_type_td_tags(self._OTHER_SEARCH_KEY, self._vehicle_type_td_tags_pairs)
        other_link_tags = _get_link_tags_from_td_tags(other_td_tags)
        link_tags = bus_link_tags + other_link_tags
        return create_links_dictionary(link_tags, self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, self._session)
        all_p_tags = sub_page_content.find_all('p')
        filtered_p_tags = find_all_attribute_matching_or_error(
            elements=all_p_tags,
            attribute="style",
            value_to_match=" text-align: left; "
        )
        directions = _read_directions(filtered_p_tags)
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, self._session)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="style",
            value_to_match=" text-align: left;  "
        )

        stops_set: set[str] = set()
        for td_tag in filtered_td_tags:
            div_tag = td_tag.find_next('div')
            stop_name = div_tag.text.strip()
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mpk_krakow = MpkKrakow()
    mpk_krakow.generate_data()
    print_list_str(mpk_krakow.get_transit_agency_name(), mpk_krakow.errors)
