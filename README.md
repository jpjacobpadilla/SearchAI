<p align="center">
    <img src="https://github.com/jpjacobpadilla/SearchAI/raw/381e4e9c369ee1f73fa945e68e1a09ce39289196/searchai.png">
Google Search & News tool with advanced filters and LLM-friendly output formats!
</p>

- Search Google with **20+ powerful filters**  
- Get results in **LLM-optimized Markdown** and **JSON** formats 
- Built-in support for **asyncio, proxies, regional targeting**, and more!

---

### Install

```
$ pip install search-ai-core
```

## Examples

### Basic search

```python
from search_ai import search

results = search('Best LLM')

for result in results:
    print(result)
```

Output:

```plaintext
SearchResult(title="LLM Leaderboard 2025 - Vellum AI", link="https://www.vellum.ai/llm-leaderboard", description="This LLM leaderboard displays the latest public benchmark performance for SOTA model versions released after April 2024.")
SearchResult(title="What is your favorite LLM right now? : r/singularity - Reddit", link="https://www.reddit.com/r/singularity/comments/1impsjl/what_is_your_favorite_llm_right_now/", description="Gemini 2.0 pro is amazing at writing tasks specially because of the long context window. Try it out. It can even write in style of famous ...")
SearchResult(title="Top 9 Large Language Models as of May 2025 | Shakudo", link="https://www.shakudo.io/blog/top-9-large-language-models", description="Below, we highlighted the top 9 LLMs that we think are currently making waves in the industry, each with distinct capabilities and specialized strengths.")
SearchResult(title="The best large language models (LLMs) in 2025 - Zapier", link="https://zapier.com/blog/best-llm/", description="There are dozens of major LLMs, and hundreds that are arguably significant for some reason or other. These are 14 of the best LLMs available now.")
SearchResult(title="LLM Rankings - OpenRouter", link="https://openrouter.ai/rankings", description="Leaderboard · 1. OpenAI: GPT-4o-mini · 2. Anthropic: Claude 3.7 Sonnet · 3. Google: Gemini 2.0 Flash · 4. Google: Gemini 2.5 Pro Preview · 5. Google: Gemini 2.5 ...")
SearchResult(title="Best LLM Benchmarks for code? - Cursor - Community Forum", link="https://forum.cursor.com/t/best-llm-benchmarks-for-code/36022", description="I have been struggling to find good benchmarks for LLMs to use with coding. Now we have ~10 models to choose from all with pros/cons.")
SearchResult(title="Best Small LLM For Rag - Models - Hugging Face Forums", link="https://discuss.huggingface.co/t/best-small-llm-for-rag/143971", description="Among the 7 or 8B models, Ministral instruct 2410 GGUF is the best for me in french (IQ4 XS is small), so it's probably also the best among the ...")
SearchResult(title="LLM Leaderboard - Compare GPT-4o, Llama 3, Mistral, Gemini ...", link="https://artificialanalysis.ai/leaderboards/models", description="Comparison and ranking the performance of over 30 AI models (LLMs) across key metrics including quality, price, performance and speed.")
SearchResult(title="25 of the best large language models in 2025 - TechTarget", link="https://www.techtarget.com/whatis/feature/12-of-the-best-large-language-models", description="Top current LLMs · BERT · Claude · Cohere · DeepSeek-R1 · Ernie · Falcon · Gemini · Gemma.")
SearchResult(title="The Best LLM Is.... (A breakdown for every category) - YouTube", link="https://www.youtube.com/watch?v=0K66T6J1pVc", description="Comparing large language models can be confusing, so I created a benchmarking system that ranks them in 17 key categories—like search, ...")
```

### Using filters


```python
from search_ai import search, Filters

search_filters = Filters(
    in_title="python",              # Only include results with "python" in the title
    tlds=[".edu", ".org"],          # Restrict results to .edu and .org domains
    https_only=True,                # Only include websites that support HTTPS
    exclude_sites='quora.com',      # Exclude results from quora.com
    exclude_filetypes='pdf'         # Exclude PDF documents from results
)

results = search(filters=search_filters)
for result in results:
    print(result.title)
```

Output:

