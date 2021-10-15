import base64

from transit_agencies.commons.generation_util import encrypt_json

if __name__ == '__main__':
    input = "łąka"

    encode_string = encrypt_json(input)

    decode_bytes_before = encode_string.encode("utf-8")
    decode_base64_bytes_shifted: list[int] = []
    for byte in decode_bytes_before:
        decode_base64_bytes_shifted.append(byte - 1)
    decode_bytes_after = bytes(decode_base64_bytes_shifted)
    decode_base64_bytes = base64.b64decode(decode_bytes_after)
    decode_string = decode_base64_bytes.decode("utf-8")

    assert decode_string == input