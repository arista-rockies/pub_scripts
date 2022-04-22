This script can be run on vEOS or cEOS and can do the following:
  - Generate  random MAC Address and Serial Number
  - Allow user to specify custom MAC Address or Serial Number or both
  - Can create the script and event-handler needed for OPSF / ISIS to work properly on cEOS

To use copy the contents of this script to the vEOS or cEOS device.


bash-4.2# python3 EOS-Lab.py 

optional arguments:
  -h, --help
    show this help message and exit
  -sn 
    Specify custom Serial Number
  -mac 
    Specify custom Mac Address
  -int
    Create OSPF/ISIS interface re-mapping requirements
