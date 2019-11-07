# -*- coding: utf-8 -*-
# Filename: spec
# Author: brayton
# Datetime: 2019-Oct-14 4:00 PM

from collections import namedtuple

Message = namedtuple(
    typename='Message',
    field_names=(
        'id',           # message id
        'log_cls',      # log type
        'logs',         # logs content
        'timeout',      # timeout
        'deserializer', # unpack logs
        'timestamp'     # timestamp/ms
    )
)

Task = namedtuple(
    typename='Task',
    field_names=(
        'cls',
        'topic',
        'partitions',
        'group',
    )
)
Task.__new__.__defaults__ = (None, '', '0', 'group0')

# Message = namedtuple(
#     typename='Message',
#     field_names=(
#         'message_id',   # Message Id (uuid)
#         'topic',        # Name of the Kafka topic (str)
#         'partition',    # Topic partition (int)
#         'offset',       # Offset (int)
#         'key',          # Message key (bytes | None)
#         'value'         # Message value (bytes)
#     )
# )


if __name__ == '__main__':
    a = Task()
    print(a)
