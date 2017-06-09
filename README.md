# bbb-pwm
python pwm for the beaglebone black

This BBB PWM library for interacting with the pwm resources using the linux sysfs interface can adapt to
the changing pwmchip filenames that sometimes occur after reboot with version 4.4 of the kernel.
The little snippit of code that adapts to the shifting filenames is thanks to samual.bucquet.
The rest is just dressing.

two methods of use are:
 * as a class
   'pwm = PWM("EHRPWM0A")'
   The user mananges the opening and closing of the resource and handles any events appropriately
   to ensure the pwm device is left in the state desired on program exit.
 * as a context handler
   'with PWM("EHRPWM0A") as pwm:'
   The context manager handles the opening and closing of the resource and makes a best effort
   to cleanup/shutdown any pwm resources used.

If the user either doesnt care or intends that the pwm is left running after program exit, then used as a
simple class may be appropriate.  Otherwise, use as a context handler to ensure pwm's are off and unexported if an
unhandled exception should trickle to the top.

caveat: this library assumes that altho the pwmchip file suffix value may change, the order of the pwmchip
filenames does not.

TODO:
 * consider porting to [pwmpy](https://github.com/scottellis/pwmpy) interface, then overloading only bbb specific functions.
 * verify caveat assumption is a safe assumption.
  