#!/usr/bin/python

import argparse
import errno
import json
import jsonpointer
import os
import requests
import sys


class KubeError(Exception):
    pass


class NotRegistered(KubeError):
    pass

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--etcd-server', '-s',
                   default='http://localhost:4001')
    p.add_argument('--cluster-size', '-z',
                   default=1,
                   type=int)
    p.add_argument('--registration-cache', '-R',
                   default='/etc/kubernetes/minion.json')
    p.add_argument('--cluster-id', '-c',
                   default='kube')

    ops = p.add_mutually_exclusive_group()
    ops.add_argument('--register', '-r')
    ops.add_argument('--is-cluster-ready',
                   action='store_true')
    ops.add_argument('--is-master',
                   action='store_true')
    ops.add_argument('--master',
                   action='store_true')
    ops.add_argument('--minions',
                   action='store_true')
    ops.add_argument('--info',
                   action='store_true')
    return p.parse_args()

def register():
    global args
    url = '{etcd_server}/v2/keys/{cluster_id}/minions'.format(
        etcd_server=args.etcd_server,
        cluster_id=args.cluster_id)

    res = requests.post(url, data={'value': args.register})
    res.raise_for_status()

    data = res.json()
    
    with open(args.registration_cache, 'w') as fd:
        json.dump(data['node'], fd)

    return (0, data['node']['createdIndex'])


def is_cluster_ready():
    global args
    url = '{etcd_server}/v2/keys/{cluster_id}/minions'.format(
        etcd_server=args.etcd_server,
        cluster_id=args.cluster_id)

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    current_size = len(data['node']['nodes'])

    if current_size >= args.cluster_size:
        return (0, 'cluster ready with %d nodes (needed %d)' % (
            current_size, args.cluster_size))
    else:
        return (1, 'cluster is not ready: have %d nodes, need %d' % (
            current_size, args.cluster_size))


def get_nodes():
    global args
    url = '{etcd_server}/v2/keys/{cluster_id}/minions'.format(
        etcd_server=args.etcd_server,
        cluster_id=args.cluster_id)

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    return sorted(data['node']['nodes'],
                   key=lambda node: node['createdIndex'])

def get_master():
    master = get_nodes()[0]
    return master


def get_master_addr():
    master = get_master()
    return (0, master['value'])


def get_minions():
    minions = get_nodes()[1:]
    return minions


def get_minion_addrs():
    minions = get_minions()
    return (0, ' '.join(minion['value'] for minion in minions))


def get_cluster_info():
    master = get_master()
    minions = get_minions()

    text = [
        'size: %d' % (len(minions) + 1),
        'master: %s' % master['value'],
        'minions: %s' % ' '.join(minion['value'] for minion in minions),
    ]

    return (0, '\n'.join(text))

def is_master():
    global args
    url = '{etcd_server}/v2/keys/{cluster_id}/minions'.format(
        etcd_server=args.etcd_server,
        cluster_id=args.cluster_id)

    try:
        with open(args.registration_cache) as fd:
            registration = json.load(fd)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise NotRegistered('system is not registered')

    master = get_master()

    if master['createdIndex'] == registration['createdIndex']:
        return (0, 'This node is the cluster master')
    else:
        return (1, 'This node is not the cluster master')


def main():
    global args

    args = parse_args()

    if args.register:
        retval, msg = register()
    elif args.is_cluster_ready:
        retval, msg = is_cluster_ready()
    elif args.is_master:
        retval, msg = is_master()
    elif args.master:
        retval, msg = get_master_addr()
    elif args.minions:
        retval, msg = get_minion_addrs()
    elif args.info:
        retval, msg = get_cluster_info()

    print msg
    sys.exit(retval)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KubeError as exc:
        print 'ERROR:', exc
        sys.exit(1)

