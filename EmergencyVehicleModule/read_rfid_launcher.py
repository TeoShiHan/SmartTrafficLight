from FakeDevices import *
import logging

log = logging.getLogger (__name__)

try:
    gui = Gui()
    gui.add(MifareRfid('testcards.json'))
    from EmergencyVehicleModule.read_rfid import *

except:
    log.exception('------------log-----------')
    
gui.quit()
print('Program terminated')
