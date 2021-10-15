from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.safari.webdriver import WebDriver

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import print_generation_results
from transit_agencies.commons.search_util import find_first_attribute_matching_or_error


class MpkRzeszow(TransitAgency):  # nie gotowe
    _MAIN_PAGE_LINK = "http://einfo.erzeszow.pl/?tab=2"

    def get_transit_agency_name(self) -> str:
        return "MPK Rzeszów"

    def _get_data_file_name_without_extension(self) -> str:
        raise Exception("_get_json_file_name not implemented")

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        browser: WebDriver = webdriver.Firefox()
        browser.get(self._MAIN_PAGE_LINK)
        html = browser.page_source
        main_page_content = BeautifulSoup(html, 'html.parser')

        # main_page_content = get_page_content_extended(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        first_div_tag = find_first_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="id",
            value_to_match="dvTab2RoutesContent"
        )

        browser.get("http://einfo.erzeszow.pl/Home/GetTracks?routeId=39714&ttId=0")
        html = browser.page_source
        sub_page_content = BeautifulSoup(html, 'html.parser')

        browser.quit()
        return {}

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        return []

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        return []


if __name__ == '__main__':
    mpk_rzeszow = MpkRzeszow()
    mpk_rzeszow.generate_data()
    print_generation_results(mpk_rzeszow.get_transit_agency_name(), mpk_rzeszow.errors)
