
# marsmode-mediavolume
# - media volume, based off tesla clock ticks instead of blind sleep timer

import binascii
import time
from datetime import datetime
from panda import Panda

p = Panda()

p.set_can_speed_kbps(0,500)
p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
step_count = 0
while True:
	try:
		can_recv = p.can_recv()
		for address, _, dat, _ in can_recv:
			if address == 0x528:
				step_count = step_count + 1
				car_clock = datetime.fromtimestamp(int(binascii.hexlify(dat),16))
				print("Car Clock: ", car_clock)
				if step_count == 7:
					p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
				if step_count == 8:
					p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
					print("sent event")
					step_count = 0
	except Exception as e:
		print("Exception caught ",e)
		time.sleep(3.2)
