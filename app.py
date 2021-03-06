'''

Web app to read a webform and control a stepper motor

'''

import RPi.GPIO as GPIO 	#import the gpio library
import time			#import the time library

#flask is a python web server
from flask import Flask, render_template, request  

#initiate the web server
app = Flask(__name__)

#sets the gpio to match the BCM number and not the physical pin number on the pin header
GPIO.setmode(GPIO.BCM)

#global variables
rpm = 0
revolutions = 0
direction = 1

enable_pin = 18		#GPIO 18 is connected to 1,2 EN and 3,4 EN of the L293D chip physical pins 1 and 9
coil_A_1_pin = 4	#GPIO 4 is connected to 1A pin of the L293D chip physical pin 2
coil_A_2_pin = 17	#GPIO 17 is connected to 2A pin of the L293D chip physical pin 7
coil_B_1_pin = 23	#GPIO 23 is connected to 3A pin of the L293D chip physical pin 10
coil_B_2_pin = 24	#GPIO 24 is connected to 4A pin of the L293D chip physical pin 15


#Configure the gpio pins as outputs
GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

def forward(delay, cycles):  
  for i in range(0, cycles):  #loop through the number of cycles
    setStep(1, 0, 1, 0)       #Step #1 turn on coil A forward and B forward
    time.sleep(delay)         #delay before turning on the next step in the sequence.
    setStep(0, 1, 1, 0)       #Step #2 turn on coil A reverse and B forward
    time.sleep(delay)         #delay before turning on the next step in the sequence.
    setStep(0, 1, 0, 1)       #Step #2 turn on coil A reverse and B reverse
    time.sleep(delay)         #delay before turning on the next step in the sequence.
    setStep(1, 0, 0, 1)       #Step #2 turn on coil A forward and B reverse
    time.sleep(delay)
 
def backwards(delay, steps):  
  for i in range(0, steps):
    setStep(1, 0, 0, 1)
    time.sleep(delay)
    setStep(0, 1, 0, 1)
    time.sleep(delay)
    setStep(0, 1, 1, 0)
    time.sleep(delay)
    setStep(1, 0, 1, 0)
    time.sleep(delay)
  
def setStep(w1, w2, w3, w4):      #Function to turn on the corresponding gpio pins
  GPIO.output(coil_A_1_pin, w1)   #Set the outputs accordingly
  GPIO.output(coil_A_2_pin, w2)   #.
  GPIO.output(coil_B_1_pin, w3)   #.
  GPIO.output(coil_B_2_pin, w4)   #.
 
def stepperGo(direction, delay, cycles):  #Function to initate the stepper motor in motion
  GPIO.output(enable_pin, 1)  #Bring the enable pin high to turn on the L293D motor driver chip

  #Direction is handled as a boolean value 1 is forward 0 is reverse
  if direction:
    forward(delay,cycles)  #if forward turn the motor forwards
  else:
    backwards(delay,cycles)#if backwards turn the motor forwards

  setStep(0,0,0,0)  # when the motor is finished turn off all coils.

  GPIO.output(enable_pin, 0) #turn off the L293D chip

@app.route("/")
def main():
   # if the browse is asking for "/" page return main.html to the browser
   return render_template('main.html')

# When the submit button is pushed on the webpage
@app.route("/submit", methods=['POST'])
def handle_data(): #get the data
   rpm = request.form.get('speed', default=0, type=int)  #get the input for speed
   revolutions = request.form.get('revs',default=0,type=int) #get the input for revolution
   direction = request.form.get('direction',default=1,type=int) #get the input for direction

   #delay = sec / step = 1 revolution / 200 steps * 60 sec / 1 minute * 1 minute / (RPM) revolutions
   #delay = 0.3 / RPM
   delay = 0.3 / rpm

   # there are 200 steps per revolution
   # each cycle is 4 steps => 50 cycles / revolution
   steps = int(revolutions * 50)

   #since the user input for direction is 1 or 0 we need create a string
   #to add to the output.  If direction = 1 then dirstr = forward 
   #otherwise dirstr = backwards
   dirstr=""
   if direction:
     dirstr = "forward"
   else:
     dirstr = "backwards"

   #out put a message that states what the motor is doing.
   print ("{0} @ {1} RPM for {2} cycles".format(dirstr, rpm,steps))

   #run the motor
   stepperGo(direction,delay,steps)

   #reload the main page
   return render_template('main.html')


#The only function of the main code is to start the server.
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)

