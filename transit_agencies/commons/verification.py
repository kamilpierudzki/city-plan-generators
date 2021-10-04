def verify_links_dictionary(vehicle_links_dictionary: dict[str, str]):
    _is_not_dictionary = type(vehicle_links_dictionary) is not dict
    if _is_not_dictionary:
        return VerificationResult(is_error=True, error_message="verify_links_dictionary. Input argument is not directory")

    for key in vehicle_links_dictionary:
        _is_key_not_string = type(key) is not str
        if _is_key_not_string:
            return VerificationResult(is_error=True, error_message="verify_links_dictionary. Key is not string " + key)

        _is_value_not_string = type(vehicle_links_dictionary[key]) is not str
        if _is_value_not_string:
            return VerificationResult(is_error=True,
                                      error_message="verify_links_dictionary. Value is not string " + vehicle_links_dictionary[key])

        _is_value_not_containing_http = "http" not in vehicle_links_dictionary[key]
        if _is_value_not_containing_http:
            return VerificationResult(is_error=True,
                                      error_message="verify_links_dictionary. Value does not contain http " + vehicle_links_dictionary[key])
    return VerificationResult(is_error=False, error_message="no error")


def verify_lines_list(vehicle_lines_list: list[dict[str:str]]):
    _is_not_list = type(vehicle_lines_list) is not list
    if _is_not_list:
        return VerificationResult(is_error=True, error_message="verify_lines_list. Input argument is not list")

    for dictionary in vehicle_lines_list:
        for key in dictionary:
            _is_key_not_string = type(key) is not str
            if _is_key_not_string:
                return VerificationResult(is_error=True, error_message="verify_lines_list. Key is not string " + key)

            _is_value_not_string = type(dictionary[key]) is not str
            if _is_value_not_string:
                return VerificationResult(is_error=True,
                                          error_message="verify_lines_list. Value is not string " + dictionary[key])
    return VerificationResult(is_error=False, error_message="no error")


def verify_stops_dictionary(vehicle_stops_dictionary: dict[str, list[str]]):
    _is_not_dictionary = type(vehicle_stops_dictionary) is not dict
    if _is_not_dictionary:
        return VerificationResult(is_error=True, error_message="verify_stops_dictionary. Input argument is not directory")

    for key in vehicle_stops_dictionary:
        _is_key_not_string = type(key) is not str
        if _is_key_not_string:
            return VerificationResult(is_error=True, error_message="verify_stops_dictionary. Key is not string " + key)

    return VerificationResult(is_error=False, error_message="no error")


class VerificationResult:
    def __init__(self, is_error, error_message):
        self.is_error = is_error
        self.error_message = error_message
