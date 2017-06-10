# from  samuel . bucquet Tue, 13 Sep 2016 05:49:33 -0700
# https://groups.google.com/forum/#!msg/beagleboard/u9We3y-yrZc/z1dKE4F-BQAJ
#
# As I encountered the same behaviour as yours when switching to kernel 4.4,
# I resolved mine with the cape_universal (the default with the official
# image provided) with a line 'config-pin P9_14 pwm' for the PWM1A for ex.
# But, the numbering of the PWMs differ at each booting of the bbb ! not very
# easy to handle, so after I saw the PWM with npwm == 2 are not the ECAP ones

# https://www.kernel.org/doc/Documentation/pwm.txt

import os
import glob
import linux_pwm as linux_pwm

class PWM(linux_pwm.PWM):
    def __init__(self, deviceName):
        #self.device = {}
        # self.opened = False

        # self.enabled = False
        # self.inverted = False
        # self.period = 10000000
        # self.active_time = 0

        self._chip, self._channel = self.find_pwm(deviceName)

        # self._chip = self.device['chip']
        # self._channel = self.device['channel']
        self.base = '/sys/class/pwm/pwmchip{:d}'.format(self._chip)
        self.path = self.base + '/pwm{:d}'.format(self._channel)

        print 'base: {}'.format(self.base)
        print 'path: {}'.format(self.path)
        
        if not os.path.isdir(self.base):
            raise FileNotFoundError('Directory not found: ' + self.base)

        return

    # allow using class as a context manager for more reliable cleanup
    def __enter__(self):
        #self.open()
        self.export()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #self.close()
        self.enable = False
        self.unexport()
        return

    # build relationship between the pwm resource names and their sysfs filenames
    def find_pwm(self, deviceName):
        ecap_pwms = ('ECAPPWM0', 'ECAPPWM2')
        ehr_pwms = ('EHRPWM0A', 'EHRPWM0B', 'EHRPWM1A', 'EHRPWM1B', 'EHRPWM2A', 'EHRPWM2B')

        if not (deviceName in ecap_pwms) and not (deviceName in ehr_pwms):
            raise KeyError('Undefined device. Possible choices are: {}'.format(ecap_pwms+ehr_pwms))

        devices = {}
        path = '/sys/class/pwm'
        chips = glob.glob('{}/pwmchip*'.format(path))
        ecap_index = 0
        ehr_index = 0
        for chip in chips:
            print 'looking in: ' + '{}/npwm'.format(chip)
            chip_index = int(chip.replace(path+'/pwmchip',''))
            npwm = int(open('{}/npwm'.format(chip)).read())
            if npwm == 1:
                # On BBB, ecap chips have one channel
                if ecap_index == 0:
                    channel_index = 0
                    device_name = ecap_pwms[ecap_index]
                    devices[device_name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    device = devices[device_name]
                    print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(path, device['chip'],
                                                                         device['channel'], device_name)
                elif ecap_index == 1:
                    channel_index = 2
                    device_name = ecap_pwms[ecap_index]
                    devices[device_name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    device = devices[device_name]
                    print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(path, device['chip'],
                                                                         device['channel'], device_name)
                else:
                    pass
                ecap_index += 1
                print
            elif npwm == 2:
                # while ehr chips have 2 channels
                for channel_index in [0, 1]:
                    device_name = ehr_pwms[ehr_index+channel_index]
                    devices[device_name] = {'chip' : chip_index, 'channel' : channel_index}
                    
                    device = devices[device_name]
                    print ' (assigning {}/pwmchip{}/pwm{} to {})'.format(path, device['chip'],
                                                                         device['channel'], device_name)
                    
                ehr_index += 2
                print
            else:
                print '(unrecognized chip npwm count)'

            device = devices[deviceName]
        return (device['chip'], device['channel'])

    # def open(self):
    #     print '{}/export'.format(self.base), self.device['channel']
    #     open('{}/export'.format(self.base), 'w').write('{:d}'.format(self._channel))
    #     self.opened = True
    #     return

    # def close(self):
    #     if self.opened:
    #         self.is_enabled = False
    #         print '{}/unexport'.format(self.base), self.device['channel']
    #         open('{}/unexport'.format(self.base), 'w').write('{:d}'.format(self._channel))
    #     self.opened = False
    #     return

    # def write(self, device, command, value):
    #     print 'write {} to {}/{}'.format(value, self.path, command)
    #     open('{}/{}'.format(self.path, command), 'w').write(value)

    # @property
    # def is_enabled(self):
    #     return self.enabled

    # @is_enabled.setter 
    # def is_enabled(self, boolean):
    #     self.enabled = boolean
    #     if self.enabled == True:
    #         state = '1'
    #     else:
    #         state = '0'
    #     self.write(self.device, 'enable', state)
    #     return

    # @property
    # def is_inverted(self):
    #     return self.inverted

    # @is_inverted.setter 
    # def is_inverted(self, boolean):
    #     self.inverted = boolean
    #     if self.inverted == True:
    #         state = 'inversed'
    #     else:
    #         state = 'normal'
    #     self.write(self.device, 'polarity', state)
    #     return

    # @property
    # def frequency(self):
    #     return 1/self.period

    # @frequency.setter
    # def frequency(self, hertz):
    #     if hertz < 1:
    #         hertz = 1
    #     elif hertz > 10e6:
    #         hertz = 10e6
            
    #     self.period = 1.0/float(hertz)
    #     val = '{}'.format(int(self.period * 1e9))
    #     self.write(self.device, 'period', val)
    #     return

    # @property
    # def dutycycle(self):
    #     return self.active_time / self.period * 100

    # @dutycycle.setter
    # def dutycycle(self, percent):
    #     if percent < 0.0:
    #         percent = 0
    #     elif percent > 100.0:
    #         percent = 100.0
            
    #     nanoseconds = int(self.period * percent/100 * 1e9)
    #     self.active_time = nanoseconds
    #     val = '{}'.format(nanoseconds)
    #     self.write(self.device, 'duty_cycle', val)
    #     return

if __name__ == '__main__':
    import time

    # use the pwm class as a simple object
    pwm = PWM('ECAPPWM0')
    pwm.export()
    pwm.frequency = 1000000
    pwm.duty_cycle = 100000
    pwm.enable = True
    time.sleep(2)
    pwm.enable = False
    pwm.unexport()

    time.sleep(2)
    
    # use the pwm class as a context manager
    with PWM('ECAPPWM0') as pwm:
        pwm.frequency = 1000000
        pwm.duty_cycle = 100000
        pwm.enable = True
        time.sleep(2)
        
    #pwm.open()
    # pwm.is_inverted = False
    # pwm.dutycycle = 0
    # pwm.frequency = 1000
    # pwm.is_enabled = True
    # print 'pwm enabled = {}'.format(pwm.enabled)
        
    # pwm.dutycycle = 25.0
    # time.sleep(2)
    # pwm.dutycycle = 50.0
    # time.sleep(2)
    # pwm.dutycycle = 75.0
    # time.sleep(2)
    # pwm.dutycycle = 95.0
    # time.sleep(2)

    # # do clean up.
    # pwm.is_enabled = False
    # pwm.close()

    # time.sleep(1)

    # # use the pwm class as a context manager
    # with PWM('ECAPPWM0') as pwm:
    #     pwm.is_inverted = False
    #     pwm.dutycycle = 0
    #     pwm.frequency = 1000
    #     pwm.is_enabled = True
    #     print 'pwm enabled = {}'.format(pwm.enabled)
        
    #     pwm.dutycycle = 25.0
    #     time.sleep(2)
    #     pwm.dutycycle = 50.0
    #     time.sleep(2)
    #     pwm.dutycycle = 75.0
    #     time.sleep(2)
    #     pwm.dutycycle = 95.0
    #     time.sleep(2)
        
    # # try opening a non existent pwm resource 
    # with PWM('ECAPPWM1') as pwm:
    #     pwm.is_inverted = False