```plaintext
Welcome to Python.org
Python Tutorial - W3Schools
Python (programming language) - Wikipedia
Learn Python - Free Interactive Python Tutorial
CS50's Introduction to Programming with Python | Harvard University
Real Python: Python Tutorials
Python for Everybody Specialization - Coursera
scikit-learn: machine learning in Python — scikit-learn 1.6.1 ...
Table Of Contents - Learn Python the Hard Way
Python Institute - PROGRAM YOUR FUTURE
```

### Regional targeting

```python
from search_ai import search, regions

results = search('Python', region=regions.JAPAN)

for result in results:
    print(result.title)
```

Output:

```plaintext
Welcome to Python.org
python.jp: プログラミング言語 Python 総合情報サイト
【入門】Pythonとは｜活用事例やメリット、できること、学習方法 ...
ゼロからのPython入門講座 - python.jp
Pythonの開発環境を用意しよう！（Windows） - Progate
Python - Wikipedia
プログラミング言語のPythonとは？その特徴と活用方法 - 発注ナビ
Python試験・資格、データ分析試験・資格を運営する一般社団法人 ...
Pythonの導入方法｜ソフトの利用方法 - 東京経済大学
Pythonとは？開発に役立つ使い方、トレンド記事やtips - Qiita
```

### Search news

```python
from search_ai import search

results = search('United States', mode='news')

for result in results:
    print(result.title)
```

Output:

```plaintext
Trump’s foreign policy is not so unusual for the US – he just drops the facade of moral leadership
'I didn’t vote for him': How American tourists are navigating global perceptions
The ‘quiet’ crisis brewing between the US and South Korea
Kremlin calls Trump 'emotional' after US president says Putin is 'crazy'
What’s Trump’s Vision on China, Russia and the World?
Canada welcomes King Charles against a backdrop of tensions with Trump
Memorial Day storms cause travel delays as millions prepare to head home
U.S. economy will be growing faster than 3% this time next year, predicts Treasury’s Bessent
E.U. says it will fast-track tariff talks with U.S. after Trump threats
America’s Senate plans big changes for the House’s spending bill
```

### Markdown & JSON formats

Once extracted, you can retrieve the results in either Markdown or JSON format for further processing.  

