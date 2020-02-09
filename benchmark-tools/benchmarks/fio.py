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
"""File I/O tests."""

import os

from benchmarks import benchmark, helpers
from harness.machine import Machine
from workloads.fio import read_bandwidth, write_bandwidth
from workloads.fio import read_io_ops, write_io_ops


#pylint: disable-msg=too-many-arguments
#pylint: disable-msg=too-many-locals
def fio(machine: Machine,
        test: str,
        ioengine: str = "sync",
        size: int = 1024 * 1024 * 1024,
        iodepth: int = 4,
        blocksize: int = 1024 * 1024,
        time: int = -1,
        mount_dir: str = "",
        filename: str = "file.dat",
        tmpfs: bool = False,
        ramp_time: int = 0,
        **kwargs: dict) -> str:
    """
    For more on fio see:
    https://media.readthedocs.org/pdf/fio/latest/fio.pdf

    :param test: test to run (read, write, randread, randwrite, etc.)
    :param ioengine: The engine for I/O.
    :param iodepth: The I/O for certain engines.
    :param blocksize: The blocksize for reads and writes in bytes (if an integer) or 4k, 1m, etc.
    :param size: The size of the generated file in bytes (if an integer) or 5g, 16k, 1m etc.
    :param time: if test is time based, how long to run in seconds
    :param filename: name of the file to creat inside container. For a path of /dir/dir/file,
    the script setup a volume like 'docker run -v mount_dir:/dir/dir fio' and fio will create
    (and delete) the file /dir/dir/file. If tmpfs is set, this /dir/dir will be a tmpfs.
    :param mount_dir: absolute path on the host to mount a bind mount.
    :param tmpfs: if true, mount on tmpfs.
    :param ramp_time: time to run before recording statistics
    :return: The output of fio as a string.
    """
    # Pull the image before dropping caches.
    image = machine.pull("fio")

    if not mount_dir:
        stdout, _ = machine.run("pwd")
        mount_dir = stdout.rstrip()

    # Setup the volumes.
    volumes = {mount_dir: {"bind": "/disk", "mode": "rw"}} if not tmpfs else None
    tmpfs = {"/disk": ""} if tmpfs else None

    # Construct a file in the volume.
    filepath = os.path.join("/disk", filename)

    # If we are running a read test, us fio to write a file and then flush file
    # data from memory.
    if "read" in test:
        machine.container(image, volumes=volumes, tmpfs=tmpfs, **kwargs).run(
            test="write", ioengine="sync", size=size, iodepth=iodepth, blocksize=blocksize,
            path=filepath)
        helpers.drop_caches(machine)

    # Run the test.
    time_str = "--time_base --runtime={time}".format(time=time) if int(time) > 0 else ""
    res = machine.container(image, volumes=volumes, tmpfs=tmpfs, **kwargs).run(
        test=test, ioengine=ioengine, size=size, iodepth=iodepth, blocksize=blocksize,
        time=time_str, path=filepath, ramp_time=ramp_time)

    machine.run("rm {path}".format(path=os.path.join(mount_dir.rstrip(), filename)))

    return res


@benchmark(metrics=[read_bandwidth, read_io_ops], machines=1)
def read(*args, **kwargs):
    """Read test.\n"""
    return fio(*args, test="read", **kwargs)


@benchmark(metrics=[read_bandwidth, read_io_ops], machines=1)
def randread(*args, **kwargs):
    """Random read test.\n"""
    return fio(*args, test="randread", **kwargs)


@benchmark(metrics=[write_bandwidth, write_io_ops], machines=1)
def write(*args, **kwargs):
    """Write test.\n"""
    return fio(*args, test="write", **kwargs)


@benchmark(metrics=[write_bandwidth, write_io_ops], machines=1)
def randwrite(*args, **kwargs):
    """Random write test.\n"""
    return fio(*args, test="randwrite", **kwargs)
