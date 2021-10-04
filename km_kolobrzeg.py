import bs4.element

from TransitAgency import TransitAgency
from implementation.commons.generation_util import get_page_content, create_links_dictionary, print_list_str
from implementation.commons.search_util import find_all_attribute_matching_or_error, \
    find_first_attribute_matching_or_error


def _get_line_number(key: str) -> str:
    split = key.split(": ")
    number = split[0]
    return number


class KmKolobrzeg(TransitAgency):
    _MAIN_PAGE_LINK = "http://www.km.kolobrzeg.pl/rozklad-jazdy"
    _SUB_PAGE_LINK = "http://www.km.kolobrzeg.pl"

    def get_transit_agency_name(self) -> str:
        return "KM Kołobrzeg"

    def _get_line_direction_json_file_name(self) -> str:
        return "km_kolobrzeg.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "km_kolobrzeg_stops.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["jm-module-content", "clearfix"]
        )

        nested_div_tags: list[bs4.element.Tag] = []
        for div_tag in filtered_div_tags:
            nested_div_tag = div_tag.find_next('div')
            nested_div_tags.append(nested_div_tag)

        first_nested_div_tags = find_first_attribute_matching_or_error(
            elements=nested_div_tags,
            attribute="class",
            value_to_match=["dj-megamenu-wrapper"]
        )
        ul_tag = first_nested_div_tags.find_next('ul')
        bus_link_tags = ul_tag.find_all('a')
        bus_link_tags_without_first = bus_link_tags[1:]

        bus_dictionary = create_links_dictionary(bus_link_tags_without_first, self._SUB_PAGE_LINK)
        bus_dictionary_updated: dict[str, str] = {}
        for key in bus_dictionary:
            bus_dictionary_updated[_get_line_number(key)] = bus_dictionary[key]
        return bus_dictionary_updated

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_h1_tags = sub_page_content.find_all('h1')
        first_h1_tag = find_first_attribute_matching_or_error(
            elements=all_h1_tags,
            attribute="itemprop",
            value_to_match="headline"
        )
        raw_directions_text = first_h1_tag.text
        directions_combined = raw_directions_text.split(": ")[1]
        directions_cut = directions_combined.split(" - ")
        return [directions_cut[0].strip(), directions_cut[1].strip()]

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        try:
            filtered_td_tags = find_all_attribute_matching_or_error(
                elements=all_td_tags,
                attribute="width",
                value_to_match="35%"
            )
        except Exception:
            filtered_td_tags = find_all_attribute_matching_or_error(
                elements=all_td_tags,
                attribute="style",
                value_to_match="width: 35%;"
            )

        stops_set: set[str] = set()
        for td_tag in filtered_td_tags:
            raw_text = td_tag.text.strip()
            if len(raw_text) > 0:
                stops_set.add(raw_text)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    km_kolobrzeg = KmKolobrzeg()
    km_kolobrzeg.generate_data()
    print_list_str(km_kolobrzeg.get_transit_agency_name(), km_kolobrzeg.errors)
