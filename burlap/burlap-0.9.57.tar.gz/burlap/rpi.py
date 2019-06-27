"""
Raspberry Pi
===================

Tools for configuring software and features specific to a Raspberry Pi.
"""
import os
import getpass

import six

from burlap import Satchel
from burlap.constants import *
from burlap.decorators import task

RPI2 = 'rpi2'
RPI3 = 'rpi3'

class RaspberryPiSatchel(Satchel):
    """
    Tools for configuring the Raspberry Pi.

    Most of these were written for the Raspberry Pi 2, but now target the Raspberry Pi 3.
    """

    name = 'rpi'

    def set_defaults(self):
        self.env.i2c_enabled = False
        self.env.gpio_enabled = False
        self.env.camera_enabled = False

        # The group used for allowing access to /dev/ttyACM* serial devices.
        self.env.serial_group = 'dialout'

        self.env.hardware_version = RPI3

#         self.env.firmware_update_bin_url = \
#             'https://raw.githubusercontent.com/Hexxeh/rpi-update/master/rpi-update'

        self.env.gpu_mem = 256

        # The SD card reader and mount info.
        self.env.sd_device = '/dev/sdb'
        self.env.sd_media_mount_dir = '/dev/sdb1'
        self.env.sd_media_mount_dir2 = '/dev/sdb2'

        # Raspbian specifics.
        # Should be one of the filenames found at:
        # https://downloads.raspberrypi.org
        self.env.raspbian_image_zip = 'raspbian_lite_latest.zip'
        self.env.raspbian_download_url = 'https://downloads.raspberrypi.org/raspbian_lite_latest'
        self.env.raspbian_mount_point = '/mnt/img'
        # Should be one of the filenames found at:
        # https://github.com/dhruvvyas90/qemu-rpi-kernel
        self.env.raspbian_kernel = 'kernel-qemu-4.1.13-jessie'

        # Ubuntu specifics.
        # NOTE: found to work reliably on both RPi3 and RPi2.
        self.env.ubuntu_download_url = \
            'http://phillw.net/isos/pi2/ubuntu-minimal-16.04-server-armhf-raspberry-pi.img.xz'

        self.env.conf_os_type = RASPBIAN
        self.env.conf_os_release = JESSIE

        self.env.libvirt_boot_dir = '/var/lib/libvirt/boot'
        self.env.libvirt_images_dir = '/var/lib/libvirt/images'

#         self.env.default_hostname = 'raspberrypi'
#         self.env.default_user = 'pi'
#         self.env.default_password = 'raspberry'

    @task
    def show_firmware(self):
        r = self.local_renderer
        r.sudo('cat /boot/.firmware_revision')

    @task
    def update_firmware(self):
        r = self.local_renderer
        r.pc('Updating firmware.')

