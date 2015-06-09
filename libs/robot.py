# -*- coding: utf-8 -*-
# from selenium.webdriver import Chrome as WDriver
from selenium.webdriver import PhantomJS as WDriver
from selenium.webdriver.common.keys import Keys
import time
import logging
import threading
from libs.extractor.Parser import Parser, ContentWrapper

logger = logging.getLogger(__name__)

class Robot(WDriver):
    def __init__(self, controller, rid, *args, **kwargs):
        super(Robot, self).__init__()
        self._parser_threads = set()
        self.controller = controller
        self.id = rid
        self.stop = False
        self.is_auth = False
        self.scroll_times = kwargs.get('scroll_times', 0)
        self.needs_scroll = False
        self._current_instruction = ''

    def start(self):
        while not self.stop:
            self.controller.get_instructions(self)

    def _login(self, username, password):
        logger.debug("Login")
        self.get('http://fb.com')
        self.find_element_by_name('email').send_keys(username)
        self.find_element_by_name('pass').send_keys(password)
        self.find_element_by_name('pass').send_keys(Keys.RETURN)
        self.is_auth = True
        self.needs_scroll = True

        return

    def _visit(self, page_model):
        logger.debug("Visiting %s-%s " % (page_model.type, page_model.id))
        if not self.is_auth:
            _init_user = self.controller.initial_login_user
            # import pdb; pdb.set_trace()
            self._login(_init_user.get('username'), _init_user.get('password').strip())
        self.get('http://www.facebook.com/%s' % page_model.id)
        self.needs_scroll = True

    def perform(self, function_name, args):
        self.controller.instructions_lock.release()
        self._current_instruction = function_name
        getattr(self, function_name, '_no_attribute_found')(*args)
        if self.needs_scroll:
            page_m = None
            if function_name == '_visit':
                page_m = args[0]
            self._scroll(page_model=page_m)
            
        return

    def _no_attribute_found(self, *args, **kwargs):
        logger.error("No such function \"%s\": attrs = (%s , %s)" % (self._current_instruction, str(args), str(kwargs)))
        return

    def _scroll(self, **kwargs):
        logger.debug("Starting scroll")
        for i in range(self.scroll_times):
            logger.debug("Scrolling time %d/%d" % (i+1, self.scroll_times))
            self.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            while self.execute_script('return window.scrollMaxY == window.scrollY'):
                time.sleep(1)
        self.needs_scroll = False
        _parser_thread = threading.Thread(target=self._parser, name='Parser', args=(kwargs,))
        _parser_thread.start()
        _parser_thread.join()
        self._parser_threads.add(_parser_thread)

        return

    def _parser(self,kwargs):
        logger.debug("Starting parsing thread...")
        parser = Parser(self, page_model=kwargs.get('page_model'))
        parser.prepare_page()
        for content_wrapper in parser.content_wrappers:
            cw = ContentWrapper(content_wrapper, self)
            cw.collect_target_ids()
        parser.start_parsing()
        return
