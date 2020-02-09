# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Benchmark helpers."""

from datetime import datetime
from harness.machine import Machine

class Timer:
    """Helper to time runtime of some call. Usage:

    with Timer as t:
        # do something.
        t.get_time_in_seconds()
    """
    def __init__(self):
        self._start = datetime.now()

    def __enter__(self):
        self.start()
        return self

    def start(self):
        """Starts the timer."""
        self._start = datetime.now()

    def elapsed(self):
        """:return: the elapsed time in seconds."""
        return (datetime.now() - self._start).total_seconds()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass


def drop_caches(machine: Machine):
    """Drops caches on the machine.

    :param machine: A machine
    :return: None
    """
    machine.run("sudo sync")
    machine.run("sudo sysctl vm.drop_caches=3")
    machine.run("sudo sysctl vm.drop_caches=3")