#         packager = self.packager
#         if packager == APT:
#             r.sudo('apt-get install -y binutils')
#         else:
#             raise NotImplementedError
        self.install_packages()

        # Install most recent version of rpi-update, if not present.
        r.sudo_if_missing(
            fn='/usr/bin/rpi-update',
            cmd='curl -L --output /usr/bin/rpi-update {firmware_update_bin_url} && '
                'chmod +x /usr/bin/rpi-update')

        # Update firmware.
        r.sudo("sudo rpi-update")

        # Reboot to take effect.
        self.reboot(wait=300, timeout=60)

    @task
    def fix_eth0_rename(self, hardware_addr):
        """
        A bug as of 2016.10.10 causes eth0 to be renamed to enx*.
        This renames it to eth0.

        http://raspberrypi.stackexchange.com/q/43560/29103
        """
        r = self.local_renderer
        r.env.hardware_addr = hardware_addr
        r.sudo('ln -s /dev/null /etc/udev/rules.d/80-net-name-slot.rules')
        r.append(
            text=r'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '\
                r'ATTR\{address\}=="{hardware_addr}", '\
                r'ATTR\{dev_id\}=="0x0", '\
                r'ATTR\{type\}=="1", '\
                r'KERNEL=="eth*", NAME="eth0"',
            filename='/etc/udev/rules.d/70-persistent-net.rules',
            use_sudo=True,
        )

    def assume_localhost(self):
        """
        Sets connection parameters to localhost, if not set already.
        """
        if not self.genv.host_string:
            self.genv.host_string = 'localhost'
            self.genv.hosts = ['localhost']
            self.genv.user = getpass.getuser()

    @task
    def init_raspbian_disk(self, yes=0):
        """
        Downloads the latest Raspbian image and writes it to a microSD card.

        Based on the instructions from:

        https://www.raspberrypi.org/documentation/installation/installing-images/linux.md
        """
        self.assume_localhost()

        yes = int(yes)
        device_question = 'SD card present at %s? ' % self.env.sd_device
        if not yes and not six.moves.input(device_question).lower().startswith('y'):
            return

        r = self.local_renderer
        r.local_if_missing(
            fn='{raspbian_image_zip}',
            cmd='wget {raspbian_download_url} -O raspbian_lite_latest.zip')

        r.lenv.img_fn = \
            r.local("unzip -l {raspbian_image_zip} | sed -n 4p | awk '{{print $4}}'", capture=True) or '$IMG_FN'
        r.local('echo {img_fn}')
        r.local('[ ! -f {img_fn} ] && unzip {raspbian_image_zip} {img_fn} || true')
        r.lenv.img_fn = r.local('readlink -f {img_fn}', capture=True)
        r.local('echo {img_fn}')

        with self.settings(warn_only=True):
            r.sudo('[ -d "{sd_media_mount_dir}" ] && umount {sd_media_mount_dir} || true')
        with self.settings(warn_only=True):
            r.sudo('[ -d "{sd_media_mount_dir2}" ] && umount {sd_media_mount_dir2} || true')

        r.pc('Writing the image onto the card.')
        r.sudo('time dd bs=4M if={img_fn} of={sd_device}')

        # Flush all writes to disk.
        r.run('sync')

    @task
    def init_ubuntu_disk(self, yes=0):
        """
        Downloads the latest Ubuntu image and writes it to a microSD card.

        Based on the instructions from:

            https://wiki.ubuntu.com/ARM/RaspberryPi

        For recommended SD card brands, see:

            http://elinux.org/RPi_SD_cards

        Note, if you get an error like:

            Kernel panic-not syncing: VFS: unable to mount root fs

        that means the SD card is corrupted. Try re-imaging the card or use a different card.
        """
        self.assume_localhost()

        yes = int(yes)

        if not self.dryrun:
            device_question = 'SD card present at %s? ' % self.env.sd_device
            inp = six.moves.input(device_question).strip()
            print('inp:', inp)
            if not yes and inp and not inp.lower().startswith('y'):
                return

        r = self.local_renderer

        # Confirm SD card is present.
        r.local('ls {sd_device}')

        # Download image.
        r.env.ubuntu_image_fn = os.path.abspath(os.path.split(self.env.ubuntu_download_url)[-1])
        r.local('[ ! -f {ubuntu_image_fn} ] && wget {ubuntu_download_url} || true')

        # Ensure SD card is unmounted.
        with self.settings(warn_only=True):
            r.sudo('[ -d "{sd_media_mount_dir}" ] && umount {sd_media_mount_dir}')
        with self.settings(warn_only=True):
            r.sudo('[ -d "{sd_media_mount_dir2}" ] && umount {sd_media_mount_dir2}')

        r.pc('Writing the image onto the card.')
        r.sudo('xzcat {ubuntu_image_fn} | dd bs=4M of={sd_device}')

        # Flush all writes to disk.
        r.run('sync')

    #EXPERIMENTAL
    @task
    def init_raspbian_vm(self):
        """
        Creates an image for running Raspbian in a QEMU virtual machine.

        Based on the guide at:

            https://github.com/dhruvvyas90/qemu-rpi-kernel/wiki/Emulating-Jessie-image-with-4.1.x-kernel
        """

        r = self.local_renderer

        r.comment('Installing system packages.')
        r.sudo('add-apt-repository ppa:linaro-maintainers/tools')
        r.sudo('apt-get update')
        r.sudo('apt-get install libsdl-dev qemu-system')

        r.comment('Download image.')
        r.local('wget https://downloads.raspberrypi.org/raspbian_lite_latest')
        r.local('unzip raspbian_lite_latest.zip')
        #TODO:fix name?
        #TODO:resize image?

        r.comment('Find start of the Linux ext4 partition.')
        r.local(
            "parted -s 2016-03-18-raspbian-jessie-lite.img unit B print | "
            "awk '/^Number/{{p=1;next}}; p{{gsub(/[^[:digit:]]/, "", $2); print $2}}' | sed -n 2p", assign_to='START')

        r.local('mkdir -p {raspbian_mount_point}')
        r.sudo('mount -v -o offset=$START -t ext4 {raspbian_image} $MNT')

        r.comment('Comment out everything in ld.so.preload')
        r.local("sed -i 's/^/#/g' {raspbian_mount_point}/etc/ld.so.preload")

        r.comment('Comment out entries containing /dev/mmcblk in fstab.')
        r.local("sed -i '/mmcblk/ s?^?#?' /etc/fstab")

        r.sudo('umount {raspbian_mount_point}')

        r.comment('Download kernel.')
        r.local('wget https://github.com/dhruvvyas90/qemu-rpi-kernel/blob/master/{raspbian_kernel}?raw=true')
        r.local('mv {raspbian_kernel} {libvirt_images_dir}')

        r.comment('Creating libvirt machine.')
        r.local('virsh define libvirt-raspbian.xml')

        r.comment('You should now be able to boot the VM by running:')
        r.comment('')
        r.comment('    qemu-system-arm -kernel {libvirt_boot_dir}/{raspbian_kernel} '
            '-cpu arm1176 -m 256 -M versatilepb -serial stdio -append "root=/dev/sda2 rootfstype=ext4 rw" '
            '-hda {libvirt_images_dir}/{raspbian_image}')
        r.comment('')
        r.comment('Or by running virt-manager.')

    @task
    def create_raspbian_vagrant_box(self):
        """
        Creates a box for easily spinning up a virtual machine with Vagrant.

        http://unix.stackexchange.com/a/222907/16477
        https://github.com/pradels/vagrant-libvirt
        """

        r = self.local_renderer

        r.sudo('adduser --disabled-password --gecos "" vagrant')

        #vagrant user should be able to run sudo commands without a password prompt

        r.sudo('echo "vagrant ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vagrant')
        r.sudo('chmod 0440 /etc/sudoers.d/vagrant')

        r.sudo('apt-get update')
        r.sudo('apt-get install -y openssh-server')

        #put ssh key from vagrant user

        r.sudo('mkdir -p /home/vagrant/.ssh')
        r.sudo('chmod 0700 /home/vagrant/.ssh')
        r.sudo('wget --no-check-certificate https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub -O /home/vagrant/.ssh/authorized_keys')
        r.sudo('chmod 0600 /home/vagrant/.ssh/authorized_keys')
        r.sudo('chown -R vagrant /home/vagrant/.ssh')

        #open sudo vi /etc/ssh/sshd_config and change

        #PubKeyAuthentication yes
        #PermitEmptyPasswords no
        r.sudo("sed -i '/AuthorizedKeysFile/s/^#//g' /etc/ssh/sshd_config")
        #PasswordAuthentication no
        r.sudo("sed -i '/PasswordAuthentication/s/^#//g' /etc/ssh/sshd_config")
        r.sudo("sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/g' /etc/ssh/sshd_config")

        #restart ssh service using

        #sudo service ssh restart

        #install additional development packages for the tools to properly compile and install
        r.sudo('apt-get upgrade')
        r.sudo('apt-get install -y gcc build-essential')
        #TODO:fix? throws dpkg: error: fgets gave an empty string from `/var/lib/dpkg/triggers/File'
        #r.sudo('apt-get install -y linux-headers-rpi')

        #do any change that you want and shutdown the VM . now , come to host machine on which guest VM is running and goto
        #the /var/lib/libvirt/images/ and choose raw image in which you did the change and copy somewhere for example /test

        r.sudo('mkdir /tmp/test')
        r.sudo('cp {libvirt_images_dir}/{raspbian_image} /tmp/test')
        r.sudo('cp {libvirt_boot_dir}/{raspbian_kernel} /tmp/test')

        #create two file metadata.json and Vagrantfile in /test do entry in metadata.json
        r.render_to_file('rpi/metadata.json', '/tmp/test/metadata.json')
        r.render_to_file('rpi/Vagrantfile', '/tmp/test/Vagrantfile')

        #convert test.img to qcow2 format using
        r.sudo('qemu-img convert -f raw -O qcow2  {libvirt_images_dir}/{raspbian_image}  {libvirt_images_dir}/{raspbian_image}.qcow2')

        #rename ubuntu.qcow2 to box.img
        r.sudo('mv {libvirt_images_dir}/{raspbian_image}.qcow2 {libvirt_images_dir}/box.img')

        #Note: currently,libvirt-vagrant support only qcow2 format. so , don't change the format just rename to box.img.
        #because it takes input with name box.img by default.
        #create box

        r.sudo('cd /tmp/test; tar cvzf custom_box.box ./metadata.json ./Vagrantfile ./{raspbian_kernel} ./box.img')

        #add box to vagrant

        #vagrant box add --name custom custom_box.box

        #go to any directory where you want to initialize vagrant and run command bellow that will create Vagrant file

        #vagrant init custom

        #start configuring vagrant VM

        #vagrant up --provider=libvirt
        #TODO:fix? Error while creating domain: Error saving the server: Call to virDomainDefineXML failed: XML error: No PCI buses available

    @property
    def packager_repositories(self):
        d = {}
        # Recommended by https://wiki.ubuntu.com/ARM/RaspberryPi
        if self.env.conf_os_type == UBUNTU:
            if self.env.hardware_version == RPI2:
                d[APT] = ['ppa:ubuntu-raspi2/ppa']
            elif self.env.hardware_version == RPI3:
                d[APT] = ['ppa:ubuntu-raspi2/ppa-rpi3']
        return d

    @property
    def packager_system_packages(self):
        UBUNTU_lst = [
            'curl', 'gcc', 'python-dev', 'git',
            'binutils',
            'rpi-update',
            'raspi-config',
        ]
        RASPBIAN_lst = [
            'curl', 'gcc', 'python-dev', 'git',
            'rpi-update',
            'binutils',
        ]

        if self.env.i2c_enabled:
            UBUNTU_lst.extend(['python-smbus', 'i2c-tools', 'git', 'python-dev', 'libi2c-dev'])
            RASPBIAN_lst.extend(['python-smbus', 'i2c-tools', 'git', 'python-dev', 'libi2c-dev'])

        return {
            UBUNTU: UBUNTU_lst,
            RASPBIAN: RASPBIAN_lst,
        }

    @task
    def test_i2c(self):
        r = self.local_renderer
        #https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
        r.sudo('i2cdetect -y 1')

    @task
    def configure_hdmi(self):
        """
        Configures HDMI to support hot-plugging, so it'll work even if it wasn't
        plugged in when the Pi was originally powered up.

        Note, this does cause slightly higher power consumption, so if you don't need HDMI,
        don't bother with this.

        http://raspberrypi.stackexchange.com/a/2171/29103
        """
        r = self.local_renderer

        # use HDMI mode even if no HDMI monitor is detected
        r.enable_attr(
            filename='/boot/config.txt',
            key='hdmi_force_hotplug',
            value=1,
            use_sudo=True,
        )

        # to normal HDMI mode (Sound will be sent if supported and enabled). Without this line,
        # the Raspbmc would switch to DVI (with no audio) mode by default.
        r.enable_attr(
            filename='/boot/config.txt',
            key='hdmi_drive',
            value=2,
            use_sudo=True,
        )

    @task
    def test_camera(self):
        r = self.local_renderer
        ret = r.run('vcgencmd get_camera')
        if not self.dryrun:
            assert 'detected=1' in ret, 'Camera was not detected.'
            assert 'supported=1' in ret, 'Camera is not supported.'
            print('Camera is detected and supported!')

    @task
    def configure_camera(self):
        """
        Enables access to the camera.

            http://raspberrypi.stackexchange.com/questions/14229/how-can-i-enable-the-camera-without-using-raspi-config
            https://mike632t.wordpress.com/2014/06/26/raspberry-pi-camera-setup/

        Afterwards, test with:

            /opt/vc/bin/raspistill --nopreview --output image.jpg

        Check for compatibility with:

            vcgencmd get_camera

        which should show:

            supported=1 detected=1

        """
        #TODO:check per OS? Works on Raspbian Jessie
        r = self.local_renderer
        if self.env.camera_enabled:
            r.pc('Enabling camera.')
            #TODO:fix, doesn't work on Ubuntu, which uses commented-out values

            # Set start_x=1
            #r.sudo('if grep "start_x=0" /boot/config.txt; then sed -i "s/start_x=0/start_x=1/g" /boot/config.txt; fi')
            #r.sudo('if grep "start_x" /boot/config.txt; then true; else echo "start_x=1" >> /boot/config.txt; fi')
            r.enable_attr(
                filename='/boot/config.txt',
                key='start_x',
                value=1,
                use_sudo=True,
            )

            # Set gpu_mem=128
