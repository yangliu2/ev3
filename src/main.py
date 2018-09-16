#!/usr/bin/env python3
from ev3dev import ev3
import sys
import time
import threading
import signal 

say = lambda sentence: ev3.Sound.speak(sentence)

def play_starwar_beginning():
    ev3.Sound.play_song((
        ('D4', 'e3'),      # intro anacrouse
        ('D4', 'e3'),
        ('D4', 'e3'),
        ('G4', 'h'),       # meas 1
        ('D5', 'h'),
        ('C5', 'e3'),      # meas 2
        ('B4', 'e3'),
        ('A4', 'e3'),
        ('G5', 'h'),
        ('D5', 'q'),
        ('C5', 'e3'),      # meas 3
        ('B4', 'e3'),
        ('A4', 'e3'),
        ('G5', 'h'),
        ('D5', 'q'),
        ('C5', 'e3'),      # meas 4
        ('B4', 'e3'),
        ('C5', 'e3'),
        ('A4', 'h.')
    ))

def signal_handler(signal, frame):
    done.set()

def move(done):
    lm = ev3.LargeMotor('outB'); assert lm.connected
    
    rm = ev3.LargeMotor('outC'); assert rm.connected
    
    cl = ev3.ColorSensor(); assert cl.connected
    cl.mode='COL-AMBIENT'
    
    speed = -250 #cl.value() is too low

    lm.run_forever(speed_sp=speed)
    rm.run_forever(speed_sp=speed)

    while not done.is_set():
        time.sleep(1)  
    
    #stop both motors
    lm.stop(stop_action='brake')
    rm.stop(stop_action='brake')
    lm.wait_while('running')
    rm.wait_while('running')
    
    #run around in a circle
    done.clear()
    lm.run_forever(speed_sp=speed)
    
    while not done.is_set():
        time.sleep(1)
        
    lm.stop(stop_action='brake')
    lm.wait_while('running')

def feel(done):
    ir = ev3.InfraredSensor(); assert ir.connected
    ts = ev3.TouchSensor(); assert ts.connected

    screen = ev3.Screen()
    sound = ev3.Sound()

    screen.draw.text((60,40), 'Going for a walk')
    screen.update()

    while ir.proximity > 30:
        if done.is_set(): 
            break
        time.sleep(0.1)

    done.set() #this will set it running in a circle
    
    ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.RED)
    ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.RED)
    
    screen.clear()
    screen.draw.text((60,20), 'There is something is front of me')
    screen.update()
    
    while not ts.is_pressed:
        sound.speak("Where should I go next?").wait()
        time.sleep(0.5)
    
    done.set() #will stop the circle dance

def walk_then_circle():
    
    done = threading.Event()
    signal.signal(signal.SIGINT,  signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Now that we have the worker functions defined, lets run those in separate
    # threads.
    move_thread = threading.Thread(target=move, args=(done,))
    feel_thread = threading.Thread(target=feel, args=(done,))

    move_thread.start()
    feel_thread.start()

    # The main thread will wait for the 'back' button to be pressed.  When that
    # happens, it will signal the worker threads to stop and wait for their completion.
    btn = ev3.Button()
    while not btn.backspace and not done.is_set():
        time.sleep(1)

    done.set()
    move_thread.join()
    feel_thread.join()  

    ev3.Sound.speak('Farewell and good bye!').wait()
    ev3.Leds.all_off()

def load_button_echo():

    btn = ev3.Button()

    def left(state):
        say('Left button {0}'.format('pressed' if state else 'released'))
        
    def right(state):
        say('Right button {0}'.format('pressed' if state else 'released'))
        
    def up(state):
        say('Up button {0}'.format('pressed' if state else 'released'))
        
    def down(state):
        say('Down button {0}'.format('pressed' if state else 'released'))
        
    def enter(state):
        say('Enter button {0}'.format('pressed' if state else 'released'))
        
    def backspace(state):
        say('Backspace button {0}'.format('pressed' if state else 'released'))

    btn.on_left = left
    btn.on_right = right
    btn.on_up = up
    btn.on_down = down
    btn.on_enter = enter
    btn.on_backspace = backspace

    while True:
        #Check for currenly pressed buttons. 
        #If the new state differs from the old state, 
        #call the appropriate button event handlers.
        btn.process()

        #exit if both the left and right buttons are pressed simultaneously
        if btn.check_buttons(buttons=['left','right']):
            break
        time.sleep(0.1)

def touch_sensor_setup():
    ts = ev3.TouchSensor()
    say("Touch sensor activated.")
    while True:
        if ts.is_pressed:
            say("Ouch!")
        time.sleep(0.5)

def color_sensor():
    #WORKING TO COLOR SENSOR:

    ts = ev3.TouchSensor()

    cl = ev3.ColorSensor()
    cl.mode = 'COL-COLOR' #returns an integer [0,7]
    #cl.mode='COL-REFLECT' #measures reflected light intensity and returns an integer [0,100]
    #cl.mode='COL-AMBIENT' #measures ambient light intensity and returns an integer [0,100]
    #cl.mode='RGB-RAW' #returns RGB tuple ([0,1020], [0,1020], [0,1020])

    colors = ('unknown black blue green yellow red white brown'.split())

    while not ts.value():
        ev3.Sound.speak(colors[cl.value()]).wait()
        time.sleep(1)

def rotate_head(degree):
    '''
    degree: 
        positive number is left
        negative number is right
    with speed_sp as 100, there are 140 position_sp available for the head
    '''
    #WORKING WITH MEDIUM MOTOR:

    mm = ev3.MediumMotor()

    #shoot a ball in the specified direction
    #speed_sp recommended range is [-1400, 1400]

    mm.run_to_rel_pos(speed_sp=100, position_sp=degree)

def setup():
    load_button_echo()
    touch_sensor_setup()

def main():
    setup()
    # color_sensor()
    
    # play_starwar_beginning()
    # ev3.Sound.play('sound/imperial_march.wav').wait()
    
    # walk_then_circle()
    

    


if __name__ == '__main__':
    main()