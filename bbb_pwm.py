"""BeagleBone Black specific PWM driver sysfs interface"""

import os
import glob

# we overload init from https://github.com/scottellis/pwmpy to find_pwm's on beaglebone black
import pwmpy as linux_pwm

__author__ = 'Coburn Wightman'
__version__ = '0.1'
__license__ = 'New BSD'
__copyright__ = 'Copyright (c) 2017 Coburn Wightman'


class PWM(linux_pwm.PWM):
    def __init__(self, pwm_device_name):
        """ Specify the pwm device name when creating an instance

        The Linux kernel driver exports a sysfs interface like this

            /sys/class/pwm/pwmchip<chip>/pwm<channel>

        A <chip> can have multiple <channels>.

        (see https://www.kernel.org/doc/Documentation/pwm.txt for more info)

        The channel and chip are determined by the kernel driver, and with kernel 4.4 
        on beaglebone black, the chip number oddly can change with reboot.

        This class sorts out and hides the changing chip numbers by allowing the device
        to be selected by name rather than chip and channel. 

        PWM devices available on the beaglebone black are:
        'ECAPPWM0', 'ECAPPWM2', 'EHRPWM0A', 'EHRPWM0B', 'EHRPWM1A', 'EHRPWM1B', 'EHRPWM2A', 'EHRPWM2B'

        To use the BBB pwm's create instances this way

            pwm0 = PWM('ECAPPWM0')

        or as a context manager

            with PWM('ECAPPWM0) as pwm1:

        """

        self.root = '/sys/class/pwm'

        self.device_name = pwm_device_name
        self._chip, self._channel = self.find_pwm(self.device_name)

        self.base = '{}/pwmchip{:d}'.format(self.root, self._chip)
        self.path = self.base + '/pwm{:d}'.format(self._channel)

        if not os.path.isdir(self.base):
            raise FileNotFoundError('Directory not found: ' + self.base)

        return

    # allow using class as a context manager for more reliable cleanup
    def __enter__(self):
        self.export()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.enable = False
        self.inversed = False
        self.unexport()
        return

    @property
    def name(self):
        """The pwm device name used by this instance.
        Read-only, set in the constructor.
        """
        return self.device_name
        
    # build relationship between the pwm device names and their sysfs filenames
    #
    # Based on work by samuel . bucquet Tue, 13 Sep 2016 05:49:33 -0700
    # https://groups.google.com/forum/#!msg/beagleboard/u9We3y-yrZc/z1dKE4F-BQAJ
    #
    def find_pwm(self, device_name):
        """ build relationship between the pwm device names and their sysfs filenames
        returns integer tuple of chip and channel of the requested pwm device

        Based on work by samuel . bucquet Tue, 13 Sep 2016 05:49:33 -0700
        https://groups.google.com/forum/#!msg/beagleboard/u9We3y-yrZc/z1dKE4F-BQAJ
        """
        
        ecap_pwms = ('ECAPPWM0', 'ECAPPWM2')
        ehr_pwms = ('EHRPWM0A', 'EHRPWM0B', 'EHRPWM1A', 'EHRPWM1B', 'EHRPWM2A', 'EHRPWM2B')

        if not (device_name in ecap_pwms) and not (device_name in ehr_pwms):
            possible_device_names = ecap_pwms + ehr_pwms
            raise KeyError('Unrecognized device name. Possible choices are: {}'.format(possible_device_names))

        devices = {}
        chips = glob.glob('{}/pwmchip*'.format(self.root))
        # print chips
        ecap_index = 0
        ehr_index = 0
        for chip in chips:
            # print 'looking in: ' + '{}/npwm'.format(chip)
            chip_index = int(chip.replace(self.root+'/pwmchip',''))
            npwm = int(open('{}/npwm'.format(chip)).read())
            if npwm == 1:
                # On BBB, ecap chips have one channel
                if ecap_index == 0:
                    channel_index = 0
                    name = ecap_pwms[ecap_index]
                    devices[name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    # device = devices[name]
                    # print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(self.root, device['chip'], device['channel'], name)
                elif ecap_index == 1:
                    channel_index = 2
                    name = ecap_pwms[ecap_index]
                    devices[name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    # device = devices[name]
                    # print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(self.root, device['chip'], device['channel'], name)
                else:
                    pass
                ecap_index += 1
                # print
            elif npwm == 2:
                # while ehr chips have 2 channels
                for channel_index in [0, 1]:
                    name = ehr_pwms[ehr_index+channel_index]
                    devices[name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    # device = devices[name]
                    # print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(self.root, device['chip'], device['channel'], name)
                ehr_index += 2
                # print
            else:
                print '(unrecognized chip npwm count)'

        device = devices[device_name]
        return (device['chip'], device['channel'])

    @property
    def inversed(self):
        """normal polarity or inversed, boolean"""
        with open(self.path + '/polarity', 'r') as f:
            value = f.readline().strip()

        return True if value == 'inversed' else False

    @inversed.setter
    def inversed(self, value):
        with open(self.path + '/polarity', 'w') as f:
            if value:
                f.write('inversed')
            else:
                f.write('normal')

if __name__ == '__main__':
    import time

    # use the pwm class as a simple object
    pwm = PWM('ECAPPWM0')
    pwm.export()
    print 'driving {}: chip{} pwm{}'.format(pwm.name, pwm.chip, pwm.channel)
    pwm.period = int(1e9 / 1000)
    pwm.duty_cycle = int(pwm.period * 0.25)
    pwm.inversed = False
    print 'inversed is {}'.format(pwm.inversed)
    pwm.enable = True
    time.sleep(2)
    pwm.enable = False
    pwm.unexport()
    
    time.sleep(2)
    
    # use the pwm class as a context manager
    with PWM('ECAPPWM0') as pwm:
        pwm.period = int(1e9 / 1000)
        pwm.duty_cycle = int(pwm.period * 0.25)
        pwm.inversed = True
        print 'inversed is {}'.format(pwm.inversed)
        pwm.enable = True
        time.sleep(2)

        pwm.period = int(1e9 / 1000)
        pwm.duty_cycle = int(pwm.period * 0.9)
        time.sleep(2)

    # try an non-existent pwm device name
    with PWM('ECAPPWM1') as pwm:
        pwm.period = 1000000
        pwm.duty_cycle = 100000
        pwm.inversed = True
        pwm.enable = True
        time.sleep(2)