#             r.sudo('if grep "gpu_mem" /boot/config.txt; then true; else echo "gpu_mem=128" >> /boot/config.txt; fi')
            r.enable_attr(
                filename='/boot/config.txt',
                key='gpu_mem',
                value=r.env.gpu_mem,
                use_sudo=True,
            )

            # Compile the Raspberry Pi binaries.
            #https://github.com/raspberrypi/userland
            r.run('cd ~; git clone https://github.com/raspberrypi/userland.git; cd userland; ./buildme')
            r.run('touch ~/.bash_aliases')
            #r.run("echo 'PATH=$PATH:/opt/vc/bin\nexport PATH' >> ~/.bash_aliases")
            r.append(r'PATH=$PATH:/opt/vc/bin\nexport PATH', '~/.bash_aliases')
            #r.run("echo 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/vc/lib\nexport LD_LIBRARY_PATH' >> ~/.bash_aliases")
            r.append(r'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/vc/lib\nexport LD_LIBRARY_PATH', '~/.bash_aliases')
            r.run('source ~/.bashrc')
            r.sudo('ldconfig')

            # Allow our user to access the video device.
            r.sudo("echo 'SUBSYSTEM==\"vchiq\",GROUP=\"video\",MODE=\"0660\"' > /etc/udev/rules.d/10-vchiq-permissions.rules")
            r.sudo("usermod -a -G video {user}")

            r.reboot(wait=300, timeout=60)

            self.test_camera()

        else:
            r.disable_attr(
                filename='/boot/config.txt',
                key='start_x',
                use_sudo=True,
            )
            r.disable_attr(
                filename='/boot/config.txt',
                key='gpu_mem',
                use_sudo=True,
            )
            r.reboot(wait=300, timeout=60)

    @task
    def fix_lsmod_for_pi3(self):
        """
        Some images purporting to support both the Pi2 and Pi3 use the wrong kernel modules.
        """
        r = self.local_renderer
        r.env.rpi2_conf = '/etc/modules-load.d/rpi2.conf'
        r.sudo("sed '/bcm2808_rng/d' {rpi2_conf}")
        r.sudo("echo bcm2835_rng >> {rpi2_conf}")

    @task
    def configure_gpio(self):
        #TODO:check per OS? Works on Raspbian Jessie and Ubuntu 16.
        r = self.local_renderer
        if self.env.gpio_enabled:
            r.pc('Enabling GPIO.')

            # assumes init_project ran first
            r.sudo("usermod -a -G gpio {user}")
            #sudo chown root:gpio /sys/class/gpio/unexport /sys/class/gpio/export
            #sudo chmod 220 /sys/class/gpio/unexport /sys/class/gpio/export

            # Make GPIO accessible to non-root users.
            #Obsolete in Ubuntu 16?
