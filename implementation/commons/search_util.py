import bs4.element


def find_first_attribute_matching_or_error(
        elements: bs4.element.ResultSet,
        attribute: str,
        value_to_match
) -> bs4.element.Tag:
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_attr_matching = attr == value_to_match
            if is_attr_matching:
                return element
        except KeyError:
            continue
    raise Exception("Error, elements do not match")


def find_all_attribute_matching_or_error(
        elements: bs4.element.ResultSet,
        attribute: str,
        value_to_match
) -> list[bs4.element.Tag]:
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_attr_matching = attr == value_to_match
            if is_attr_matching:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result


def find_all_containing_value_or_error(elements: list[bs4.element.Tag], attribute: str, value_to_match: str):
    _result: list[bs4.element.Tag] = []
    for element in elements:
        try:
            attr = element.attrs[attribute]
            is_element_containing_value = value_to_match in attr
            if is_element_containing_value:
                _result.append(element)
        except KeyError:
            continue
    if len(_result) == 0:
        raise Exception("Error, elements do not match")
    return _result
