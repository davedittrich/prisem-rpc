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

from setuptools import setup, find_packages
import os
import versioneer

setup(
    version=versioneer.get_version(),
    packages={'': 'prisem-rpc'},
    cmdclass=versioneer.get_cmdclass(),
    setup_requires=['pbr>=2.0'],
    pbr=True)
