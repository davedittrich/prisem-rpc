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
RPC Shell Base Class for Common Functionality

See the class documentation below for details.

"""

import sys
import os
import copy
import inspect
import locale
import logging
import socket
import arrow
import time
import pika
import json
import uuid
import base64
import hashlib
import platform
import yaml

from optparse import OptionParser as opt_parser
from dateutil import tz

import semantic_version

VERSION = '1.1.3'
# v = semantic_version.Version(VERSION)
# PROTOCOLVER = "%d.%d" % (v.major, v.minor)
# RELEASE = "%d" % (v.patch)
PROTOCOLVER = '0.5.5'
RELEASE = VERSION

#
# Defaults
#
# TODO(dittrich): Temporary fix
# The following is a temporary fix until there is time to
# refactor the code to use the rpc_config dictionary
# directly.

def extract(_dict, namespace=None):
        if not namespace: namespace = globals()
        namespace.update(_dict)

# Set defaults (may be over-ridden by rpc_config.yml file)

RPC_VHOST = '/'
RPC_SERVER = 'localhost'
RPC_DOMAIN = 'localdomain'
RPC_USER = 'rpc_user'
RPC_PWD = 'rpc_user'
RPC_RPCEXCHANGE = ''
RPC_LOGEXCHANGE = 'logs'
RPC_QUEUEBASE = 'rpc'
RPC_DISPLAY_UTC = True

def load_config():
    """
    Load configuration defaults. The first file found is loaded, using
    the following order:

    1. Environment variable RPC_CONFIG;
    2. File "rpc_config.yml" in the current working directory;
    3. File ".rpc_config.yml" in the user's HOME directory.

    If none of these are found, set defaults using hard-coded values.

    Example rpc_config.yml file:

    ---

    RPC_VHOST: '/'
    RPC_SERVER: 'localhost'
    RPC_DOMAIN: 'localdomain'
    RPC_USER: 'rpc_user'
    RPC_PWD: 'rpcm3pwd'
    RPC_RPCEXCHANGE: ''
    RPC_LOGEXCHANGE: 'logs'
    RPC_QUEUEBASE: 'rpc'
    RPC_DISPLAY_UTC: False

    """
    _conf_file = "rpc_config.yml"
    path1 = os.getenv("RPC_CONFIG", None)
    if path1 is not None:
        path1 = os.path.expanduser(path1)
        if os.path.isdir(path1):
            path1 += "/{}".format(_conf_file)
    try:
        path2 = os.getcwd() + "/{}".format(_conf_file)
    except OSError:
        path2 = None
    path3 = os.path.expanduser("~/.{}".format(_conf_file))

    for path in [path1, path2, path3]:
        if path is not None and os.path.exists(path):
            try:
                with open(path) as rpc_config:
                    _dict = yaml.load(rpc_config)
                extract(_dict)
            except Exception as e:
                continue
            return
    return

load_config()

LOGGER = logging.getLogger(__name__)

def context(level=1):
    (frame, filename, line_number, function_name, lines, index) = \
            inspect.getouterframes(inspect.currentframe())[level]
    return "%s:%s in %s" % (filename, line_number, function_name)

def check_path(path):
    """Validate whether program path exists."""
    if not os.path.exists(path):
        print "%s does not exist" % path
        sys.exit(1)
    return True

def rdb():
    import rdb
    rdb.set_trace()

def version():
    """Print program name and version, then exit."""
    print("{} {}".format(os.path.basename(sys.argv[0]), VERSION))
    sys.exit(0)


class RPC_Base_Object(object):
    """Base object for common attributes of all classes.

    """

    NAME = 'RPC_Base_Object'
    PROGRAM = 'unspecified_program'
    try:
        HOSTNAME = "{}.{}".format(socket.gethostname(), RPC_DOMAIN)
    except NameError:
        HOSTNAME = socket.getfqdn()
    except Exception as e:
        raise e

    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug', False)
        self.verbose = kwargs.pop('verbose', False)
        self.program = kwargs.pop('program', self.PROGRAM)
        self.logfile = kwargs.pop('logfile', None)
        self.scriptname = os.path.basename(kwargs.pop('scriptname', self.PROGRAM))
        self.hostname = self.HOSTNAME
        (_shortname, _extension) = \
            os.path.splitext(self.scriptname)
        if self.logfile is not None:
            if self.debug:
                logging.basicConfig(filename=self.logfile,
                        level=logging.DEBUG)
            else:
                logging.basicConfig(filename=self.logfile,
                        level=logging.INFO)

    def get_hostname(self):
        """Get hostname"""
        return self.hostname

    def get_platform(self):
        """Get platform version info"""
        return platform.version()

    def get_pika_version(self):
        """Get pika version"""
        return pika.__version__

    def get_pid(self):
        """Get process ID"""
        return os.getpid()

    def get_protocol_version(self):
        """ Get protocol version number."""
        return PROTOCOLVER

    def get_release(self):
        """ Get release number."""
        return RELEASE

    def get_name(self):
        return self.NAME

    def get_time(self):
        """Get current time."""
        return int(time.time())

    def load_config(self, _rpc_config_file=None):
        """Load configuration from ~/.rpc_config.yml file."""


    def logdebug(self, message):
        """Log message at DEBUG level."""
        dt = self.iso8601_date()
        LOGGER.debug("[+] %s %s" % (dt, context(2)))
        LOGGER.debug("[+] %s %s" % (dt, message))
        self.be_verbose(message)

    def loginfo(self, message):
        """Log message at INFO level."""
        dt = self.iso8601_date()
        LOGGER.info("[+] %s %s" % (dt, message))
        self.be_verbose(message)

    def be_verbose(self, message):
        """Send message to screen (via stderr) if in --verbose mode."""
        if self.verbose:
            dt = self.iso8601_date()
            sys.stderr.write('[+] %s %s\n' % (dt, message))

class RPC_Frame_Object(RPC_Base_Object):
    """Frame Object for RPC requests and responses.

    """

    NAME = 'RPC_Frame_Object'

    def __init__(self, *args, **kwargs):
        # Process keyword args in base class
        RPC_Base_Object.__init__(self, *args, **kwargs)
        self.appdata = {'none': 'none'}

    def get_release(self):
        """ Get release number."""
        return RELEASE

    def set_appdata(self, appdata={'none':'none'}):
        if type(appdata) is dict:
            self.appdata = appdata
        else:
            raise TypeError('appdata must be a dictionary')

    def get_appdata(self):
        """Get application data for frame (request/response).
        Over-ride this in inhereted objects."""
        return self.appdata

    def get_dict(self):
        return {'name': self.get('name'),
                'release': self.get_release(),
                'protocolver': self.get_protocol_version(),
                'hostname': self.get_hostname(),
                'platform': self.get_platform(),
                'pika_version': self.get_pika_version(),
                'pid': self.get_pid(),
                'time': self.get_time,
                'appdata': self.get_appdata()}

    def json(self):
        """Return JSON version of dictionary."""
        return json.dumps(self.get_dict())

    #def loads(self, body):
    #    dict = json.loads(body)
    #    self.name = dict['name']
    #    self.protocolver = dict['protocolver']
    #    self.time = dict['time']
    #    self.appdata = dict['appdata']

    def loads(self, data):
        if type(data) is str:
            jsonstr = data
        else:
            jsonstr = str(data)
        dict = json.loads(jsonstr)
        for k, v in dict.items():
            if k not in ['protocolver', 'time']:
                setattr(self, k.lower().replace('-', '_'), v)

    def prettyprint(self):
        """Return prettyprint string representation of object."""
        return json.dumps(self.get_dict(),
                sort_keys=True,
                indent=4,
                separators=(',', ': '))

    def get(self, attribute):
        """Get attribute."""
        return getattr(self,attribute,None)

    def __len__(self):
        return len(self.__str__())

    def __str__(self):
        """Return string representation of object."""
        return self.json()

    def terse(self):
        dict = copy.deepcopy(self.get_dict())
        if dict.has_key('appdata'):
            for item in dict['appdata'].keys():
                if type(dict['appdata'][item]) in [str,unicode] \
                        and len(dict['appdata'][item]) > 128:
                    td = dict['appdata'][item]
                    ts = "<<%d bytes; SHA1: %s>>" % \
                                (len(td), hashlib.sha1(td).hexdigest())
                    dict['appdata'][item] = ts
        return str(dict)

class RPC_Object(RPC_Base_Object):
    """Object for RPC client and servers.

    """

    NAME = 'Generic RPC_Object'

    def __init__(self, *args, **kwargs):
        # Process client+server related keywords here
        self.server = kwargs.pop('server', RPC_SERVER)
        if self.server is None:
            self.server = RPC_SERVER
        self.rpcexchange = kwargs.pop('rpcexchange', RPC_RPCEXCHANGE)
        self.logexchange = kwargs.pop('logexchange', RPC_LOGEXCHANGE)
        self.queuebase = kwargs.pop('queuebase', RPC_QUEUEBASE)
        self.vhost = kwargs.pop('vhost', RPC_VHOST)
        self.user = kwargs.pop('user', RPC_USER)
        self.pwd = kwargs.pop('pwd', RPC_PWD)
        RPC_Base_Object.__init__(self, *args, **kwargs)
        self.queue_name = None
        self.set_queue_name(self.queuebase)
        self.name = self.program

    def get(self, attribute):
        """Get attribute."""
        return getattr(self,attribute,None)

    def set_queue_name(self, base=RPC_QUEUEBASE):
        self.queue_name = "%s_%s" % (base, self.get_protocol_version())

    def get_queue_name(self):
        """Get queue name."""
        return self.queue_name

    def set_rpc_exchange(self, exchange=RPC_RPCEXCHANGE):
        """Set RPC exchange."""
        self.rpcexchange = exchange

    def get_rpc_exchange(self):
        """Get RPC exchange."""
        return self.rpcexchange

    def set_log_exchange(self, exchange=RPC_LOGEXCHANGE):
        """Set log exchange."""
        self.logexchange = exchange

    def get_log_exchange(self):
        """Get log exchange."""
        return self.logexchange


class RPCShellCommon(RPC_Object):
    """ RPC Shell common functionality root class.

    This abstract base class implements basic functions that are common to
    RPC shells of all kinds.

    This class is intended to be the top (root) class in a multi-level
    class hierarchy.  User-facing classes (i.e.  bottom of the hierarchy)
    should not be subclassed directly from this class.

    """

    # options that are common across ALL RPC shells
    COMMON_OPTIONS = [ {'s':'-d', 'l':'--debug',
                         'dest':'debug',
                         'action':'store_true', 'default':False,
                         'help':'Print debug-level messages to stderr.'},
                       {'s':'-u', 'l':'--usage',
                         'dest':'usage',
                         'action':'store_true', 'default':False,
                         'help':'Print usage information.'},
                       {'s':'-v', 'l':'--verbose',
                         'dest':'verbose',
                         'action':'store_true', 'default':False,
                         'help':'Be verbose (on stdout) about what ' +
                         'is happening.'},
                        {'s':'-e', 'l':'--rpc-exchange', 'dest':'rpcexchange',
                         'action':'store', 'default':'rpc', 'type':'str',
                         'metavar': 'RPCEXCHANGE',
                         'help': 'Exchange to use (default: \'rpc\')'},
                        {'l':'--log-exchange', 'dest':'logexchange',
                         'action':'store', 'default':'logs', 'type':'str',
                         'metavar': 'LOGEXCHANGE',
                         'help': 'Exchange to use (default: \'rpc\')'},
                        {'s':'-e', 'l':'--queue-base', 'dest':'queuebase',
                         'action':'store', 'default':'rpc', 'type':'str',
                         'metavar': 'QUEUE',
                         'help': 'Queue to use (default: \'rpc\')'},
                        {'s':'-s', 'l': '--log-file',
                         'dest':'log_to_file',
                         'action':'store_true', 'default':False,
                         'help':'Log to local file'},
                        {'s':'-l', 'l':'--log-syslog',
                         'dest':'log_to_syslog',
                         'action':'store_true', 'default':False,
                         'help':'Log to local syslog'},
                        {'s':'-F', 'l':'--syslog-facility', 'dest':'facility',
                         'action':'store', 'default':'LOG_LOCAL4', 'type':'str',
                         'help':'Log detector alerts to syslog using ' +
                             'specified facility'},
                        {'s':'-L', 'l':'--syslog-priority', 'dest':'priority',
                         'action':'store', 'default':'LOG_WARNING',
                         'type':'str',
                         'help':'Log detector alerts to syslog at specified ' +
                             'priority level'},
                         ]

    NAME = 'UnnamedGenericRPCShell'
    DEFAULT_TO_UTC=True

    USAGE = 'usage: %prog [options] ...'

    def __init__(self, *args, **kwargs):
        """Instantiate common shell object and parse commandline options."""
        RPC_Object.__init__(self, *args, **kwargs)

        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  #proper commas in nums
        self.parser = None
        self.connection = None
        self.channel = None
        self.logchannel = None
        self.creds = None
        self.display_utc = self.DEFAULT_TO_UTC
        self.idstr = "%s program=%s pika_version=%s release=%s host=%s pid=%d date=%s" % \
                (self.scriptname,
                self.program,
                self.get_pika_version(),
                self.get_release(),
                self.get_hostname(),
                self.get_pid(),
                self.iso8601_date())
        self.uuid = uuid.uuid4()

    def iso8601_date(self,ts=None):
        """Outputs time in ISO 8601 format(string)."""
        if ts is None:
            ts = arrow.utcnow()
        else:
            try:
                ts = arrow.get(ts)
            except Exception:
                LOGGER.info("[!!!] arrow parse error: \"%s\"" % ts)
            finally:
                ts = arrow.utcnow()
        if self.get_display_utc():
            LOGGER.debug("[+] displaying in utc")
            return "%s" % ts.to('UTC')
        else:
            LOGGER.debug("[+] displaying in localtime")
            return "%s" % ts.to('local')

    def seconds_to_iso8601_date(self, seconds):
        """Takes seconds from epoch time and converts to ISO 8601 format(string)."""
        return arrow.get(seconds)

    def iso8601_date_to_seconds(self, ts):
        """Takes ISO 8601 format(string) and converts into epoch time."""
        return arrow.get(ts).timestamp

    def get_default_to_utc(self):
        """Get the default for display in UTC."""
        return self.DEFAULT_TO_UTC

    def set_display_utc(self,flag=None):
        """Set the toggle for display of time in UTC."""
        if flag is None:
            self.display_utc = self.DEFAULT_TO_UTC
        else:
            self.display_utc = flag
        return self.display_utc

    def set_log_utc(self,flag=None):
        """Set the toggle for logging of time in UTC."""
        if flag is None:
            self.log_utc = self.DEFAULT_TO_UTC
        else:
            self.log_utc = flag
        return self.log_utc

    def set_display_in_localtime(self,flag=None):
        """Set the toggle for display of time in local time."""
        if flag is None:
            self.display_utc = not self.DEFAULT_TO_UTC
        else:
            self.display_utc = not flag
        return self.display_utc

    def get_display_utc(self):
        """Return whether we should display in UTC."""
        return self.display_utc

    def get_display_in_localtime(self):
        """Return whether we should display in local time."""
        return not self.display_utc

    def normalize_timestamp(self, ts=None):
        """Adjust timestamp according to localtime/UTC setting."""
        seconds = self.iso8601_date_to_seconds(ts)
        if self.display_utc:
            return arrow.get(seconds)
        else:
            return arrow.get(seconds)

    def get_uuid(self):
        return self.uuid

    def get_idstr(self):
        return self.idstr

    def dbg(self, message, *parameters):
        """If debugging is enabled, print the message with any passed
        parameters substituted into the message.

        """
        if self.debug:
            plist = list(parameters)
            if plist:
                sys.stderr.write(message.format(*plist))
            else:
                sys.stderr.write(message)
        return

    def _parse_options(self, options, extra_arg_count=0):
        """Parse all options, and store any extra arguments.

        Creates a RPCShellOptParse parser and parses the options list.  In the
        options list, each option is a dictionary, where all dictionary keys are
        the same as in a normal OptionParser object, except that the "s" key
        points to the short option string and the "l" key points to the long
        option (normally passed by positional arguments to the
        OptionParser.add_option() method.

        In addition to options, the method supports required arguments via the
        extra_arg_count parameter.  The said parameter specifies how many
        arguments are required.  When set to 1 or more, the object's
        self.extra_args variable will be set to a list with the one or more
        unnamed commandline arguments.

        """

        self.parser = opt_parser.RPCShellOptParser(self.USAGE)
        self.parser.add_dict_options(options)
        (options, args) = self.parser.parse_args() # actually parse all options

        if len(args) < (extra_arg_count):
            self.parser.error('Missing at least one required argument. ' +
                'See usage.')
        elif len(args) > (extra_arg_count):
            self.parser.error('Too many commandline argument(s). See usage.')

        # For any detector-specific option that includes the 'var' keyword we
        # set the value of var to that option's user-supplied value
        for option in options:
            setattr(self, option['dest'], getattr(options, option['dest']))

        if extra_arg_count > 0:     # only set s.extra_args if need to, so it
            self.extra_args = args  #   can be overridden by subclasses

    def get_credentials(self, user=None, pwd=None):
        """ Create credentials object for connecting to AMQP server. """
        self.logdebug("Getting credentials (user %s)" % self.user)
        self.creds = pika.PlainCredentials(self.user, self.pwd)

    def get_connection(self):
        """Connect to AMQP server."""
        if self.creds is None:
            raise Exception("No credentials")
        self.logdebug("Getting connection paramaters for server %s" % self.server)
        self.params = pika.ConnectionParameters(self.server,
            virtual_host=self.vhost,
            credentials=self.creds)
        self.logdebug("Connecting to server %s, virtual host: %s" % (self.server, self.vhost))
        try:
            self.connection = pika.BlockingConnection(self.params)
        except pika.exceptions.AMQPConnectionError as e:
            self.logdebug(str(e))
            sys.stderr.write(str(e) + "\n")
            sys.exit(1)
        except Exception:
            raise
        self.logdebug("Connected to server %s" % self.server)

    def declare_logexchange(self):
        self.logchannel.exchange_declare(exchange=self.logexchange,
                type='fanout')

    def get_logchannel(self):
        """Get logging channel."""
        if self.connection is not None:
            self.logdebug("Getting log channel")
            self.logchannel = self.connection.channel()
            self.logdebug("Got channel %r" % self.logchannel)
        else:
            raise Exception("No connection")

    # For format of loglines, see
    # http://foswiki.prisem.washington.edu/Development/AMQP_RPC
    # See also (tho we may not conform with) https://tools.ietf.org/html/rfc5424

    def client_log_bcast(self, message="", level="INFO",
            name=None, submodule="-"):
        if name is None:
            name = self.scriptname
        logline = "{0} {1} {2} {3} [{4}] [{5}] {6} {7}".format(
                self.iso8601_date(),
                self.get_hostname(),
                self.get_uuid(),
                name,
                submodule,
                self.get_pid(),
                level,
                message)
        self.logchannel.basic_publish(exchange=self.logexchange,
                routing_key='',
                body=logline)

    def get_channel(self):
        """Get channel."""
        if self.connection is not None:
            self.logdebug("Getting channel")
            self.channel = self.connection.channel()
            self.logdebug("Got channel %r" % self.channel)
        else:
            raise Exception("No connection")

    def exchange_declare(self):
        """Declare exchange."""
        #self.logdebug("Declaring exchange %s" % self.get_exchange())
        #self.channel.exchange_declare(exchange=self.get_exchange(),
        #    exchange_type="direct",
        #    auto_delete=False)
        pass

    def queue_declare(self):
        """Declare queue (must be over-ridden)."""
        raise Exception('queue_declare() not over-ridden.')

    def basic_publish(self):
        """Basic Publish (must be over-ridden)."""
        raise Exception('basic_publish() not over-ridden.')

    #def bind_queue(self, queue=None):
    #    """Bind queue."""
    #    self.logdebug("Binding to queue \"%s\" " % self.get_queue_name() +
    #                 "on exchange %s" % self.get_exchange())
    #    self.channel.queue_bind(queue=self.get_queue_name(),
    #        exchange=self.get_exchange(),
    #        routing_key=self.get_queue_name())



if __name__ == '__main__':
    for pgm in ["/bin/bash", "/usr/local/bin/ipgrep", "/bin/foobar"]:
        if check_path(pgm):
            print "%s exists" % pgm
    sys.exit(0)
