from src.utils.search import clean_search_text


def test_validate_search_text():
    in_out = [
        ('prefix:', ''),
        ('prefix:e', 'e'),
        ('prefix:esch prefix:col', 'esch prefix:col'),
        ('prefix:~!@#$%^&*()_+', ''),
        ('~!@#$%^&*()_+', ''),
        (', , ,', ''),
        ('Xanthomonas-like sp. V4.BO.41', 'Xanthomonas-like sp. V4.BO.41'),
    ]

    for input, output in in_out:
        assert clean_search_text(input) == output
