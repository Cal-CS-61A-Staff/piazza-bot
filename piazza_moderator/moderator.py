import logging

import piazza_api

from piazza_moderator.utils import reformat

class Moderator(object):
    cls_id = None
    suggestions = []
    body = '{}'

    def __init__(self, cls_id=None, email=None):
        if cls_id is None:
            cls_id = self.cls_id
        self._piazza = self.authenticate(email)
        self._network = self._piazza.network(cls_id)
        self._info = self._piazza.get_user_profile()

    @property
    def info(self):
        """Return account information."""
        return self._info

    def authenticate(self, email):
        """Create a Piazza API object and prompts the user to log in."""
        piazza = piazza_api.Piazza()
        if email is None:
            # piazza_api uses raw_input if email is None,
            # which isn't Python 3 compatible
            email = input('Email: ')
        piazza.user_login(email)
        return piazza

    def add_suggestions(self, suggestions):
        """Register more suggestions with the moderator."""
        self.suggestions = self.suggestions + suggestions

    def get_unread_posts(self):
        """Retrieve unread posts from the class."""
        unread = self._network.feed_filters.unread()
        filtered = self._network.get_filtered_feed(unread)['feed']
        logging.info('Found {} posts'.format(len(filtered)))
        return [Post(p['nr'], self) for p in filtered]

    def run(self):
        """Read all unread posts and make suggestions."""
        posts = self.get_unread_posts()
        for post in posts:
            logging.info('Post {}: can_suggest={}, suggested={}'
                         .format(post.id, post.can_suggest, post.suggested))
            if post.can_suggest and not post.suggested:
                post.suggest()

class Post(object):
    def __init__(self, post_num, moderator):
        self.post_num = post_num
        self._moderator = moderator
        self._network = moderator._network

        self.subject = ''
        self.content = ''
        self.folders = []
        self.tags = []
        self.can_suggest = False  # suggest only if no instructor activity
        self.suggested = True     # don't suggest if already made a suggestion
        self._populate_fields()

    def _populate_fields(self):
        """Parse response data and set attributes."""
        data = self._network.get_post(self.post_num)
        self._data = data

        self.id = data['id']

        self.subject = data['history'][0]['subject']
        self.content = data['history'][0]['content']

        # metadata
        self.folders = data['folders']
        self.tags = data['tags']

        self.can_suggest = not self.has_instructor_activity(data)

    def has_instructor_activity(self, data):
        """Returns whether there has been any instructor activity on the post.
        The moderator will only make a suggestion if there has been no
        instructor activity.

        There are three forms of instructor activity:
            1. An instructor created the post
            2. An instructor edited the post
            3. An instructor posted a followup on the post
        """
        # 1. An instructor created the post
        if 'instructor-note' in self.tags:
            return True

        # 2. An instructor edited the post
        edited_by = [change['uid'] for change in data['change_log']]
        edited_users = self._network.get_users(edited_by)
        if any(user['admin'] for user in edited_users):
            return True

        # 3. An instructor posted a followup on the post
        children = data['children']
        followups, i_answer, s_answer = [], None, None
        for child in children:
            child_type = child['type']
            if child_type == 'followup':
                followups.append(child)
            elif child_type == 'i_answer':
                i_answer = child
            elif child_type == 's_answer':
                s_answer = child
            else:
                continue

        followup_children = sum([f['children'] for f in followups], [])
        followup_all = [f['uid'] for f in followups + followup_children]
        followup_users = self._network.get_users(followup_all) # random order
        uid_to_user = {u['id']: u for u in followup_users}

        followup_users = [uid_to_user[uid] for uid in followup_all]
        followup_starters = followup_users[:len(followups)]
        followup_responders = followup_users[len(followups):]
        if any(user['admin'] for user in followup_users):
            return True

        # No instructor activity! Check if a suggestion has already been made.
        my_id = self._moderator.info['user_id']
        self.suggested = my_id in followup_starters
        return False

    def analyze(self):
        """Analyze the post by returning a set of suggestions."""
        logging.debug('Post {}'.format(self.post_num))
        logging.debug('Subject: {}'.format(self.subject))
        logging.debug('Content: {}'.format(self.content))
        logging.debug('Folders: {}'.format(self.folders))
        logging.debug('Tags: {}'.format(self.tags))

        return [
            s.apply(self)
            for s in self._moderator.suggestions if s.applies(self)
        ]

    def suggest(self):
        """Analyze the post to see if any moderator suggestions apply."""
        suggestions = self.analyze()
        if suggestions:
            suggestions = ['{}. {}'.format(i, suggestion)
                           for i, suggestion in enumerate(suggestions, 1)]
            formatted = self._moderator.body.format('\n'.join(suggestions))
            result = reformat(formatted)
            logging.debug(result)
            self._network.create_followup({'id': self.id}, result)
