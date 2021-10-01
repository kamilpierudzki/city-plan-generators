import bs4

from TransitAgency import TransitAgency
from implementation.commons.generation_util import get_page_content, create_links_dictionary, print_list_str
from implementation.commons.search_util import find_all_attribute_matching_or_error, find_all_containing_value_or_error, \
    find_first_attribute_matching_or_error


def _read_active_direction(div_active_direction: bs4.element.Tag) -> str:
    _div = div_active_direction.div
    _active_direction = _div.text.strip()
    return _active_direction


def _read_inactive_direction(div_inactive_direction: bs4.element.Tag) -> str:
    all_link_tags = div_inactive_direction.find_all('a')
    matching_link_tag = find_first_attribute_matching_or_error(
        elements=all_link_tags,
        attribute="class",
        value_to_match=["timetable-link", "timetable-link-image", "timetable-link-image-secondary"]
    )
    inactive_direction = matching_link_tag.text.strip()
    return inactive_direction


class WtpWarszawa(TransitAgency):
    _MAIN_PAGE_LINK = "https://www.wtp.waw.pl/rozklady-jazdy/"

    _main_page_content: bs4.BeautifulSoup = None
    _tram_tag_links: list[bs4.element.Tag] = None
    _bus_tag_links: list[bs4.element.Tag] = None
    _filtered_links: list[bs4.element.Tag] = None

    def __init__(self):
        super(WtpWarszawa, self).__init__()
        self._main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_links = self._main_page_content.find_all('a')
        self._filtered_links = find_all_attribute_matching_or_error(
            elements=all_links,
            attribute="class",
            value_to_match=["timetable-button", "timetable-button-tile"]
        )

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_divs = sub_page_content.find_all('div')
        active_div = find_first_attribute_matching_or_error(
            elements=all_divs,
            attribute="class",
            value_to_match=["timetable-line-header-summary-details-direction-item", "active"]
        )
        active_direction = _read_active_direction(active_div)

        try:
            inactive_div = find_first_attribute_matching_or_error(
                elements=all_divs,
                attribute="class",
                value_to_match=["timetable-line-header-summary-details-direction-item"]
            )
            inactive_direction = _read_inactive_direction(inactive_div)
            return [active_direction, inactive_direction]
        except Exception:
            return [active_direction]

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_tag_links = find_all_containing_value_or_error(
            elements=self._filtered_links,
            attribute="aria-label",
            value_to_match="Tramwaj"
        )
        return create_links_dictionary(tram_tag_links)

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_tag_links = find_all_containing_value_or_error(
            elements=self._filtered_links,
            attribute="aria-label",
            value_to_match="Autobus"
        )
        return create_links_dictionary(bus_tag_links)

    def get_transit_agency_name(self) -> str:
        return "Warszawski Transport Publiczny"

    def _get_line_direction_json_file_name(self) -> str:
        return "wtp_warszawa.json"

    def _get_stops_data_json_file_name(self) -> str:
        return "wtp_warszawa_stops.json"

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_link_tags = sub_page_content.find_all('a')
        direction_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["timetable-link", "timetable-route-point", "name", "active", "follow"]
        )
        result_set: set[str] = set()
        for link_tag in direction_link_tags:
            raw_text = link_tag.text
            stop = raw_text.strip()
            result_set.add(stop)

        result_list = list(result_set)
        return result_list


if __name__ == '__main__':
    wtp_warszawa = WtpWarszawa()
    wtp_warszawa.generate_data()
    print_list_str(wtp_warszawa.get_transit_agency_name(), wtp_warszawa.errors)
