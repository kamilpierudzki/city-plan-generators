import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_all_containing_value_or_error


def _filtered_vehicle_type_tables(search_key, all_table_tags) -> list[bs4.element.Tag]:
    _filtered_tables: list[bs4.element.Tag] = []
    for table in all_table_tags:
        table_text = table.text.casefold()
        if search_key in table_text:
            _filtered_tables.append(table)
    if len(_filtered_tables) == 0:
        raise Exception("Error, _filtered_vehicle_type_tables did not filter any element")
    return _filtered_tables


def _filter_all_link_tags_for_table_tags(vehicle_type_table_tags):
    _result = []
    for table in vehicle_type_table_tags:
        _all_links = table.find_all('a')
        for link in _all_links:
            _result.append(link)
    if len(_result) == 0:
        raise Exception("Error, _filter_all_link_tags_for_table_tags did not filter any element")
    return _result


def _get_all_unique_directions(h4_tags) -> list[str]:
    _directions_set: set[str] = set()
    for h4 in h4_tags:
        raw_text_1 = str(h4.contents[0])
        _directions_set.add(raw_text_1)
        raw_text_2 = str(h4.contents[2])
        _directions_set.add(raw_text_2)
    if len(_directions_set) == 0:
        raise Exception("Error, _get_all_unique_directions did not find any element")
    return list(_directions_set)


def _unique_stops(link_tags: list[bs4.element.Tag]) -> list[str]:
    _result_set: set[str] = set()
    for link in link_tags:
        _result_set.add(link.text)
    if len(_result_set) == 0:
        raise Exception("Error: unique_stops did not return any element")
    return list(_result_set)


class MpkWroclaw(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.wroclaw.pl/rozklady-jazdy"
    _TRAM_SEARCH_KEY = "tram"
    _BUS_SEARCH_KEY = "auto"

    _main_page_content: bs4.BeautifulSoup = None
    _all_table_tags: list[bs4.element.Tag] = None

    def __init__(self):
        super().__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_table_tags = self._main_page_content.find_all('table')
        self._all_table_tags = find_all_attribute_matching_or_error(
            elements=all_table_tags,
            attribute="class",
            value_to_match=["table", "table-bordered", "table-schedule"]
        )

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_h4_tags = sub_page_content.find_all('h4')
        filtered_h4_tags = find_all_attribute_matching_or_error(
            elements=all_h4_tags,
            attribute="class",
            value_to_match=["text-normal"]
        )
        return _get_all_unique_directions(filtered_h4_tags)

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        filtered_tram_table_tags = _filtered_vehicle_type_tables(self._TRAM_SEARCH_KEY, self._all_table_tags)
        all_links_in_table_tags = _filter_all_link_tags_for_table_tags(filtered_tram_table_tags)
        return create_links_dictionary(all_links_in_table_tags, self._MAIN_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        filtered_bus_table_tags = _filtered_vehicle_type_tables(self._BUS_SEARCH_KEY, self._all_table_tags)
        all_links_in_table_tags = _filter_all_link_tags_for_table_tags(filtered_bus_table_tags)
        return create_links_dictionary(all_links_in_table_tags, self._MAIN_PAGE_LINK)

    def get_transit_agency_name(self) -> str:
        return "MPK Wrocław"

    def _get_line_direction_json_file_name(self) -> str:
        return "mpk_wroclaw.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "mpk_wroclaw_stops.json"

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_link_tags = sub_page_content.find_all('a')
        filtered_link_tags = find_all_containing_value_or_error(
            elements=all_link_tags,
            attribute="href",
            value_to_match="/przystanek"
        )
        return _unique_stops(filtered_link_tags)


if __name__ == '__main__':
    mpk_wroclaw = MpkWroclaw()
    mpk_wroclaw.generate_data()
    print_list_str(mpk_wroclaw.get_transit_agency_name(), mpk_wroclaw.errors)
