import colorama
import urllib.parse

async def url_decode(text: str) -> str:
    """
    decodes a URL-encoded string until it is fully decoded 
    or a maximum of 100 iterations is reached.

    Args:
        text (str): The URL-encoded string to decode.

    Returns:
        str: The fully decoded string or the original string if no decoding is possible.
    """
    k = 0
    uq_prev = text
    while k < 100:
        uq = urllib.parse.unquote_plus(uq_prev)
        if uq == uq_prev:
            break
        else:
            uq_prev = uq
    return uq_prev

async def red_detected_print(text: str) -> str:
    """
    Checks if the text contains any red flags and returns a formatted string.

    Args:
        text (str): The text flags

    Returns:
        str: The formatted string with red flags highlighted.
    """
 
    return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}"

async def green_detected_print(text: str) -> str:
    """
    Checks if the text contains any red flags and returns a formatted string.

    Args:
        text (str): The text.

    Returns:
        str: The formatted string with green.
    """
 
    return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}"
    