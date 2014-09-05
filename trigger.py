#!/usr/bin/python
import time
import RPi.GPIO as gpio


def get_arguments():  # Returns a dictionary of arguments, results can be None if required=False.
    import argparse
    parser = argparse.ArgumentParser(description='Turn the trigger pin on for a sensor.')
    parser.add_argument('-g', '--trigger', help='Number of the GPIO pin used for the trigger input.', required=True)
    parser.add_argument('-t', '--time', help='Duration to send the HIGH signal to the trigger pin, in seconds. Default'
                                             'is 0.000010', required=False)
    parser.add_argument('-l', '--loop', help='Loop infinitely.', action='store_true')
    parser.add_argument('-d', '--delay', help='Delay between triggers, in seconds. Only works while looping (-l)',
                        required=False)
    args = vars(parser.parse_args())
    return args


def trigger_output(trig_pin, time_on):
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)

    gpio.setup(trig_pin, gpio.OUT)  # GPIO output = the pin that's connected to "Trig" on the sensor
    gpio.output(trig_pin, gpio.LOW)

    # A pulse of length 10Us will trigger the sensor to transmit 8 cycles of ultrasonic waves at 40kHz
    gpio.output(trig_pin, True)
    time.sleep(time_on)
    gpio.output(trig_pin, False)

    gpio.cleanup()


def main():
    args = get_arguments()
    # File Name to output data to
    trig_pin = int(args['trigger'])
    # Duration to have pin on (default 10us)
    time_on = 0.000010
    if args['time'] is not None:
        time_on = float(args['time'])
    delay = 0.0
    if args['delay'] is not None:
        delay = float(args['delay'])

    while True:
        print("Pin on...")
        trigger_output(trig_pin, time_on)
        print("Pin off.")
        if not args['loop']:
            break
        time.sleep(delay)
    print("Finished.")


main()
