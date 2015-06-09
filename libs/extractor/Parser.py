# -*- coding: utf-8 -*-
import codecs
from lxml import etree
from urllib.parse import parse_qs , urlparse
from libs.models import UserModel
import os
import logging
import ast
import time


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class ContentWrapper(etree.HTMLParser):
    def __init__(self, wrapper_elem, robot, *args, **kwargs):
        super(ContentWrapper, self).__init__(*args, **kwargs)
        # _p = etree.HTMLParser(encoding='utf-8')
        # self._document = etree.HTML(wrapper_html, parser=_p)
        self._document = wrapper_elem
        self.robot = robot
        self.controller = self.robot.controller
        self._target_ids_xpath = ".//a[@data-hovercard]/@data-hovercard"

    def collect_target_ids(self):
        profiles = self._document.xpath(self._target_ids_xpath)
        notify_cond = not len(self.controller.users_queue.pending_pages)
        users_set = set()
        for profileLink in profiles:
            url = urlparse(profileLink)
            user_id = parse_qs(url.query)['id'][0]
            user_type = url.path.split('/')[-1].split('.')[0]
            logging.debug("Adding new user : ('%s', '%s')" % (str(user_id), str(user_type)))
            self.controller.add_user(UserModel(user_id, user_type))
        if notify_cond:
            with self.controller.target_ids_cond:
                self.controller.target_ids_cond.notifyAll()


