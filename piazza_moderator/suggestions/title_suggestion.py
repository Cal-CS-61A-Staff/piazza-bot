import re

from piazza_moderator.suggestions.base_suggestion import Suggestion

class TitleSuggestion(Suggestion):
    def __init__(self, re_tag, res_folder):
        self._re_tag = re_tag
        self._res_folder = res_folder

    def applies(self, post):
        found = False
        for folder in post.folders:
            for folder_re in self._res_folder:
                folder_match = re.search(folder_re, folder)
                if folder_match is not None:
                    found = True
        if not found:
            return False

        title_match = re.search(self._re_tag, post.subject)
        return title_match is None

    def apply(self, post):
        return 'This post is missing a tag in the title, such as [HW01 Q01].'
