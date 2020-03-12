#!/bin/bash

# Run the following in order

sudo ./set_guest_kernel.sh
sudo ./set_guest_rootfs.sh
sudo ./set_config.sh
sudo ./set_network.sh
#sudo ./start_guest_machine.sh

#more detail: https://github.com/firecracker-microvm/firecracker/blob/master/docs/getting-started.md
# Custom kernel & rootfs
# https://github.com/firecracker-microvm/firecracker/blob/master/docs/rootfs-and-kernel-setup.md
