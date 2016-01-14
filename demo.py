import logging

from piazza_moderator.moderator import Moderator
from piazza_moderator import suggestions

class TestModerator(Moderator):
    cls_id = 'ijbvcz5bt7i4px'
    body = """
    It looks like your post doesn't follow Piazza guidelines in the following
    ways. Fixing these may help you get a useful response more quickly!

    {}

    This suggestion was made automatically by a bot.
    """

    def __init__(self, cls_id=cls_id, email='bot@cs61a.org'):
        super().__init__(cls_id, email)

        import re
        my_suggestions = [
            suggestions.TitleSuggestion(
                re.compile(r'\[(?:hw|proj)\d+\s*q(\d+|ec)\]', re.I),
                [r'^hw', r'^proj']
            ),
        ]
        self.add_suggestions(my_suggestions)

if __name__ == '__main__':
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    test = TestModerator()
    test.run()
