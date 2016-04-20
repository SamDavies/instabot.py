import datetime
import random
import time

from logable import Logable

url = 'https://www.instagram.com/'
url_login = 'https://www.instagram.com/accounts/login/ajax/'
url_logout = 'https://www.instagram.com/accounts/logout/'


class User(Logable):
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
        log_string = 'Try to login by %s...' % (self.username)
        self.write_log(log_string)
        self.session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                                     'ig_vw': '1920', 'csrftoken': '',
                                     's_network': '', 'ds_user_id': ''})
        self.login_post = {'username': self.username,
                           'password': self.password}
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
        r = self.session.get(url)
        self.session.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5 * random.random())
        login = self.session.post(url_login, data=self.login_post,
                                  allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.session.get('https://www.instagram.com/')
            finder = r.text.find(self.username)
            if finder != -1:
                self.login_status = True
                log_string = 'Look like login by %s success!' % (self.username)
                self.write_log(log_string)
            else:
                self.login_status = False
                self.write_log('Login error! Check your login data!')
        else:
            self.write_log('Login error! Connection error!')

    def logout(self):
        now_time = datetime.datetime.now()
        log_string = 'Logout: likes - %i, follow - %i, unfollow - %i, comments - %i.' % \
                     (self.like_counter, self.follow_counter,
                      self.unfollow_counter, self.comments_counter)
        self.write_log(log_string)

        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            logout = self.session.post(url_logout, data=logout_post)
            self.write_log("Logout success!")
            self.login_status = False
        except:
            self.write_log("Logout error!")
