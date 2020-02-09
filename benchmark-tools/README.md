# Benchmark Tools

These scripts are tools for collecting performance data for Docker-based tests.

## Setup

The scripts assume the following:
 * You have a local machine capable of running python3.5. This machine will be refered to as the "local"
 machine.
 * You have some machine(s) with docker installed. These machines will be refered to as the "Environment".
 * Environment machines have the runtime(s) under test installed, such that you
    can run docker with a command like: `docker run --runtime=$RUNTIME your/image`.
 * You are able to login to machines in the environment with the local machine via ssh
 and the user for ssh can run docker commands without using `sudo`.
 * The docker daemon on each of your environment machines is listening on `unix:///var/run/docker.sock`
   (docker's default).

For configuring the environment manually, consult the [dockerd documentation][dockerd].

For configuring the local machine install:
 * Python 3.5
 * pip3

A makefile is provided to make it easy to get set up, and it requires:
 * make
 * virtualenv
 * [libcap headers](https://pythonhosted.org/python-prctl/)

It is recommended that you run in a virtualenv, and after running `make`, you can activate it with
`source venv/bin/activate`.

## Environment

All benchmarks require a user defined yaml file describe the environment. These
files are of the form:

```yaml
machine1: local
machine2:
  hostname: 100.100.100.100
  username: username
  key_path: ~/private_keyfile
  key_password: passphrase
machine3:
  project: benchmark-environment
  zone: us-west1-a
  instance_name: example-instance
  username: example-user
```

The yaml file defines an environment with three machines named `machine1`, `machine2` and `machine3`.
machine1 is the local machine. machine2 is the machine at `100.100.100.100` reachable by the
command `ssh -i ~/key_path username@100.100.100.100` and login using the passphrase `key_password`.
machine3 is a Google Cloud Platform (GCP) virtual machine that will be created automatically in the
GCP project `benchmark-environment` in the zone `us-west1-a` with name `example-instance` when
running `perf.py`. `perf.py` will also handle logging into `username@external_ip_of_vm` to run the
benchmarks.

The above is an example only. Generally machines should be uniform, since they
are treated as such by the tests. Machines must also be accessible to each other
via their default routes. Furthermore, some benchmarks will meaningless if running on the local machine,
such as density.

For remote machines, `hostname`, `key_path`, and `username` are required and others are optional. In addition
key files must be generated [using the instrcutions below](#generating-ssh-keys).

The above yaml file can be checked for correctness with the `validate` command
in the top level perf.py script:

`python3 perf.py validate examples/localhost.yaml`

## Running benchmarks

To list available benchmarks, use the `list` commmand:

```bash
python3 perf.py list

...
Benchmark: sysbench.cpu
Metrics: events_per_second
    Run sysbench CPU test. Additional arguments can be provided for sysbench.

    :param max_prime: The maximum prime number to search.
```

To run benchmarks, use the `run` command. For example, to run the sysbench benchmark above:

```bash
python3 perf.py run --env examples/localhost.yaml sysbench.cpu
```

You can run parameterized benchmarks, for example to run with different
runtimes:

```bash
python3 perf.py run --env examples/localhost.yaml --runtime=runc --runtime=runsc sysbench.cpu
```

Or with different parameters:

```bash
python3 perf.py run --env examples/localhost.yaml --max_prime=10 --max_prime=100 sysbench.cpu
```

## Writing benchmarks

To write new benchmarks, you should familiarize yourself with the structure of
the repository. There are three key components.

## Harness

The harness makes use of the [docker py SDK][docker-py]. It is advisable that
you familiarize yourself with that API when making changes, specifically:

 * clients
 * containers
 * images

In general, benchmarks need only interact with the `Machine` objects provided to
the benchmark function, which are the machines defined in the environment.
These objects allow the benchmark to define the relationships between different
containers, and parse the output.

## Workloads

The harness requires workloads to run. These are all available in the
`workloads` directory.

In general, a workload consists of a Dockerfile to build it (while these are not
hermetic, in general they should be as fixed and isolated as possible), some
parses for output if required, parser tests and sample data. Provided the test
is named after the workload package and contains a function named `sample`, this
variable will be used to automatically mock workload output when the `--mock`
flag is provided to the main tool.

## Writing benchmarks

Benchmarks define the tests themselves. All benchmarks have the following
function signature:

```python
def my_func(output) -> float:
    return float(output)

@benchmark(metrics = my_func, machines = 1)
def my_benchmark(machine: Machine, arg: str):
    return "3.4432"
```

Each benchmark takes a variable amount of position arguments as
`harness.Machine` objects and some set of keyword arguments. It is
recommended that you accept arbitrary keyword arguments and pass them through
when constructing the container under test.

To write a new benchmark, open a module in the `benchmarks` directory and use
the above signature. You should add a descriptive doc string to describe what
your benchmark is and any test centric arguments.

## Generating SSH Keys
The scripts only support RSA Keys, and ssh library used in paramiko. Paramiko only supports RSA
keys that look like the following (PEM format):

```bash
$ cat /path/to/ssh/key

-----BEGIN RSA PRIVATE KEY-----
...private key text...
-----END RSA PRIVATE KEY-----

```

To generate ssh keys in PEM format, use the [`-t rsa -m PEM -b 4096`][RSA-keys].
option.

[dockerd]: https://docs.docker.com/engine/reference/commandline/dockerd/
[docker-py]: https://docker-py.readthedocs.io/en/stable/
[paramiko]: http://docs.paramiko.org/en/2.4/api/client.html
[RSA-keys]: https://serverfault.com/questions/939909/ssh-keygen-does-not-create-rsa-private-key