If the `extend` argument is set to `True`, the content of the result's websites will also be included in the output.
To achieve this functionality, SearchAI uses [Playwright](https://github.com/microsoft/playwright) to load and extract content
from websites. In addition to extracting the main content of a page, SearchAI also tries to find metadata on pages, such as
an author name and twitter handle.

Getting results in markdown ([example](https://github.com/jpjacobpadilla/SearchAI/blob/c8c160a8d57e51ccb1c215ad27d652809a3d6da9/examples/markdown_example.py)):

```python
SearchResults.markdown(
    extend=False,           # Set to True to fetch and include page content
    content_length=1000,    # Limit the length of extracted content
    ignore_links=False,     # Exclude hyperlinks in the content
    ignore_images=True,     # Exclude images from the content
    only_page_content=False # If True, omits metadata from the output
)
```

Getting results in json ([example](https://github.com/jpjacobpadilla/SearchAI/blob/c8c160a8d57e51ccb1c215ad27d652809a3d6da9/examples/json_example.py)):

```python
SearchResults.json(
    extend=False,           # Set to True to fetch and include page content
    content_length=1000,    # Limit the length of extracted content
    ignore_links=False,     # Exclude hyperlinks in the content
    ignore_images=True,     # Exclude images from the content
)
```

### Using proxies

Google is very finicky about the IP address you use.  
If you'd like to use proxies, you can create a proxy object using `Proxy` and pass it into either `search` or `async_search`.

```python
from search_ai import Proxy, search

proxy = Proxy(
    protocol="[protocol]",
    host="[host]",
    port=9999,
    username="optional username",
    password="optional password"
)

search('query', proxy=proxy)
```

### Async support

SearchAI also supports Asyncio! Instead of using `search`, use `async_search`. The
async version will return an `AsyncSearchResults` which will contain multiple instances of `AsyncSearchResult`.

```python
from search_ai import async_search

results = await async_search(...)
await results.json(extend=True)
```

## All filters

You can narrow down searches by including filters like so:

```python
Filters(
    sites="example.com",
    tlds=[".edu", ".gov"],
    filetype="pdf",
    exclude_sites=["facebook.com", "twitter.com"],
    after=date(2023, 1, 1),
    in_title="python",
    not_in_url=["login", "signup"]
)
```

Here is a complete list of all the filters in SearchAI:

| Filter                  | Description                                                             | Example (str)        | Example (list)                        |
|-------------------------|-------------------------------------------------------------------------|----------------------|---------------------------------------|
| `sites`                 | Only show results from specific domains                                 | `"example.com"`      | `["example.com", "another.com"]`      |
| `tlds`                  | Only show results from specific top-level domains (e.g. `.gov`, `.edu`) | `".edu"`             | `[".edu", ".gov"]`                    |
| `filetype`              | Only show documents of a specific file type (only one allowed)          | `"pdf"`              |                                       |
| `https_only`            | Only show websites that support HTTPS                                   | `True`               |                                       |
| `exclude_sites`         | Exclude results from specific domains                                   | `"facebook.com"`     | `["facebook.com", "twitter.com"]`     |
| `exclude_tlds`          | Exclude results from specific top-level domains                         | `".xyz"`             | `[".xyz", ".ru"]`                     |
| `exclude_filetypes`     | Exclude documents with specific file types                              | `"doc"`              | `["doc", "xls"]`                      |
| `exclude_https`         | Exclude HTTPS pages                                                     | `True`               |                                       |
| `before`                | Only show results before this date                                      | `date(2022, 12, 31)` |                                       |
| `after`                 | Only show results after this date                                       | `date(2023, 1, 1)`   |                                       |
| `any_keywords`          | Require at least one word anywhere in the page                          | `"python"`           | `["python", "django"]`                |
| `all_keywords`          | Require all of these words somewhere in the page                        | `"ai"`               | `["ai", "ml", "nlp"]`                 |
| `exact_phrases`         | Include results with exact phrases                                      | `"machine learning"` | `["deep learning", "language model"]` |
| `exclude_all_keywords`  | Exclude pages containing certain words                                  | `"ads"`              | `["ads", "tracking"]`                 |
| `exclude_exact_phrases` | Exclude results with exact phrases                                      | `"click here"`       | `["click here", "buy now"]`           |
| `in_title`              | Require specific words in the title                                     | `"resume"`           | `["resume", "portfolio"]`             |
| `in_url`                | Require specific words in the URL                                       | `"blog"`             | `["blog", "tutorial"]`                |
| `in_text`               | Require specific words in the page text                                 | `"case study"`       | `["case study", "example"]`           |
| `not_in_title`          | Exclude pages with specific words in the title                          | `"login"`            | `["login", "signup"]`                 |
| `not_in_url`            | Exclude pages with specific words in the URL                            | `"register"`         | `["register", "checkout"]`            |
| `not_in_text`           | Exclude pages with specific words in the page text                      | `"error"`            | `["error", "404"]`                    |
| `stock`                 | Search for a specific stock via its ticker                              | `"TSLA"`             |                                       |

## Search Configuration Options

The `search` and `async_search` functions have the following parameters that you can use to optimize your searches with:

| Parameter    | Type                   | Description                                                | Default    |
| ------------ | ---------------------- | ---------------------------------------------------------- | ---------- |
| `query`      | `str`                  | The search query string.                                   | `""`       |
| `filters`    | `Filters \| None`      | Optional `Filters` object to narrow search results.        | `None`     |
| `mode`       | `'search'` \| `'news'` | Select between general web search or Google News results.  | `"search"` |
| `count`      | `int`                  | Number of results to return.                               | `10`       |
| `offset`     | `int`                  | Number of results to skip at the beginning.                | `0`        |
| `unique`     | `bool`                 | If `True`, removes duplicate URLs across results.          | `False`    |
| `safe`       | `bool`                 | If `True`, uses Google SafeSearch.                         | `True`     |
| `region`     | `str \| None`          | Suggested region for search results.                       | `None`     |
| `proxy`      | `Proxy \| None`        | Optional `Proxy` object to route requests through a proxy. | `None`     |
| `sleep_time` | `int` or `float`       | Time in seconds to wait between requests.                  | `0.5`      |

