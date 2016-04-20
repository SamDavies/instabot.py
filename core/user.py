import logging
import random
import time

from settings import *

logger = logging.getLogger(__name__)


class User(object):
    # All counter.
    like_counter = 0
    follow_counter = 0
    unfollow_counter = 0
    comments_counter = 0
    login_status = False

    def __init__(self, session, username, password):
        super(User, self).__init__()
        self.user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36")
        self.accept_language = 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'

        self.session = session
        self.username = username.lower()
        self.password = password

    def login(self):
        log_string = 'Try to login by %s...' % self.username
        logger.info(log_string)
        self.session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                                     'ig_vw': '1920', 'csrftoken': '',
                                     's_network': '', 'ds_user_id': ''})
        self.session.headers.update({'Accept-Encoding': 'gzip, deflate',
                                     'Accept-Language': self.accept_language,
                                     'Connection': 'keep-alive',
                                     'Content-Length': '0',
                                     'Host': 'www.instagram.com',
                                     'Origin': 'https://www.instagram.com',
                                     'Referer': 'https://www.instagram.com/',
                                     'User-Agent': self.user_agent,
                                     'X-Instagram-AJAX': '1',
                                     'X-Requested-With': 'XMLHttpRequest'})
        login_post = {'username': self.username,
                      'password': self.password}
        r = self.session.get(URL)
        self.session.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5 * random.random())
        login = self.session.post(URL_LOGIN, data=login_post,
                                  allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.session.get('https://www.instagram.com/')
            finder = r.text.find(self.username)
            if finder != -1:
                self.login_status = True
                log_string = 'Look like login by %s success!' % self.username
                logger.info(log_string)
            else:
                self.login_status = False
                logger.info('Login error! Check your login data!')
        else:
            logger.info('Login error! Connection error!')

    def logout(self):
        log_string = 'Logout: likes - %i, follow - %i, unfollow - %i, comments - %i.' % \
                     (self.like_counter, self.follow_counter,
                      self.unfollow_counter, self.comments_counter)
        logger.info(log_string)

        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            self.session.post(URL_LOGOUT, data=logout_post)
            logger.info("Logout success!")
            self.login_status = False
        except:
            logger.info("Logout error!")
