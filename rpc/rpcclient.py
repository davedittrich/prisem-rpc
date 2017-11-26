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
RPC Client Class

See the class documentation below for details.

"""

import pika
import uuid

from rpc import rpc_common
from rpc import rpcresponse

class RPC_Client(rpc_common.RPCShellCommon):
    """RPC Client object to be extended by RPC clients.

    """

    NAME = 'Generic RPC Client'

    def __init__(self, *args, **kwargs):
        rpc_common.RPCShellCommon.__init__(self, *args, **kwargs)
        self.get_credentials()
        self.get_connection()
        self.get_logchannel()
        self.declare_logexchange()
        self.loginfo(self.get_idstr())
        self.get_channel()
        #self.exchange_declare()
        self.logdebug("Declaring callback queue")
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.logdebug("Client basic_consume, callback %s, queue %s" \
                % (self.on_response, self.callback_queue))
        self.channel.basic_consume(self.on_response, no_ack=True,
            queue=self.callback_queue)

    def client_log_request(self, request):
        if self.debug:
            fname = "%s-lastrequest.txt" % self.program
            self.logdebug("Logging request to %s" % fname)
            lastreq = open(fname, "w")
            lastreq.write(request.prettyprint() + '\n')
            lastreq.close()

    def logdebug(self, message):
        """Override logdebug from RPCShellCommon to send to fanout."""
        rpc_common.RPCShellCommon.logdebug(self, message)
        if self.logchannel is not None and self.debug:
            self.client_log_bcast(message)

    def loginfo(self, message):
        """Override loginfo from RPCShellCommon to send to fanout."""
        rpc_common.RPCShellCommon.loginfo(self, message)
        if self.logchannel is not None:
            self.client_log_bcast(message)

    def client_basic_publish(self, request):
        """Client basic publish."""
        self.client_log_request(request)
        self.logdebug("Client basic publish: exchange=%s queue=%s correlation_id=%s" \
                % (self.get_rpc_exchange(), self.get_queue_name(), self.correlation_id))
        self.channel.confirm_delivery()
        self.channel.basic_publish(
                exchange='', # self.get_rpc_exchange(),
                routing_key=self.get_queue_name(),
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.correlation_id,
                    ),
                body=str(request))
        self.logdebug("Client basic publish complete")

    def call(self, request):
        from time import time
        self.amqresponse = None
        responseobj = rpcresponse.RPC_Response(program=self.program)

        self.correlation_id = str(self.get_uuid())
        start = int(time())
        self.client_basic_publish(request)
        self.logdebug("Waiting for response from server...")
        while self.amqresponse is None:
            self.connection.process_data_events()
        # want to return (retcode, stdout, stderr) instead
        self.logdebug("Returning from call()")
        self.loginfo("Response to call() took %d seconds (host %s, pid %d)" % \
                (int((time() - start)), self.get_hostname(), self.get_pid()))
        responseobj.loads(self.amqresponse)
        return responseobj

    def on_response(self, ch, method, props, body):
        self.logdebug("Comparing correlation_id %s with %s" \
                    % (self.correlation_id, props.correlation_id))
        if self.correlation_id == props.correlation_id:
            self.logdebug("Got response for correlation_id %s" \
                    % self.correlation_id)
            self.amqresponse = body

