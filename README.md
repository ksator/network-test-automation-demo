**Table of contents**

- [ANTA demo using an ATD lab](#anta-demo-using-an-atd-lab)
  - [About ANTA](#about-anta)
  - [Set up the ATD lab](#set-up-the-atd-lab)
    - [About ATD](#about-atd)
    - [Start an ATD instance](#start-an-atd-instance)
    - [Load the EVPN lab on ATD](#load-the-evpn-lab-on-atd)
    - [Check the state of spine1](#check-the-state-of-spine1)
    - [Check the requirements on the switches](#check-the-requirements-on-the-switches)
  - [Install the packages on devbox](#install-the-packages-on-devbox)
  - [Clone this repository on devbox](#clone-this-repository-on-devbox)
  - [Create the inventory files](#create-the-inventory-files)
  - [Test devices reachability](#test-devices-reachability)
  - [Test devices](#test-devices)
    - [Define the tests](#define-the-tests)
    - [Run the tests](#run-the-tests)
    - [Fix the issue](#fix-the-issue)
    - [Re run the tests](#re-run-the-tests)
  - [Collect commands output](#collect-commands-output)
  - [Collect the scheduled show tech-support files](#collect-the-scheduled-show-tech-support-files)
  - [Clear the list of MAC addresses which are blacklisted in EVPN](#clear-the-list-of-mac-addresses-which-are-blacklisted-in-evpn)
    - [Create 5 mac moves within 180 seconds](#create-5-mac-moves-within-180-seconds)
    - [Clear the blacklisted MAC addresses](#clear-the-blacklisted-mac-addresses)
  - [Clear counters](#clear-counters)

# ANTA demo using an ATD lab

Here's the instructions to use ANTA with an ATD lab

## About ANTA

ANTA stands for **Arista Network Test Automation**  
ANTA is a Python package to automate tests on Arista devices.  
The ANTA source code and documentation are in this [repository](https://github.com/ksator/network-test-automation)

## Set up the ATD lab

### About ATD

ATD stands for **Arista Test Drive**  

### Start an ATD instance

Here's the ATD topology:

![images/atd_topology.png](images/atd_topology.png)

Login to the Arista Test Drive portal and start an instance.

### Load the EVPN lab on ATD

Load the EVPN lab on your ATD instance

![images/atd_configuration.png](images/atd_configuration.png)

This lab uses 2 spines and 2 leaves:

- Spine1 and spine2
- Leaf1 and leaf3

Leaf2 and leaf4 are not used.

Here's the EVPN lab topology:
![images/atd_evpn_lab_topology.png](images/atd_evpn_lab_topology.png)

The script configured the lab with the exception of leaf3:

- Leaves <-> spines interfaces are configured with an IPv4 address
- eBGP is configured between spines and leaves (underlay, IPv4 unicast address family)
- BFD is configured for the eBGP sessions (IPv4 unicast address family)
- 2 loopback interfaces are configured per leaf
- 1 loopback interface is configured per spine
- eBGP is configured between spines and leaves (overlay, EVPN address family, Loopback0)
- VXLAN is configured on the leaves (Loopback1)
- Default VRF only

### Check the state of spine1

ssh to spine1 and run some EOS commands to check the state

![images/atd_spine1.png](images/atd_spine1.png)

```text
spine1#show ip bgp summary
spine1#show bgp evpn summary
spine1#sh lldp neighbors
```

Some BGP sessions are not established.
This is expected because Leaf3 is not yet configured.

### Check the requirements on the switches

```text
spine1#show management api http-commands
```

## Install the packages on devbox

Use the devbox shell
![images/atd_devbox_shell.png](images/atd_devbox_shell.png)

Run this command:

```shell
pip install git+https://github.com/ksator/network-test-automation.git
```

Run this command to verify the packages and its dependencies are installed:

```bash
pip list
```

Run these commands in a Python interactive session:

```python
>>> from anta.tests import *
>>> dir()        
>>> help(verify_bgp_evpn_state)
>>> exit()
```

The scripts are installed here:

```bash
ls -l /home/arista/.local/bin/
```

Run this command to add this path to the PATH env variable

```bash
echo $HOME
echo $PATH
export PATH="$HOME/.local/bin:$PATH"
echo $PATH
```

Run this command to verify you can now run the scripts:

```bash
check-devices.py --help
```

Run this commands on devbox to install some additional packages:

```bash
sudo apt-get install tree unzip -y
```

## Clone this repository on devbox

```shell
git clone https://github.com/ksator/anta-demo.git
cd anta-demo
```

## Create the inventory files

Run this command on devbox to check the inventory files:

```bash
ls inventory
```

There is already an inventory file for the leaves and another one for all devices.
But there is no inventory file for the spines.
Run this command on devbox to check to generate from CVP an inventory file with the IP address of all the devices under the container `Spine`.

```bash
create-devices-inventory-from-cvp.py -cvp 192.168.0.5 -u arista -o inventory -c Spine
more inventory/Spine.txt
```

## Test devices reachability

Run this command on devbox:

```bash
check-devices-reachability.py -i inventory/all.txt -u arista
```

## Test devices

### Define the tests

ATD uses cEOS or vEOS so we wont run the hardware tests.  
This lab doesnt use MLAG, OSPF, IPv6, RTC ... so we wont run these tests as well.

Some tests can be used for all devices like the checking the EOS version or checking of the NTP status.  

About the Spines versus the leaves, they usually have a different number of BGP sessions and a different number of loopback interfaces.
So, some tests should be used only for the spines, and some tests should be used only for the leaves.  

Here's the inventory files:

```bash
ls inventory
```

Here's the tests:

```bash
ls tests
```

### Run the tests

Run these commands to test the devices:

```bash
check-devices.py -i inventory/all.txt -t tests/all.yaml -o tests_result_all.txt -u arista
check-devices.py -i inventory/Spine.txt -t tests/Spine.yaml -o tests_result_Spine.txt -u arista
check-devices.py -i inventory/Leaf.txt -t tests/Leaf.yaml -o tests_result_Leaf.txt -u arista
```

Run these commands to check the result:

```bash
cat tests_result_all.txt
cat tests_result_Spine.txt
cat tests_result_Leaf.txt
```

Some tests failed.
This is expected because leaf3 is not yet configured.

### Fix the issue

Lets configure leaf3 using eAPI.

```bash
python configure-leaf3.py
```

### Re run the tests

Lets re run all the tests.

```bash
check-devices.py -i inventory/all.txt -t tests/all.yaml -o tests_result_all.txt -u arista
check-devices.py -i inventory/Spine.txt -t tests/Spine.yaml -o tests_result_Spine.txt -u arista
check-devices.py -i inventory/Leaf.txt -t tests/Leaf.yaml -o tests_result_Leaf.txt -u arista
```

Run these commands to check the result:

```bash
cat tests_result_all.txt
cat tests_result_Spine.txt
cat tests_result_Leaf.txt
```

All tests passed.

## Collect commands output

Run these commands on devbox:

```bash
more eos-commands.yaml
collect-eos-commands.py -i inventory/all.txt -c eos-commands.yaml -o show_commands -u arista
tree show_commands
more show_commands/192.168.0.10/text/show\ version
```

## Collect the scheduled show tech-support files

```text
spine1# sh running-config all | grep tech
spine1# bash ls /mnt/flash/schedule/tech-support/
```

Run these commands on devbox:

```bash
collect-sheduled-show-tech.py -i inventory/all.txt -u arista -o show_tech
tree show_tech
unzip show_tech/spine1/xxxx.zip -d show_tech
ls show_tech/mnt/flash/schedule/tech-support/
ls show_tech/mnt/flash/schedule/tech-support/ | wc -l
```

```text
spine1# bash ls /mnt/flash/schedule/tech-support/
```

## Clear the list of MAC addresses which are blacklisted in EVPN

### Create 5 mac moves within 180 seconds

Run this command alternately on host1 and host2 in order to create 5 mac moves within 180 seconds:

```bash
bash sudo ethxmit --ip-src=10.10.10.1 --ip-dst=10.10.10.2 -S 948e.d399.4421 -D ffff.ffff.ffff et1 -n 1
```

Leaf1 or leaf3 concludes that a duplicate-MAC situation has occurred (948e.d399.4421)

```text
leaf3#show mac address-table
leaf3#show bgp evpn host-flap
leaf3#show logging | grep EVPN-3-BLACKLISTED_DUPLICATE_MAC
```

### Clear the blacklisted MAC addresses

Run this command on devbox to clear on devices the list of MAC addresses which are blacklisted in EVPN:

```bash
evpn-blacklist-recovery.py -i inventory/all.txt -u arista
```

Verify:

```text
leaf3#show mac address-table
leaf3#show bgp evpn host-flap
leaf3#show logging | grep EVPN-3-BLACKLISTED_DUPLICATE_MAC
```

## Clear counters

```bash
spine1#sh interfaces counters
```

Run these commands on devbox:

```bash
clear-counters.py -i inventory/all.txt -u arista
```

```bash
spine1#sh interfaces counters
```
