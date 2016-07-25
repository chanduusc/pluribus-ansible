#!/usr/bin/python
""" PN-CLI vrouter-bgp-add/vrouter-bgp-remove/vrouter-bgp-modify """

import subprocess
import shlex

DOCUMENTATION = """
---
module: pn_vrouterbgp
author: "Pluribus Networks"
short_description: CLI command to add/remove/modify vrouter-bgp
description:
  - Execute vrouter-bgp-add, vrouter-bgp-remove, vrouter-bgp-modify command.
  - Each fabric, cluster, standalone switch, or virtual network (VNET) can
    provide its tenants with a vRouter service that forwards traffic between
    networks and implements Layer 4 protocols.
options:
  pn_cliusername:
    description:
      - Login username
    required: true
    type: str
  pn_clipassword:
    description:
      - Login password
    required: true
    type: str
  pn_cliswitch:
    description:
    - Target switch to run the cli on.
    required: False
    type: str
  pn_command:
    description:
      - The C(pn_command) takes the vrouter-bgp command as value.
    required: true
    choices: vrouter-bgp-add, vrouter-bgp-remove, vrouter-bgp-modify
    type: str
  pn_vrouter_name:
    description:
      - Specify a name for the vRouter service.
    required: true
    type: str
  pn_neighbor:
    description:
      - Specify a neighbor IP address to use for BGP.
    required_if: vrouter-bgp-add
    type: str
  pn_remote_as:
    description:
      - Specify the remote Autonomous System(AS) number. This value is between
        1 and 4294967295.
    required_if: vrouter-bgp-add
    type: str
  pn_next_hop_self:
    description:
      - Specify if the next-hop is the same router or not.
    type: bool
  pn_password:
    description:
      - Specify a password, if desired.
    type: str
  pn_ebgp:
    description:
      - Specify a value for external BGP to accept or attempt BGP connections
        to external peers, not directly connected, on the network. This is a
        value between 1 and 255.
    type: int
  pn_prefix_listin:
    description:
      - Specify the prefix list to filter traffic inbound.
    type: str
  pn_prefix_listout:
    description:
      - Specify the prefix list to filter traffic outbound.
    type: str
  pn_route_reflector:
    description:
      - Specify if a route reflector client is used.
    type: bool
  pn_override_capability:
    description:
      - Specify if you want to override capability.
    type: bool
  pn_soft_reconfig:
    description:
      - Specify if you want a soft reconfiguration of inbound traffic.
    type: bool
  pn_max_prefix:
    description:
      - Specify the maximum number of prefixes.
    type: int
  pn_max_prefix_warn:
    description:
      - Specify if you want a warning message when the maximum number of
        prefixes is exceeded.
    type: bool
  pn_bfd:
    description:
      - Specify if you want BFD protocol support for fault detection.
    type: bool
  pn_multiprotocol:
    description:
      - Specify a multi-protocol for BGP.
    choices: ipv4-unicast, ipv6-unicast
    type: str
  pn_weight:
    description:
      - Specify a default weight value between 0 and 65535 for the neighbor
        routes.
    type: int
  pn_default_originate:
    description:
      - Specify if you want announce default routes to the neighbor or not.
    type: bool
  pn_keepalive:
    description:
      - Specify BGP neighbor keepalive interval in seconds.
    type: str
  pn_holdtime:
    description:
      - Specify BGP neighbor holdtime in seconds.
    type: str
  pn_route_mapin:
    description:
      - Specify inbound route map for neighbor.
    type: str
  pn_route_mapout:
    description:
      - Specify outbound route map for neighbor.
    type: str
  pn_quiet:
    description:
      - Enable/disable system information.
    required: false
    type: bool
    default: true
"""

EXAMPLES = """
- name: add vrouter-bgp
  pn_vrouterbgp:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'vrouter-bgp-add'
    pn_vrouter_name: 'ansible-vrouter'
    pn_neighbor: 104.104.104.1
    pn_remote_as: 1800

- name: remove vrouter-bgp
  pn_vrouterbgp:
    pn_cliusername: admin
    pn_clipassword: admin
    pn_command: 'vrouter-delete'
    pn_name: 'ansible-vrouter'
"""

RETURN = """
command:
  description: the CLI command run on the target node(s).
stdout:
  description: the set of responses from the vrouterbpg command.
  returned: always
  type: list
stderr:
  description: the set of error responses from the vrouterbgp command.
  returned: on error
  type: list
changed:
  description: Indicates whether the CLI caused changes on the target.
  returned: always
  type: bool
"""


