from selenium.webdriver import Chrome as WDriver
from selenium.webdriver.common.keys import Keys
import logging
import threading
import pyorient

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s', )


class FindNameRobot:
    def __init__(self):
        self.robots_threads = {}
        self.robots = {}
        self.number_of_threads = 1
        self.remain_ids = set()
        self.done_ids = set()
        self.error_ids = set()
        self.lock = threading.Lock()
        logging.debug("connect to the db")
        self.client = pyorient.OrientDB("localhost", 2424)
        session_id = self.client.connect("root", "root")
        self.client.db_open("SampleDataV2", "root", "root")
        logging.debug("getting the ids from the db")
        for record in self.client.command("select id from ContentOwnerABS where True limit=25"):
            self.remain_ids.add(record.id)

        logging.debug("new %s ids to manipulate..." % str(len(self.remain_ids)))

    def _init_robot(self, id):
        robot = WDriver()
        logging.debug("initialize")
        self.robots.update({str(id): robot})
        logging.debug("get facebook.com")
        robot.get('http://fb.com')

        logging.debug("login")
        robot.find_element_by_name('email').send_keys('arabic_sendbad@yahoo.com')
        robot.find_element_by_name('pass').send_keys('2855930022040')
        robot.find_element_by_name('pass').send_keys(Keys.RETURN)

        for index in range(len(self.remain_ids)):
            self.lock.acquire()
            user_id = self.remain_ids.pop()
            self.lock.release()
            try:
                self.get_name_for_id(robot, user_id)
            except:
                logging.debug("error while updating record with id=%s" % str(user_id))
                self.error_ids.add(user_id)
            else:
                self.done_ids.add(user_id)
        robot.close()
        return

    def main(self, *args, **kwargs):
        number_of_threads = args[0] | 1
        for i in range(number_of_threads):
            t = threading.Thread(name="Robot_" + str(i), target=self._init_robot, args=(i,))
            t.start()
            self.robots_threads.update({str(i): t})

        for thr in self.robots_threads.values():
            thr.join()

    def get_name_for_id(self, robot, id):
        logging.debug("loading page with id = %s" % str(id))
        robot.get('http://fb.com/' + str(id))
        user_name = robot.title
        logging.debug("updating record with id = %s" % str(id))
        self.client.command('UPDATE ContentOwnerABS set fbName="%s" WHERE id="%s"' % (str(user_name), str(id)))


if __name__ == '__main__':
    obj = FindNameRobot()
    obj.main(5)
    logging.debug("closing db connection")
    obj.client.db_close()
