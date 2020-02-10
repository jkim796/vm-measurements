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
"""Machine abstraction. This is the primary API for benchmarks."""

import logging
import subprocess
import re
import time
import docker

from harness import LOCAL_WORKLOADS_PATH, tunnel_dispatcher, ssh_connection
from harness.container import Container, MockContainer, DockerContainer


class Machine:
    """The machine object is the primary object for benchmarks. Machine objects
    are passed to each metric function call and benchmarks use machines to
    access real connections to those machines."""

    def run(self, cmd: str):
        """Convenience method for running a bash command on a machine object.
        Some machines may point to the local machine, and thus, do not have ssh
        connections. Run runs a command either local or over ssh and returns the
        output stdout and stderr as strings.

        :param cmd: command to run as a string.
        """
        raise NotImplementedError

    def read(self, path: str) -> str:
        """Reads the contents of some file. This will be mocked.

        :param path: path to the file to be read.
        :return: the file contents.
        """
        raise NotImplementedError

    def pull(self, workload: str) -> str:
        """Send the given workload to the machine, build and tag it, then return
        the tagged name. All images must be defined by the workloads
        directory.

        :param workload: the workload name.
        :return: the workload tag.
        """
        raise NotImplementedError

    def container(self, image: str, **kwargs) -> Container:
        """Returns a container object.

        :param image: the pulled image tag.
        :return: a Container object.
        """
        raise NotImplementedError

    def sleep(self, amount: float):
        """Sleeps the given amount of time."""
        raise NotImplementedError


class MockMachine(Machine):
    """A mocked machine."""

    def run(self, cmd: str) -> (str, str):
        return "", ""

    def read(self, path: str) -> str:
        # Load the contents from the machine_mocks directory.
        return open("harness/machine_mocks/%s" % path, "r").read()

    def pull(self, workload: str) -> str:
        return workload  # Workload is the tag.

    def container(self, image: str, **kwargs) -> Container:
        return MockContainer(image)

    def sleep(self, amount: float):
        pass


def get_address(machine: Machine) -> str:
    """Return a machine's default address."""
    default_route, _ = machine.run("ip route get 8.8.8.8")
    return re.search(" src ([0-9.]+) ", default_route).group(1)


class LocalMachine(Machine):
    """The local machine."""

    def __init__(self, name):
        self._name = name
        self._docker_client = docker.from_env()

    def __str__(self):
        return self._name

    def run(self, cmd: str) -> (str, str):
        process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")

    def read(self, path: str) -> str:
        # Read the exact path locally.
        return open(path, 'r').read()

    def pull(self, workload: str) -> str:
        # Run the docker build command locally.
        logging.info("Building %s@%s locally...", workload, self._name)
        self.run("docker build --tag={} {}".format(
            workload, LOCAL_WORKLOADS_PATH.format(workload)))
        return workload # Workload is the tag.

    def container(self, image: str, **kwargs) -> Container:
        # Return a local docker container directly.
        return DockerContainer(self._docker_client, get_address(self), image, **kwargs)

    def sleep(self, amount: float):
        time.sleep(amount)


class RemoteMachine(Machine):
    """Remote machine accessible via an SSH connection."""

    def __init__(self, name, **kwargs):
        self._name = name
        self._ssh_connection = ssh_connection.SSHConnection(name, **kwargs)
        self._tunnel = tunnel_dispatcher.Tunnel(name, **kwargs)
        self._tunnel.connect()
        self._docker_client = self._tunnel.get_docker_client()

    def __str__(self):
        return self._name

    def run(self, cmd: str) -> (str, str):
        return self._ssh_connection.run(cmd)

    def read(self, path: str) -> str:
        # Just cat remotely.
        stdout, stderr = self._ssh_connection.run("cat '{}'".format(path))
        return stdout + stderr

    def pull(self, workload: str) -> str:
        # Push to the remote machine and build.
        logging.info("Building %s@%s remotely...", workload, self._name)
        remote_path = self._ssh_connection.send_workload(workload)
        self.run("docker build --tag={} {}".format(workload, remote_path))
        return workload # Workload is the tag.

    def container(self, image: str, **kwargs) -> Container:
        # Return a remote docker container.
        return DockerContainer(self._docker_client, get_address(self), image, **kwargs)

    def sleep(self, amount: float):
        time.sleep(amount)


class GCPMachine(MockMachine):
    """Remote machine backed by GCP VM. Created by GCPMachineProducer"""
    def __init__(self, name, instance):
        self.name = name
        self.instance = instance
