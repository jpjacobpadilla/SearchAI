import json
from search_ai import search, Filters

results = search('Python', filters=Filters(sites='jacobpadilla.com'), count=3)

markdown = results.json(extend=True, content_length=500)

print(json.dumps(markdown, indent=4))


"""
Example output:

[
    {
        "title": "The Inner Workings of Python Dataclasses Explained",
        "link": "https://jacobpadilla.com/articles/python-dataclass-internals",
        "description": "Discover how Python dataclasses work internally! Learn how to use __annotations__ and exec() to make our own dataclass decorator!",
        "author": "Jacob Padilla",
        "twitter": "@jpjacobpadilla",
        "page_preview": "[Jacob Padilla](/)\n\n  * [Github](https://github.com/jpjacobpadilla)\n  * [Articles](/articles)\n  * [Photography](/photography)\n  * [Contact](/contact)\n\n\n\n# The Inner Workings of Python Dataclasses Explained\n\nPosted on December 24, 2024\n\n# Table of Contents\n\n  * The Main Concepts\n  * First Version\n  * The Frozen Argument\n  * Adding a __repr__\n  * Conclusion\n\n\n\nDataclasses in Python are pretty cool, but have you ever wondered how they work internally? In this article, I\u2019m going to recreate a simple"
    },
    {
        "title": "A Deep Dive Into Python's functools.wraps Decorator",
        "link": "https://jacobpadilla.com/articles/functools-deep-dive",
        "description": "Take a deep dive into Python's functools.wraps decorator to learn how it maintains metadata in your code. A concise guide to effective decorator use.",
        "author": "Jacob Padilla",
        "twitter": "@jpjacobpadilla",
        "page_preview": "[Jacob Padilla](/)\n\n  * [Github](https://github.com/jpjacobpadilla)\n  * [Articles](/articles)\n  * [Photography](/photography)\n  * [Contact](/contact)\n\n\n\n# A Deep Dive Into Python's functools.wraps Decorator\n\nPosted on January 4, 2024 \u2022 Last updated on March 23, 2024\n\n#  Table of Contents \n\n  * What Does functools.wraps Do?\n  * Decorators Without functools.wraps\n  * Decorators With functools.wraps\n    * Transferring Extra Metadata\n  * Final Thoughts\n\n\n\nDecorators in Python are great! So far, my f"
    },
    {
        "title": "Python Custom Exceptions: How to Create and Organize Them",
        "link": "https://jacobpadilla.com/articles/custom-python-exceptions",
        "description": "Master custom exceptions in Python: from creation to organization. Enhance code readability and enable precise error handling. Guide & best practices.",
        "author": "Jacob Padilla",
        "twitter": "@jpjacobpadilla",
        "page_preview": "[Jacob Padilla](/)\n\n  * [Github](https://github.com/jpjacobpadilla)\n  * [Articles](/articles)\n  * [Photography](/photography)\n  * [Contact](/contact)\n\n\n\n# Python Custom Exceptions: How to Create and Organize Them\n\nPosted on October 24, 2023 \u2022 Last updated on October 27, 2024\n\n#  Table of Contents \n\n  * Why Make Custom Exceptions?\n  * Creating a Basic Custom Exception\n    * Raising & Catching Custom Exceptions\n  * Add a Default Message to Your Exceptions\n  * Exception Class Hierarchy\n  * Organizi"
    }
]
"""