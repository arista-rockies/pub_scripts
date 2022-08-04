# Fuction to format the port description 
def formatDesc(neiDevice, neiPort):
    portSplit = neiPort.split('net')
    deviceSplit = neiDevice
    return(f'{deviceSplit}_E{portSplit[-1]}')
    # Example Spine-1_E5


# Function to add port description to all interfaces with LLDP neighbors detected
def addDesc(localPort, description):
    ctx.runDeviceCmds([
        'enable', 
        'configure', 
        f'interface {localPort}',
        f'description {description}'
        ])

# Create log entry
ctx.alog('Gathering LLDP Neighbor information')

# Gather the LLDP neighbor data from the device
cmdOut = ctx.runDeviceCmds([
    'enable', 
    'show lldp neighbors'
    ])

###################################
###### Testing with Logging #######
###################################

# ctx.alog(f'{cmdOut}')

# [
#     {'error': '', 'response': {}}, 
#     {'error': '', 'response': {'lldpNeighbors': 
#         [
#         {'neighborDevice': 'studios-spine-1', 'neighborPort': 'Ethernet1', 'port': 'Ethernet1', 'ttl': 120}, 
#         {'neighborDevice': 'studios-spine-2', 'neighborPort': 'Ethernet1', 'port': 'Ethernet2', 'ttl': 120}, 
#         {'neighborDevice': 'studios-leaf1b', 'neighborPort': 'Ethernet11', 'port': 'Ethernet11', 'ttl': 120}, 
#         {'neighborDevice': 'studios-leaf1b', 'neighborPort': 'Ethernet12', 'port': 'Ethernet12', 'ttl': 120}, 
#         {'neighborDevice': 'studios-spine-1', 'neighborPort': 'Management0', 'port': 'Management0', 'ttl': 120}, 
#         {'neighborDevice': 'studios-spine-2', 'neighborPort': 'Management0', 'port': 'Management0', 'ttl': 120}, 
#         {'neighborDevice': 'studios-leaf2a', 'neighborPort': 'Management0', 'port': 'Management0', 'ttl': 120}, 
#         {'neighborDevice': 'studios-leaf1b', 'neighborPort': 'Management0', 'port': 'Management0', 'ttl': 120}, 
#         {'neighborDevice': 'studios-leaf2b', 'neighborPort': 'Management0', 'port': 'Management0', 'ttl': 120}], 
#         ]
#     
# ]   

###################################
###### Testing with Logging #######
###################################


# cmdOut[1] identifies the second command passed in runDeviceCmds. 'response' is the output of the cmdOut[1] command.  
resp = cmdOut[1]['response']['lldpNeighbors']

# Create log entry
ctx.alog(f'{len(resp)} LLDP Neigbors detected.  Configuring description on identified ports')

# Loop through the LLDP neighbors and configure the port descriptions
for i in resp:
    desc = formatDesc(i['neighborDevice'], i['neighborPort'])
    addDesc(i['port'], desc)

# Create log entry
ctx.alog(f'{len(resp)} Port descriptions have been added based on LLDP Neighbors')