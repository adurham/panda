# marsmode-mediaback
# - uses media back (left scroll wheel tilt left)
# - only use with Streaming app (no back funcion)
# - NOT COMPATIBLE with other music audio sources that use the back button
# - No on-screen indications (discrete)
# - Based on tesla clock ticks (won't activate if not proper tesla CAN communication)
import binascii
import time
from panda import Panda

p = Panda()

p.set_can_speed_kbps(0,500)
p.set_can_speed_kbps(1,500)
p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

step_count = 0

while True:
	try:
		can_data = p.can_recv()
		for ev_id, _, ev_data, _ in can_data:
			if ev_id == 0x528: # clock tick 1s
				step_count = step_count + 1
				if step_count == 5:
					p.can_send(0x3c2,b"\x29\x95\x00\x00\x00\x00\x00\x00",0) # media back
					step_count = 0
	except Exception as e:
		print("Exception caught ",e)
		time.sleep(1.2)"

		# reset panda device or crash out for libusb
		p = Panda()

		p.set_can_speed_kbps(0,500)
		p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
