import logging
import random

import time

from core.api import API
from threading import Timer

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, user):
        self.user = user
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
        :return: true to stop the infinite loop
        """
        raise NotImplementedError("A subclass of Bot needs to override the 'stopping_criteria' method")

    @staticmethod
    def add_time(target_time):
        """
        Add a bit of randomness to the target time
        :param target_time: the perfect time
        """
        return target_time * 0.9 + target_time * 0.2 * random.random()


class FollowBot(Bot):
    def __init__(self, media, user):
        super(FollowBot, self).__init__(user)
        # the media that should be used to follow users
        self.media = media
        # keep a list of users that I have followed
        self.follow_list = []

    def get_next_media(self):
        item = self.media.get_next_item()
        return {
            "owner_id": item["owner"]["id"]
        }

    def epoch(self):
        owner_id = self.get_next_media()["owner_id"]
        log_string = "Try to follow: %s" % owner_id
        logger.info(log_string)
        self.API.follow(owner_id)
        self.follow_list.append([owner_id, time.time()])

    def stopping_criteria(self):
        return False
