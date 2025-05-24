from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.types import StringConstraints


TLD = Annotated[str, StringConstraints(pattern=r"^\.[a-zA-Z]{2,}$")]
FileType = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9]{2,10}$")]
Keyword = Annotated[str, StringConstraints(pattern=r"^[^\s]+$")]


class Filters(BaseModel):
    sites: str | list[str] | None = Field(None, description="Only show results from specific domains")
    tlds: TLD | list[TLD] | None = Field(None, description="Only show results from specific top-level domains (e.g., .gov, .edu)")
    filetype: FileType | None = Field(None, description="Only show documents that are a specific file type")
    https_only: bool = Field(False, description="Only show websites that support HTTPS")

    keywords: Keyword | list[Keyword] | None = Field(None, description="Require specific words anywhere in the page")
    exact_phrases: str | list[str] | None = Field(None, description="Include results with exact phrases")
    title_words: str | list[str] | None = Field(None, description="Require specific words in the title")
    url_words: str | list[str] | None = Field(None, description="Require specific words in the URL")
    text_words: str | list[str] | None = Field(None, description="Require specific words in the page text")

    before: date | None = Field(None, description="Only show results before this date")
    after: date | None = Field(None, description="Only show results after this date")

    exclude_sites: str | list[str] | None = Field(None, description="Exclude results from specific domains")
    exclude_tlds: TLD | list[TLD] | None = Field(None, description="Exclude results from specific top-level domains")
    exclude_filetypes: FileType | list[FileType] | None = Field(None, description="Exclude documents with specific file types")
    exclude_https: bool = Field(False, description="Exclude HTTPS pages")

    exclude_keywords: Keyword | list[Keyword] | None = Field(None, description="Exclude pages containing certain words")
    exclude_exact_phrases: str | list[str] | None = Field(None, description="Exclude results with exact phrases")
    exclude_title_words: str | list[str] | None = Field(None, description="Exclude pages with specific words in the title")
    exclude_url_words: str | list[str] | None = Field(None, description="Exclude pages with specific words in the URL")
    exclude_text_words: str | list[str] | None = Field(None, description="Exclude pages with specific words in the page text")

    def compile_filters(self) -> str:
        def to_list(val: str | list[str] | None) -> list[str]:
            if val is None:
                return []
            return val.split(' ') if isinstance(val, str) else val

        def group_includes(values: list[str], op: str | None = None) -> str:
            if not values:
                return ""

            if len(values) == 1:
                return f"{op}:{values[0]}" if op else f'"{values[0]}"'

            if op:
                return f'({ ' | '.join(f'{op}:{v}' for v in values) })'
            return f'({' | '.join(f'"{v}"' for v in values)})'

        def group_excludes(op: str, values: list[str]) -> list[str]:
            return [f"-{op}:{v}" for v in values]

        filters = []

        filters.append(group_includes(to_list(self.sites), 'site'))
        filters.append(group_includes(to_list(self.tlds), 'site'))

        filters.append(group_includes(to_list(self.filetype), "filetype"))
        filters.append(group_includes(to_list(self.keywords)))

        if isinstance(self.exact_phrases, str):
            filters.append(f'"{self.exact_phrases}"')
        elif isinstance(self.exact_phrases, list):
            filters.extend([f'"{phrase}"' for phrase in self.exact_phrases])

        if self.https_only:
            filters.append("inurl:https")

        filters.extend([f"intitle:{w}" for w in to_list(self.title_words)])
        filters.extend([f"inurl:{w}" for w in to_list(self.url_words)])
        filters.extend([f"intext:{w}" for w in to_list(self.text_words)])

        if self.before:
            filters.append(f"before:{self.before.isoformat()}")
        if self.after:
            filters.append(f"after:{self.after.isoformat()}")

        # Negative Filters
        if isinstance(self.exact_phrases, str):
            filters.append(f'-"{self.exact_phrases}"')
        elif isinstance(self.exact_phrases, list):
            filters.extend([f'-"{phrase}"' for phrase in self.exact_phrases])

        filters.extend(group_excludes("site", to_list(self.exclude_sites)))
        filters.extend(group_excludes("site", to_list(self.exclude_tlds)))

        if self.exclude_https:
            filters.append("-inurl:https")

        filters.extend(group_excludes("filetype", to_list(self.exclude_filetypes)))
        filters.extend([f"-{w}" for w in to_list(self.exclude_keywords)])
        filters.extend([f"-inurl:{w}" for w in to_list(self.exclude_url_words)])
        filters.extend([f"-intitle:{w}" for w in to_list(self.exclude_title_words)])
        filters.extend([f"-intext:{w}" for w in to_list(self.exclude_text_words)])

        return " ".join([f for f in filters if f])