#             r.sudo("echo 'SUBSYSTEM==\"gpio*\", PROGRAM=\"/bin/sh -c '"
#                 "chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio; "
#                 "chown -R root:gpio /sys/devices/virtual/gpio && "
#                 "chmod -R 770 /sys/devices/virtual/gpio'\"' > /etc/udev/rules.d/99-com.rules")
        else:
            pass

    @task
    def configure_sound(self):
        r = self.local_renderer
        r.sudo('usermod -G audio {user}')
        r.enable_attr(
            filename='/boot/config.txt',
            key='dtparam=audio',
            value='on',
            use_sudo=True,
        )

    @task
    def test_sound(self):
        r = self.local_renderer
        ret = r.sudo('aplay /usr/share/sounds/alsa/Front_Center.wav')
        assert 'error' not in ret.lower()

    @task
    def test_gpio(self, pin=20):
        r = self.local_renderer
        r.env.gpio_dir = '/sys/class/gpio'
        r.env.gpio_pin = pin
        r.run('cd {gpio_dir}; echo {gpio_pin} > export')
        r.run('cd {gpio_dir}; echo out > gpio{gpio_pin}/direction')
        r.run('cd {gpio_dir}; echo 1 > gpio{gpio_pin}/value')
        r.run('sleep 1')
        r.run('cd {gpio_dir}; echo 0 > gpio{gpio_pin}/value')
        r.run('cd {gpio_dir}; echo {gpio_pin} > unexport')

    @task
    def configure_serial(self):
        r = self.local_renderer
        r.sudo('usermod -a -G {serial_group} {user}')

    @task
    def configure_i2c(self):
        #TODO:fix? causes RPi3 to become unbootable?
        r = self.local_renderer
        if self.env.i2c_enabled:
            r.pc('Enabling I2C.')

            #r.sudo('apt-get install --yes python-smbus i2c-tools git python-dev')

