import logging
import random
import time
from threading import Timer

from core.api import API

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, user, media):
        self.user = user
        self.media = media
        self.API = API(self.user)

    def run(self, interval):
        self._repeating_epoch(interval)

    def _repeating_epoch(self, interval):
        if not self.stopping_criteria():
            Timer(interval, self._repeating_epoch, (interval,)).start()
            self.epoch()

    def epoch(self):
        """
        This is where a single iteration of the operation is run.
        The run function will call this function every interval.
        :return:
        """
        raise NotImplementedError("A subclass of Bot needs to override the 'epoch' method")

    def stopping_criteria(self):
        """
        This function defines the condition for stopping the infinite loop.
        Default will loop forever.
        :return: true to stop the infinite loop
        """
        return False

    @staticmethod
    def add_time(target_time):
        """
        Add a bit of randomness to the target time
        :param target_time: the perfect time
        """
        return target_time * 0.9 + target_time * 0.2 * random.random()


class FollowBot(Bot):
    def __init__(self, user, media):
        super(FollowBot, self).__init__(user, media)
        # keep a list of users that I have followed
        self.follow_list = []

    def epoch(self):
        owner_id = self.media.get_media()[0]["owner"]["id"]
        log_string = "Try to follow: %s" % owner_id
        logger.info(log_string)
        self.API.follow(owner_id)
        self.follow_list.append([owner_id, time.time()])


class LikeBot(Bot):
    def __init__(self, user, media, media_max_like, media_min_like):
        super(LikeBot, self).__init__(user, media)
        # keep a list of users that I have followed
        self.media_max_like = media_max_like
        self.media_min_like = media_min_like

    def epoch(self):
        media = self.media.get_media()
        self.API.like_all_exist_media(media, self.media_max_like, self.media_min_like, media_size=1)


class UnfollowAllBot(Bot):
    def __init__(self, user, media, refresh_rate):
        super(UnfollowAllBot, self).__init__(user, media)
        self.refresh_rate = refresh_rate
        self.following_ids = []
        self.get_following_list()

    def get_following_list(self):
        self.following_ids = []

    def epoch(self):
        user_id = self.following_ids[-1]
        log_string = "Try to unfollow: %s" % user_id
        logger.info(log_string)
        self.API.unfollow(user_id)
        self.following_ids = self.following_ids[:-1]


class CommentBot(Bot):
    def __init__(self, user, media, comment_maker):
        super(CommentBot, self).__init__(user, media)
        # keep a list of users that I have followed
        self.comment_maker = comment_maker

    def epoch(self):
        item = self.media.get_media()[0]['id']
        log_string = "Try to comment: %s" % item
        logger.info(log_string)
        self.API.comment(item, self.comment_maker.generate_comment())
