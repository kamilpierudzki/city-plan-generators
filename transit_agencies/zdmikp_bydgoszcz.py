import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_list_str, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error


def _get_tram_and_bus_link_tags_2(
        link_tags: list[bs4.element.Tag],
        tram_start_idx: int,
        tram_end_idx: int
) -> (list[bs4.element.Tag], list[bs4.element.Tag]):
    tram_link_tags: list[bs4.element.Tag] = []
    bus_link_tags: list[bs4.element.Tag] = []

    for link_tag in link_tags:
        text = link_tag.text
        if len(text) == 0:
            continue

        try:
            link_number = int(text)
            is_tram_number = link_number in range(tram_start_idx, tram_end_idx + 1)
            if is_tram_number:
                tram_link_tags.append(link_tag)
            else:
                bus_link_tags.append(link_tag)
        except ValueError:
            bus_link_tags.append(link_tag)

    return tram_link_tags, bus_link_tags


def _get_tram_and_bus_link_tags(p_tags: list[bs4.element.Tag]) -> (list[bs4.element.Tag], list[bs4.element.Tag]):
    tram_link_tags: list[bs4.element.Tag] = []
    bus_link_tags: list[bs4.element.Tag] = []

    is_tram = None
    for p_tag in p_tags:
        if "TRAM" in p_tag.text:
            is_tram = True
            continue
        if "BUS" in p_tag.text:
            is_tram = False
            continue
        if len(p_tag.text) == 0:
            continue

        link = p_tag.find_next('a')
        if link is None:
            continue

        if is_tram is None:
            continue
        elif is_tram:
            tram_link_tags.append(link)
            continue
        elif not is_tram:
            bus_link_tags.append(link)
            continue

    return tram_link_tags, bus_link_tags


class ZdmikpBydgoszcz(TransitAgency):
    _MAIN_PAGE_LINK = "http://www.zdmikp.bydgoszcz.pl/rozklady/paczka/linie.htm"
    _SUB_PAGE_LINK = "http://www.zdmikp.bydgoszcz.pl/rozklady/paczka/"
    # UPDATE THIS INFORMATION
    _TRAM_LINE_RANGE_BEGIN = 1
    _TRAM_LINE_RANGE_END = 11

    _tram_link_tags: list[bs4.element.Tag] = []
    _bus_link_tags: list[bs4.element.Tag] = []

    def __init__(self):
        super().__init__()
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_link_tags = main_page_content.find_all('a')
        tram_bus_link_tags_pair = _get_tram_and_bus_link_tags_2(
            all_link_tags,
            self._TRAM_LINE_RANGE_BEGIN,
            self._TRAM_LINE_RANGE_END
        )
        self._tram_link_tags = tram_bus_link_tags_pair[0]
        self._bus_link_tags = tram_bus_link_tags_pair[1]

    def get_transit_agency_name(self) -> str:
        return "Zarząd Dróg Miejskich i Komunikacji Publicznej w Bydgoszczy"

    def _get_line_direction_json_file_name(self) -> str:
        return "zdmikp_bydgoszcz.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "zdmikp_bydgoszcz_stops.json"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._tram_link_tags, self._SUB_PAGE_LINK)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        return create_links_dictionary(self._bus_link_tags, self._SUB_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["kierunki"]
        )

        directions: list[str] = []
        for td_tag in filtered_td_tags:
            direction = td_tag.contents[2].text
            directions.append(direction)

        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["td_jszary"]
        )

        stops_link_tags: list[bs4.element.Tag] = []
        for td_tag in filtered_td_tags:
            link_tags = td_tag.find_all('a')
            stops_link_tags = stops_link_tags + link_tags

        stops_set: set[str] = set()
        for link_tag in stops_link_tags:
            stop_name = link_tag.text
            stops_set.add(stop_name)

        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    zdikp_bydgoszcz = ZdmikpBydgoszcz()
    zdikp_bydgoszcz.generate_data()
    print_list_str(zdikp_bydgoszcz.get_transit_agency_name(), zdikp_bydgoszcz.errors)
