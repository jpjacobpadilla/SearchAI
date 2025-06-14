from search_ai import search, Filters

search_filters = Filters(stock='ORCL', in_title='earnings')
results = search(mode='news', filters=search_filters, count=8)

for result in results:
    print(result.title)

"""
Oracle stock touches all-time high after earnings beat
Oracle Stock (ORCL) Is About to Report Q4 Earnings Tomorrow. Here Is What to Expect
How Will Oracle Stock React To Its Upcoming Earnings?
Oracle Announces Fiscal 2025 Fourth Quarter and Fiscal Full Year Financial Results
Oracle Earnings and Chip Demand
Earnings week ahead: ADBE, ORCL, GME, GTLB, CHWY, and more (NASDAQ:ADBE)
Oracle stock touches all-time high after earnings beat
Oracle Stock Falls On Earnings, Sales Miss. Tech Giant Touts Strong AI Demand.
"""
