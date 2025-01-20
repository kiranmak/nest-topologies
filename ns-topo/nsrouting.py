# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""
import unittest
from glob import glob
import time
import logging
from os.path import isfile
from nest import config
from nest.topology_map import TopologyMap
from nest.topology import Node, connect
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces

import subprocess
from subprocess import Popen, PIPE

class SubprocessManager:
    def __init__(self, command):
        self.command = command
        self.process = None
        self.stdout = None
        self.stderr = None

    def __enter__(self):
        print("Start the subprocess when entering the context.")
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the process is terminated when exiting the context."""
        if self.process:
            self.process.terminate()
            self.process.wait()

    def communicate(self):
        """Communicate with the process to capture output."""
        if not self.process:
            raise RuntimeError("Process not started.")
        self.stdout, self.stderr = self.process.communicate()
        return self.stdout, self.stderr


class NSRoutingDaemon:
    def __init__(self, namespace, daemon, test_name):
        ns_id = namespace

        basedir = os.path("/tmp/nest", test_name, namespace)
        os.makedirs(basedir, exist_ok=True)

        pid_file = os.path(basedir,
                           namespace + "_" + daemon + ".pid")
        self.cmd = f"ip netns exec {ns_id}" +
                  f" {FRR_DAEMONPATH}{daemon} -F " +
                  f" traditional -s -n -N {ns_id}"

    def start(self):
        command = self.cmd.split()
        with SubprocessManager(command) as manager:
            print("Command:",  subprocess.list2cmdline(command))
            stdout, stderr = manager.communicate()
            print("Standard Output:", stdout)
            print("Standard Error:", stderr)

'''
ns_id = "r0"
interface = "eth-r1r2-0"
pid_file = "/tmp/r1_pid.pid"
conf_file = "/tmp/r1_zebra.conf"
FRR_DAEMONPATH = "/usr/lib/frr/"
cmd2 = "--config_file {conf_file} -n --retain --pid_file {pid_file}"

new_cmd = "/usr/lib/frr/zebra -d -F traditional -n --retain --pid_file /tmp/r0_pid.pid"
'''

