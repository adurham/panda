# Mars Mode Advanced
# ================================================================================
# - starts enabled by default
# - starts in media-volume mode
# - press pause,pause (left scroll wheel button press) to enable/disable
# - press back,back (left scroll wheel tilt left) to cycle mode
# - mode order: volume down/up, speed down/up, media back button (for Streaming audio app)
# - disables when vehicle is placed in park

import binascii
import time
import random
from panda import Panda

p = Panda()

p.set_can_speed_kbps(0,500)
p.set_safety_mode(Panda.SAFETY_SILENT)

step_count = 0
mode_enabled = 1
mode_signal = 0
boot_init = 0
parked = 0

last_lt = 0
last_rt = 0

print("panda connected")

while True:
    try:
        can_data = p.can_recv()
        for ev_id, _, ev_data, _ in can_data:
            if ev_id == 0x528: # tesla clock tick 1s
                # display startup sequence on first tick detect after boot
                if boot_init == 0:
                    boot_init = 1
                    p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

                    # flag startup with speed adjust
                    p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                    time.sleep(0.5)
                    p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
                    time.sleep(0.5)
                    p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                    time.sleep(0.5)
                    p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
                    time.sleep(0.5)

                    p.set_safety_mode(Panda.SAFETY_SILENT)

                # now standard tickle when enabled
                if mode_enabled == 1:
                    step_count = step_count + 1
                    if step_count >= 5:
                        step_count = 0
                        time.sleep(random.uniform(0,2))
                        if mode_signal == 0:
                            print("- media vol signals SENT")
                            p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                            time.sleep(0.3)
                            p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
                        elif mode_signal == 1:
                            print("- speed signal SENT")
                            p.can_send(0x3c2,b"\x29\x55\x00\x3f\x00\x00\x00\x00",0) # speed down
                            time.sleep(0.3)
                            p.can_send(0x3c2,b"\x29\x55\x00\x01\x00\x00\x00\x00",0) # speed up
                        else:
                            print("- media back signal SENT")
                            p.can_send(0x3c2,b"\x29\x95\x00\x00\x00\x00\x00\x00",0) # media back

            # check for steering wheel control inputs
            elif ev_id == 0x3c2:
                # evd = ev_data.hex()
                #if evd == "4955000000000000": # play/pause
                if ev_data[0]==0x49 and ev_data[1]==0x55:
                    print("- play/pause detected")
                    step_count = 0
                    delta_lt = time.time() - last_lt
                    if delta_lt < 0.75 and delta_lt > 0.20:
                        # double tap detected, swap mode
                        print("- double tap detected ", delta_lt)
                        if mode_enabled == 0:
                            # start things up
                            print("--> ACTIVATING")
                            mode_enabled = 1
                            p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
    
                            # flag startup with speed adjust
                            p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                            time.sleep(0.5)
                            p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
    
                        else:
                            # shut things down
                            print("--> DEACTIVATING")
                            mode_enabled = 0
                            p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
                            time.sleep(0.5)
                            p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                            time.sleep(0.5)
                            p.set_safety_mode(Panda.SAFETY_SILENT)
                    else:
                        print("- lt single click, ", delta_lt)
                        last_lt = time.time()


                # check for mode swap with right thumb button double click
                # elif ev_data.hex() == "2965000000000000":
                # check for mode swap with left thumb tilt left double click
                # elif evd == "2995000000000000":
                elif ev_data[0]==0x29 and ev_data[1]==0x95:
                    print("- rt detected")
                    step_count = 0
                    delta_rt = time.time() - last_rt
                    if delta_rt < 0.75 and delta_rt > 0.20:
                        # double tap detected, swap mode
                        last_rt = 0
                        mode_signal = (mode_signal + 1)%3
                        print("--> MODE SWAP to ",mode_signal)

                        if mode_enabled == 0:
                            p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
    
                        # flag change with vol adjust
                        p.can_send(0x3c2,b"\x29\x55\x3f\x00\x00\x00\x00\x00",0) # vol down
                        time.sleep(0.5)
                        p.can_send(0x3c2,b"\x29\x55\x01\x00\x00\x00\x00\x00",0) # vol up
                        time.sleep(0.5)
    
                        if mode_enabled == 0:
                            p.set_safety_mode(Panda.SAFETY_SILENT)

                    else:
                        print("- rt single click, ", delta_rt)
                        last_rt = time.time()

            # check for putting vehicle in park, auto-disable
            elif ev_id == 0x118:
                # print("gear ",ev_data[2]," ",bin(ev_data[2]))
                if ev_data[2]==50:
                    if parked == 0:
                        parked = 1
                        print("Changing to PARK mode")
                        if mode_enabled == 1:
                            p.set_safety_mode(Panda.SAFETY_SILENT)
                else:
                    if parked == 1:
                        parked = 0
                        print("Changing to NON-PARK mode")
                        if mode_enabled == 1:
                            p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

    
    except Exception as e:
        print("Exception caught ",e)
        time.sleep(1.2)
            
