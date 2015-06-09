# -*- coding: utf-8 -*-
from libs.decorators import Singleton


class UserModel:
    def __init__(self, user_id, user_type):
        self.id = user_id
        self.type = user_type


@Singleton
class UsersSetModel:
    def __init__(self):
        self.done_pages = dict()
        self.pending_pages = dict()

    def add(self, user_model):
        if user_model.id not in self.done_pages:
            self.pending_pages.update({user_model.id: user_model})

    def pop(self):
        pop_item = self.pending_pages.popitem()
        # import pdb; pdb.set_trace()
        self.done_pages.update({pop_item[0]: pop_item[1]})
        return pop_item[1]

