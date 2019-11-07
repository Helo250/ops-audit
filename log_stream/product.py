# -*- coding: utf-8 -*-
# Filename: product
# Author: brayton
# Datetime: 2019-Oct-14 4:45 PM


import dill
from kafka import KafkaProducer
from typing import Union
import uuid
import time
from typing import Optional
import logging
from collections import namedtuple

from log_stream.spec import Message
from setting import KAFKA_SERIALIZER, KAFKA_DESERIALIZER

_logger = logging.getLogger('kafka.producer')


class Queue(object):
    def __init__(self,
                 topic: str,
                 bootstrap_servers,
                 timeout=None):
        self._topic = topic
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=KAFKA_SERIALIZER,
            value_serializer=KAFKA_SERIALIZER
        )
        self._timeout = timeout
        self.spec = EnqueueSpec(
            topic=topic,
            producer=self.producer,
            timeout=timeout
        )

    @property
    def producer(self):
        return self._producer

    def close(self):
        self._producer.close()

    def enqueue(self, log: namedtuple):
        return self.spec.enqueue(value=log)


class EnqueueSpec(object):
    def __init__(self, topic: str, producer: KafkaProducer, timeout=None):
        self.topic = topic
        self.producer = producer
        self.timeout = timeout

    def enqueue(self, value: namedtuple = None, topic=None):
        timestamp = int(time.time() * 1000)  # timestamp ms
        message = Message(
            id=uuid.uuid4(),
            log_cls=value.__class__.__name__,
            logs=dill.dumps(value),
            deserializer=dill.loads,
            timeout=self.timeout,
            timestamp=timestamp,
        )
        topic = topic or self.topic
        _logger.debug(f'Send message: {message} to topic<{topic}> at {timestamp}')
        print(f'Send message: {message} to topic<{topic}> at {timestamp}')
        return self.producer.send(
            topic=topic,
            key=hash(message),
            value=message,
            timestamp_ms=timestamp
        )

