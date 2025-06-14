from datetime import date

import pytest

from search_ai import Filters


@pytest.mark.parametrize(
    'field, value, expected',
    [
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
        ('all_keywords', 'ai', '"ai"'),
        ('all_keywords', ['ai', 'ml'], '"ai" "ml"'),
        ('all_keywords', ['ai'], '"ai"'),
        ('any_keywords', 'ai', '"ai"'),
        ('any_keywords', ['ai', 'ml'], '("ai" | "ml")'),
        ('any_keywords', ['ai'], '"ai"'),
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
        ('exclude_all_keywords', 'ads', '-ads'),
        ('exclude_all_keywords', ['spam', 'click'], '-spam -click'),
        ('exclude_all_keywords', ['ads'], '-ads'),
        ('exclude_exact_phrases', 'bad ad', '-"bad ad"'),
        ('exclude_exact_phrases', ['fake news', 'scam'], '-"fake news" -"scam"'),
        ('not_in_title', 'promo', '-intitle:promo'),
        ('not_in_title', ['clickbait', 'ad'], '-intitle:clickbait -intitle:ad'),
        ('not_in_url', 'track', '-inurl:track'),
        ('not_in_url', ['ref', 'share'], '-inurl:ref -inurl:share'),
        ('not_in_text', 'cookie', '-intext:cookie'),
        ('not_in_text', ['ads', 'popup'], '-intext:ads -intext:popup'),
        ('stock', 'TSLA', 'stock:TSLA'),
        ('stock', 'BRK.A', 'stock:BRK.A'),
    ],
)
def test_individual_fields(field, value, expected):
    filter_obj = Filters(**{field: value})
    compiled_filters = filter_obj.compile_filters()
    assert compiled_filters == expected


@pytest.mark.parametrize(
    'field, value',
    [
        ('filetype', 'toolongfilename123'),
        ('filetype', 'we!rd'),
        ('exclude_filetypes', 'we!rd'),
        ('exclude_filetypes', ['bad!', '!!']),
        ('all_keywords', 'with space'),
        ('all_keywords', 'with space'),
        ('any_keywords', ['ok', 'bad word']),
        ('any_keywords', ['ok', 'bad word']),
        ('exclude_all_keywords', 'white space'),
        ('exclude_all_keywords', ['fine', 'break this']),
        ('tlds', '.invalidtld'),
        ('tlds', ['.edu', '.badzone']),
        ('exclude_tlds', '.invalidtld'),
        ('exclude_tlds', ['.edu', '.badzone']),
        ('stock', 'U.S. Energy'),
        ('stock', 'HOOOOD'),
        ('stock', ['NET']),
    ],
)
def test_field_validation(field, value):
    with pytest.raises(ValueError, match=r'.*'):
        Filters(**{field: value})


@pytest.mark.parametrize(
    'kwargs, expected',
    [
        ({'sites': 'example.com', 'all_keywords': 'ai'}, 'site:example.com "ai"'),
        ({'tlds': '.com', 'all_keywords': ['ai', 'llm']}, 'site:.com "ai" "llm"'),
        ({'tlds': '.com', 'any_keywords': ['ai', 'llm']}, 'site:.com ("ai" | "llm")'),
        (
            {
                'sites': ['a.com', 'b.com'],
                'filetype': 'pdf',
                'exact_phrases': ['openai api', 'machine learning'],
                'https_only': True,
                'in_title': ['research', 'ai'],
            },
            '(site:a.com | site:b.com) filetype:pdf "openai api" "machine learning" inurl:https intitle:research intitle:ai',
        ),
        (
            {
                'exclude_sites': ['spam.com'],
                'exclude_all_keywords': ['ads', 'clickbait'],
                'not_in_url': 'ref',
                'exclude_https': True,
            },
            '-site:spam.com -inurl:https -ads -clickbait -inurl:ref',
        ),
        (
            {
                'tlds': ['.gov', '.edu'],
                'before': date(2020, 1, 1),
                'after': date(2010, 5, 10),
                'in_text': ['compliance', 'report'],
                'exclude_tlds': ['.xyz'],
            },
            '(site:.gov | site:.edu) intext:compliance intext:report before:2020-01-01 after:2010-05-10 -site:.xyz',
        ),
        (
            {
                'filetype': 'ppt',
                'exclude_filetypes': ['exe', 'bat'],
                'any_keywords': ['presentation', 'slides'],
            },
            'filetype:ppt ("presentation" | "slides") -filetype:exe -filetype:bat',
        ),
        (
            {'in_url': 'docs', 'in_title': 'introduction', 'exclude_exact_phrases': 'outdated info'},
            'intitle:introduction inurl:docs -"outdated info"',
        ),
        (
            {'sites': 'example.org', 'in_text': 'summary', 'exclude_all_keywords': 'draft'},
            'site:example.org intext:summary -draft',
        ),
        (
            {'sites': 'example.org', 'in_text': 'summary', 'exclude_all_keywords': ['draft', 'ai', 'bot']},
            'site:example.org intext:summary -draft -ai -bot',
        ),
        (
            {
                'sites': ['news.com', 'media.com'],
                'in_url': ['breaking', 'live'],
                'not_in_text': ['subscribe', 'cookie'],
            },
            '(site:news.com | site:media.com) inurl:breaking inurl:live -intext:subscribe -intext:cookie',
        ),
        (
            {
                'exact_phrases': 'deep learning',
                'exclude_exact_phrases': 'deprecated method',
                'in_title': 'tutorial',
                'not_in_title': 'sponsored',
            },
            '"deep learning" intitle:tutorial -"deprecated method" -intitle:sponsored',
        ),
        (
            {
                'in_title': 'earnings',
                'stock': 'ORCL',
                'sites': ['finance.yahoo.com', 'reuters.com'],
            },
            '(site:finance.yahoo.com | site:reuters.com) stock:ORCL intitle:earnings',
        ),
    ],
)
def test_combined_fields(kwargs, expected):
    filter_obj = Filters(**kwargs)
    compiled_filters = filter_obj.compile_filters()
    assert compiled_filters == expected
