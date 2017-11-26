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
RPC Server Class

See the class documentation below for details.

"""

import pika
import sys

from rpc import rpc_common

class RPC_Server(rpc_common.RPCShellCommon):
    """RPC Server object to be extended by RPC servers.

    """

    NAME = 'Generic RPC Service'

    def __init__(self, *args, **kwargs):
        rpc_common.RPCShellCommon.__init__(self, *args, **kwargs)
        self.get_credentials()
        self.get_connection()
        self.get_channel()
        self.get_logchannel()
        self.loginfo(self.get_idstr())
        exchange = self.get_rpc_exchange()
        if exchange is not '':
            self.logdebug("Declaring exchange %s" % exchange)
        self.logdebug("Declaring queue %s" % self.get_queue_name())
        self.channel.queue_declare(queue=self.get_queue_name(),
                auto_delete=False)
        if exchange is not '':
            self.logdebug("Binding queue %s to exchange %s" \
                    % (self.get_queue_name(), exchange))
            self.channel.queue_bind(queue=self.get_queue_name(),
                    exchange=self.get_rpc_exchange(),
                    routing_key=self.get_queue_name())

    def server_log_response(self, response):
        if self.debug:
            fname = "%s-lastresponse.txt" % self.program
            self.logdebug("Logging response to %s" % fname)
            lastresp = open(fname, "w")
            lastresp.write(self.responseobj.prettyprint() + '\n')
            lastresp.close()

    def logdebug(self, message):
        """Override logdebug from RPCShellCommon to send to fanout."""
        rpc_common.RPCShellCommon.logdebug(self, message)
        if self.logchannel is not None and self.debug:
            self.server_log_bcast(message)

    def loginfo(self, message):
        """Override loginfo from RPCShellCommon to send to fanout."""
        rpc_common.RPCShellCommon.loginfo(self, message)
        if self.logchannel is not None:
            self.server_log_bcast(message)

    def server_log_bcast(self, message):
        logline = "%s: %s" % (self.get_uuid(), message)
        self.logchannel.basic_publish(exchange=self.logexchange,
                routing_key='',
                body=logline)

#    def server_basic_publish(self, response, routing_key,
#            delivery_tag, correlation_id):
#        """Server basic publish."""
#
#        if self.debug:
#            fname = "%s-lastresponse.txt" % self.program
#            self.logdebug("Logging response to %s" % fname)
#            lastresp = open(fname, "w")
#            lastresp.write(str(response) + '\n')
#            lastresp.close()
#        self.logdebug("Server basic publish: routing_key=%s correlation_id=%s" \
#                % (routing_key, correlation_id))
#        self.channel.confirm_delivery()
#        self.channel.basic_publish(exchange='',
#                routing_key=routing_key,
#                properties=pika.BasicProperties(
#                    correlation_id=correlation_id),
#                body=str(response.json()))
#        self.logdebug("Server basic publish complete")
#        self.logdebug("basic_ack delivery_tag %s" % delivery_tag)
#        self.channel.basic_ack(delivery_tag=delivery_tag)

    def run(self):
        """Run an RPC service (using self.on_request() for processing request)."""
        self.logdebug("Setting basic_qos, prefetch_count=1")
        self.channel.basic_qos(prefetch_count=1)
        self.logdebug("Basic_consume, callback on_request(), queue %s" \
                % self.get_queue_name())
        self.channel.basic_consume(self.on_request,
            queue=self.get_queue_name())
        self.logdebug("Server waiting for RPC calls.")
        self.channel.start_consuming()
        #except KeyboardInterrupt:
        #    sys.stderr.write("Exiting on keyboard interrupt.\n")
        #    self.logdebug("Exiting on keyboard interrupt.")
        #except Exception:
        #    raise

