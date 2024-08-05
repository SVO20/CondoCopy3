import base64
import zlib
from pathlib import Path


def expand_compressed(bytes) -> str:
    # Decompresses and decodes bytes that were compressed and encoded
    return zlib.decompress(base64.b64decode(bytes)).decode('utf-8')


def compress_text(text) -> bytes:
    # Compresses and encodes a given text string
    compressed = zlib.compress(text.encode('utf-8'))
    return base64.b64encode(compressed)


def bytes_to_pep8_constant(bytes, const_name, line_length):
    # Formats bytes into a Python constant with specified line length
    const_name = const_name.upper()
    str_bytes = bytes.decode('utf-8')
    chunks = [str_bytes[i:i + line_length] for i in range(0, len(str_bytes), line_length)]

    const_str = f"{const_name} = (\n"
    for chunk in chunks:
        const_str += f"    b'{chunk}'\n"
    const_str = const_str.rstrip('\n') + ")"

    return const_str


# Place here the path to file to encode to Python-code
filename = Path("../settings.toml")
constant_name = 'default_settings'


if __name__ == "__main__":
    # Read from file
    with open(filename, 'r') as file:
        content = file.read()

    # Compress and encode to bytes
    compressed_bytes = compress_text(content)
    assert content == expand_compressed(compressed_bytes)

    # Convert bytes to a code
    str_python_constant = bytes_to_pep8_constant(compressed_bytes, constant_name, 80)

    print(str_python_constant)      # bytestring formatted as a Python constant
                                    # (complies with PEP8 with a specified codeline length)"

