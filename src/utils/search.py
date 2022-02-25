import re


def clean_search_text(text: str):
    """
    Used for `search_text` argument when destined for FULLTEXT search queries
    The search text should already be validated as a string by jsonschema

    This function is called because:
    * Fulltext will error on only non-alphanum characters
    * Legacy: some apps send over the search text prefixed with "prefix:"
    and so that must be corrected for. So a prefixed "prefix:"
    will always be stripped off
    """
    if not text:
        return text

    # Legacy compensation
    if text.startswith('prefix:'):
        text = text[7:]

    if not text:
        return text

    if not re.search(r'[a-zA-Z0-9]', text):
        return ''

    return text
