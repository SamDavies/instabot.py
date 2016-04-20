import random

from core.api import API


class Media(object):

    def __init__(self, user, tag_list):
        self.user = user
        self.API = API(self.user)
        self.tag_list = tag_list
        self.current_media = []

        # TODO max number of items to remember, when too many reset pointer

    def get_next_item(self):
        return self.API.get_media_id_by_tag(random.choice(self.tag_list))[0]
