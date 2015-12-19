"""
piazza-moderator makes instructors' lives easier by:
  - suggesting ways for students to improve their questions
    (e.g. better titles and error output)
  - identifying posts that may be duplicates
"""

from piazza_moderator.moderator import Moderator

class CS61A(Moderator):
    cls_id = 'id52tzq2i7yfx'

__version__ = '0.1.0'
