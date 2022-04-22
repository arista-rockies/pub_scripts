#!python3

import argparse
import json
import os
import random
import socket
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-sn', help='Specify custom Serial Number')
parser.add_argument('-mac', help='Specify custom Mac Address')
parser.add_argument('-int', action='store_true', help='Only create OSPF/ISIS interface re-mapping requirements')

args = parser.parse_args()

##################################################################################
# step 1: Figure out which version of Lab EOS is running on the device
##################################################################################
def getEOS():
    showVer = os.popen('Cli -p 15 -c \'show version | json\'').read()
    showVerJson = json.loads(showVer)

    if 'vEOS' in showVerJson['modelName']:
        return '/mnt/flash/veos-config'
    elif 'cEOS' in showVerJson['modelName']:
        return '/mnt/flash/ceos-config'
    else:
        # TODO throw an error and exit
        pass


##################################################################################
# step 2: If cEOS do interface remapping for OSPF/ISIS to function properly
##################################################################################
def intRemap():
    interfaces = []

    script = open('/mnt/flash/afterStartup.sh', 'a')
    script.write('#!/usr/bin/env bash\n')
    script.write('\n')
    script.write('#Rename interfaces\n')
    script.write('bash << INTFCMDS\n')

    for interface in socket.if_nameindex():
        if 'eth' in interface[-1]:
            interfaces.append(interface[-1])

    for interface in interfaces:
        newInterfaceName = interface.replace('h', '')
        script.write('sudo ip link set dev {} down\n'.format(interface))
        script.write('sudo ip link set dev {} name {}\n'.format(interface, newInterfaceName))
        script.write('sudo ip link set dev {} up\n'.format(newInterfaceName))

    script.write('INTFCMDS\n')
    script.write('sleep 2\n')
    script.write('\n')
    script.write('#Reset Interfaces\n')
    script.write('Cli -A << CLICMDS\n')
    script.write('enable\n')
    script.write('agent Fru terminate\n')
    script.write('agent Etba terminate\n')
    script.write('CLICMDS\n')

    script.close()
    print('/mnt/flash/afterStartup.sh has been successfully created')

    os.system(
        '''Cli -p 15 -c $\'
        config \n  
        event-handler Update-Ints \n
        trigger on-boot \n
        action bash /mnt/flash/afterStartup.sh \n
        delay 30 \n
        write memory \n
        \''''
    )

    print('event-handler Updat-Ints has been created')
    print('')


##################################################################################
# step 3: Check to see if configuration already exists and ask the user what to do
##################################################################################
def checkConfig(configPath):
    print('Checking to see if {} already exists'.format(configPath))
    if os.path.exists(configPath):
        response = input('{} already exists. Would you like to replace the existing config? [y/n]'.format(configPath))
        if response.lower() == 'y':
            print('Replacing existing config file with newly generated config')
            return True

        elif response.lower() == 'n':
            print('Exiting! {} creation cancelled by user'.format(configPath))
            return False

        else:
            print('Unknown response provided.  Exiting!')
            sys.exit()
    else:
        print('Config file doeesn\'t exist, creting {}'.format(configPath))
        return True
        # genConfig()


##################################################################################
# step 4: Generate config file
##################################################################################
def genConfig():
    serial = ''
    mac = ''
    macList = []

    # if not len(sys.argv) > 1:
    if not args.sn or args.mac:
        for i in range(1, 4):
            randMac = "".join(random.sample("0123456789abcdef", 2))
            macList.append(randMac)
    else:
        pass

    if args.sn:
        serial = 'SERIALNUMBER={}'.format(args.sn)
    else:
        serial = 'SERIALNUMBER={}EOS00{}{}{}'.format(eosConfigLoc[11], macList[0], macList[1], macList[2])

    if args.mac:
        mac = 'SYSTEMMACADDR={}'.format(args.mac)
    else:
        # print(macList)
        mac = 'SYSTEMMACADDR=001c.73{}.{}{}'.format(macList[0], macList[1], macList[2])

    with open(eosConfigLoc, 'w') as out:
        out.write('{}\n{}\n'.format(serial, mac))

    os.chmod(eosConfigLoc, 0o755)

    print('{} generated with: \n{} \n{}'.format(eosConfigLoc, serial, mac))


if __name__ == "__main__":
    eosConfigLoc = getEOS()

    if args.int:
        if eosConfigLoc == '/mnt/flash/ceos-config':
            print('Re-mapping interfaces')
            intRemap()

        else:
            print('ERROR: Interfaces can only be re-mapped on cEOS.  Exiting!')
            sys.exit()

    else:
        # configNeeded = checkConfig(eosConfigLoc)

        if checkConfig(eosConfigLoc) == True:
            if eosConfigLoc == '/mnt/flash/ceos-config':
                intRemap()
                genConfig()
            else:
                genConfig()
