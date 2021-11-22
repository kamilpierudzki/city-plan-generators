import bs4.element

from transit_agencies.commons.TransitAgency import TransitAgency
from transit_agencies.commons.generation_util import get_page_content, print_generation_results
from transit_agencies.commons.search_util import find_all_attribute_matching_or_error


def _read_number_for_div(img_tag: bs4.element.Tag) -> str:
    src = img_tag['src']
    split: list[str] = src.split("/")
    split_len: int = len(split)
    number_with_file_extension = split[split_len - 1]
    number = number_with_file_extension.replace(".png", "")
    return number


class MzkBielskoBiala(TransitAgency):
    _MAIN_PAGE_LINK = "https://komunikacja.um.bielsko.pl/index.php/rozklad-jazdy-do-wydruku/"
    _STOPS_PAGE_LINK = "https://komunikacja.um.bielsko.pl/index.php/linie-komunikacyjne/"

    _number_div_tags_dict: dict[str, bs4.element.Tag] = {}
    _stops_number_div_tags_dict: dict[str, bs4.element.Tag] = {}

    def generate_data(self):
        main_page_content = get_page_content(self._MAIN_PAGE_LINK)
        all_div_tags = main_page_content.find_all('div')
        filtered_div_tags = find_all_attribute_matching_or_error(
            elements=all_div_tags,
            attribute="class",
            value_to_match=["wp-block-media-text", "alignwide", "is-stacked-on-mobile"]
        )

        for div_tag in filtered_div_tags:
            img_tag = div_tag.find_next('img')
            number = _read_number_for_div(img_tag)
            self._number_div_tags_dict[number] = div_tag

        stops_content = get_page_content(self._STOPS_PAGE_LINK)
        stops_all_div_tags = stops_content.find_all('div')
        stops_filtered_div_tags = find_all_attribute_matching_or_error(
            elements=stops_all_div_tags,
            attribute="class",
            value_to_match=["wp-block-media-text", "alignwide", "is-stacked-on-mobile"]
        )
        for div_tag in stops_filtered_div_tags:
            img_tag = div_tag.find_next('img')
            number = _read_number_for_div(img_tag)
            self._stops_number_div_tags_dict[number] = div_tag
        TransitAgency.generate_data(self)

    def get_transit_agency_name(self) -> str:
        return "MZK Bielsko-Biała"

    def _get_data_file_name_without_extension(self) -> str:
        return "mzk_bielsko_biala"

    def _get_tram_links_dictionary(self) -> dict[str, str]:
        return {}

    def _get_bus_links_dictionary(self) -> dict[str, str]:
        result_dict: dict[str, str] = {}
        for key in self._number_div_tags_dict:
            result_dict[key] = "http|" + key  # to satisfy verification
        return result_dict

    def _get_directions_for_sub_page(self, url: str) -> list[str]:
        line_number = url.split("|")[1]
        directions: list[str] = []
        for key in self._number_div_tags_dict:
            if key == line_number:
                div_tag = self._number_div_tags_dict[key].find_next('div')
                strong_tags = div_tag.find_all('strong')
                for strong_tag in strong_tags:
                    direction = strong_tag.text
                    direction = direction.replace(":", "")
                    direction = direction.replace("Kierunek", "")
                    directions.append(direction.strip())
                break
        return directions

    def _get_all_stops_for_link(self, url: str) -> list[str]:
        line_number = url.split("|")[1]
        stops_set: set[str] = set()
        for key in self._stops_number_div_tags_dict:
            if key == line_number:
                p_tag = self._stops_number_div_tags_dict[key].find_next('p')
                stops_combined = p_tag.text
                stops_combined = stops_combined.replace("Trasa wariantowa", "")
                stops_combined = stops_combined.replace("…", "")
                stops_combined = stops_combined.replace("(wybrane kursy)", "")
                stops_combined = stops_combined.replace(":", "")
                stops_combined = stops_combined.replace("Kierunek", "")
                stops_split = stops_combined.split("–")
                for stop in stops_split:
                    stops_set.add(stop.strip())
                break
        stops_list = list(stops_set)
        return stops_list


if __name__ == '__main__':
    mzk_bielsko_biala = MzkBielskoBiala()
    mzk_bielsko_biala.generate_data()
    print_generation_results(mzk_bielsko_biala.get_transit_agency_name(), mzk_bielsko_biala.errors)
