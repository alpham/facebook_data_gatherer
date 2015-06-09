# -*- coding: utf-8 -*-
import threading
import traceback
import os
import logging

from libs.models import UsersSetModel
from libs.robot import Robot


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
)

d = logging.debug

INPUT_USERS_FILE = os.path.join(os.path.join(os.getcwd(), 'input'), 'users')


class Controller(object):
    BUSY = False
    DONE_JOINING = False

    def __init__(self, robos_num, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        d('Initiating the controller')
        self.input_users = []
        self.users_queue = UsersSetModel()
        self.robots = {}
        self.robot_threads = {}
        self.robos_num = robos_num

        self.initial_login_user = None
        self._init_dirs()
        self.instructions_lock = threading.Lock()
        self.expect_target_ids = False
        self.target_ids_cond = threading.Condition()
        with open(os.path.join(os.getcwd(),'libs/static/js/jquery-1.11.2.min.js')) as jq_file:
            self.jquery_script = jq_file.read()
        
    def start(self):
        d('Starting getting input users')
        self._get_input_users()
        d('Initiating %s ROBOS' % str(self.robos_num))
        self._init_robots(self.robos_num)

    def _get_input_users(self):
        d('Opening file "%s"' % INPUT_USERS_FILE)
        with open(INPUT_USERS_FILE, 'r') as f:
            for line in f:
                login_d = {}
                login = line.split('\t')
                login_d['username'] = login[0]
                login_d['password'] = login[1]
                self.input_users.append(login_d)

        self.initial_login_user = self.input_users[0]

    def _init_robots(self, robos_num):
        for i in range(1, robos_num + 1):
            d('Initiating ROBO_%s' % str(i))
            robot = threading.Thread(name='ROBOT_%s' % str(i), target=self._worker, args=(i,))
            self.robot_threads.update({i: robot})
            robot.start()

        for (rob_id, rob_thread) in self.robot_threads.items():
            rob_thread.join()
        self.DONE_JOINING = True
        return


    def _worker(self, robot_id):
        """
        Starting the robot in new thread
        :param robot_id: the id of robot
        :return:
        """
        robot = Robot(self, rid=robot_id, scroll_times=3)
        self.robots.update({robot_id: robot})
        d('Starting ROBO_%s' % str(robot_id))
        robot.start()
        d('End of robot_thread %s ' % str(robot_id))
        return

    def get_instructions(self, robot):
        """
        Decides the next instruction for the robot
        :param robot: the robot to which the controller should send the next instruction
        :return:
        """
        d('ROBO_%s requires his new instructions' % str(robot.id))
        self.instructions_lock.acquire()
        try:
            d('Deciding new instruction for ROBO_%s' % str(robot.id))
            if self.input_users:
                input_user = self.input_users.pop()
                d('Do _login(username, password)')
                self.expect_target_ids = True
                robot.perform('_login', (input_user['username'].rstrip(), input_user['password'].rstrip()))
            
            elif self.expect_target_ids:
                d('Expecting target ids')
                if not len(self.users_queue.pending_pages):
                    d('Waiting for target ids')
                    with self.target_ids_cond:
                        self.target_ids_cond.wait()
                        
                page_to_visit = self.users_queue.pop()
                robot.perform('_visit', (page_to_visit,))
            
            else:
                robot.perform('end_robot', ())

            d('Finish Deciding for ROBO_%s' % str(robot.id))

        except:
            traceback.print_exc()
        return

    def add_user(self, user):
        """
        Adding user into the queue
        :param user: User object to add in the queue
        :return: boolean
        """
        logging.debug("Adding user id = %s " % str(user.id))
        logging.debug("The set has %s users till now" % str(len(self.users_queue.pending_pages)))
        return self._add_user(user)

    def _add_user(self, user):
        self.users_queue.add(user)
        return True

    def pop_user(self):
        """
        Getting user object from the queue
        :return: User
        """
        return self._pop_user()

    def _pop_user(self):
        return self.users_queue.pop()

    def _init_dirs(self):
        cwd = os.getcwd()
        self._input_dir = os.path.join(cwd, 'input')
        self._output_dir = os.path.join(cwd, 'output')
        self._temp_dir = os.path.join(cwd, 'temp')
        self._config_dir = os.path.join(cwd, 'config')
