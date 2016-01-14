class Suggestion(object):
    def applies(self, post):
        """Return whether this suggestion would be useful for the post."""
        raise NotImplementedError

    def apply(self, post):
        """Returns a text suggestion for the post."""
        raise NotImplementedError
