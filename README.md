This repository contains scripts and configurations to launch a
cluster of Fedora Atomic hosts and then automatically deploy
Kubernetes on top of that cluster.

First run:

    make

Then start the discovery service (replacing the arguments to `--image`
and `--key-name` with values appropriate to your environment):

    nova boot --image larsks-atomic-20141121 \
      --flavor m1.small \
      --key-name lars \
      --user-data userdata-discovery \
      atomic-discovery

Then start the Atomic cluster, after setting `DISCOVERY_IP` to the
fixed ip address of the discovery image your stared in the previous
step:

    nova boot --image larsks-atomic-20141121 \
      --flavor m1.small \
      --key-name lars \
      --num-instances 3 \
      --user-data userdata-cluster \
      --meta discovery_url=http://${DISCOVERY_IP}:4001/v2/keys/_etcd/registry/$(uuidgen) \
      --meta cluster_size=3 \
      atomic-node

You can set `--num-instances` to control the number of nodes in the
cluster.  Make sure that you adjust the `cluster_size` metadata value
to match.

Note that you will need the `uuidgen` binary for the above to work,
but if you don't have it you can simply replace the call to
`$(uuidgen)` with any unique value.

This will:

- Create N instances running Fedora Atomic
- Create an etcd cluster running on all of these instances
- Pick a cluster master, and configure it as a Kubernetes master
- Configure all systems as Kubernetes minions
- Install and configure [Flannel][] on the cluster to
  provide container networking

[flannel]: https://github.com/coreos/flannel

