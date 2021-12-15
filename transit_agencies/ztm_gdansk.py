import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error, \
    find_all_containing_value_or_error


def _read_direction(td_tag: bs4.element.Tag) -> str:
    direction_raw = td_tag.contents[1].contents[0]
    direction = str(direction_raw)
    return direction


def _read_stop_name(link_tag: bs4.element.Tag) -> str:
    stop_name = link_tag.text
    return stop_name


class ZtmGdansk(TransitAgency):
    _MAIN_PAGE_LINK = "https://ztm.gda.pl/rozklady/"
    _TRAM_SEARCH_KEY = "Tram"
    _BUS_SEARCH_KEY = "bus"

    def __init__(self):
        super().__init__()
        self._link_parent_img_tags: list[bs4.element.Tag] = []

    def generate_data(self):
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_link_tags = main_page_content.find_all('a')
        filtered_link_tags = find_all_attribute_matching_or_error(
            elements=all_link_tags,
            attribute="class",
            value_to_match=["main-route-number", "block"]
        )
        for link_tag in filtered_link_tags:
            parent_tag = link_tag.parent
            img_tag = parent_tag.find_next("img")
            self._link_parent_img_tags.append(img_tag)
        TransitAgency.generate_data(self)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_td_tags = sub_page_content.find_all('td')
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["text-center", "bg-lightgray"]
        )
        directions: list[str] = []
        for td_tag in filtered_td_tags:
            directions.append(_read_direction(td_tag))
        return directions

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        tram_link_tags = self._get_vehicle_link_tags(self._TRAM_SEARCH_KEY)
        return create_links_dictionary(tram_link_tags, self._MAIN_PAGE_LINK)

    def _get_vehicle_link_tags(self, search_key: str) -> list[bs4.element.Tag]:
        vehicle_img_tags = find_all_containing_value_or_error(
            elements=self._link_parent_img_tags,
            attribute="alt",
            value_to_match=search_key
        )
        vehicle_link_tags: list[bs4.element.Tag] = []
        for img_tag in vehicle_img_tags:
            link_tag = img_tag.find_next('a')
            vehicle_link_tags.append(link_tag)
        return vehicle_link_tags

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        bus_link_tags = self._get_vehicle_link_tags(self._BUS_SEARCH_KEY)
        return create_links_dictionary(bus_link_tags, self._MAIN_PAGE_LINK)

    def get_transit_agency_name(self) -> str:
        return "ZTM Gdańsk"

    def _get_data_file_name_without_extension(self) -> str:
        return "ztm_gdansk"

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content = get_page_content(url)
        all_div_tags = sub_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["sprite", "pd"]
        )
        link_tags_containing_stop_name: list[bs4.element.Tag] = []
        for div_tag in filtered_div_tags:
            link_tag = div_tag.find_next('a')
            link_tags_containing_stop_name.append(link_tag)

        stops_set: set[str] = set()
        for link_tag in link_tags_containing_stop_name:
            stops_set.add(_read_stop_name(link_tag))

        stops_list: list[str] = list(stops_set)
        return stops_list


if __name__ == '__main__':
    ztm_gdansk = ZtmGdansk()
    ztm_gdansk.generate_data()
    print_generation_results(ztm_gdansk.get_transit_agency_name(), ztm_gdansk.errors)
