#   Copyright 2018 Red Hat, Inc.
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
from oslo_config import cfg
from oslo_log import log as logging

from osc_lib.i18n import _
from osc_lib import utils

from tripleoclient import command
from tripleoclient import constants
from tripleoclient import utils as oooutils
from tripleoclient.workflows import deployment


CONF = cfg.CONF
logging.register_options(CONF)
logging.setup(CONF, '')


class ExternalUpgradeRun(command.Command):
    """Run external major upgrade Ansible playbook

       This will run the external major upgrade Ansible playbook,
       executing tasks from the undercloud. The upgrade playbooks are
       made available after completion of the 'overcloud upgrade
       prepare' command.

    """

    log = logging.getLogger(__name__ + ".ExternalUpgradeRun")

    def get_parser(self, prog_name):
        parser = super(ExternalUpgradeRun, self).get_parser(prog_name)
        parser.add_argument('--static-inventory',
                            dest='static_inventory',
                            action="store",
                            default=None,
                            help=_('Path to an existing ansible inventory to '
                                   'use. If not specified, one will be '
                                   'generated in '
                                   '~/tripleo-ansible-inventory.yaml')
                            )
        parser.add_argument("--ssh-user",
                            dest="ssh_user",
                            action="store",
                            default="tripleo-admin",
                            help=_("DEPRECATED: Only tripleo-admin should be "
                                   "used as ssh user.")
                            )
        parser.add_argument('--tags',
                            dest='tags',
                            action="store",
                            default="",
                            help=_('A string specifying the tag or comma '
                                   'separated list of tags to be passed '
                                   'as --tags to ansible-playbook. ')
                            )
        parser.add_argument('--skip-tags',
                            dest='skip_tags',
                            action="store",
                            default="",
                            help=_('A string specifying the tag or comma '
                                   'separated list of tags to be passed '
                                   'as --skip-tags to ansible-playbook. ')
                            )
        parser.add_argument('--stack', dest='stack',
                            help=_('Name or ID of heat stack '
                                   '(default=Env: OVERCLOUD_STACK_NAME)'),
                            default=utils.env('OVERCLOUD_STACK_NAME',
                                              default='overcloud'))
        parser.add_argument('-e', '--extra-vars', dest='extra_vars',
                            action='append',
                            help=('Set additional variables as key=value or '
                                  'yaml/json'),
                            default=[])
        parser.add_argument('--no-workflow', dest='no_workflow',
                            action='store_true',
                            default=True,
                            help=_('This option no longer has any effect.')
                            )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        _, ansible_dir = self.get_ansible_key_and_dir(
            no_workflow=True,
            stack=parsed_args.stack,
            orchestration=self.app.client_manager.orchestration
        )
        deployment.config_download(
            log=self.log,
            clients=self.app.client_manager,
            stack=oooutils.get_stack(
                self.app.client_manager.orchestration,
                parsed_args.stack
            ),
            output_dir=ansible_dir,
            verbosity=oooutils.playbook_verbosity(self=self),
            ansible_playbook_name=constants.EXTERNAL_UPGRADE_PLAYBOOKS,
            inventory_path=oooutils.get_tripleo_ansible_inventory(
                parsed_args.static_inventory,
                parsed_args.ssh_user,
                parsed_args.stack,
                return_inventory_file_path=True
            ),
            tags=parsed_args.tags,
            skip_tags=parsed_args.skip_tags
        )
        self.log.info("Completed Overcloud External Upgrade Run.")
