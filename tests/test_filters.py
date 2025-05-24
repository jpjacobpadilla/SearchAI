from datetime import date

import pytest
import pydantic

from search_ai import Filters


@pytest.mark.parametrize('field, value, expected', [
    ('sites', 'example_a.com', 'site:example_a.com'),
    ('sites', ['example_a.com', 'example_b.com'], '(site:example_a.com | site:example_b.com)'),

    ('tlds', '.gov', 'site:.gov'),
    ('tlds', ['.gov', '.edu'], '(site:.gov | site:.edu)'),

    ('filetype', 'pdf', 'filetype:pdf'),

    ('https_only', True, 'inurl:https'),

    ('before', date(1999, 12, 31), 'before:1999-12-31'),
    ('before', date(2023, 6, 15), 'before:2023-06-15'),
    ('before', date(2100, 1, 1), 'before:2100-01-01'),

    ('after', date(2000, 1, 1), 'after:2000-01-01'),
    ('after', date(2022, 11, 30), 'after:2022-11-30'),
    ('after', date(2099, 12, 31), 'after:2099-12-31'),

    ('keywords', 'ai', '"ai"'),
    ('keywords', ['ai', 'ml'], '("ai" | "ml")'),
    ('keywords', ['ai'], '"ai"'),

    ('exact_phrases', 'openai api', '"openai api"'),
    ('exact_phrases', ['foo bar', 'baz qux'], '"foo bar" "baz qux"'),

    ('in_title', 'research', 'intitle:research'),
    ('in_title', ['ai', 'ml'], 'intitle:ai intitle:ml'),

    ('in_url', 'docs', 'inurl:docs'),
    ('in_url', ['api', 'ref'], 'inurl:api inurl:ref'),

    ('in_text', 'hello', 'intext:hello'),
    ('in_text', ['world', 'vector'], 'intext:world intext:vector'),

    ('exclude_sites', 'spam.com', '-site:spam.com'),
    ('exclude_sites', ['a.com', 'b.com'], '-site:a.com -site:b.com'),

    ('exclude_tlds', '.biz', '-site:.biz'),
    ('exclude_tlds', ['.xyz', '.info'], '-site:.xyz -site:.info'),

    ('exclude_filetypes', 'exe', '-filetype:exe'),
    ('exclude_filetypes', ['bin', 'dat'], '-filetype:bin -filetype:dat'),

    ('exclude_https', True, '-inurl:https'),

    ('exclude_keywords', 'ads', '-ads'),
    ('exclude_keywords', ['spam', 'click'], '-spam -click'),

    ('exclude_exact_phrases', 'bad ad', '-"bad ad"'),
    ('exclude_exact_phrases', ['fake news', 'scam'], '-"fake news" -"scam"'),

    ('not_in_title', 'promo', '-intitle:promo'),
    ('not_in_title', ['clickbait', 'ad'], '-intitle:clickbait -intitle:ad'),

    ('not_in_url', 'track', '-inurl:track'),
    ('not_in_url', ['ref', 'share'], '-inurl:ref -inurl:share'),

    ('not_in_text', 'cookie', '-intext:cookie'),
    ('not_in_text', ['ads', 'popup'], '-intext:ads -intext:popup')
])
def test_individual_fields(field, value, expected):
    filter_obj = Filters(**{field: value})
    compiled_filters = filter_obj.compile_filters()
    assert compiled_filters == expected


@pytest.mark.parametrize("field, value", [
    ("filetype", "toolongfilename123"),
    ("filetype", "we!rd"),

    ("exclude_filetypes", "we!rd"),
    ("exclude_filetypes", ["bad!", "!!"]),

    ("keywords", "with space"),
    ("keywords", ["ok", "bad word"]),

    ("exclude_keywords", "white space"),
    ("exclude_keywords", ["fine", "break this"]),

    ("tlds", ".invalidtld"),
    ("tlds",  [".edu", ".badzone"]),

    ("exclude_tlds", ".invalidtld"),
    ("exclude_tlds", [".edu", ".badzone"])
])
def test_field_validation(field, value):
    with pytest.raises(ValueError, match=".*"):
        Filters(**{field: value})
