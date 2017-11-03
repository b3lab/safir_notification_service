#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from safir_notification_service.alarm.alarm_handler import AlarmHandler
from safir_notification_service.openstack.connector import OpenstackConnector


class TestOpenstackConnector(unittest.TestCase):
    openstack_conn = OpenstackConnector('altyapitest-admin')

    def test_template(self):
        print('HERE')
        self.assertTrue(True)

    def test_openstackclient(self):
        self.assertIsNotNone(self.openstack_conn.conn)
        self.assertIsNotNone(self.openstack_conn.aodh_conn)

    def test_get_server(self):
        print(self.openstack_conn.get_compute_server(
                    "0d8ca708-0e3e-4d1b-8845-642b8726049f"))

    def test_get_alarm(self):
        print(self.openstack_conn.get_aodh_alarm(
                '6636baed-b58e-4f55-9950-0e3ed0b20615'))

    def test_alarm_handler(self):
        alarm_handler = AlarmHandler()
        alarm_handler.handle_alarm('6636baed-b58e-4f55-9950-0e3ed0b20615',
                                   'alarm', 'ok', 'my reason')