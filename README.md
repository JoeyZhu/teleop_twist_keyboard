# teleop_twist_keyboard
Generic Keyboard Teleop for ROS.
added manual override control.
press d to publish cmd_vel on /cmd_vel_manual and request a service named /serial_bot_node/manual_cmd_srv for manual.
press a to publish on /cmd_vel.


#Launch
To run: `rosrun teleop_twist_keyboard teleop_twist_keyboard.py`

#Usage
```
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U    I    O
   J    K    L
   M    <    >

t : up (+z)
b : down (-z)

anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit
```

