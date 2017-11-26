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
RPC Response Class

See the class documentation below for details.

"""

import json
import base64

from rpc.rpc_common import RPC_Frame_Object

RETCODE = 1
STDOUT = 'undefined_stdout\n'
STDERR = 'undefined_stderr\n'

class RPC_Response(RPC_Frame_Object):
    """RPC Response object.

    """

    NAME = 'RPC_Response'

    def __init__(self, *args, **kwargs):
        RPC_Frame_Object.__init__(self, *args, **kwargs)
        self.name = self.program

    def get_stdout(self):
        """Return stdout text."""
        return self.appdata['stdout']

    def get_stderr(self):
        """Return stderr text."""
        return self.appdata['stderr']

    def get_retcode(self):
        """Get return code."""
        return self.appdata['retcode']

    def set_response(self, retcode, stdout_, stderr_):
        """Set response from triple (retcode, stdout_, stderr_)."""
        self.retcode = retcode
        self.stdout = stdout_
        self.stderr = stderr_

    def load_response(self, dict):
        """Load response from dictionary."""
        self.retcode = dict['retcode']
        self.stdout = dict['stdout']
        self.stderr = dict['stderr']

    def get_response(self):
        """Get response dictionary."""
        return self.get_appdata()

