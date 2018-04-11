
# Software Installation

## E-BAM PLUS Raspberry Pi Interface

This project is based on Raspbian Lite (Jessie). Software-related setup is
covered on this page. 

> Strictly speaking, you could accomplish the following using other Linux
> distributions and/or using other hardware. 


### O/S Setup

Setting up Raspbian from scratch. *Experienced users may prefer to skip this
section.*

#### Initial Config

1. Login using default credentials (*pi* / *raspberry*)
2. Modify system settings (`sudo raspi-config`)
    * Change your password
    * Update your locale/keyboard map/timezone/etc
    * Enable the SSH server (*not on by default*)
    * Update your hostname (to, say, `ebam-plus`?)

#### User Setup

Though not required, our SOP is to create a new user other than `pi` for
administration (ref: <https://www.raspberrypi.org/documentation/linux/usage/users.md>)

Assuming this user is named `sally`:
1. Login as admin user (by default, `pi`)
2. Create new user (`sudo adduser sally`)
	* Prompt info (name, office, ph#) is optional
	* Give strong password
3. Grant new user admin rights (`sudo visudo`)
	* Duplicate this line: `root		ALL=(ALL:ALL) ALL`
	* Update copied line to: `sally	ALL=NOPASSWD: ALL`
4. Log out; log in as the new user
5. Delete old user (`sudo userdel -r pi`)

#### Base Packages

First, do a complete system update: `sudo apt-get update && sudo apt-get dist-upgrade -y`

Next, install necessary packages and useful utilities (`sudo apt-get install ...`)
* `git`
* `tmux`

#### Shell Access

Add some public SSH keys to your new administrative user account and
disable password login.
* See <https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2>

#### Automatic Updates

Since this device will be left running unattended, install packages to support
automatic updates.
```
$ sudo apt-get update
$ sudo apt-get install unattended-upgrades -y
```


### Off Button Support

Although of limited use inside the enclosure, a physical button is installed to safely turn the Pi off.
* See <https://github.com/patricktokeeffe/rpi-off-button>


### RPi-Monitor

To monitor overall computer performance, install
[RPi-Monitor](https://rpi-experiences.blogspot.com).

1. [Install](https://xavierberger.github.io/RPi-Monitor-docs/11_installation.html)
2. Update packages and enable update hook
    * `sudo /etc/init.d/rpimonitor update`
    * `sudo /etc/init.d/rpimonitor install_auto_package_status_update`
3. Fix up network config (no longer active by default since introduction of
   [predictable network names](https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/)
    * `sudo nano /etc/rpimonitor/template/network.conf`
    * Uncomment first two config blocks (optionally updating `eth0` if you have
      enabled predictable names)
    * Uncomment final config block for statistics
    * Comment out existing status-content-line entries in third config block
      and uncomment the "Ethernet sent..." line

