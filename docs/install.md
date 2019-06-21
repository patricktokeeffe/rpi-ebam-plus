
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
4. Grant new user serial port access (`sudo usermod -a -G dialout sally`)
5. Log out; log in as the new user
6. Delete old user (`sudo userdel -r pi`)

#### Base Packages

First, do a complete system update: `sudo apt-get update && sudo apt-get dist-upgrade -y`

Next, install necessary packages and useful utilities (`sudo apt-get install ...`)
* `git`
* `tmux`
* `minicom`

Then do a little bit of config to make serial port usage easier (`sudo minicom -s`):
* Serial port setup
    * Serial Device: `/dev/ttyUSB0`
    * Hardware flow control: No
* Save setup as dfl


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

#### Watchdog Timer

Enable automatic rebooting if the hardware hangs somehow.
First enable hardware support:
```
sudo nano /boot/config.txt
```
```diff
 ...
+##watchdog
+dtparam=watchdog=on
```
```
sudo reboot
```

Then install *watchdog* and fix its broken *systemd* service file:
```
sudo apt install watchdog -y
sudo bash -c "cp /lib/systemd/system/watchdog.service /etc/systemd/system/
> echo 'WantedBy=multi-user.target' >> /etc/systemd/system/watchdog.service"
```

Update the configuration file:
```
sudo nano /etc/watchdog.conf
```
```diff
 ...
-#max-load-1       = 24
+max-load-1       = 24

 ...
-#watchdog-device        = /dev/watchdog
+watchdog-device        = /dev/watchdog
+
+watchdog-timeout = 10
```

Finally enable the service:
```
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

And optionally test with null pointer dereference:
```
echo c > /proc/sysrq-trigger
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


### Data Share Directory

Create a new public directory that will be served via http/ftp/samba
and populate with symlinks:
```
sudo mkdir -m 1777 /share
```
```
sudo ln -s /var/run/ebam /var/log/ebam/latest
sudo ln -s /var/log/ebam /share/ebam
```

By serving an `ebam` directory, we can easily expose other logfile
sets later on (e.g. NTP stats or some environmental sensors).


### SAMBA

Install the *samba* package so Windows clients recognize the hostname, and
users can anonymously browse from local network clients.
```
sudo apt install samba -y
```
```
sudo cp src/etc/samba/smb.conf /etc/samba/
```

> **This isn't working for windows clients yet**

Symptoms:
* can see computer in network list
* can open computer and see share
* sometimes can even open share and see "ebam" folder
* at no point can ebam folder be opened:
    * "You do not have permission to access {shared folder name}"
* frequently get (the same?) errors opening share home folder too

Tab trail:
* <https://github.com/wsular/rpi-python-iaq-sensor/blob/stash/etc/samba/smb.conf>
    * tried re-using IAQ code but it didn't work
* <https://askubuntu.com/questions/258284/setting-up-an-anonymous-public-samba-share-to-be-accessed-via-windows-7-and-xbmc>
    * this person gets prompted for user/pswd, but clears user from field and logins
      successfully as anon user. they report server is *not* visible via file browser
    * reported key to success was `security = share` (said `security=user`+`map to user=Bad User`
      wasn't working for them)
* <https://askubuntu.com/questions/781963/simple-samba-share-no-password?noredirect=1&lq=1>
    * this user wants full read & write access not anon guest
    * comment to top answer indicates key is `chmod 777 /share`
    * top answer mentions resetting w/ `dpkg-reconfigure samba-common`
* <https://www.raspberrypi.org/forums/viewtopic.php?p=1249692>
    * forum user brings up Windows 10 intentionally disabling guest access (Jan 2018)
      likely could have arrived in Windows 7?
    * tried adding registry key ....\AllowInsecureGuestAuth and still didn't work
* <https://raspberrypi.stackexchange.com/questions/15108/unable-to-access-samba-file-share>
    * 2014, options referenced in smb.conf no longer exist in default setup
* <https://stackoverflow.com/questions/17078414/samba-shares-seen-in-windows-but-cannot-connect>
    * marked as answered (Jul 2013) key is `guest account = nfsnobody` and
      `map to guest = bad user` in the global section
* <https://www.debuntu.org/samba-how-to-share-files-for-your-lan-without-userpassword/>
    * old tutorial using `security = share` ... I tried and was told `share` was invalid option
* <https://ubuntuforums.org/showthread.php?t=1709425>
    * another discussion about `security = user`+`map to guest = bad user` combo
    * this didn't seem to change anything when tried
* <https://serverfault.com/questions/895570/how-to-configure-samba-to-work-with-windows-10-1709>
    * another user with Windows 10 problems, and answers with reference links
    * hours-new post complains windows 7 clients impacted too


### Nginx

This web server will allow users to reach RPi-Monitor, a data website, and
basic log file browsing via the same website.

> *Note we are not using secure HTTP because this device does not have a DNS entry
> and self-signed certificates offer no real advantage (i.e. our server is read-only).

Refer to the *Usages* > *Authentication and secure access* section of the
documentation (<https://xavierberger.github.io/RPi-Monitor-docs/34_autentication.html>)
for examples.

Install *nginx*, disable the default site and create a new one:
```
sudo apt install nginx -y
```
```
sudo rm /etc/nginx/sites-enable/default
sudo nano /etc/nginx/sites-available/ebam
```

Copy provided configuration file:
```
sudo cp src/etc/nginx/sites-available/ebam /etc/nginx/sites-available/ebam
```

Enable the new site and restart *nginx*:
```
sudo ln -s /etc/nginx/sites-available/ebam /etc/nginx/sites-enabled/ebam
sudo systemctl restart nginx
```


### Development Setup

1. Install the python package manager (`sudo apt-get install python-pip -y`)
2. Then re-install using itself for possible updates (`sudo pip install pip`)
3. Finally, install required packages:
```
sudo pip install python-dev pyserial pandas
```
> *Packages must be installed system-wide or the service executable will not be
> able to load them - therefore, do not omit `sudo` when calling `pip`.*


### Data Acquisition Script

The script needs to be run each hour; it is not a continuous process at this time.
Just use `sudo crontab -e` (or your favorite method) to run 5 mins past the hour:
```
5 * * * * /path/to/the/repo/src/getbam
```




