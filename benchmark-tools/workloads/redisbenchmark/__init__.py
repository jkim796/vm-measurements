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
"""Redis-benchmark tool."""

import re


OPERATIONS = [
    "PING_INLINE",
    "PING_BULK",
    "SET",
    "GET",
    "INCR",
    "LPUSH",
    "RPUSH",
    "LPOP",
    "RPOP",
    "SADD",
    "HSET",
    "SPOP",
    "LRANGE_100",
    "LRANGE_300",
    "LRANGE_500",
    "LRANGE_600",
    "MSET",
]

METRICS = dict()

# Bind a metric for each operation noted above.
for op in OPERATIONS:
    def bind(metric):
        """Bind op to a new scope."""
        def parse(data: str, **kwargs) -> float:
            """Operation throughput in requests/sec."""
            regex = r"\"" + metric + r"( .*)?\",\"(\d*.\d*)"
            res = re.compile(regex).search(data)
            if res:
                return float(res.group(2))
            return 0.0
        parse.__name__ = metric
        return parse
    METRICS[op] = bind(op)
