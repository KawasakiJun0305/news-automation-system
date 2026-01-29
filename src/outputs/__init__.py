"""
出力モジュール

HTML、Markdown、Notionなど、各種フォーマットへの出力を担当
"""

from .html_generator import HTMLGenerator

__all__ = ['HTMLGenerator']
