from selenium.webdriver import PhantomJS as DRIVERX
from selenium.webdriver.common.keys import Keys
import logging


class get_post_info(DRIVERX):
    def __init__(self):
        super(get_post_info, self).__init__()
        print("Initializing robot")
        self.username = 'arabic_sendbad@yahoo.com'
        self.password = '2855930022040'
        self.main_url = 'http://fb.com'
        self.is_login = False

    def _login(self):
        print("Login")
        self.get(self.main_url)
        self.find_element_by_name('email').send_keys(self.username)
        self.find_element_by_name('pass').send_keys(self.password)
        self.find_element_by_name('pass').send_keys(Keys.RETURN)
        self.is_login = True

    def get_post_data_from_url(self, url):
        print("getting data from URL")
        if not self.is_login:
            self._login()
        self.get(url)
        data = self._get_post_and_comments()
        return data

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def _get_post_and_comments(self):
        print("Getting post data")
        post = self.find_element_by_xpath(
            "//div[contains(@class, 'userContentWrapper')]//div[contains(@class, 'userContent')]")
        self._get_hidden_comments()
        comments = []
        print("Getting comments data")
        for comment_element in self._get_comment_elements():
            comments.append(comment_element.text)
        result = {}
        result.update(comments=comments, post=post.text)
        return result

    def _get_hidden_comments(self):
        # TODO : show all hidden comments of large posts
        print("Show all hidden comments")

    def _get_comment_elements(self):
        comments = self.find_elements_by_xpath(
            "//ul[contains(@class, 'UFIList')]//span[contains(@class, 'UFICommentBody')]")
        return comments

# Example of usage
"""
data = {}
with get_post_info() as x:
    data = x.get_post_data_from_url('https://www.facebook.com/DayTalk/posts/840863529296774')

print(data.get('post'))

comments = data.get('comments')
for comment in comments:
    print(comment)

print(len(comments))
"""
