import json
import random
import time

from logable import Logable


class API(Logable):
    def __init__(self, user):
        super(API, self).__init__()
        self.user = user
        self.url_tag = 'https://www.instagram.com/explore/tags/'
        self.url_likes = 'https://www.instagram.com/web/likes/%s/like/'
        self.url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'
        self.url_comment = 'https://www.instagram.com/web/comments/%s/add/'
        self.url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
        self.url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'

        # If instagram ban you - query return 400 error.
        self.error_400 = 0
        # If you have 3 in row 400 error - look like you banned.
        self.error_400_to_ban = 3
        # If InstaBot think you have banned - going to sleep.
        self.ban_sleep_time = 2 * 60 * 60

    def get_media_id_by_tag(self, tag):
        """ Get media ID set, by your hashtag """

        if self.user.login_status:
            log_string = "Get media id by tag: %s" % (tag)
            self.write_log(log_string)
            if self.user.login_status == 1:
                built_url_tag = '%s%s%s' % (self.url_tag, tag, '/')
                try:
                    r = self.user.session.get(built_url_tag)
                    text = r.text

                    finder_text_start = ('<script type="text/javascript">'
                                         'window._sharedData = ')
                    finder_text_start_len = len(finder_text_start) - 1
                    finder_text_end = ';</script>'

                    all_data_start = text.find(finder_text_start)
                    all_data_end = text.find(finder_text_end, all_data_start + 1)
                    json_str = text[(all_data_start + finder_text_start_len + 1) \
                        : all_data_end]
                    all_data = json.loads(json_str)

                    return list(all_data['entry_data']['TagPage'][0]['tag']['media']['nodes'])
                except:
                    self.write_log("Exept on get_media!")
                    time.sleep(60)
                    return []
            else:
                return 0

    def like_all_exist_media(self, media_by_tag, media_max_like, media_min_like, like_delay=None, media_size=-1):
        """ Like all media ID that have self.media_by_tag """

        if self.user.login_status:
            if media_by_tag != 0:
                i = 0
                for d in media_by_tag:
                    # Media count by this tag.
                    if media_size > 0 or media_size < 0:
                        media_size -= 1
                        l_c = media_by_tag[i]['likes']['count']
                        if ((media_max_like >= l_c >= media_min_like) or
                                (media_max_like == 0 and l_c >= media_min_like) or
                                (media_min_like == 0 and l_c <= media_max_like) or
                                (media_min_like == 0 and media_max_like == 0)):
                            log_string = "Try to like media: %s" % media_by_tag[i]['id']
                            self.write_log(log_string)
                            like = self.like(media_by_tag[i]['id'])
                            # comment = self.comment(self.media_by_tag[i]['id'], 'Cool!')
                            # follow = self.follow(self.media_by_tag[i]["owner"]["id"])
                            if like != 0:
                                if like.status_code == 200:
                                    # Like, all ok!
                                    self.error_400 = 0
                                    self.user.like_counter += 1
                                    log_string = "Liked: %s. Like #%i." % \
                                                 (media_by_tag[i]['id'], self.user.like_counter)
                                    self.write_log(log_string)
                                elif like.status_code == 400:
                                    log_string = "Not liked: %i" % like.status_code
                                    self.write_log(log_string)
                                    # Some error. If repeated - can be ban!
                                    if self.error_400 >= self.error_400_to_ban:
                                        # Look like you banned!
                                        time.sleep(self.ban_sleep_time)
                                    else:
                                        self.error_400 += 1
                                else:
                                    log_string = "Not liked: %i" % like.status_code
                                    self.write_log(log_string)
                                    return False
                                    # Some error.
                                i += 1
                                if like_delay:
                                    time.sleep(like_delay * 0.9 +
                                               like_delay * 0.2 * random.random())
                                else:
                                    return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
            else:
                self.write_log("No media to like!")

    def like(self, media_id):
        """ Send http request to like media by ID """
        if self.user.login_status:
            url_likes = self.url_likes % media_id
            try:
                like = self.user.session.post(url_likes)
                last_liked_media_id = media_id
            except:
                self.write_log("Exept on like!")
                like = 0
            return like

    def unlike(self, media_id):
        """ Send http request to unlike media by ID """
        if self.user.login_status:
            url_unlike = self.url_unlike % media_id
            try:
                unlike = self.user.session.post(url_unlike)
            except:
                self.write_log("Exept on unlike!")
                unlike = 0
            return unlike

    def comment(self, media_id, comment_text):
        """ Send http request to comment """
        if self.user.login_status:
            comment_post = {'comment_text': comment_text}
            url_comment = self.url_comment % media_id
            try:
                comment = self.user.session.post(url_comment, data=comment_post)
                if comment.status_code == 200:
                    self.user.comments_counter += 1
                    log_string = 'Write: "%s". #%i.' % (comment_text, self.user.comments_counter)
                    self.write_log(log_string)
                return comment
            except:
                self.write_log("Exept on comment!")
        return False

    def follow(self, user_id):
        """ Send http request to follow """
        if self.user.login_status:
            url_follow = self.url_follow % user_id
            try:
                follow = self.user.session.post(url_follow)
                if follow.status_code == 200:
                    self.user.follow_counter += 1
                    log_string = "Follow: %s #%i." % (user_id, self.user.follow_counter)
                    self.write_log(log_string)
                return follow
            except:
                self.write_log("Exept on follow!")
        return False

    def unfollow(self, user_id):
        """ Send http request to unfollow """
        if self.user.login_status:
            url_unfollow = self.url_unfollow % user_id
            try:
                unfollow = self.user.session.post(url_unfollow)
                if unfollow.status_code == 200:
                    self.user.unfollow_counter += 1
                    log_string = "Unfollow: %s #%i." % (user_id, self.user.unfollow_counter)
                    self.write_log(log_string)
                return unfollow
            except:
                self.write_log("Exept on unfollow!")
        return False
