# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Create a GCP VM instance."""

import os
import time
import socket
import getpass
import logging
import timeout_decorator
import googleapiclient.discovery
from Crypto.PublicKey import RSA
from harness import ssh_connection


def _list_instances(compute, project, zone):
    """
    List all instances of a certain project located in a certain zone.

    :param compute: compute resource for interacting with a GCP API.
    :param project: Google Cloud project ID.
    :param zone: compute Engine zone to deploy the VM to.
    :return: all VM instances deployed in the zone of the project.
    """
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


#pylint: disable-msg=too-many-arguments
def _create_instance(compute, project, zone, name, username, private_key_path):
    """
    Create a VM instance as specified by the arguments.

    :param compute: compute resource for interacting with a GCP API.
    :param project: Google Cloud project ID.
    :param zone: compute Engine zone to deploy the VM to.
    :param name: name of the VM instance.
    :param username: username to log into the VM.
    :param private_key_path: location to store ssh key.
    :return: operation to create the VM instance.
    """
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='debian-cloud', family='debian-9').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine.
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    # (TODO): add a custom option for startup script that users can provide
    #  their own package requirements.
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()

    # Get information of local host.
    local_hostname = socket.gethostbyname(socket.gethostname())
    local_username = getpass.getuser()
    ssh_key_name = "%s@%s" % (local_username, local_hostname)
    ssh_public_key = _generate_or_fetch_ssh_key(ssh_key_name, private_key_path)

    # pylint: disable=all
    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
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

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'ssh-keys',
                'value': '%s:%s' % (local_username, ssh_public_key)
            }, {
                'key': 'docker-user',
                'value': username
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


def _wait_for_operation(compute, project, zone, operation):
    """
    Wait for an operation to finish.

    :param compute: compute resource for interacting with a GCP API.
    :param project: Google Cloud project ID.
    :param zone: compute Engine zone to deploy the VM to.
    :param operation: operation to wait for the result.
    :return: error of the operation result; None if nothing goes wrong.
    """
    logging.debug('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            logging.debug("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def _generate_or_fetch_ssh_key(public_key_name, private_key_path):
    """
    Generate a ssh key pair if private_key_path and the corresponding public key
    file do not exist and write them into files, use the existing key pairs
    otherwise

    :param public_key_name: name for the public key, embedded as the end of the
    public key file.
    :param private_key_path: location of the private key will be written to.
    :return: the public key corresponding to the generated private key.
    """

    public_key_path = "%s.pub" % private_key_path

    # Reuse the existing SSH key pairs when possible.
    if os.path.isfile(private_key_path) and os.path.isfile(public_key_path):
        public_key = open(public_key_path, 'r').read()
        return public_key

    # Generate a new private key.
    private_key = RSA.generate(4096)
    with open(private_key_path, "wb") as file:
        os.chmod(private_key_path, 0o0600)
        file.write(private_key.exportKey('PEM'))

    # Get the public key.
    pubkey = private_key.publickey()
    public_key = "%s %s" % (
        pubkey.exportKey('OpenSSH').decode('utf-8'), public_key_name)
    with open(public_key_path, "w") as file:
        file.write(public_key)

    return public_key


@timeout_decorator.timeout(180)
def _check_startup_script_finished(name, hostname, key_path, username):
    """
    It takes around two minutes for startup-script to finish installing
    all the required packages for running benchmark tools. We use a SSH client
    to check if the VM is ready (e.g. Docker is running) periodically.
    """

    connection = ssh_connection.SSHConnection(name, hostname, key_path,
                                              username)
    while True:
        # Loop until the user has the permission to run docker
        _, stderr = connection.run("docker run hello-world")
        if stderr:
            time.sleep(5)
        else:
            break


def create_gcp_instance(project, zone, instance_name, username):
    """
    Create a GCP instance specified by the arguments.

    :param project: Google Cloud project ID.
    :param zone: compute Engine zone to deploy the VM to.
    :param instance_name: name of the VM instance.
    :param username: username to log into the VM.
    :param kwargs: auxiliary arguments from the YAML file.
    :return: a dictionary containing the information to log into this newly
    created VM.
    """
    logging.basicConfig(filename=os.path.join(
        os.path.dirname(__file__), "vm_creation.log"), level=logging.DEBUG)

    compute = googleapiclient.discovery.build('compute', 'v1')

    private_key_path = os.path.expanduser("~/.ssh/%s.PEM" % instance_name)

    logging.debug('Creating instance.')

    operation = _create_instance(compute, project, zone, instance_name,
                                 username,
                                 private_key_path)

    _wait_for_operation(compute, project, zone, operation['name'])

    instances = _list_instances(compute, project, zone)

    logging.debug('Instances in project %s and zone %s:', project, zone)

    vm_dict = {}
    for instance in instances:
        logging.debug(' - %s', instance['name'])
        vm_external_ip = str(
            instance['networkInterfaces'][0]['accessConfigs'][0]
            ['natIP'])
        if instance_name == instance['name']:
            vm_dict = {
                'hostname': vm_external_ip,
                'username': username,
                'key_path': private_key_path
            }

    logging.debug("""
  Instance created.
  It will take a minute or two for the instance to complete work.
  """)

    _check_startup_script_finished(instance_name, vm_external_ip,
                                   private_key_path, username)

    return vm_dict
