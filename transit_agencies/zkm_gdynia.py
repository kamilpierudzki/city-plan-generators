import bs4

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_generation_results, create_links_dictionary
from transit_agencies.commons.search_util import find_all_containing_values_or_error, \
    find_all_attribute_matching_or_error


def _process_sub_page_link(link_tag: bs4.element.Tag, sub_link_to_append: str) -> str:
    link: str = link_tag.attrs["href"]
    link = link.replace("..", "")
    link = link.replace(".htm", "0.htm")
    return sub_link_to_append + link


def _process_sub_page_link_number(link_tag: bs4.element.Tag) -> str:
    try:
        return link_tag.next_element.text.strip()
    except Exception:
        return link_tag.text.strip()


class ZkmGdynia(TransitAgency):
    _MAIN_PAGE_LINK = "https://zkmgdynia.pl/rozklady/linie0.htm"
    _SUB_PAGE_LINK = "https://zkmgdynia.pl"

    def get_transit_agency_name(self) -> str:
        return "ZKM Gdynia"

    def _get_data_file_name_without_extension(self) -> str:
        return "zkm_gdynia"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content: bs4.BeautifulSoup = get_page_content(self._MAIN_PAGE_LINK, verify=False)
        all_link_tags = main_page_content.find_all("a")
        filtered_link_tags = find_all_containing_values_or_error(
            elements=all_link_tags,
            attribute="href",
            values_to_match=["rozklady"]
        )
        return create_links_dictionary(
            filtered_link_tags,
            sub_link_to_append=self._SUB_PAGE_LINK,
            line_number_processor=_process_sub_page_link_number,
            link_processor=_process_sub_page_link
        )

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        sub_page_content: bs4.BeautifulSoup = get_page_content(url, verify=False)
        all_td_tags = sub_page_content.find_all("td")
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["bialy"]
        )

        directions_set: set[str] = set()
        for td_tag in filtered_td_tags:
            direction = td_tag.contents[1].text
            directions_set.add(direction)

        directions_list: list[str] = list(directions_set)
        return directions_list

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        sub_page_content: bs4.BeautifulSoup = get_page_content(url, verify=False)
        all_td_tags = sub_page_content.find_all("td")
        filtered_td_tags = find_all_attribute_matching_or_error(
            elements=all_td_tags,
            attribute="class",
            value_to_match=["bialy"]
        )

        stops_set: set[str] = set()
        for td_tag in filtered_td_tags:
            table_tag: bs4.element.Tag = td_tag.find_parent("table")
            all_link_tags: list[bs4.element.Tag] = table_tag.find_all("a")
            for link_tag in all_link_tags:
                stop = link_tag.text.strip()
                stops_set.add(stop)

        stops_list: list[str] = list(stops_set)
        return stops_list


if __name__ == '__main__':
    zkm_gdynia = ZkmGdynia()
    zkm_gdynia.generate_data()
    print_generation_results(zkm_gdynia.get_transit_agency_name(), zkm_gdynia.errors)
