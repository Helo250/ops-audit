# -*- coding: utf-8 -*-
# Filename: testing
# Author: brayton
# Datetime: 2019-Oct-15 4:11 PM

import unittest
from multiprocessing import Process
from kafka import KafkaProducer, KafkaConsumer
from time import sleep
from random import choice
from string import printable
import dill

from log_stream.spec import Task
from log_stream.product import Queue
from log_stream.consume import WorkShop


def random_msg(length: int = 20):
    return ''.join([choice(printable) for _ in range(length)])


class ProductMock:
    def __init__(self, topic, bootstrap_servers, events):
        self._topic = topic
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self._pevent = events

    def run(self):
        while True:
            sleep(1)
            if self._pevent.pause.is_set():
                sleep(5)
                continue
            elif self._pevent.stop.is_set():
                break
            message = random_msg()
            self.producer.send(self._topic, dill.dumps(message))


class ConsumeMock:
    def __init__(self, tasks, bootstrap_server):
        pass


class LogStreamTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bootstrap_servers = 'localhost:9092'
        self.tasks = {
            Task(cls='login_log', topic='loginlog', group='loginlog01', partitions='0'),
            # Task(cls='ftp_log', topic='ftplog', group='ftplog01', partitions='0'),
        }
        self.producers = []
        self._build_producer()
        self._build_consumer()

    def tearDown(self) -> None:
        self.workshop.stop()

    def _build_producer(self):
        for task in self.tasks:
            self.producers.append(
                Queue(task.topic, self.bootstrap_servers)
            )

    def _build_consumer(self):
        self.workshop = WorkShop(self.tasks, self.bootstrap_servers)

    # def test_send_log(self):
    #     for producer in self.producers:
    #         message = random_msg()
    #         res = producer.enqueue(message)
    #         print(res)
    #         producer.close()

    def test_consume_log(self):
        self.workshop.start()


# def test():
#     bootstrap_servers = 'localhost:9092'
#     tasks = {
#         Task(cls='login_log', topic='loginlog', group='loginlog01'),
#         Task(cls='ftp_log', topic='ftplog', group='ftplog01', partitions='1'),
#     }
#     # for task in tasks:
#     workshop = WorkShop(tasks, bootstrap_servers)
#     workshop.start()

# def test_consumer():
#     consumer = KafkaConsumer(*('loginlog',), bootstrap_servers='localhost:9092')
#     print('>>>>>>>>>>>.', consumer)
#     for msg in consumer:
#         print('>>>>>>>>>>>>>>', msg)


if __name__ == '__main__':
    unittest.main()
    # test()
    # test_consumer()
