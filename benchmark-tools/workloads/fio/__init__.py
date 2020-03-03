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
"""FIO benchmark tool."""

import json


def read_bandwidth(data: str, **kwargs) -> int:
    """file i/o bandwidth."""
    return json.loads(data)["jobs"][0]["read"]["bw"] * 1024


def write_bandwidth(data: str, **kwargs) -> int:
    """file i/o bandwidth."""
    return json.loads(data)["jobs"][0]["write"]["bw"] * 1024


def read_io_ops(data: str, **kwargs) -> float:
    """file i/o operations per second"""
    return float(json.loads(data)["jobs"][0]["read"]["iops"])


def write_io_ops(data: str, **kwargs) -> float:
    """file i/o operations per second"""
    return float(json.loads(data)["jobs"][0]["write"]["iops"])


# change function names so we just print "bandwidth" and "io_ops
read_bandwidth.__name__ = "bandwidth"
write_bandwidth.__name__ = "bandwidth"
read_io_ops.__name__ = "io_ops"
write_io_ops.__name__ = "io_ops"
