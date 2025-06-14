from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator
from pydantic.types import StringConstraints
from publicsuffix2 import PublicSuffixList


FileType = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z0-9]{2,10}$')]
Keyword = Annotated[str, StringConstraints(pattern=r'^[^\s]+$')]
StockTicker = Annotated[str, StringConstraints(pattern=r'^[A-Z]{1,5}(\.[A-Z])?$')]

psl = PublicSuffixList()


def to_list(val: str | list[str] | None) -> list[str]:
    if val is None:
        return []
    return val.split(' ') if isinstance(val, str) else val


def group_includes(values: list[str], op: str | None = None) -> str:
    if not values:
        return ''

    if len(values) == 1:
        return f'{op}:{values[0]}' if op else f'"{values[0]}"'

    if op:
        parts = [f'{op}:{v}' for v in values]
    else:
        parts = [f'"{v}"' for v in values]

    return f'({" | ".join(parts)})'


def group_excludes(op: str, values: list[str]) -> list[str]:
    return [f'-{op}:{v}' for v in values]


def validate_tld(v: str | list[str] | None):
    # TODO: make type a generic type
    if not v:
        return v

    tlds = v if isinstance(v, list) else [v]
    for tld in tlds:
        if not psl.get_tld(tld, strict=True):
            raise ValueError(f'{tld!r} is an invalid top-level domain according to https://publicsuffix.org')

    return v


class Filters(BaseModel):
    # fmt: off
    sites: str | list[str] | None = Field(None, description='Only show results from specific domains')
    tlds: Annotated[str | list[str] | None, AfterValidator(validate_tld)] = Field(None, description='Only show results from specific top-level domains (e.g., .gov, .edu)')
    filetype: FileType | None = Field(None, description='Only show documents that are a specific file type. Note: Google only supports one filetype per search.')
    https_only: bool = Field(False, description='Only show websites that support HTTPS')
    stock: StockTicker | None = Field(None, description='Get results for a specific stock ticker')

    exclude_sites: str | list[str] | None = Field(None, description='Exclude results from specific domains')
    exclude_tlds: Annotated[str | list[str] | None, AfterValidator(validate_tld)] = Field(None, description='Exclude results from specific top-level domains')
    exclude_filetypes: FileType | list[FileType] | None = Field(None, description='Exclude documents with specific file types')
    exclude_https: bool = Field(False, description='Exclude HTTPS pages')

    before: date | None = Field(None, description='Only show results before this date')
    after: date | None = Field(None, description='Only show results after this date')

    any_keywords: Keyword | list[Keyword] | None = Field(None, description='Require at least one word anywhere in the page')
    all_keywords: Keyword | list[Keyword] | None = Field(None, description='Require specific words anywhere in the page')
    exact_phrases: str | list[str] | None = Field(None, description='Include results with exact phrases')

    exclude_all_keywords: Keyword | list[Keyword] | None = Field(None, description='Exclude pages containing certain words')
    exclude_exact_phrases: str | list[str] | None = Field(None, description='Exclude results with exact phrases')

    in_title: str | list[str] | None = Field(None, description='Require specific words in the title')
    in_url: str | list[str] | None = Field(None, description='Require specific words in the URL')
    in_text: str | list[str] | None = Field(None, description='Require specific words in the page text')

    not_in_title: str | list[str] | None = Field(None, description='Exclude pages with specific words in the title')
    not_in_url: str | list[str] | None = Field(None, description='Exclude pages with specific words in the URL')
    not_in_text: str | list[str] | None = Field(None, description='Exclude pages with specific words in the page text')
    # fmt: on

    def compile_filters(self) -> str:
        filters = []

        filters.append(group_includes(to_list(self.sites), 'site'))
        filters.append(group_includes(to_list(self.tlds), 'site'))
        filters.append(group_includes(to_list(self.stock), 'stock'))

        filters.append(group_includes(to_list(self.filetype), 'filetype'))
        filters.append(group_includes(to_list(self.any_keywords)))
        filters.extend([f'"{w}"' for w in to_list(self.all_keywords)])

        if self.exact_phrases:
            phrase_list = self.exact_phrases if isinstance(self.exact_phrases, list) else [self.exact_phrases]
            filters.extend([f'"{phrase}"' for phrase in phrase_list])

        if self.https_only:
            filters.append('inurl:https')

        filters.extend([f'intitle:{w}' for w in to_list(self.in_title)])
        filters.extend([f'inurl:{w}' for w in to_list(self.in_url)])
        filters.extend([f'intext:{w}' for w in to_list(self.in_text)])

        if self.before:
            filters.append(f'before:{self.before.isoformat()}')
        if self.after:
            filters.append(f'after:{self.after.isoformat()}')

        # Negative Filters
        if self.exclude_exact_phrases:
            phrase_list = (
                self.exclude_exact_phrases
                if isinstance(self.exclude_exact_phrases, list)
                else [self.exclude_exact_phrases]
            )
            filters.extend([f'-"{phrase}"' for phrase in phrase_list])

        filters.extend(group_excludes('site', to_list(self.exclude_sites)))
        filters.extend(group_excludes('site', to_list(self.exclude_tlds)))

        if self.exclude_https:
            filters.append('-inurl:https')

        filters.extend(group_excludes('filetype', to_list(self.exclude_filetypes)))
        filters.extend([f'-{w}' for w in to_list(self.exclude_all_keywords)])

        filters.extend([f'-inurl:{w}' for w in to_list(self.not_in_url)])
        filters.extend([f'-intitle:{w}' for w in to_list(self.not_in_title)])
        filters.extend([f'-intext:{w}' for w in to_list(self.not_in_text)])

        return ' '.join([f for f in filters if f])
