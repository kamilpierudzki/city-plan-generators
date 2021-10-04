import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_list_str, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_attribute_matching_or_error, find_all_containing_values_or_error


class MpkLodz(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.mpk.lodz.pl/rozklady/linie.jsp"
    _SUB_PAGE_LINK = "https://www.mpk.lodz.pl/rozklady/"

    _all_link_tags: list[bs4.element.Tag] = None

    def __init__(self):
        super().__init__()
        main_page_link = get_page_content(self._MAIN_PAGE_LINK, verify=False)
        self._all_link_tags = main_page_link.find_all('a')

    def get_transit_agency_name(self) -> str:
        return "MPK Łódź"

    def _get_line_direction_json_file_name(self) -> str:
        return "mpk_lodz.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "mpk_lodz_stops.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        first_link_tag = find_first_attribute_matching_or_error(
            elements=self._all_link_tags,
            attribute="name",
            value_to_match="Tramwaje"
        )
        td_tag = first_link_tag.parent.nextSibling
        tram_all_tags = td_tag.find_all('a')
        return create_links_dictionary(tram_all_tags, self._SUB_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_first_link_tag = find_first_attribute_matching_or_error(
            elements=self._all_link_tags,
            attribute="name",
            value_to_match="Autobusy"
        )
        bus_td_tag = bus_first_link_tag.parent.nextSibling
        bus_all_tags = bus_td_tag.find_all('a')

        night_bus_first_link_tag = find_first_attribute_matching_or_error(
            elements=self._all_link_tags,
            attribute="name",
            value_to_match="Nocne"
        )
        night_bus_td_tag = night_bus_first_link_tag.parent.nextSibling
        night_bus_all_tags = night_bus_td_tag.find_all('a')

        return create_links_dictionary(bus_all_tags + night_bus_all_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, verify=False)
        all_div_tags = sub_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["headSign"]
        )

        directions: list[str] = []
        for div_tag in filtered_div_tags:
            direction = str(div_tag.contents[0])
            directions.append(direction)
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, verify=False)
        all_link_tags = sub_page_content.find_all('a')
        filtered_link_tags = find_all_containing_values_or_error(
            elements=all_link_tags,
            attribute="href",
            values_to_match=["direction", "lineId", "timetableId", "stopNumber"]
        )

        stops_set: set[str] = set()
        for link_tag in filtered_link_tags:
            stop_name = link_tag.text.strip()
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mpk_lodz = MpkLodz()
    mpk_lodz.generate_data()
    print_list_str(mpk_lodz.get_transit_agency_name(), mpk_lodz.errors)
