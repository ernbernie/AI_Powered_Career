import pytest
import markdown

def test_markdown_to_html():
    md = """# Header

- Item 1
- Item 2
"""
    html = markdown.markdown(md)
    assert '<h1>' in html
    assert '<ul>' in html
    assert '<li>Item 1</li>' in html
    assert '<li>Item 2</li>' in html 