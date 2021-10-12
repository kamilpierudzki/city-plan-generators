import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, create_links_dictionary, print_list_str
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error, \
    find_all_containing_any_of_values_or_error, find_all_attribute_matching_or_error


def _read_directions(div_tags: list[bs4.element.Tag]) -> [str]:
    _directions = []
    for div_direction in div_tags:
        strong_tag = div_direction.find_next('strong')
        direction = strong_tag.text
        _directions.append(direction)
    if len(_directions) == 0:
        raise Exception("Error: did not found directions in _read_directions")
    return _directions


class GzmZtm(TransitAgency):
    _MAIN_PAGE_LINK = "https://rj.metropoliaztm.pl"

    _main_page_content: bs4.BeautifulSoup = None
    _all_divs: bs4.element.ResultSet = None

    def __init__(self):
        super().__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        self._all_divs = self._main_page_content.find_all('div')

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_div_tags = sub_page_content.find_all('div')
        try:
            filtered_div_direction_tags = find_all_attribute_matching_or_error(
                elements=all_div_tags,
                attribute="class",
                value_to_match=["list-group-item", "list-group-item-warning"]
            )
            directions = _read_directions(filtered_div_direction_tags)
            return directions
        except Exception:
            url_sub_sub_page_link = self._get_link_to_sub_sub_page_when_exception(all_div_tags)
            return self._get_directions_for_sub_page(url_sub_sub_page_link)

    def _get_link_to_sub_sub_page_when_exception(self, all_div_tags: list[bs4.element.Tag]) -> str:
        div_with_links = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["panel-heading", "text-center"]
        )
        sub_sub_page_link_tag = div_with_links.find_next('a')
        url_sub_sub_page_link = self._MAIN_PAGE_LINK + sub_sub_page_link_tag.attrs['href']
        return url_sub_sub_page_link

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_div = find_first_attribute_matching_or_error(
            elements=self._all_divs,
            attribute="id",
            value_to_match="line_type-2-1"
        )
        tram_divs = tram_div.find_next('div')
        tram_timetable_links = tram_divs.find_all('a')
        return create_links_dictionary(tram_timetable_links, self._MAIN_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_divs = find_all_containing_any_of_values_or_error(
            elements=self._all_divs,
            attribute="id",
            values_to_match=["line_type-2-1", "line_type-5-1", "line_type-1-13", "line_type-1-1", "line_type-1-2",
                             "line_type-1-9", "line_type-1-7"]
        )
        bus_timetable_links = []
        for bus_div in bus_divs:
            bus_sub_div = bus_div.find_next('div')
            all_bus_sub_div_links = bus_sub_div.find_all('a')
            bus_timetable_links.append(all_bus_sub_div_links)

        bus_timetable_links_flatten = [item for sublist in bus_timetable_links for item in sublist]

        return create_links_dictionary(bus_timetable_links_flatten, self._MAIN_PAGE_LINK)

    def get_transit_agency_name(self) -> str:
        return "Górnośląsko-Zagłębowska Metropolia ZTM"

    def _get_line_direction_json_file_name(self) -> str:
        return "gzm_ztm.json"

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_link_tags = sub_page_content.find_all('a')
        try:
            filtered_link_tags = find_all_containing_any_of_values_or_error(
                elements=all_link_tags,
                attribute="class",
                values_to_match=[
                    ["direction-list-group-item", "list-group-item", "direction-non-primary"],
                    ["direction-list-group-item", "list-group-item"]
                ]
            )

            result_set: set[str] = set()
            for link_tag in filtered_link_tags:
                raw_text = link_tag.text
                stop = raw_text.strip()
                result_set.add(stop)

            result_list = list(result_set)
            return result_list
        except Exception:
            all_div_tags = sub_page_content.find_all('div')
            url_sub_sub_page_link = self._get_link_to_sub_sub_page_when_exception(all_div_tags)
            return self._get_all_stops_for_link(url_sub_sub_page_link)


if __name__ == '__main__':
    gzm_ztm = GzmZtm()
    gzm_ztm.generate_data()
    print_list_str(gzm_ztm.get_transit_agency_name(), gzm_ztm.errors)
