# bbb-pwm
python pwm for the beaglebone black

This BBB PWM library can work with the changing pwmchip filenames that can occur after
reboot with version 4.4 of the kernel.  The little snippit of code that adapts to the
shifting filenames is thanks to samual.bucquet.  The rest is just dressing.

caveat: this library assumes that only the pwmchip file suffix value changes, not the order of the filenames.

TODO:
 * get access to the two remaining pwm channels
 * add a dictionary to map pins to resources and to allow opening by pin-name or resource-name.
 * verify caveat.
  