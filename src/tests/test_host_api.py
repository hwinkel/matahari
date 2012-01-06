#!/usr/bin/env python

"""
  test_host_api.py - Copyright (c) 2011 Red Hat, Inc.
  Written by Dave Johnson <dajo@redhat.com>

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the
  Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

import commands as cmd
import matahariTest as testUtil
import unittest
import time
import sys
import os

connection = None
host = None
err = sys.stderr

# Initialization
# =====================================================

class HostTestsSetup(object):
    def __init__(self):
        self.broker = testUtil.MatahariBroker()
        self.broker.start()
        time.sleep(3)
        self.host_agent = testUtil.MatahariAgent("matahari-qmf-hostd")
        self.host_agent.start()
        time.sleep(3)
        self.connect_info = testUtil.connectToBroker('localhost', '49001')
        self.sess = self.connect_info[1]
        self.reQuery()

    def teardown(self):
        self.disconnect()
        self.host_agent.stop()
        self.broker.stop()

    def disconnect(self):
        testUtil.disconnectFromBroker(self.connect_info)

    def reQuery(self):
        self.host = testUtil.findAgent(self.sess,'host', 'Host', cmd.getoutput('hostname'))
        self.props = self.host.getProperties()

def setUp(self):
    global connection
    global host
    connection = HostTestsSetup()
    host = connection.host

def tearDown():
    global connection
    connection.teardown()

class HostApiTests(unittest.TestCase):

    # TEST - getProperties()
    # =====================================================
    def test_hostname_property(self):
        value = connection.props.get('hostname')
        self.assertEquals(value, cmd.getoutput("hostname"), "hostname not matching")

    def test_os_property(self):
        value = connection.props.get('os')
        self.assertEquals(value, cmd.getoutput("uname -a | awk '{print $1,\"(\"$3\")\"}'"), "os not matching")

    def test_arch_property(self):
        value = connection.props.get('arch')
        self.assertEquals(value, cmd.getoutput("uname -a | awk '{print $12}'"), "os not matching")

    def test_wordsize_property(self):
        value = connection.props.get('wordsize')
        uname = cmd.getoutput("uname -a")
        word_size = 0
        if "i386" in uname or "i686" in uname:
            word_size = 32
        elif "x86_64" in uname or "s390x" in uname or "ppc64" in uname:
            word_size = 64
        self.assertEquals(value, word_size, "wordsize not matching")

    def test_memory_property(self):
        value = connection.props.get('memory')
        self.assertEquals(value, int(cmd.getoutput("free | grep Mem | awk '{ print $2 }'")), "memory not matching")

    def test_swap_property(self):
        value = connection.props.get('swap')
        self.assertEquals(value, int(cmd.getoutput("free | grep Swap | awk '{ print $2 }'")), "swap not matching")

    def test_cpu_count_property(self):
        value = connection.props.get('cpu_count')
        uname = cmd.getoutput("uname -a")

        if "s390x" in uname:
            self.assertEquals(value, int(cmd.getoutput("cat /proc/cpuinfo | grep processors | awk '{ print $4 }'")), "cpu count not matching")
        else:
            self.assertEquals(value, int(cmd.getoutput("cat /proc/cpuinfo | grep processor | wc -l")), "cpu count not matching")

    def test_cpu_cores_property(self):
        # XXX Core count is still busted in F15, sigar needs to be updated
        if os.path.exists("/etc/fedora-release") and open("/etc/fedora-release", "r").read().strip() == "Fedora release 15 (Lovelock)":
            return
        value = str(connection.props.get('cpu_cores'))

        if "s390x" in cmd.getoutput("uname -a"):
            core_count = cmd.getoutput("cat /proc/cpuinfo | grep processors | awk '{ print $4 }'").strip()
        else:
            core_count = cmd.getoutput("cat /proc/cpuinfo | grep \"core id\" | uniq | wc -l").strip()

        self.assertEquals(value, core_count, "cpu core count ("+value+") not matching expected ("+core_count+")")

    def test_cpu_model_property(self):
        value = connection.props.get('cpu_model')
        uname = cmd.getoutput("uname -a")

        if "s390x" in uname:
            expected = cmd.getoutput("cat /proc/cpuinfo | grep 'processor 0' | awk -F, '{ print $3 }' | awk -F= '{ print $2 }'").strip()
            self.assertEquals(value, expected, "cpu model ("+value+") not matching expected ("+expected+")")
        elif "ppc64" in uname:
            expected = cmd.getoutput("cat /proc/cpuinfo | grep cpu | head -1")
            self.assertTrue(value in expected, "cpu model ("+value+") not found in ("+expected+")")
        else:
            expected = cmd.getoutput("cat /proc/cpuinfo | grep 'model name' | head -1 | awk -F: {'print $2'}").strip()
            self.assertEquals(value, expected, "cpu model ("+value+") not matching expected ("+expected+")")

    def test_cpu_flags_property(self):
        value = connection.props.get('cpu_flags')
        uname = cmd.getoutput("uname -a")
        if "s390x" in uname:
            self.assertEquals(value.strip(), cmd.getoutput("cat /proc/cpuinfo | grep 'features' | head -1 | awk -F: {'print $2'}").strip(), "cpu flags not matching")
        elif "ppc64" in uname:
            self.assertTrue(value in cmd.getoutput("cat /proc/cpuinfo | grep cpu | head -1"), "cpu flags not matching")
        else:
            self.assertEquals(value, cmd.getoutput("cat /proc/cpuinfo | grep 'flags' | head -1 | awk -F: {'print $2'}").strip(), "cpu flags not matching")

    def test_update_interval_property(self):
        value = connection.props.get('update_interval')
        self.assertEquals(value, 5, "update interval not matching")

    def test_last_updated_property(self):
        value = connection.props.get('last_updated')
        value = value / 1000000000
        now = int("%.0f" % time.time())
        delta = testUtil.getDelta(value, now)
        self.assertFalse(delta > 5, "last updated off gt 5 seconds")

    #def test_sequence_property(self):
    #     self.fail("no verification")

    def test_free_mem_property(self):
        value = connection.props.get('free_mem')
        top_value = int(cmd.getoutput("free | grep Mem | awk '{ print $4 }'"))
        self.assertTrue(testUtil.checkTwoValuesInMargin(value, top_value, 0.05, "free memory"), "free memory outside margin")

    def test_free_swap_property(self):
        value = connection.props.get('free_swap')
        top_value = int(cmd.getoutput("free | grep Swap | awk '{ print $4 }'"))
        self.assertTrue(testUtil.checkTwoValuesInMargin(value, top_value, 0.05, "free swap"), "free swap outside margin")

    # TEST - get_uuid()
    # =====================================================
    #def test_get_uuid_Hardware_lifetime(self):
    #    XXX requires dmidecode, which requires root
    #    result = host.get_uuid('Hardware')
    #    self.assertNotEqual(result.get('uuid'),'not-available', "not-available text not found on parm 'lifetime'")

    def test_get_uuid_Reboot_lifetime(self):
        result = host.get_uuid('Reboot')
        self.assertNotEqual(result.get('uuid'),' not-available', "Reboot lifetime returned 'not-available' ")

    def test_get_uuid_unset_Custom_lifetime(self):
        cmd.getoutput("rm -rf /etc/custom-machine-id")
        global connection
        global host
        connection.teardown()
        connection = HostTestsSetup()
        host = connection.host
        result = host.get_uuid('Custom')
        self.assertEqual(result.get('uuid'), 'not-available', "unset Custom liftetime not returning 'not-available' ("+result.get('uuid')+")")

    def test_get_uuid_unknown_lifetime(self):
        result = host.get_uuid('lifetime')
        self.assertEqual(result.get('uuid'), 'invalid-lifetime', "parm 'lifetime' not returning 'invalid-lifetime' ("+result.get('uuid')+")")

    def test_get_uuid_empty_string(self):
        result = host.get_uuid('')
        self.assertEqual(result.get('uuid'), 'invalid-lifetime', "empty string not returning 'invalid-lifetime' ("+result.get('uuid')+")")

    def test_get_uuid_zero_parameters(self):
        try:
            result = host.get_uuid()
            self.fail("no exception on zero parms")
        except Exception as e:
            pass

    # TEST - set_uuid()
    # =====================================================
    def test_set_uuid_Custom_lifetime(self):
        test_uuid = testUtil.getRandomKey(20)
        host.set_uuid('Custom', test_uuid)
        result = host.get_uuid('Custom')
        self.assertEqual(result.get('uuid'), test_uuid, "uuid value ("+result.get('uuid')+") not matching expected("+test_uuid+")")
        connection.reQuery()
        self.assertEqual(connection.props.get('custom_uuid'), test_uuid, "uuid value ("+connection.props.get('uuid')+") not matching expected("+test_uuid+")")

    def test_set_uuid_new_Custom_lifetime(self):
        test_uuid = testUtil.getRandomKey(20)
        host.set_uuid('Custom', test_uuid)
        result = host.get_uuid('Custom')
        self.assertEqual(result.get('uuid'), test_uuid, "uuid value ("+result.get('uuid')+") not matching expected("+test_uuid+")")
        connection.reQuery()
        self.assertEqual(connection.props.get('custom_uuid'), test_uuid, "uuid value ("+connection.props.get('uuid')+") not matching expected("+test_uuid+")")

    def test_set_uuid_Hardware_lifetime_fails(self):
        result = host.set_uuid('Hardware', testUtil.getRandomKey(20) )
        self.assertEqual(result.get('rc'), 23, "Unexpected return code ("+str(result.get('rc'))+"), expected 23")

    def test_set_uuid_Reboot_lifetime_fails(self):
        result = host.set_uuid('Reboot', testUtil.getRandomKey(20) )
        self.assertEqual(result.get('rc'), 23, "Unexpected return code ("+str(result.get('rc'))+"), expected 23")

    # TEST - misc
    # =====================================================
    #def test_identify(self):
    #    self.fail("no verification")

    #def test_reboot(self):
    #    self.fail("no verification")

    #def test_shutdown(self):
    #    self.fail("no verification")

