import logging

import piazza_api

class Moderator:
    cls_id = None

    def __init__(self, cls_id=None, email=None):
        if cls_id is None:
            cls_id = self.cls_id
        self._piazza = self.authenticate(email)
        self._network = self._piazza.network(cls_id)
        self._info = None

    def authenticate(self, email):
        """Create a Piazza API object and prompts the user to log in."""
        p = piazza_api.Piazza()
        if email is None:
            email = input('Email: ') # piazza_api uses raw_input if email is None
        p.user_login(email)
        return p

    @property
    def info(self):
        """Return account information."""
        if self._info is None:
            self._info = self._piazza.get_user_profile()
        return self._info

    def unread_posts(self):
        """Retrieve unread posts from the class."""
        unread = self._network.feed_filters.unread()
        filtered = self._network.get_filtered_feed(unread)['feed']
        logging.info('Found {} posts'.format(len(filtered)))
        return [Post(p['nr'], self) for p in filtered]

    def run(self):
        """Read all unread posts and make suggestions."""
        posts = self.unread_posts()
        for post in posts:
            logging.info('Post {}: can_suggest={}, suggested={}'
                         .format(post.id, post.can_suggest, post.suggested))
            if post.can_suggest and not post.suggested:
                post.suggest()

class Post:
    def __init__(self, post_id, moderator):
        self.id = post_id
        self._moderator = moderator
        self._network = moderator._network

        self.subject = ''
        self.content = ''
        self.folders = []
        self.tags = []
        self.can_suggest = False  # suggest only if no instructor activity
        self.suggested = False    # don't suggest if already made a suggestion
        self._populate_fields()

    def _populate_fields(self):
        """Parse response data and set attributes."""
        data = self._network.get_post(self.id)

        self.subject = data['history'][0]['subject']
        self.content = data['history'][0]['content']

        # metadata
        self.folders = data['folders']
        self.tags = data['tags']

        self.can_suggest = 'instructor-note' not in self.tags
        if self.can_suggest:
            edited_by = [change['uid'] for change in data['change_log']]
            edited_users = self._network.get_users(edited_by)
            self.can_suggest = not any(user['admin'] for user in edited_users)

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

        my_id = self._moderator.info['user_id']
        self.suggested = my_id in followup_all

        followup_users = self._network.get_users(followup_all) # random order
        uid_to_user = {u['id']: u for u in followup_users}

        followup_starters = [uid_to_user[uid] for uid in followup_all[:len(followups)]]
        followup_responders = [uid_to_user[uid] for uid in followup_all[len(followups):]]

        self.can_suggest = self.can_suggest and not any(u['admin'] for u in followup_users)

    def _analyze(self):
        """Analyze the post by applying a set of rules."""
        logging.debug('Post {}'.format(self.id))
        logging.debug('Subject: {}'.format(self.subject))
        logging.debug('Content: {}'.format(self.content))
        logging.debug('Folders: {}'.format(self.folders))
        logging.debug('Tags: {}'.format(self.tags))
        return None # TODO

    def suggest(self):
        """Analyze the post to see if there are any suggestions to make."""
        result = self._analyze()
        if result:
            self._network.create_followup(self.id, result)
