# bbb-pwm
python pwm for the beaglebone black

This PWM library overrides the hardware specifics of pwmpy to allow its use with the BeagleBone Black.

On BBB, the PWM related sysfs filenames in version 4.4 of the linux kernel (and others?) can sometimes change
after reboot.  This library sorts the filenames out and allows access to the pwm devices with pwmpy using
device names rather than the chip/channel definitions.

The little snippit of code that adapts to the shifting filenames is thanks to samual.bucquet.
The rest is just dressing.

dependencies: Scott's [pwmpy](https://github.com/scottellis/pwmpy) which sysfs interface

installation:
 * copy pmwpy.py to your work folder.
 * copy bbb_pwm.py to your work folder.

two methods of use are:
 * as a class
     import bbb_pwm
     pwm = bbb_pwm.PWM("EHRPWM0A")
   The user mananges the opening and closing of the resource and handles any events appropriately
   to ensure the pwm device is left in the state desired on program exit.
 * as a context handler
     import bbb_pwm
     with bbb_pwm.PWM("EHRPWM0A") as pwm:
   The context manager handles the opening and closing of the resource and makes a best effort
   to cleanup/shutdown any pwm resources used.

If the user either doesnt care or intends that the pwm is left running after program exit, then used as a
simple class may be appropriate.  Otherwise, use as a context handler to ensure pwm's are off and unexported if an
exception should happen to trickle to the top.

caveat: this library assumes that altho the pwmchip file suffix values may change, the order of the pwmchip
filenames does not.

see cape expansion [headers](http://elinux.org/Beagleboard:Cape_Expansion_Headers#8_PWMs_and_4_Timers) for pwm device names.

TODO:
 * verify caveat assumption is a safe assumption.
  