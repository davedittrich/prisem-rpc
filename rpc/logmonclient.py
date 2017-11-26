#!/usr/bin/env python
#
# Copyright (c) 2010-2017, David Dittrich <dave.dittrich@gmail.com>
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Logmon Client Class

See the class documentation below for details.

"""

import arrow
import sys
import logging
from rpc import rpc_common

LOGGER = logging.getLogger(__name__)

class LogmonClient(rpc_common.RPCShellCommon):
    """ Log monitoring client. """

    NAME = 'AMQP Logging Client'

    def __init__(self, *args, **kwargs):
        rpc_common.RPCShellCommon.__init__(self, *args, **kwargs)
        self.get_credentials()
        self.get_connection()
        self.get_logchannel()


    def callback(self, ch, method, properties, body):
        # If line does not end with newline, add one
        (t,d,m) = body.partition(' ')
        t = self.iso8601_date(t)
        if m[-1] != '\n':
            m += '\n'
        sys.stdout.write("{0} {1}".format(t,m))
        if self.logfile is not None:
            LOGGER.info("{0} {1}".format(t,m))


    def run(self):
        result = self.logchannel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        self.logchannel.queue_bind(exchange=self.logexchange,
                   queue=self.queue_name)

        self.logchannel.basic_consume(self.callback,
                      queue=self.queue_name,
                      no_ack=True)
        sys.stderr.write(' [*] Waiting for logs on exchange ' +
                '"%s". To exit press CTRL+C\n' % self.logexchange)
        self.logchannel.start_consuming()


    def sendmessage(self,message):
        """Send a message over the AMQP messagae bus."""
        if self.logchannel is not None:
            self.client_log_bcast(message)

