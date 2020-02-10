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
"""Producers of mocks."""

import harness.machine_producers.machine_producer as mp
from harness.machine import MockMachine


class MockMachineProducer(mp.MachineProducer):
    """Produces MockMachine objects."""

    def get_machines(self, num_machines) -> list:
        """Returns the request number of MockMachines."""
        return [MockMachine() for i in range(num_machines)]

    def release_machines(self, machine_list):
        """No-op."""
        return
