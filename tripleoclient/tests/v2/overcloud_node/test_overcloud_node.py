#   Copyright 2015 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock

from osc_lib.tests import utils as test_utils

from tripleoclient import constants
from tripleoclient.tests.v2.overcloud_node import fakes
from tripleoclient.v2 import overcloud_node


class TestIntrospectNode(fakes.TestOvercloudNode):

    def setUp(self):
        super(TestIntrospectNode, self).setUp()

        # Get the command object to test
        self.workflow = self.app.client_manager.workflow_engine
        execution = mock.Mock()
        execution.id = "IDID"
        self.workflow.executions.create.return_value = execution
        client = self.app.client_manager.tripleoclient
        self.websocket = client.messaging_websocket()
        self.websocket.wait_for_messages.return_value = iter([{
            "status": "SUCCESS",
            "message": "Success",
            "introspected_nodes": {},
            "execution_id": execution.id
        }] * 2)

        # Get the command object to test
        self.cmd = overcloud_node.IntrospectNode(self.app, None)

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_all_manageable_nodes_without_provide(self,
                                                             mock_playbook):
        parsed_args = self.check_parser(self.cmd,
                                        ['--all-manageable'],
                                        [('all_manageable', True)])
        self.cmd.take_action(parsed_args)
        mock_playbook.assert_called_once_with(
            workdir=mock.ANY,
            playbook=mock.ANY,
            inventory=mock.ANY,
            playbook_dir=constants.ANSIBLE_TRIPLEO_PLAYBOOKS,
            extra_vars={
                'node_uuids': [],
                'run_validations': False,
                'concurrency': 20,
                'all_manageable': True
            }
        )

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_all_manageable_nodes_with_provide(self,
                                                          mock_playbook):
        parsed_args = self.check_parser(self.cmd,
                                        ['--all-manageable', '--provide'],
                                        [('all_manageable', True),
                                         ('provide', True)])
        self.cmd.take_action(parsed_args)
        mock_playbook.assert_called_once_with(
            workdir=mock.ANY,
            playbook='cli-baremetal-introspect.yaml',
            inventory=mock.ANY,
            playbook_dir=constants.ANSIBLE_TRIPLEO_PLAYBOOKS,
            extra_vars={
                'node_uuids': [],
                'run_validations': False,
                'concurrency': 20,
                'all_manageable': True
            }
        )

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_nodes_without_provide(self, mock_playbook):
        nodes = ['node_uuid1', 'node_uuid2']
        parsed_args = self.check_parser(self.cmd,
                                        nodes,
                                        [('node_uuids', nodes)])
        self.cmd.take_action(parsed_args)
        mock_playbook.assert_called_once_with(
            workdir=mock.ANY,
            playbook='cli-baremetal-introspect.yaml',
            inventory=mock.ANY,
            playbook_dir=constants.ANSIBLE_TRIPLEO_PLAYBOOKS,
            extra_vars={
                'node_uuids': nodes,
                'run_validations': False,
                'concurrency': 20,
                'all_manageable': False
            }
        )

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_nodes_with_provide(self, mock_playbook):
        nodes = ['node_uuid1', 'node_uuid2']
        argslist = nodes + ['--provide']
        parsed_args = self.check_parser(self.cmd,
                                        argslist,
                                        [('node_uuids', nodes),
                                         ('provide', True)])
        self.cmd.take_action(parsed_args)
        mock_playbook.assert_called_once_with(
            workdir=mock.ANY,
            playbook='cli-baremetal-introspect.yaml',
            inventory=mock.ANY,
            playbook_dir=constants.ANSIBLE_TRIPLEO_PLAYBOOKS,
            extra_vars={
                'node_uuids': nodes,
                'run_validations': False,
                'concurrency': 20,
                'all_manageable': False
            }
        )

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_no_node_or_flag_specified(self, mock_playbook):
        self.assertRaises(test_utils.ParserException,
                          self.check_parser,
                          self.cmd, [], [])

    @mock.patch('tripleoclient.utils.run_ansible_playbook',
                autospec=True)
    def test_introspect_uuids_and_all_both_specified(self, mock_playbook):
        argslist = ['node_id1', 'node_id2', '--all-manageable']
        verifylist = [('node_uuids', ['node_id1', 'node_id2']),
                      ('all_manageable', True)]
        self.assertRaises(test_utils.ParserException,
                          self.check_parser,
                          self.cmd, argslist, verifylist)