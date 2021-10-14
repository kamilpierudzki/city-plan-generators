import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error


class MzkGorzowWielkopolski(TransitAgency):
    _MAIN_PAGE_LINK = "https://mzk-gorzow.com.pl/51-rozklad-jazdy.html"
    _HEADERS: dict[str, str] = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }

    _filtered_div_tags: list[bs4.element.Tag] = None

    def __init__(self):
        super().__init__()

        main_page_content = get_page_content(self._MAIN_PAGE_LINK, headers=self._HEADERS)
        all_div_tags = main_page_content.find_all('div')
        self._filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["lineName"]
        )

    def get_transit_agency_name(self) -> str:
        return "MZK Gorzów Wielkopolski"

    def _get_line_direction_json_file_name(self) -> str:
        return "mzk_gorzow_wielkopolski.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_link_tags: list[bs4.element.Tag] = []
        for div_tag in self._filtered_div_tags:
            if "tram" in div_tag.text:
                sibling_div_tag = div_tag.nextSibling
                link_tags = sibling_div_tag.find_all('a')
                tram_link_tags = tram_link_tags + link_tags

        return create_links_dictionary(tram_link_tags)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_link_tags: list[bs4.element.Tag] = []
        for div_tag in self._filtered_div_tags:
            if "bus" in div_tag.text:
                sibling_div_tag = div_tag.nextSibling
                link_tags = sibling_div_tag.find_all('a')
                bus_link_tags = bus_link_tags + link_tags

        return create_links_dictionary(bus_link_tags)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, headers=self._HEADERS)
        all_link_tags = sub_page_content.find_all('a')
        filtered_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["direction_station"]
        )

        directions_set: set[str] = set()
        for link_tag in filtered_link_tags:
            direction = link_tag.text
            direction = direction.strip()
            directions_set.add(direction)

        directions_list = list(directions_set)
        return directions_list

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url, headers=self._HEADERS)
        all_tr_tags = sub_page_content.find_all('tr')
        filtered_tr_tags = find_all_attribute_matching_or_error(
            elements=all_tr_tags,
            attribute="class",
            value_to_match=["stations"]
        )

        stops_set: set[str] = set()
        for tr_tag in filtered_tr_tags:
            stop = tr_tag.text
            stop = stop.strip()
            stops_set.add(stop)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mzk_gorzow_wielkopolski = MzkGorzowWielkopolski()
    mzk_gorzow_wielkopolski.generate_data()
    print_generation_results(mzk_gorzow_wielkopolski.get_transit_agency_name(), mzk_gorzow_wielkopolski.errors)
