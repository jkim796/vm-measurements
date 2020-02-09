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
"""Producers based on yaml files."""

from threading import Condition
import os
import yaml

import harness.machine_producers.machine_producer as mp
from harness.machine import LocalMachine, RemoteMachine
from harness.machine_producers.gcp_vm_producer.create_gcp_vm import create_gcp_instance

class YamlMachineProducer(mp.MachineProducer):
    """Loads machines from a yaml file."""

    def __init__(self, path):
        self.machines = build_machines(path)
        self.max_machines = len(self.machines)
        self.machine_condition = Condition()

    def get_machines(self, num_machines) -> list:
        if num_machines > self.max_machines:
            raise ValueError(
                "Insufficient Ammount of Machines. {ask} asked for and have {max_num} max.".format(
                    ask=num_machines, max_num=self.max_machines))

        with self.machine_condition:
            while not self._enough_machines(num_machines):
                self.machine_condition.wait(timeout=1)
            return [self.machines.pop(0) for _ in range(num_machines)]

    def release_machines(self, machine_list):
        with self.machine_condition:
            while machine_list:
                machine = machine_list.pop()
                self.machines.append(machine)
            self.machine_condition.notify()

    def _enough_machines(self, ask):
        return ask <= len(self.machines)


def build_machines(path, num_machines=-1):
    """Builds machine objects defined by the yaml file "path".

    :param path: path to a yaml file which defines machines.
    :param num_machines: optional limit on how many machine objects to build.
    :return: machine objects in a list. If num_machines is set, len(machines) <= num_machines.
    """
    data = parse_yaml(path)
    machines = []
    for key, value in data.items():
        if len(machines) == num_machines:
            return machines
        if isinstance(value, dict):
            if 'instance_name' in value:
                vm_dict = create_gcp_instance(**value)
                machines.append(RemoteMachine(key, **vm_dict))
            else:
                machines.append(RemoteMachine(key, **value))
        else:
            machines.append(LocalMachine(key))
    return machines


def parse_yaml(path):
    """Parse the yaml file pointed by path.

    :param path: path to yaml file.
    :return: contents of the yaml file as a dictionary.
    """
    data = get_file_contents(path)
    return yaml.load(data, Loader=yaml.Loader)


def get_file_contents(path):
    """Dumps the file contents to a string and returns them.

    :param path: the path to dump.
    :return: file contents as string.
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    with open(path) as input_file:
        return input_file.read()
