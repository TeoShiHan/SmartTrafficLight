import asyncio
from TrafficLight import *
from Firebase import Firebase

ORDER = ["GREEN001", "RED001", "RED002"]
ID = "TL002"

redLight = 2
yellowLight = 3
greenLight = 4

checkRed = 5
checkYellow = 6
checkGreen = 7

TL = TrafficLight(ID, redLight, yellowLight, greenLight, checkRed, checkYellow, checkGreen)


class EventListener:
    @staticmethod
    async def listen_switch_event():
        switch_instruction = await listen_switch()
        return switch_instruction


async def listen_switch():
    return fb.read_one(f"Server/Event/Switch/{ID}")


class EventAck(object):
    @staticmethod
    async def ack_switch_event():
        await EventAck.send_switch_ack()

    @staticmethod
    async def send_switch_ack():
        fb.update("Server/Event/Switch", {ID: "SWITCH ACK"})


fb = Firebase()
e = EventListener
ack = EventAck


def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key

    return "key doesn't exist"


current_display = get_key(ID, fb.access_by_path("Server/Order"))


async def sleepHalfSec():
    await asyncio.sleep(0.5)


async def main():
    light_time = 10
    indicating_display(light_time)
    while True:

        sleepTask = asyncio.create_task(sleepHalfSec())
        switchEvent = asyncio.create_task(e.listen_switch_event())
        await asyncio.gather(sleepTask, switchEvent)

        switch = switchEvent.result()

        if switch == "SWITCH" and current_display == "GREEN001":
            print("Turning yellow..........")
            yellowTask = asyncio.create_task(yellow_transition())
            yellow_check = asyncio.create_task(check_yellow_light())
            ackTask = asyncio.create_task(ack.ack_switch_event())

            yellow_functioning = await asyncio.gather(yellowTask, ackTask, yellow_check)

            switch_to_next_order(ORDER.index(current_display))

            if yellow_functioning:
                indicating_display(light_time)
            else:
                TL.traffic_light_down()

        elif switch == "SWITCH" and current_display != "GREEN001":
            redTask = asyncio.create_task(red_transition())
            ackTask = asyncio.create_task(ack.ack_switch_event())
            await asyncio.gather(redTask, ackTask)
            switch_to_next_order(ORDER.index(current_display))
            indicating_display(light_time)

        else:
            pass


async def yellow_transition():
    TL.yellowLight.turn_on()
    await asyncio.sleep(5)
    TL.yellowLight.turn_off()


async def check_yellow_light():
    count = 0
    for loop_count in range(5):
        await asyncio.sleep(0.00001)
        yellow_condition = TL.checkYellow.get_status()
        if yellow_condition == 1:
            TL.report_faulty_yellow()
            return False
        else:
            print("Yellow LED light is functioning")
            if count < 1:
                TL.yellow_light_fixed()
        await asyncio.sleep(1)
    return True


async def red_transition():
    await asyncio.sleep(5)


def switch_to_next_order(current_index):
    global current_display
    if current_index == 0 or current_index == 1:
        next_index = current_index + 1
    else:
        next_index = 0
    current_display = ORDER[next_index]


def indicating_display(light_time):
    if current_display == "GREEN001":
        green_task = asyncio.create_task(green_on_off(light_time))
        green_check = asyncio.create_task(check_green_light(light_time))
        await asyncio.gather(green_task, green_check)
    else:
        red_task = asyncio.create_task(red_on_off(light_time))
        red_check = asyncio.create_task(check_red_light(light_time))
        await asyncio.gather(red_task, red_check)


async def green_on_off(green_time):
    TL.greenLight.turn_on()
    await asyncio.sleep(green_time)
    TL.greenLight.turn_off()


async def check_green_light(green_time):
    count = 0
    for loop_count in range(math.floor(green_time)):
        await asyncio.sleep(0.00001)
        green_condition = TL.checkGreen.get_status()
        if green_condition == 1:
            TL.report_faulty_green()
            return False
        else:
            print("Green LED light is functioning")
            if count < 1:
                TL.green_light_fixed()
        await asyncio.sleep(1)
    return True


async def red_on_off(red_time):
    TL.redLight.turn_on()
    await asyncio.sleep(red_time)
    TL.redLight.turn_off()


async def check_red_light(red_time):
    count = 0
    for loop_count in range(math.floor(red_time)):
        await asyncio.sleep(0.00001)
        red_condition = TL.checkRed.get_status()
        if red_condition == 1:
            TL.report_faulty_red()
            return False
        else:
            print("Red LED light is functioning")
            if count < 1:
                TL.red_light_fixed()
        await asyncio.sleep(1)
    return True

asyncio.run(main())
