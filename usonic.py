#!/usr/bin/python
import time
import datetime
import RPi.GPIO as gpio


def get_arguments():  # Returns a dictionary of arguments, results can be None if required=False.
    import argparse
    parser = argparse.ArgumentParser(description='Records output of a HC-SRO4 sensor to a file.')
    parser.add_argument('-o', '--output', help='File to save output to.', required=True)
    parser.add_argument('-g', '--trigger', help='Number of the GPIO pin used for the trigger input.', required=True)
    parser.add_argument('-c', '--echo', help='Number of the GPIO pin used for the echo output.', required=True)
    parser.add_argument('-t', '--time', help='Duration to run program for. Default is never ending.', required=False)
    parser.add_argument('-r', '--rate', help='Amount of samples to take from sensor per second. Default is 1.',
                        required=False)
    parser.add_argument('-d', '--distance', help='Maximum detection distance in cm before timeout. Higher values'
                                                 'results in lower performance and potentially invalid results. Default'
                                                 'is 400cm.', required=False)
    parser.add_argument('-e', '--delay', help='Duration to wait before program runs. Default is 0.', required=False)
    parser.add_argument('-v', '--verbose', help='Display additional information.', action='store_true')
    args = vars(parser.parse_args())
    return args


def get_reading(max_distance, trig_pin, echo_pin):
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)

    gpio.setup(trig_pin, gpio.OUT)  # GPIO output = the pin that's connected to "Trig" on the sensor
    gpio.setup(echo_pin, gpio.IN)  # GPIO input = the pin that's connected to "Echo" on the sensor
    gpio.output(trig_pin, gpio.LOW)

    signal_off = 0.0
    signal_on = 0.0  # Initialise variables to reduce delay when recording

    # A pulse of length 10Us will trigger the sensor to transmit 8 cycles of ultrasonic waves at 40kHz
    gpio.output(trig_pin, True)
    time.sleep(0.000010)  # Wait 10 micro seconds
    gpio.output(trig_pin, False)

    start_time = time.time()
    while gpio.input(echo_pin) == 0:
        if (time.time() - start_time) * 17180.0 > max_distance:  # Defines max range. Default is 400cm.
            gpio.cleanup()
            return -1.0
    signal_off = time.time()

    while gpio.input(echo_pin) == 1:
        signal_on = time.time()

    time_passed = signal_on - signal_off
    distance = time_passed * 17180.0  # Distance = Time * Velocity. The Speed of sound in dry air is aprox. 343.6m/s
                                      # depending on temperature (assumed 20 celsius). The wave travels both ways so
                                      # this speed must be halved, giving 171.8m/s. Finally, multiply by 100 in order
                                      # to give the distance in cm.

    gpio.cleanup()
    if distance <= max_distance:
        return distance
    return -1.0


def append_data(output_filename, to_append):
    f = open(output_filename, 'a')
    f.write("{0}".format(to_append))
    f.close()


def main():
    args = get_arguments()
    # File Name to output data to
    output_filename = args['output']
    # GPIO pin numbers for the trigger and echo pins.
    trig_pin = int(args['trigger'])
    echo_pin = int(args['echo'])
    # Duration to run the sensor for (default is never ending, represented by a -1.
    run_time = -1  # Loop infinitely if not specified
    if args['time'] is not None:
        run_time = float(args['time'])
    # Maximum distance for the sensor to attempt to detect before a timeout is declared. In cm. Default 400cm.
    max_distance = 400.0
    if args['distance'] is not None:
        max_distance = float(args['distance'])
    # The delay that dictates the rate at which the sensor will be sampled. Currently does not account for sensor
    # delays. Default 1.
    rate_delay = 1.0
    if args['rate'] is not None:
        rate_delay = 1.0 / float(args['rate'])
    # The delay until the sensor starts running, for user convenience.
    if args['delay'] is not None:
        if args['verbose']:
            print("Beginning initial delay of {0} seconds".format(args['delay']))
        delay_end_time = time.time() + float(args['delay'])
        while time.time() < delay_end_time:
            time.sleep(0.05)  # Add a short delay to prevent an overly busy loop.
        if args['verbose']:
            print("Initial delay finished, beginning sensor I/O.")

    f = open(output_filename, 'w')  # Delete current contents of file
    f.close()
    start_time = time.time()
    while run_time == -1 or time.time() - start_time < run_time:
        curr_reading = get_reading(max_distance, trig_pin, echo_pin)
        time_stamp = datetime.datetime.now()
        if args['verbose']:
            if curr_reading != -1.0:
                print(curr_reading)
            else:
                print("Signal Timed out")
        append_data(output_filename, str(curr_reading) + ',' + str(time_stamp.year) + ',' + str(time_stamp.month) + ',' + str(time_stamp.day) + ',' + str(time_stamp.hour) + ',' + str(time_stamp.minute) + ',' + str(time_stamp.second) + ',' + str(time_stamp.microsecond) + '\n')
        time.sleep(rate_delay)

    if args['verbose']:
        print ("Finished running. Your output has been saved in the file '{0}'".format(output_filename))

main()
