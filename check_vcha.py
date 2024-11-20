"""
Copyright (C) 2024 Thanos Koukoulis

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA.
"""

from pyVim.connect import SmartConnect
import sys
import argparse

def connectVcenter(server, username, password):
    try:
        c = SmartConnect(host=server, user=username, pwd=password)
        return c
    except Exception as e:
        print(f"CRITICAL: Unable to connect to vCenter: {e}")
        sys.exit(3)

def getVchaClusterHealth(c):
    try:
        VchaClusterHealth = c.content.failoverClusterManager.GetVchaClusterHealth()
        return VchaClusterHealth
    except Exception as e:
        print(f"CRITICAL: Unable to get vcha cluster health: {e}")
        sys.exit(3)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", type=str)
    parser.add_argument("--user", type=str)
    parser.add_argument("--password", type=str)
    args = parser.parse_args()

    c = connectVcenter(args.server, args.user, args.password)

    VchaClusterHealth = getVchaClusterHealth(c)
    VchaRuntimeInfo = VchaClusterHealth.runtimeInfo

    print("\nVCHA Cluster Mode:",VchaRuntimeInfo.clusterMode)
    print("\nVCHA Cluster State:",VchaRuntimeInfo.clusterState)
    print("\nVCHA Node information:")
    for node in VchaRuntimeInfo.nodeInfo:
        print(node.nodeRole+": "+node.nodeIp+": "+node.nodeState)

    if (VchaRuntimeInfo.clusterState == 'healthy'):
        sys.exit(0)
    else:
        print("VCHA Health messages:")
        VchaHealthMessages = VchaClusterHealth.healthMessages
        for health_data in VchaHealthMessages:
            print(health_data.message)
        print("\nAdditional Information:",VchaClusterHealth.additionalInformation)
        sys.exit(2)

if __name__ == "__main__":
    main()

# https://developer.broadcom.com/xapis/virtual-infrastructure-json-api/8.0.3/data-structures/VchaClusterState_enum/index?scrollString=VchaClusterState
# https://developer.broadcom.com/xapis/virtual-infrastructure-json-api/8.0.3/data-structures/VchaClusterMode_enum/index?scrollString=VchaClusterMode
# https://developer.broadcom.com/xapis/virtual-infrastructure-json-api/8.0.2.0/failover-cluster-configurator/