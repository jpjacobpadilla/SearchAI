from pydantic import BaseModel, Field
from datetime import date
from typing import Annotated
from pydantic.types import StringConstraints

# Reusable string constraints
TLD = Annotated[str, StringConstraints(pattern=r"^\.[a-zA-Z]{2,}$")]
FileType = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9]{2,10}$")]
Keyword = Annotated[str, StringConstraints(pattern=r"^[^\s]+$")]


class Filters(BaseModel):
    sites: str | list[str] | None = Field(None, description="Only show results from these domains (site:)")
    tlds: TLD | list[TLD] | None = Field(None, description="Only show results from these top-level domains (e.g., .gov, .edu)")
    filetypes: FileType | list[FileType] | None = Field(None, description="Only show documents with these file types (filetype:)")
    keywords: Keyword | list[Keyword] | None = Field(None, description="Require these words anywhere in the page")
    https_only: bool = Field(False, description="Only show HTTPS pages")

    title_contains: str | list[str] | None = Field(None, description="Require at least one of these words in the title")
    url_contains: str | list[str] | None = Field(None, description="Require at least one of these words in the URL")
    text_contains: str | list[str] | None = Field(None, description="Require at least one of these words in the page text")

    title_contains_all: str | list[str] | None = Field(None, description="Require all of these words in the title")
    url_contains_all: str | list[str] | None = Field(None, description="Require all of these words in the URL")
    text_contains_all: str | list[str] | None = Field(None, description="Require all of these words in the page text")

    exact_phrases: str | list[str] | None = Field(None, description="Include results with these exact phrases")

    before: date | None = Field(None, description="Only show results before this date")
    after: date | None = Field(None, description="Only show results after this date")

    related: str | list[str] | None = Field(None, description="Show sites related to these domains")
    news_source: str | None = Field(None, description="Restrict to news from a specific publisher (Google News only)")

    exclude_exact_phrases: str | list[str] | None = Field(None, description="Exclude results with these exact phrases")
    exclude_sites: str | list[str] | None = Field(None, description="Exclude results from these domains")
    exclude_tlds: TLD | list[TLD] | None = Field(None, description="Exclude results from these top-level domains")
    exclude_https: bool = Field(False, description="Exclude HTTPS pages")
    exclude_filetypes: FileType | list[FileType] | None = Field(None, description="Exclude documents with these file types")
    exclude_url_words: str | list[str] | None = Field(None, description="Exclude results with these terms in the URL")
    exclude_keywords: Keyword | list[Keyword] | None = Field(None, description="Exclude pages containing these words")

    exclude_title_contains: str | list[str] | None = Field(None, description="Exclude pages with any of these words in the title")
    exclude_url_contains: str | list[str] | None = Field(None, description="Exclude pages with any of these words in the URL")
    exclude_text_contains: str | list[str] | None = Field(None, description="Exclude pages with any of these words in the page text")

    exclude_title_contains_all: str | list[str] | None = Field(None, description="Exclude pages containing all of these words in the title")
    exclude_url_contains_all: str | list[str] | None = Field(None, description="Exclude pages containing all of these words in the URL")
    exclude_text_contains_all: str | list[str] | None = Field(None, description="Exclude pages containing all of these words in the page text")

    def compile_filters(self) -> str:
        def to_list(val: str | list[str] | None) -> list[str]:
            if val is None:
                return []
            return val.split() if isinstance(val, str) else val

        query: list[str] = []

        # Include filters
        for site in to_list(self.sites):
            query.append(f"site:{site}")

        for tld in to_list(self.tlds):
            query.append(f"site:{tld}")

        for ft in to_list(self.filetypes):
            query.append(f"filetype:{ft}")

        for word in to_list(self.keywords):
            query.append(word)

        for phrase in to_list(self.exact_phrases):
            query.append(f'"{phrase}"')

        if self.https_only:
            query.append("inurl:https")

        for word in to_list(self.title_contains):
            query.append(f"intitle:{word}")

        for word in to_list(self.url_contains):
            query.append(f"inurl:{word}")

        for word in to_list(self.text_contains):
            query.append(f"intext:{word}")

        if all_words := to_list(self.title_contains_all):
            query.append(f"allintitle:{' '.join(all_words)}")

        if all_words := to_list(self.url_contains_all):
            query.append(f"allinurl:{' '.join(all_words)}")

        if all_words := to_list(self.text_contains_all):
            query.append(f"allintext:{' '.join(all_words)}")

        if self.before:
            query.append(f"before:{self.before.isoformat()}")

        if self.after:
            query.append(f"after:{self.after.isoformat()}")

        for site in to_list(self.related):
            query.append(f"related:{site}")

        if self.news_source:
            query.append(f"source:{self.news_source}")

        # Exclude filters
        for phrase in to_list(self.exclude_exact_phrases):
            query.append(f'-"{phrase}"')

        for site in to_list(self.exclude_sites):
            query.append(f"-site:{site}")

        for tld in to_list(self.exclude_tlds):
            query.append(f"-site:{tld}")

        if self.exclude_https:
            query.append("-inurl:https")

        for ft in to_list(self.exclude_filetypes):
            query.append(f"-filetype:{ft}")

        for word in to_list(self.exclude_keywords):
            query.append(f"-{word}")

        for word in to_list(self.exclude_url_contains):
            query.append(f"-inurl:{word}")

        for word in to_list(self.exclude_title_contains):
            query.append(f"-intitle:{word}")

        for word in to_list(self.exclude_text_contains):
            query.append(f"-intext:{word}")

        if all_words := to_list(self.exclude_title_contains_all):
            query.append(f"-allintitle:{' '.join(all_words)}")

        if all_words := to_list(self.exclude_url_contains_all):
            query.append(f"-allinurl:{' '.join(all_words)}")

        if all_words := to_list(self.exclude_text_contains_all):
            query.append(f"-allintext:{' '.join(all_words)}")

        return " ".join(query)

