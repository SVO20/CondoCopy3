import base64
import zlib


def expand_compressed(bytes) -> str:
    # Decompresses and decodes bytes that were compressed and encoded
    return zlib.decompress(base64.b64decode(bytes)).decode('utf-8')