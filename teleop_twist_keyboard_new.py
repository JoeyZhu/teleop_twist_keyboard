#!/usr/bin/env python
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty
import std_srvs.srv
from stateswitch.srv import *


def enum(**enums):
    return type('Enum', (), enums)

STATE_SIGNAL = enum(NULL=0, BOOTED=1, CHARGED_ABOVE_CRITICAL=6, DISABLE_MANUAL=7, \
ERROR_CLEARED=8, DOCK_SUCCESS=9, GO_2_BASE=10, ENABLE_MANUAL=11, ERROR_SIGNAL=12, FULL_MANUAL=13)
TASK_SIGNAL = enum(NULL=0, START_FOLLOW=3, PAUSE_TASK=6, CLEAR_TASK=7, RESUME_TASK=8, STOP_FOLLOW=9)

msg = """
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

#t : up (+z)
#b : down (-z)

anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
a/d : auto / manual control
E/r : send Error/ Clear Error state signal
default control mode: automatic

CTRL-C to quit
shift-B to start robot
"""

moveBindings = {
		'i':(1,0,0,0),
		'o':(1,0,0,-1),
		'j':(0,0,0,1),
		'l':(0,0,0,-1),
		'u':(1,0,0,1),
		',':(-1,0,0,0),
		'.':(-1,0,0,1),
		'm':(-1,0,0,-1),
		'O':(1,-1,0,0),
		'I':(1,0,0,0),
		'J':(0,1,0,0),
		'L':(0,-1,0,0),
		'U':(1,1,0,0),
		'<':(-1,0,0,0),
		'>':(-1,-1,0,0),
		'M':(-1,1,0,0),
		# 't':(0,0,1,0),
		# 'b':(0,0,-1,0),
	       }

speedBindings={
		'q':(1.1,1.1),
		'z':(.9,.9),
		'w':(1.1,1),
		'x':(.9,1),
		'e':(1,1.1),
		'c':(1,.9),
	      }
#bot control service client
def manual_cmd_client(x):
    rospy.wait_for_service('/manual_cmd_srv', timeout=5)
    try:
        manual_cmd_srv = rospy.ServiceProxy('/manual_cmd_srv',std_srvs.srv.SetBool())
        ret = manual_cmd_srv(x)
    except rospy.ServiceException, e_bot:
        print "Service call failed: %s"%e_bot
    return ret

def send_state_signal(signal):
    rospy.wait_for_service('/state_signal', timeout = 10)
    try:
    	state_signal_srv = rospy.ServiceProxy('/state_signal',state_signal)
    	ret = state_signal_srv(signal)
    except rospy.ServiceException, e:
    	print "Service call failed: %s"%e
    return ret

def send_task_signal(signal):
    rospy.wait_for_service('/robot_task_signal', timeout = 10)
    try:
    	task_signal_srv = rospy.ServiceProxy('/robot_task_signal',state_signal)
    	ret = task_signal_srv(signal)
    except rospy.ServiceException, e:
    	print "Service call failed: %s"%e
    return ret


def getKey():
	tty.setraw(sys.stdin.fileno())
	select.select([sys.stdin], [], [], 0)
	key = sys.stdin.read(1)
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	return key


def vels(speed,turn):
	return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    	settings = termios.tcgetattr(sys.stdin)
	
	pub = rospy.Publisher('cmd_vel_raw', Twist, queue_size = 1)
	rospy.init_node('teleop_twist_keyboard')

	speed = rospy.get_param("~speed", 0.5)
	turn = rospy.get_param("~turn", 1.0)
	x = 0
	y = 0
	z = 0
	th = 0
	status = 0
	try:
		print msg
		print vels(speed,turn)
		while(1):
			key = getKey()

			if key in moveBindings.keys():
				x = moveBindings[key][0]
				y = moveBindings[key][1]
				z = moveBindings[key][2]
				th = moveBindings[key][3]
			elif key in speedBindings.keys():
				speed = speed * speedBindings[key][0]
				turn = turn * speedBindings[key][1]

				print vels(speed,turn)
				if (status == 14):
					print msg
				status = (status + 1) % 15
			else:
				x = 0
				y = 0
				z = 0
				th = 0
	
				# state signal
				if (key == 'B'):
					ret = send_state_signal(STATE_SIGNAL.BOOTED)
					if(ret.feedback == 0):
						print "send BOOTED state signal succeed!"
				elif (key == 'h'):
					ret = send_state_signal(STATE_SIGNAL.CHARGED_ABOVE_CRITICAL)
					if(ret.feedback == 0):
						print "send CHARGED_ABOVE_CRITICAL state signal succeed!"
				elif (key == 'a'):
					ret = send_state_signal(STATE_SIGNAL.DISABLE_MANUAL)
					if(ret.feedback == 0):
						print "send DISABLE_MANUAL state signal succeed!"
				elif (key == 'r'):
					ret = send_state_signal(STATE_SIGNAL.ERROR_CLEARED)
					if(ret.feedback == 0):
						print "send error clear state signal succeed!"
				elif (key == 'D'):
					ret = send_state_signal(STATE_SIGNAL.DOCK_SUCCESS)
					if(ret.feedback == 0):
						print "send DOCK_SUCCESS state signal succeed!"
				elif (key == 'b'):
					ret = send_state_signal(STATE_SIGNAL.GO_2_BASE)
					if(ret.feedback == 0):
						print "send GO_2_BASE state signal succeed!"
				elif (key == 'd'):
					ret = send_task_signal(TASK_SIGNAL.PAUSE_TASK)
					ret = send_state_signal(STATE_SIGNAL.ENABLE_MANUAL)
					if(ret.feedback == 0):
						print "send ENABLE_MANUAL state signal succeed!"
				elif (key == 'E'):
					ret = send_state_signal(STATE_SIGNAL.ERROR_SIGNAL)
					if(ret.feedback == 0):
						print "send error state signal succeed!"
				elif (key == 'F'):
					ret = send_state_signal(STATE_SIGNAL.FULL_MANUAL)
					if(ret.feedback == 0):
						print "send FULL_MANUAL state signal succeed!"
				# task signal
				elif (key == 'A'):
					ret = send_task_signal(TASK_SIGNAL.PAUSE_TASK)
					if(ret.feedback == 0):
						print "send PAUSE TASK signal succeed!"
					else:
						print "send PAUSE TASK signal failed!"
				elif (key == 'T'):
					ret = send_task_signal(TASK_SIGNAL.CLEAR_TASK)
					if(ret.feedback == 0):
						print "send CLEAR_TASK signal succeed!"	
					else:
						print "send CLEAR_TASK signal failed!"
				elif (key == 'R'):
					ret = send_task_signal(TASK_SIGNAL.RESUME_TASK)
					if(ret.feedback == 0):
						print "send RESUME TASK signal succeed!"
				elif (key == 'f'):
					ret = send_task_signal(TASK_SIGNAL.START_FOLLOW)
					if(ret.feedback == 0):
						print "send START_FOLLOW TASK signal succeed!"
				elif (key == 's'):
					ret = send_task_signal(TASK_SIGNAL.STOP_FOLLOW)
					if(ret.feedback == 0):
						print "send STOP_FOLLOW TASK signal succeed!"
				elif (key == '\x1B'):
					break

			twist = Twist()
			twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = z*speed;
			twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
    			pub.publish(twist)
	except:
		print e

	finally:
		twist = Twist()
		twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
		twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
		pub.publish(twist)

    		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


