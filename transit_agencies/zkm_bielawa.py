from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results, get_page_content, create_links_dictionary
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error


class ZkmBielawa(TransitAgency):  # nie gotowe
    _MAIN_PAGE_LINK = "http://www.zkm.bielawa.pl"

    def get_transit_agency_name(self) -> str:
        return "ZKM Bielawa"

    def _get_data_file_name_without_extension(self) -> str:
        raise Exception("_get_json_file_name not implemented")

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        first_div_tags = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["box_padding_20"]
        )
        link_tags = first_div_tags.find_all('a')
        return create_links_dictionary(link_tags, self._MAIN_PAGE_LINK)

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        # sub_page_content = get_page_content(url)
        browser: WebDriver = webdriver.Firefox()
        browser.get("http://zkm.um.bielawa.pl/schedules/?lineID=4")
        html = browser.page_source
        sub_page_content = BeautifulSoup(html, 'html.parser')

        return []

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        raise Exception("_get_all_stops_for_link not implemented")


if __name__ == '__main__':
    zkm_bielawa = ZkmBielawa()
    zkm_bielawa.generate_data()
    print_generation_results(zkm_bielawa.get_transit_agency_name(), zkm_bielawa.errors)
