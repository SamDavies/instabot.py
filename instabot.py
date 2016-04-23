import atexit
import datetime
import itertools
import logging
import random
import signal
import time

import requests

from bots.bots import FollowBot, LikeBot, CommentBot
from bots.media import Media, CommentMaker
from core.api import API
from core.user import User

logger = logging.getLogger(__name__)


class InstaBot(object):
    """
    Instagram bot v 1.0
    like_per_day=1000 - How many likes set bot in one day.

    media_max_like=10 - Don't like media (photo or video) if it have more than
    media_max_like likes.

    media_min_like=0 - Don't like media (photo or video) if it have less than
    media_min_like likes.

    tag_list = ['cat', 'car', 'dog'] - Tag list to like.

    max_like_for_one_tag=5 - Like 1 to max_like_for_one_tag times by row.

    log_mod = 0 - Log mod: log_mod = 0 log to console, log_mod = 1 log to file,
    log_mod = 2 no log.

    https://github.com/LevPasha/instabot.py
    """
    # List of user_id, that bot follow
    bot_follow_list = []

    # Other.
    media_by_tag = 0

    # For new_auto_mod
    next_iteration = {"Like": 0, "Follow": 0, "Unfollow": 0, "Comments": 0}

    def __init__(self, login, password,
                 like_per_day=1000,
                 media_max_like=10,
                 media_min_like=0,
                 follow_per_day=0,
                 follow_time=5 * 60 * 60,
                 unfollow_per_day=0,
                 comments_per_day=0,
                 tag_list=['cat', 'car', 'dog'],
                 max_like_for_one_tag=5,
                 log_mod=0):

        super(InstaBot, self).__init__()

        self.time_in_day = 24 * 60 * 60
        # Like
        self.like_per_day = like_per_day
        if self.like_per_day != 0:
            self.like_delay = self.time_in_day / self.like_per_day

        # Follow
        self.follow_time = follow_time
        self.follow_per_day = follow_per_day
        if self.follow_per_day != 0:
            self.follow_delay = self.time_in_day / self.follow_per_day

        # Unfollow
        self.unfollow_per_day = unfollow_per_day
        if self.unfollow_per_day != 0:
            self.unfollow_delay = self.time_in_day / self.unfollow_per_day

        # Comment
        self.comments_per_day = comments_per_day
        if self.comments_per_day != 0:
            self.comments_delay = self.time_in_day / self.comments_per_day

        # Don't like if media have more than n likes.
        self.media_max_like = media_max_like
        # Don't like if media have less than n likes.
        self.media_min_like = media_min_like
        # Auto mod seting:
        # Default list of tag.
        self.tag_list = tag_list
        # Get random tag, from tag_list, and like (1 to n) times.
        self.max_like_for_one_tag = max_like_for_one_tag

        self.media_by_tag = []

        log_string = 'Insta Bot v1.1 start at %s:' % \
                     (datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        logger.info(log_string)

        session = requests.Session()
        # create a new user and log the user into the session
        self.user = User(session, login, password)
        self.user.login()
        self.API = API(self.user)

        signal.signal(signal.SIGTERM, self.cleanup)
        atexit.register(self.cleanup)

    def cleanup(self):
        # Unfollow all bot follow
        if len(self.bot_follow_list) > 0:
            for f in self.bot_follow_list:
                log_string = "Try to unfollow: %s" % (f[0])
                logger.info(log_string)
                self.API.unfollow(f[0])
                self.bot_follow_list.remove(f)

        # Logout
        if self.user.login_status:
            self.user.logout()

    def new_auto_mod(self):
        # ------------------- Get media_id -------------------
        if len(self.media_by_tag) == 0:
            self.media_by_tag = self.API.get_media_id_by_tag(random.choice(self.tag_list))

        media = Media(self.user, self.tag_list)
        # ------------------- Like -------------------
        like_bot = LikeBot(self.user, media, self.media_max_like, self.media_min_like)
        like_bot.run(3)
        # ------------------- Follow -------------------
        follow_bot = FollowBot(self.user, media)
        follow_bot.run(3)
        # ------------------- Comment -------------------
        comment_maker = CommentMaker()
        comment_bot = CommentBot(self.user, media, comment_maker)
        comment_bot.run(3)
        # ------------------- Unfollow All -------------------
        self.new_auto_mod_unfollow()
        # ------------------- Unfollow Non Folbacks -------------------
        # self.new_auto_mod_unfollow()

        # Bot iteration in 1 sec
        # print("Tic!")

    def new_auto_mod_unfollow(self):
        if time.time() > self.next_iteration["Unfollow"] and \
                        self.unfollow_per_day != 0 and len(self.bot_follow_list) > 0:
            for f in self.bot_follow_list:
                if time.time() > (f[1] + self.follow_time):

                    log_string = "Try to unfollow: %s" % (f[0])
                    logger.info(log_string)

                    if self.API.unfollow(f[0]):
                        self.bot_follow_list.remove(f)
                        self.next_iteration["Unfollow"] = time.time() + self.add_time(self.unfollow_delay)

    def add_time(self, time):
        """ Make some random for next iteration"""
        return time * 0.9 + time * 0.2 * random.random()


