FROM gcc:latest
COPY . /usr/src/syscall
WORKDIR /usr/src/syscall
RUN set -x && apt-get install -y numactl
RUN gcc -O2 -o syscall syscall.c
ENV count 1000000
CMD ["sh", "-c", "numactl -N 0 -m 0 ./syscall ${count}"]
