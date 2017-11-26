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
RPC Request Class

See the class documentation below for details.

"""

import json

from rpc.rpc_common import RPC_Frame_Object

class RPC_Request(RPC_Frame_Object):
    """RPC Request object.

    """

    NAME = 'RPC_Request'

    def __init__(self, *args, **kwargs):
        RPC_Frame_Object.__init__(self, *args, **kwargs)
        ARGSOPTS = {'program': self.program,
                'usage': 'true'}
        self.appdata = kwargs.pop('argsopts', ARGSOPTS)
        self.name = self.program

    def get_appdata(self):
        """Get application data for frame."""
        return self.appdata

