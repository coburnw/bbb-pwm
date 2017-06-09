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

class PWM(object):
    def __init__(self, channelName):
        self.ecap_pwms = ('ECAPPWM0', 'ECAPPWM2')
        self.ehr_pwms = ('EHRPWM0A', 'EHRPWM0B', 'EHRPWM1A', 'EHRPWM1B', 'EHRPWM2A', 'EHRPWM2B')

        self.channels = {}
        self.channel_name = channelName
        self.channel = {}
        self.opened = False

        self.enabled = False
        self.inverted = False
        self.period = 10000000
        self.active_time = 0

        self.scan()
        return

    # allow using class as a context manager for more reliable cleanup
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    # build relationship between the pwm resource names and their sysfs filenames
    def scan(self):
        path = '/sys/class/pwm'
        chips = glob.glob('{}/pwmchip*'.format(path))
        ecap_index = 0
        ehr_index = 0
        for chip in chips:
            #print 'looking in: ' + '{}/npwm'.format(chip)
            npwm = int(open('{}/npwm'.format(chip)).read())
            if npwm == 1:
                if ecap_index == 0:
                    i = 0
                    chan_name = self.ecap_pwms[ecap_index]
                    self.channels[chan_name] = {'chip' : chip, 'port' : '{}'.format(0)}
                    chan = self.channels[chan_name]
                    #print ' (assigning {}/pwm{} to {})'.format(chan['chip'], chan['port'], chan_name)
                elif ecap_index == 1:
                    i = 2
                    chan_name = self.ecap_pwms[ecap_index]
                    self.channels[chan_name] = {'chip' : chip, 'port' : '{}'.format(0)}
                    chan = self.channels[chan_name]
                    #print ' (assigning {}/pwm{} to {})'.format(chan['chip'], chan['port'], chan_name)
                else:
                    pass
                ecap_index += 1
                #print
            elif npwm == 2:
                for i in [0, 1]:
                    chan_name = self.ehr_pwms[ehr_index+i]
                    self.channels[chan_name] = {'chip' : chip, 'port' : '{}'.format(i)}
                    chan = self.channels[chan_name]
                    #print ' (assigning {}/pwm{} to {})'.format(chan['chip'], chan['port'], chan_name)
                ehr_index += 2
                #print
            else:
                print '(unrecognized chip npwm count)'
        return

    def open(self):
        if not (self.channel_name in self.ecap_pwms) and not (self.channel_name in self.ehr_pwms):
            raise KeyError('Undefined key. Possible keys are: {}'.format(self.ecap_pwms+self.ehr_pwms))
        
        self.channel = self.channels[self.channel_name]
        #print '{}/export'.format(self.channel['chip']), self.channel['port']
        open('{}/export'.format(self.channel['chip']), 'w').write(self.channel['port'])
        self.opened = True
        return

    def close(self):
        if self.opened:
            self.is_enabled = False
            #print '{}/unexport'.format(self.channel['chip']), self.channel['port']
            open('{}/unexport'.format(self.channel['chip']), 'w').write(self.channel['port'])
        self.opened = False
        return

    def write(self, channel, command, value):
        #print '{}/pwm{}/{}'.format(self.channel['chip'], self.channel['port'], command), value
        open('{}/pwm{}/{}'.format(self.channel['chip'], self.channel['port'], command), 'w').write(value)

    @property
    def is_enabled(self):
        return self.enabled

    @is_enabled.setter 
    def is_enabled(self, boolean):
        self.enabled = boolean
        if self.enabled == True:
            state = '1'
        else:
            state = '0'
        self.write(self.channel, 'enable', state)
        return

    @property
    def is_inverted(self):
        return self.inverted

    @is_inverted.setter 
    def is_inverted(self, boolean):
        self.inverted = boolean
        if self.inverted == True:
            state = 'inversed'
        else:
            state = 'normal'
        self.write(self.channel, 'polarity', state)
        return

    @property
    def frequency(self):
        return 1/self.period

    @frequency.setter
    def frequency(self, hertz):
        if hertz < 1:
            hertz = 1
        elif hertz > 10e6:
            hertz = 10e6
            
        self.period = 1.0/float(hertz)
        val = '{}'.format(int(self.period * 1e9))
        self.write(self.channel, 'period', val)
        return

    @property
    def dutycycle(self):
        return self.active_time / self.period * 100

    @dutycycle.setter
    def dutycycle(self, percent):
        if percent < 0.0:
            percent = 0
        elif percent > 100.0:
            percent = 100.0
            
        nanoseconds = int(self.period * percent/100 * 1e9)
        self.active_time = nanoseconds
        val = '{}'.format(nanoseconds)
        self.write(self.channel, 'duty_cycle', val)
        return

if __name__ == '__main__':
    import time

    # use the pwm class as a simple object
    pwm = PWM('ECAPPWM0')
    pwm.open()
    pwm.is_inverted = False
    pwm.dutycycle = 0
    pwm.frequency = 1000
    pwm.is_enabled = True
    print 'pwm enabled = {}'.format(pwm.enabled)
        
    pwm.dutycycle = 25.0
    time.sleep(2)
    pwm.dutycycle = 50.0
    time.sleep(2)
    pwm.dutycycle = 75.0
    time.sleep(2)
    pwm.dutycycle = 95.0
    time.sleep(2)

    # do clean up.
    pwm.is_enabled = False
    pwm.close()

    time.sleep(1)

    # use the pwm class as a context manager
    with PWM('ECAPPWM0') as pwm:
        pwm.is_inverted = False
        pwm.dutycycle = 0
        pwm.frequency = 1000
        pwm.is_enabled = True
        print 'pwm enabled = {}'.format(pwm.enabled)
        
        pwm.dutycycle = 25.0
        time.sleep(2)
        pwm.dutycycle = 50.0
        time.sleep(2)
        pwm.dutycycle = 75.0
        time.sleep(2)
        pwm.dutycycle = 95.0
        time.sleep(2)
        
    # try opening a non existent pwm resource 
    with PWM('ECAPPWM1') as pwm:
        pwm.is_inverted = False

