#!/usr/bin/env python2.7
# script by Alex Eames http://RasPi.tv/
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio
import RPi.GPIO as GPIO
import pygame
import pygame.camera
import picamera
import time
import string
import smtplib
 
# For guessing MIME type
import mimetypes
 
# Import the email modules we'll need
import email
import email.mime.application
 
#Import sys to deal with command line arguments
import sys
 
from pygame.locals import *

# Create a text/plain message
msg = email.mime.Multipart.MIMEMultipart()
msg['Subject'] = 'Picture of visitor at the door'
msg['From'] = "your-email-address@gmail.com"
msg['To'] = "your-email-address@gmail.com"
 
# The main body is just another attachment
body = email.mime.Text.MIMEText("""Somebody's at the door (sent from your doorbell operated by RPi)""")
msg.attach(body)
 
pygame.init()
pygame.camera.init()

GPIO.setmode(GPIO.BCM)

# GPIO 23 set up as input. It is pulled up to stop false signals
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

In=1
w = 640
h = 480
size=(w,h)
c = pygame.time.Clock() # create a clock object for timing

##print "Make sure you have a button connected so that when pressed"
##print "it will connect GPIO port 23 (pin 16) to GND (pin 6)\n"
##raw_input("Press Enter when ready\n>")
##
##print "Waiting for falling edge on port 23"
# now the program will do nothing until the signal on port 23 
# starts to fall towards zero. This is why we used the pullup
# to keep the signal high and prevent a false interrupt

##print "Press your button when ready to initiate a falling edge interrupt."
##
try:
    with picamera.PiCamera() as camera:
        while True:
##print "During this waiting time, your computer is not" 
##print "wasting resources by polling for a button press.\n"
            GPIO.wait_for_edge(23, GPIO.FALLING)

            filename = str(In)+".jpg" # ensure filename is correct
            In += 1

            camera.start_preview()
            time.sleep(5)
            camera.capture(filename)
            camera.stop_preview()
                
            screen = pygame.display.set_mode(size) 
            img=pygame.image.load(filename) 
            screen.blit(img,(0,0))
            pygame.display.flip() # update the display
            c.tick(3) # only three images per second

            # Extract the file format (pdf, epub, docx...)             
            spl_type=filename.split('.')             
            type=spl_type[len(spl_type)-1]
             
            fp=open(filename,'rb')
            att = email.mime.application.MIMEApplication(fp.read(),_subtype=type)
            fp.close()
            att.add_header('Content-Disposition','attachment',filename=filename)
            msg.attach(att)
             
            s = smtplib.SMTP('smtp.gmail.com:587')
            s.starttls()
# NOTE: you may need to get a special authentication password for this device - for gmail you will need it.
            s.login("your-login@gmail.com", "special authenticated App password")
            s.sendmail(msg['From'],msg['To'], msg.as_string())
            s.quit()

except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
#GPIO.cleanup()           # clean up GPIO on normal exit

