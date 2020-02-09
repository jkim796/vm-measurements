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

"""Producer that produces machines backed by GCP VMs."""

import copy
import time
import string
import random
import os
from http import HTTPStatus
import googleapiclient.discovery
from googleapiclient.errors import HttpError

import harness.machine_producers.machine_producer as mp
from harness.machine import GCPMachine

# See http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.instances.html#insert
# for full list of options here. This is the base config for GCP machines with a name,
# machine type, and source disk being added on creation.
# pylint: disable=all
MACHINE_CONFIG = {
    # Specify the boot disk and the image to use as a source.
    'disks': [
        {
            'boot': True,
            'autoDelete': True,
        }
    ],
    # Set preemptible by default.
    'scheduling': {
        'preemptible': True
    },
    'networkInterfaces': [{
        'network': 'global/networks/default',
        'accessConfigs': [
            {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
        ]
    }],

    # Allow the instance to access cloud storage and logging.
    'serviceAccounts': [{
        'email': 'default',
        'scopes': [
            'https://www.googleapis.com/auth/devstorage.read_write',
            'https://www.googleapis.com/auth/logging.write'
        ]
    }],
}


class GCPMachineProducer(mp.MachineProducer):
    """Creates machines from on a GCP account and makes them available for benchmarks.

    Given a user's valid GCP credentials to a GCP account set with a project,
    Machine producer will create VMs on a given GCP account. The VMs will be
    created in "project", in the availability zone "zone", based on the base
    image "image", and of the type "machine_type". It will the wrap
    those machines in a Machine object so that they can be passed to benchmark
    methods.

    Attributes:
        project: The GCP project under which VMs should be created.
        zone: The availability zone to create the VMs (e.g. us-west1-b).
        machine_type: The type of machine to create (e.g. n1-standard-1).
        image: The image link to an image from which to build.
        compute: The compute API resource.
        api_key_path: Path to an API key.
        http: a custom httplib2 object (or mock http server). Used for mocking the server.
        cache: a googleapiclient.discovery_cache.base.Cache implementation used for recording
        responses. An implementation is in "test_data/generate_mock.py".
    """

    def __init__(self, project: str, zone: str, machine_type: str, api_key_path: str=None, http=None, cache=None):
        """

        :param project: name of the project to be used. This must correspond to a user's
        GCP account.
        :param zone: zone where GCP machine should be created (e.g. us-west1-b).
        :param machine_type: machine size to be created (e.g. n1-standard-1).
        :param api_key_path: path to a valid API key for calling the GCP API. Leave none if using a Mock.
        :param http: A httplib2 object or other compatible object for constructing http requests.
        :param cache: A cache object to record responses.
        see: https://github.com/googleapis/google-api-python-client
        """
        self.project = project
        self.zone = zone
        self.machine_type = machine_type
        self.image = None
        self.api_key_path = api_key_path
        self.http = http
        self.cache = cache
        cache_discovery = True if cache else False
        if api_key_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key_path
            self.compute = \
                googleapiclient.discovery.build('compute', 'v1', cache_discovery=cache_discovery, cache=cache)
        else:
            self.compute = googleapiclient.discovery.build('compute', 'v1', http=http, developerKey="mock")

    def get_machines(self, num_machines: int) -> list:
        return [self._new_instance("machine-") for _ in range(num_machines)]

    def release_machines(self, machine_list: list):
        for machine in machine_list:
            self._delete_instance(machine)

    def set_image(self, image: str) -> str:
        """Gets the image link of 'image_name' associated with the set project.

        :param image: name of the image to be found.
        :return: image link as a str
        """
        # pylint: disable=no-member
        response = self._execute_request(
            self.compute.images().get(
                project=self.project,
                image=image)
        )
        self.image = response["selfLink"]

    def _new_instance(self, prefix: str) -> GCPMachine:
        """Creates instances with name prefix{32 random digits}.

        :param prefix: name prefix for machines
        :return: name:str - name of the machine, instance:dict - object representing
        an instance. See:
        http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.instances.html#get
        """
        name = ""
        instance = None
        while instance is None:
            try:
                # Make a randomly named instance.
                name = prefix + ''.join(random.choice(string.digits) for n in range(32))
                self._create_instance(name)
                return GCPMachine(name, self._get_instance(name))
            except HttpError as http_error:
                # If a machine exists with this name, the server returns a
                # 409 error. This should be rare.
                if http_error.resp.status == HTTPStatus.CONFLICT:
                    continue
                else:
                    raise http_error

    def _get_instance(self, name: str) -> dict:
        """Get's instance information

        :param name: Instance name.
        :return: dict - object representing an instance. See:
        http://googleapis.github.io/google-api-python-client/docs/dyn/compute_v1.instances.html#get
        """
        # pylint: disable=no-member
        return self._execute_request(self.compute.instances().get(
            project=self.project,
            zone=self.zone,
            instance=name)
        )

    def _create_instance(self, name: str):
        """Creates an instance.

        :param name: name of the instance
        :return: None
        """
        instance_config = copy.deepcopy(MACHINE_CONFIG)
        instance_config["name"] = name
        instance_config["machineType"] = \
            "zones/{zone}/machineTypes/{type}".format(zone=self.zone, type=self.machine_type)
        instance_config["disks"][0]["initializeParams"] = {"sourceImage": self.image}
        # pylint: disable=no-member
        operation = self._execute_request(
            self.compute.instances().insert(
                project=self.project,
                zone=self.zone,
                body=instance_config)
        )
        self._wait_for_operation(operation["name"])

    def _delete_instance(self, machine):
        """Tries to delete a machine based on machine's name. Machine must be
        under the project pointed to by self.project.

        :param machine: Machine object, which should probably be a GCPMachine.
        :return: None
        """
        # pylint: disable=no-member
        return self._execute_request(
            self.compute.instances().delete(
                project=self.project,
                zone=self.zone,
                instance=machine.name)
        )

    def _wait_for_operation(self, operation):
        """Waits for operation to complete.

        :param operation: operation resource. See:
        https://cloud.google.com/resource-manager/reference/rest/v1/operations/get
        :return: None
        """
        while True:
            # pylint: disable=no-member
            result = self._execute_request(
                self.compute.zoneOperations().get(
                    project=self.project,
                    zone=self.zone,
                    operation=operation)
            )

            if result['status'] == 'DONE':
                if 'error' in result:
                    raise Exception(result['error'], "Got error while waiting on operation.")
                return result
            time.sleep(1)

    def _execute_request(self, request):
        ret = request.execute()
        if self.cache:
            self.cache.set_json(ret)
        return ret


class GCPOperationWaitError(Exception):
    """Error Raised when waiting on an Operation returns an error. """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


