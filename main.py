#esptool.py --port /dev/ttyUSB0 erase_flash
#esptool.py --port /dev/ttyUSB0 --chip esp32 write_flash -z 0x1000 /home/tc/Downloads/esp32-20181118-v1.9.4-684-g51482ba92.bin
#shell --buffer-size=30 -p /dev/ttyUSB0
#cp /home/ingres/Desktop/morse.py /pyboard
import morse
import machine

# Globals
# Where is the Microphone connected?
adcpin = 36
# Where is the button connected
inputbuttonpin = 0
# How much above normal loudness level is a beep?
minloudness = 150

def stophearing(pin):
    # Setting this to zero will stop the haring of the class
    mymorse.hearingactive = 0

btn1 = machine.Pin(inputbuttonpin, machine.Pin.IN, machine.Pin.PULL_UP)
btn1.irq(trigger=machine.Pin.IRQ_RISING, handler = stophearing)        

mymorse = morse.Morse(adcpin, minloudness)
mymorse.hearformorse()
mymorse.decodeintomorse()
mymorse.decodemorseintotext()
