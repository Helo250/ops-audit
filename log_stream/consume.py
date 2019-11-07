# -*- coding: utf-8 -*-
# Filename: consume
# Author: brayton
# Datetime: 2019-Oct-14 6:25 PM

from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from collections import namedtuple, defaultdict
from multiprocessing import Process, Manager, Queue, Event
from asyncio.subprocess import Process
from asyncio import sleep
from asyncpg import create_pool
import logging
from asyncio import new_event_loop, get_event_loop
import asyncio
import uuid
import signal
from queue import Full, Empty
from concurrent.futures import ProcessPoolExecutor

from log_stream.spec import Message
from setting import KAFKA_DESERIALIZER
from utils.log_enhance import insert_log

_logger = logging.getLogger('kafka.consumer')


Events = namedtuple('Events', 'start, pause, stop')
MAX_WAIT_QUEUE_SIZE = 2


class Worker(object):
    def __init__(self, task: namedtuple, workshop):
        self._task = task
        self._multi = workshop
        self.consumer = KafkaConsumer(
            bootstrap_servers=workshop.bootstrap_servers,
            group_id=task.group or f'{task.topic}-{uuid.uuid4()}',
            key_deserializer=KAFKA_DESERIALIZER,
            value_deserializer=KAFKA_DESERIALIZER,
            enable_auto_commit=False,
            auto_offset_reset='earliest',
        )
        self._alive = True
        self._scene = dict()

    def signal_handler(self, sig, frame):
        self._multi.loop.add_callback_from_signal(self._clean)
        self._alive = False

    def _clean(self):
        self.consumer.close()

    def process_signal(self):
        _logger.info('setting signal handler')
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def prepare(self):
        topic = self._task.topic
        partitions = self._task.partitions
        self.consumer.unsubscribe()
        print('111', self.consumer.topics())
        if partitions:
            partitions = [TopicPartition(topic, int(part)) for part in partitions.split(',')]
            assert len(partitions) == 1, 'current task should assigned only one partition'
            self.consumer.assign(partitions)
            # self.consumer.seek_to_beginning(*partitions)
            # self.consumer.seek(TopicPartition(topic, 0), 0)
        else:
            self.consumer.subscribe([topic])
        print('consumer topics', self._task, id(self.consumer), self.consumer.topics())

    def set_scene(self, **context):
        self._scene = context

    @property
    def alive(self):
        return bool(self._alive)

    async def process_message(self, msg: Message):
        self.set_scene(**msg._asdict())
        logs = msg.deserializer(msg.logs)
        sql, args = insert_log(logs)
        print('record log', args)
        with open(f'/tmp/{self._task.topic}', 'a+') as f:
            f.write(f'args: {args}')
        # async with self._multi.app.db.acquire() as cur:
        #     await cur.execute(sql, args)
        _logger.debug('insert log successfully')

    async def do(self):
        while self.alive:
            print('tick')
            try:
                record = next(self.consumer)
                _logger.info(f'current record '
                             f'(topic:{record.topic}, partition:{record.partition}, offset:{record.offset})')
                msg: Message = record.value
                await self.process_message(msg)
                self.consumer.commit(record.offset)
            except StopIteration:
                _logger.error('The consumer is down...')
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self._alive = False

    async def idel(self):
        await sleep(1)

    async def start(self, **kwargs):
        self.process_signal()
        self.prepare()
        await self.do()


class WorkShop(object):
    def __init__(self, tasks: set, bootstrap_servers, app):
        self._tasks = self._tasks_cp = tasks
        self.bootstrap_servers = bootstrap_servers
        self.app = app
        self.executor = ProcessPoolExecutor(max_workers=1)
        self.workers = defaultdict(set)     # registry workers

    @property
    def task(self):
        return self._tasks_cp

    def list_workers(self):
        for workers in self.workers.values():
            for worker in workers:
                yield worker

    @property
    def loop(self):
        return self.app.loop
        # if not hasattr(self, '_loop'):
        #     setattr(self, '_loop', new_event_loop())
        # return getattr(self, '_loop')

    def add_task(self, task):
        self._tasks.add(task)
        self._tasks_cp.add(task)

    def assign_task(self):
        print(self._tasks)
        while self._tasks:
            task = self._tasks.pop()
            worker = Worker(task, self)
            self.workers[task].add(worker)

    async def run(self):
        await asyncio.gather(*[worker.start() for worker in self.list_workers()], loop=self.loop)

    def stop(self):
        for worker in self.list_workers():
            worker.stop()
        # self.loop.stop()
        _logger.info('Stop consumer workshop successfully...')

    async def start(self):
        self.assign_task()
        await self.run()
        # self.executor.submit(self.run)
        # self.loop.run_forever()