#             r.sudo("sh -c 'echo \"i2c-bcm2708\" >> /etc/modules'")
#             r.sudo("sh -c 'echo \"i2c-dev\" >> /etc/modules'")
#             r.sudo("sh -c 'echo \"dtparam=i2c1=on\" >> /boot/config.txt'")
#             r.sudo("sh -c 'echo \"dtparam=i2c_arm=on\" >> /boot/config.txt'")

            # Allow non-root users to access I2C.
            # http://quick2wire.com/non-root-access-to-spi-on-the-pi/
            # https://github.com/fivdi/i2c-bus/blob/master/doc/raspberry-pi-i2c.md
            # https://blogs.ncl.ac.uk/francisfranklin/2014/03/23/using-i2c-with-the-raspberry-pi-step-1-modules-and-packages/
            r.sudo('groupadd -f --system spi')
            r.sudo('adduser {user} spi')
            r.sudo('adduser {user} i2c')
            r.append(text='SUBSYSTEM=="spidev", GROUP="spi"', filename='/etc/udev/rules.d/90-spi.rules', use_sudo=True)
            r.append(text='SUBSYSTEM=="i2c-dev", MODE="0666"', filename='/etc/udev/rules.d/99-i2c.rules', use_sudo=True)
            r.append(text='KERNEL=="i2c-[0-7]",MODE="0666"', filename='/etc/udev/rules.d/90-i2c.rules', use_sudo=True)

            r.append(text='i2c-bcm2708', filename='/etc/modules', use_sudo=True)
            r.append(text='i2c-dev', filename='/etc/modules', use_sudo=True)
            r.append(text='dtparam=i2c1=on', filename='/boot/config.txt', use_sudo=True)
            r.append(text='dtparam=i2c_arm=on', filename='/boot/config.txt', use_sudo=True)

            r.reboot(wait=300, timeout=60)

            # If I2C is working, running this should show addresses in use.
            ret = r.sudo('i2cdetect -y 1')
            if not self.dryrun:
                assert ret, 'I2C configuration failed!'
        else:
            pass

    @task(precursors=['packager', 'user', 'timezone', 'avahi', 'nm', 'ntpclient', 'sshnice'])
    def configure(self):
        self.update_firmware()
        self.configure_i2c()
        self.configure_camera()
        self.configure_gpio()
        self.configure_serial()
        self.configure_sound()

RaspberryPiSatchel()