class Parser(object):
    
    """
    Extracting data on the live page using javascript.
    """
    def __init__(self, robot, *args, **kwargs):
        # etree.HTMLParser.__init__(self)
        self.page_model= kwargs.get('page_model')
        self.robot = robot
        self.content_wrapper_css = 'div.userContentWrapper'
        self.pager_links_css = self.content_wrapper_css + ' li.UFIPagerRow a.UFIPagerLink'
        self.comment_link_css = self.content_wrapper_css + ' a.comment_link'
        self.see_more_links = self.content_wrapper_css + ' a.see_more_link'
        self.feed_back_css = self.content_wrapper_css + " a.UFIBlingBox.uiBlingBox.feedbackBling[rel='ignore']"

        # inject jQuery script
        self._inject_jquery()
        # self.content_wrappers = self._get_content_wrappers()
        self.parent_node = etree.Element('page')
        if self.page_model:
            self.parent_node.attrib.update({'type': str(self._get_page_type()), 'id': str(self.page_model.id)})
        self.document = etree.ElementTree(self.parent_node)

    def prepare_page(self):
        logging.debug("Prepare page")
        # click on "Comment" link on each post
        self._click_comment()
        # click on all pagers "View more comments..."
        self._click_pagers()
        # click on "See more" links
        self._see_more()
        # save to file
        self._init_parser()
        # get userContentWrappers
        self.content_wrappers = self._get_content_wrappers()

    def _init_parser(self):
        html_str = self.robot.execute_script('return $("html").get(0).outerHTML')
        html_parser = etree.HTMLParser(encoding = 'utf-8',remove_blank_text=True)
        self.tree = etree.HTML(html_str, parser=html_parser)

    def start_parsing(self):
        self.prepare_page()
        logging.debug("Start parsing...")
        if self.content_wrappers:
            logging.debug("parsing %s content wrappers" % str(len(self.content_wrappers)))
            for wrapper in self.content_wrappers:
                w_id = str(wrapper.attrib.get('data-gt'))
                params_str = wrapper.xpath('.//form//input[@name="feedback_params" and @value]')
                if params_str:
                    params_str = params_str[0].attrib['value']
                else:
                    params_str = '{}'

                params_dict = ast.literal_eval(params_str)

                post_node = etree.Element('post', {'post_id': params_dict.get('target_fbid') or '', 'author': params_dict.get('actor') or params_dict.get('target_profile_id') or '' })
                for key,value in params_dict.items():
                    post_node.attrib.update({str(key): str(value)})

                self.parent_node.append(post_node)
                content_node = etree.Element('field', {'name': 'content'})
                content_node.text = '\n'.join(wrapper.xpath('.//div[contains(@class,"userContent")]//p//text()'))
                post_node.append(content_node)
                self._append_comments_of(post_node, w_id)
                self._append_likes_of(post_node, w_id)
                self._append_shares_of(post_node, w_id)

            logging.debug("Saving XML file")
            if self.page_model:
                file_path = os.path.join(os.getcwd(),'output/%s.xml' % (str(self.page_model.id),))
            else:
                file_path = os.path.join(os.getcwd(),'output/%s_%s.xml' % ('starting_newsfeed_random', str(time.time())))
            with codecs.open(file_path, 'w+', encoding='utf-8') as file_handle:
                file_handle.write(etree.tostring(self.document, pretty_print=True).decode('utf-8'))


    def _inject_jquery(self):
        logging.debug("Injecting jQuery")
        self.robot.execute_script(self.robot.controller.jquery_script)
        self.robot.execute_script(""";
window.eventFire = function(el, etype){
if (el.fireEvent) {
el.fireEvent('on' + etype);
} else {
var evObj = document.createEvent('Events');
evObj.initEvent(etype, true, false);
el.dispatchEvent(evObj);
}
};""")
        logging.debug("jQuery is successfully injected")
        return

    def _see_more(self):
        logging.debug("See more...")
        self.robot.execute_script("$.each($('div.userContentWrapper div.userContent[id] a.see_more_link'),function(index,val){window.eventFire(val,'click')})")
        logging.debug("All posts are exposed")
        return

    def _get_content_wrappers(self):
        logging.debug("Getting content wrappers")
        content_wrappers = self.tree.xpath("//div[contains(@class,'userContentWrapper') and not(descendant::div[contains(@class,'userContentWrapper')])]")
        return content_wrappers

    def _click_comment(self):
        logging.debug("Clicking comment_links to show comments")
        self.robot.execute_script("$.each($('div.userContentWrapper a.comment_link'),function(index,val){window.eventFire(val, 'click')})")
        logging.debug("All comment blocks are appeared")
        return

    def _click_pagers(self):
        logging.debug("Getting all hidden comments")
        while self.robot.execute_script("return $('div.userContentWrapper a.UFIPagerLink')"):
            self.robot.execute_script("$.each($('div.userContentWrapper a.UFIPagerLink'),function(index,val){window.eventFire(val, 'click')})")
            time.sleep(1)
        logging.debug('Got all hidden comments')

    def _append_comments_of(self, post_node, w_id):
        comments_of_wrapper = self.tree.xpath("//div[contains(@class,'userContentWrapper') and @data-gt='%s']//li[contains(@class,'UFIComment')]" % (w_id))
        comment_block_node = etree.Element('field', name='comments')

        for comment in comments_of_wrapper:
            comment_href = comment.xpath(".//a[contains(@class,'uiLinkSubtle')]")[0].attrib.get("href")
            url = urlparse(comment_href)
            comment_id = parse_qs(url.query).get('comment_id')
            if comment_id:
                comment_id = str(comment_id[0])
            else:
                comment_id = str(comment_id)

            data_reactid = comment.attrib['data-reactid']
            _reactid = data_reactid[data_reactid.index('$comment') + len('$comment') : ]
            _ids = _reactid.split(':')[0]
            ids = _ids.split('_')
            post_id = ids[0]

            data_hovercard_str = comment.xpath('.//a[contains(@class,"UFICommentActorName")]')[0].attrib.get('data-hovercard')
            user_id = data_hovercard_str[data_hovercard_str.index('id=') + len('id='):data_hovercard_str.index('&')]

            comment_body = '\n'.join(comment.xpath('.//*[contains(@class,"UFICommentBody")]//text()'))
            timestamp = str(comment.xpath(".//abbr[contains(@class,'livetimestamp')]")[0].attrib.get("data-utime"))

            comment_node = etree.Element('comment', {'id': comment_id, 'author': user_id})
            comment_node.text = comment_body
            comment_node.attrib.update({"post_id": post_id})
            comment_node.attrib.update({"comment_href": comment_href})
            comment_node.attrib.update({'content_timestamp': timestamp})
            comment_block_node.append(comment_node)

        post_node.append(comment_block_node)
        return

    def _append_likes_of(self, post_node, w_id):
        pass

    def _append_shares_of(self, post_node, w_id):
        pass

    def _get_page_type(self):
        return str(self.page_model.type)