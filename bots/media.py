import random

import itertools

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

    def get_media(self):
        return self.API.get_media_id_by_tag(random.choice(self.tag_list))


class CommentMaker(object):

    def generate_comment(self):
        c_list = list(itertools.product(
                ["this", "the", "your"],
                ["photo", "picture", "pic", "shot", "snapshot"],
                ["is", "looks", "feels", "is really"],
                ["great", "super", "good", "very good",
                 "good", "wow", "WOW", "cool",
                 "GREAT", "magnificent", "magical", "very cool",
                 "stylish", "so stylish", "beautiful",
                 "so beautiful", "so stylish", "so professional",
                 "lovely", "so lovely", "very lovely",
                 "glorious", "so glorious", "very glorious",
                 "adorable", "excellent", "amazing"],
                [".", "..", "...", "!", "!!", "!!!"]))

        repl = [("  ", " "), (" .", "."), (" !", "!")]
        res = " ".join(random.choice(c_list))
        for s, r in repl:
            res = res.replace(s, r)
        return res.capitalize()
