from datetime import date
from search_ai import search, Filters


search_filters = Filters(
    stock='ORCL',
    in_title='earnings',
    after=date(year=2025, month=6, day=10)
)

results = search(mode='news', filters=search_filters, count=8)

for result in results:
    print(result.title)

"""
Oracle stock touches all-time high after earnings beat
Oracle Stock (ORCL) Is About to Report Q4 Earnings Tomorrow. Here Is What to Expect
Oracle Announces Fiscal 2025 Fourth Quarter and Fiscal Full Year Financial Results
Oracle Earnings and Chip Demand
Oracle stock touches all-time high after earnings beat
Transcript : Oracle Corporation, Q4 2025 Earnings Call, Jun 11, 2025
Oracle (ORCL) Stock Hits All-Time Highs After Earnings, Now Valued at $560 Billion: Crypto Market Implications
"""
