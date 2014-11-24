#!/usr/bin/python

import argparse
import json
import jsonpointer
import os
import requests
import sys
import pickle
import errno

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--metadata-addr', '-m',
                   default='169.254.169.254')
    p.add_argument('--list-keys', '-k',
                   action='store_true')
    p.add_argument('--no-cache', '-n',
                   action='store_true')
    p.add_argument('--cache',
                   default='/var/lib/cloud/instance/obj.pkl')
    p.add_argument('pointer', nargs='?')
    return p.parse_args()


def get_md_from_cache():
    global args

    with open(args.cache) as fd:
        try:
            data = pickle.load(fd)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                return None

    return data.metadata


def get_md_from_service():
    global args

    res = requests.get(
        'http://{metadata_addr}/openstack/latest/meta_data.json'.format(
            metadata_addr=args.metadata_addr))
    res.raise_for_status()
    data = res.json()

    return data


def main():
    global args

    args = parse_args()
    data = None

    if not args.no_cache:
        data = get_md_from_cache()

    if data is None:
        data = get_md_from_service()

    if args.pointer:
        val = jsonpointer.resolve_pointer(data, args.pointer)
    else:
        val = data

    if args.list_keys:
        print '\n'.join(val.keys())
    else:
        print val

if __name__ == '__main__':
    main()


