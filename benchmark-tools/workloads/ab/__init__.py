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
"""Apachebench tool."""

import re


def transfer_rate(data: str, **kwargs) -> float:
    """Mean transfer rate in Kbytes/sec."""
    regex = r"Transfer rate:\s+(\d+\.?\d+?)\s+\[Kbytes/sec\]\s+received"
    return float(re.compile(regex).search(data).group(1))


def latency(data: str, **kwargs) -> float:
    """Mean latency in milliseconds."""
    regex = r"Total:\s+\d+\s+(\d+)\s+(\d+\.?\d+?)\s+\d+\s+\d+\s"
    res = re.compile(regex).search(data)
    return float(res.group(1))


def requests_per_second(data: str, **kwargs) -> float:
    """Requests per second."""
    regex = r"Requests per second:\s+(\d+\.?\d+?)\s+"
    res = re.compile(regex).search(data)
    return float(res.group(1))