def main():
    """ This portion is for arguments parsing """
    module = AnsibleModule(
        argument_spec=dict(
            pn_cliusername=dict(required=True, type='str',
                                aliases=['username']),
            pn_clipassword=dict(required=True, type='str',
                                aliases=['password']),
            pn_cliswitch=dict(required=False, type='str', aliases=['switch']),
            pn_command=dict(required=True, type='str',
                            choices=['vrouter-bgp-add', 'vrouter-bgp-remove',
                                     'vrouter-bgp-modify'],
                            aliases=['command']),
            pn_vrouter_name=dict(required=True, type='str',
                                 aliases=['vrouter_name']),
            pn_neighbor=dict(type='str', aliases=['neighbor']),
            pn_remote_as=dict(type='str', aliases=['remote_as']),
            pn_next_hop_self=dict(type='bool', aliases=['next_hop_self']),
            pn_password=dict(type='str', aliases=['bgp_password']),
            pn_ebgp=dict(type='int', aliases=['ebgp']),
            pn_prefix_listin=dict(type='str', aliases=['prefix_listin']),
            pn_prefix_listout=dict(type='str', aliases=['prefix_listout']),
            pn_route_reflector=dict(type='bool', aliases=['route_reflector']),
            pn_override_capability=dict(type='bool',
                                        aliases=['override_capability']),
            pn_soft_reconfig=dict(type='bool', aliases=['soft_reconfig']),
            pn_max_prefix=dict(type='int', aliases=['max_prefix']),
            pn_max_prefix_warn=dict(type='bool', aliases=['max_prefix_warn']),
            pn_bfd=dict(type='bool', aliases=['bfd']),
            pn_multiprotocol=dict(type='bool',
                                  choices=['ipv4-unicast', 'ipv6-unicast'],
                                  aliases=['multiprotocol']),
            pn_weight=dict(type='int', aliases=['weight']),
            pn_default_originate=dict(type='bool',
                                      aliases=['default_originate']),
            pn_keepalive=dict(type='str', aliases=['keepalive']),
            pn_holdtime=dict(type='str', aliases=['holdtime']),
            pn_route_mapin=dict(type='str', aliases=['route_mapin']),
            pn_route_mapout=dict(type='str', aliases=['route_mapout']),
            pn_quiet=dict(default=True, type='bool', aliases=['quiet'])
        ),
        required_if=(
            ["pn_command", "vrouter-bgp-add",
             ["pn_vrouter_name", "pn_neighbor", "pn_remote_as"]],
            ["pn_command", "vrouter-bgp-remove",
             ["pn_vrouter_name", "pn_neighbor"]],
            ["pn_command", "vrouter-bgp-modify",
             ["pn_vrouter_name", "pn_neighbor"]]
        )
    )

    cliusername = module.params['pn_cliusername']
    clipassword = module.params['pn_clipassword']
    cliswitch = module.params['pn_cliswitch']
    command = module.params['pn_command']
    vrouter_name = module.params['pn_vrouter_name']
    neighbor = module.params['pn_neighbor']
    remote_as = module.params['pn_remote_as']
    next_hop_self = module.params['pn_next_hop_self']
    password = module.params['pn_password']
    ebgp = module.params['pn_ebgp']
    prefix_listin = module.params['pn_prefix_listin']
    prefix_listout = module.params['pn_prefix_listout']
    route_reflector = module.params['pn_route_reflector']
    override_capability = module.params['pn_override_capability']
    soft_reconfig = module.params['pn_soft_reconfig']
    max_prefix = module.params['pn_max_prefix']
    max_prefix_warn = module.params['pn_max_prefix_warn']
    bfd = module.params['pn_bfd']
    multiprotocol = module.params['pn_multiprotocol']
    weight = module.params['pn_weight']
    default_originate = module.params['pn_default_originate']
    keepalive = module.params['pn_keepalive']
    holdtime = module.params['pn_holdtime']
    route_mapin = module.params['pn_route_mapin']
    route_mapout = module.params['pn_route_mapout']
    quiet = module.params['pn_quiet']

    # Building the CLI command string
    if quiet is True:
        cli = ('/usr/bin/cli --quiet --user ' + cliusername + ':' +
               clipassword + ' ')
    else:
        cli = '/usr/bin/cli --user ' + cliusername + ':' + clipassword + ' '

    if cliswitch:
        cli += ' switch ' + cliswitch

    cli += command + ' vrouter-name ' + vrouter_name

    if neighbor:
        cli += ' neighbor ' + neighbor

    if remote_as:
        cli += ' remote-as ' + str(remote_as)

    if next_hop_self is True:
        cli += ' next-hop-self '
    if next_hop_self is False:
        cli += ' no-next-hop-self '

    if password:
        cli += ' password ' + password

    if ebgp:
        cli += ' ebgp-multihop ' + str(ebgp)

    if prefix_listin:
        cli += ' prefix-list-in ' + prefix_listin

    if prefix_listout:
        cli += ' prefix-list-out ' + prefix_listout

    if route_reflector is True:
        cli += ' route-reflector-client '
    if route_reflector is False:
        cli += ' no-route-reflector-client '

    if override_capability is True:
        cli += ' override-capability '
    if override_capability is False:
        cli += ' no-override-capability '

    if soft_reconfig is True:
        cli += ' soft-reconfig-inbound '
    if soft_reconfig is False:
        cli += ' no-soft-reconfig-inbound '

    if max_prefix:
        cli += ' max-prefix ' + str(max_prefix)

    if max_prefix_warn is True:
        cli += ' max-prefix-warn-only '
    if max_prefix_warn is False:
        cli += ' no-max-prefix-warn-only '

    if bfd is True:
        cli += ' bfd '
    if bfd is False:
        cli += ' no-bfd '

    if multiprotocol:
        cli += ' multi-protocol ' + multiprotocol

    if weight:
        cli += ' weight ' + str(weight)

    if default_originate is True:
        cli += ' default-originate '
    if default_originate is False:
        cli += ' no-default-originate '

    if keepalive:
        cli += ' neighbor-keepalive-interval ' + keepalive

    if holdtime:
        cli += ' neighbor-holdtime ' + holdtime

    if route_mapin:
        cli += ' route-map-in ' + route_mapin

    if route_mapout:
        cli += ' route-map-out ' + route_mapout

    # Run the CLI command
    vrouterbgpcmd = shlex.split(cli)
    response = subprocess.Popen(vrouterbgpcmd, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True)

    # 'out' contains the output
    # 'err' contains the err messages
    out, err = response.communicate()

    # Response in JSON format
    if err:
        module.exit_json(
            command=cli,
            stderr=err.rstrip("\r\n"),
            changed=False
        )

    else:
        module.exit_json(
            command=cli,
            stdout=out.rstrip("\r\n"),
            changed=True
        )

# Ansible boiler-plate
from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()

