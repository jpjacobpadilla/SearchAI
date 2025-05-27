from search_ai import search, Filters

results = search('Python', filters=Filters(sites='jacobpadilla.com'), count=3)

markdown = results.markdown(extend=True, content_length=1_500)
print(markdown)

"""
Example output:

# Search Results

**Title:** The Inner Workings of Python Dataclasses Explained
**Link:** https://jacobpadilla.com/articles/python-dataclass-internals
**Description:** Discover how Python dataclasses work internally! Learn how to use __annotations__ and exec() to make our own dataclass decorator!
**Author:** Jacob Padilla
**Twitter:** @jpjacobpadilla

## Page Preview:

[Jacob Padilla](/)

  * [Github](https://github.com/jpjacobpadilla)
  * [Articles](/articles)
  * [Photography](/photography)
  * [Contact](/contact)



# The Inner Workings of Python Dataclasses Explained

Posted on December 24, 2024

# Table of Contents

  * The Main Concepts
  * First Version
  * The Frozen Argument
  * Adding a __repr__
  * Conclusion



Dataclasses in Python are pretty cool, but have you ever wondered how they work internally? In this article, I’m going to recreate a simple dataclass decorator to explain some of the key concepts behind this cool module!

# The Main Concepts

Dataclass decorators are pretty unique - instead of the decorator wrapping the class in another object, which is what a standard decorator would do, the dataclass decorator just uses the metadata from the user-defined class to create a few methods, adds those methods to the user-defined class, and then returns the same class that it received like this:
    
    
    def dataclass(cls):
        # Modify cls...
        return cls
    
    @dataclass
    class Example:
        Pass

The decorator is able to modify the user-defined class with the help of the `__annotations__` dunder attribute, which provides the metadata to the decorator, and `exec`, a function the dataclass module uses to create the new methods. Since these two Python features are the core of how a dataclass works, let’s go over them first:

`__annotations__` is a dictionary in Python that stores type hints for variable
----------
**Title:** A Deep Dive Into Python's functools.wraps Decorator
**Link:** https://jacobpadilla.com/articles/functools-deep-dive
**Description:** Take a deep dive into Python's functools.wraps decorator to learn how it maintains metadata in your code. A concise guide to effective decorator use.
**Author:** Jacob Padilla
**Twitter:** @jpjacobpadilla

## Page Preview:

[Jacob Padilla](/)

  * [Github](https://github.com/jpjacobpadilla)
  * [Articles](/articles)
  * [Photography](/photography)
  * [Contact](/contact)



# A Deep Dive Into Python's functools.wraps Decorator

Posted on January 4, 2024 • Last updated on March 23, 2024

#  Table of Contents 

  * What Does functools.wraps Do?
  * Decorators Without functools.wraps
  * Decorators With functools.wraps
    * Transferring Extra Metadata
  * Final Thoughts



Decorators in Python are great! So far, my favorite use case for them is using decorators to store first-class functions, which is what Flask's `app.route` decorator does. However, due to the language's underlying mechanics, wrapping one object over another can result in the loss of valuable metadata from the encapsulated object. This is why it's crucial to use the wraps decorator from the Python Standard Library's functools (function tools) module when developing your own Python decorators.

# What Does functools.wraps Do?

`functools.wraps`, an easy-to-use interface for `functools.update_wrapper`, is a decorator that automatically transfers the key metadata from a callable (generally a function or class) to its wrapper. Typically, this wrapper is another function, but it can be any callable object such as a class.

Besides the `wrapped` parameter, which accepts the callable that gets enclosed by the wrapper, there are two more arguments that we can play around with:
    
    
    @functools.wraps(wrapped, assigned=WRAPPER_ASSI
----------
**Title:** Python Custom Exceptions: How to Create and Organize Them
**Link:** https://jacobpadilla.com/articles/custom-python-exceptions
**Description:** Master custom exceptions in Python: from creation to organization. Enhance code readability and enable precise error handling. Guide & best practices.
**Author:** Jacob Padilla
**Twitter:** @jpjacobpadilla

## Page Preview:

[Jacob Padilla](/)

  * [Github](https://github.com/jpjacobpadilla)
  * [Articles](/articles)
  * [Photography](/photography)
  * [Contact](/contact)



# Python Custom Exceptions: How to Create and Organize Them

Posted on October 24, 2023 • Last updated on October 27, 2024

#  Table of Contents 

  * Why Make Custom Exceptions?
  * Creating a Basic Custom Exception
    * Raising & Catching Custom Exceptions
  * Add a Default Message to Your Exceptions
  * Exception Class Hierarchy
  * Organizing Multiple Custom Exceptions
  * Best Practices & Conclusion



Custom exceptions are a great way to enhance your projects and make it easy for others to work with your code! In this article, I delve into how I make and organize custom exceptions for my projects.

# Why Make Custom Exceptions?

Python has many built-in exceptions, such as ValueError, TypeError, IndexError, and about 64 others, but they are all very general. Many times, it can be much better to make tailored exceptions for specific scenarios in your projects. For example, let's say you're building a social media bot that posts tweets on Twitter/X for you. There's no built-in exception that can accurately describe an error such as not being able to click on the “Post Tweet” button or an error involving the Twitter website being down.

# Creating a Basic Custom Exception

To make a basic custom exception, all we really want to do is make a different name for the “default” exception that accurately describes a potential e
"""
