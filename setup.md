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

Install the *watchdog* package:
> *In latest releases, it is no longer necessary to fix the *systemd*
> service file (Jun 2019).* 👍
```
sudo apt install watchdog -y
```
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

Follow [these instructions](https://xavierberger.github.io/RPi-Monitor-docs/11_installation.html).

Update packages and enable update hook:
```
sudo /etc/init.d/rpimonitor update
sudo /etc/init.d/rpimonitor install_auto_package_status_update
```

Fix up network config (no longer active by default since introduction of
[predictable network names](https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/):
* `sudo nano /etc/rpimonitor/template/network.conf`
* Uncomment first two config blocks (optionally updating `eth0` if you have
  enabled predictable names)
* Uncomment final config block for statistics
* Comment out existing status-content-line entries in third config block
  and uncomment the "Ethernet sent..." line

Set to listen on localhost only:
```
sudo nano /etc/rpimonitor/daemon.conf
```
```diff
-#daemon.addr=0.0.0.0
+daemon.addr=127.0.0.1
```
```
sudo systemctl restart rpimonitor
```


### Data Access Setup

#### FTP

Install an FTP server for universal copy-paste access
(default configuration works okay):
```
sudo apt install vsftpd -y
```

Create new user *ebam* for FTP login (only, no shell access):
```
sudo adduser -s /bin/false ebam
sudo nano /etc/shells
```
```diff
 ...
+/bin/false
```

Create new directory to hold shared folders (& reset ownership):
```
sudo mkdir /home/ebam/data
sudo chown -R ebam:ebam /home/ebam/data
```

Retrict ftp login to *ebam* by blacklisting other users (ex: *pi*):
```
sudo nano /etc/ftpusers
```
```diff
 ...
+pi
```

> **Notes on *vsftpd***
>
> * trying to setup anon browse access
>     * throws writeable root chroot errors
>     * anon cannot follow symlinks
> * seting up user based access
>     * chrome does not permit login FTP browse
>     * chroot'ed users cannot follow symlinks
>     * chroot'ed users must have read-only home dir
>     * non-chroot users can browse/get lost in file system
> * using bind vs symlinks
>     * nobody can see into nested `mount --bind` folders
>     * the `mount --bind` command isn't persistant anyway
>     * windows explorer FTP cannot symlink or bind (sometimes?)
>     * <https://serverfault.com/questions/972337/vsftp-accessing-nested-mounted-folders>


#### Data Share Folder

Symlink the runtime folder with latest values into the EBAM log
directory, then symlink the EBAM log directory into the FTP homedir:
```
sudo ln -s /run/ebam /var/log/ebam/latest
sudo ln -s /var/log/ebam /home/ebam/data
```

This folder (`/home/ebam/data`) will be the base directory (`/`) 
for HTTP/S browsing (`/data/`) and the SAMBA share ("Data") (see below).
Since the FTP user is not chroot'ed, make another symlink to provide
the same short path structure (i.e. `ftp://<hostname>/data/ebam/...`):
```
sudo ln -s /home/ebam/data /data
```


#### Windows Shares

Install the *samba* package so Windows clients recognize the hostname and
browse the computer anonymously from the local network.
```
sudo apt install samba -y
```

Then copy the provided configuration, which will create a public, read-only
share named "data" which maps to `/home/ebam/data`:
```
sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak
sudo cp src/etc/samba/smb.conf /etc/samba/
sudo systemctl restart smbd
```


#### Nginx

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

Copy provided configuration file, which publishes:
* web root (`/var/www/html`) as `/`
* RPi-Monitor (localhost:8888) as `/status`
* data folder (`/home/ebam/data`) as `/data`
* *eventually: AQI plot (bokeh server) as `/` instead*
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


### Data Acquisition Scripts

Finally, copy the source files to corresponding system directories:
```
git clone https://github.com/patricktokeeffe/rpi-ebam-plus
 ...
cd rpi-ebam-plus
sudo cp src/ /
```

Because a `cron.d/` service file is included, copying the source files is
sufficient to initiate automatic data acquisition from the E-BAM PLUS.

