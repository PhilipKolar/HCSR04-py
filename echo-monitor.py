#!/usr/bin/python
import time
import RPi.GPIO as gpio


def get_arguments():  # Returns a dictionary of arguments, results can be None if required=False.
    import argparse
    parser = argparse.ArgumentParser(description='Monitor the echo pin for changes in output and the precise time any'
                                                 'changes happen.')
    parser.add_argument('-e', '--echo', help='Number of the GPIO pin used for the echo output.', required=True)
    args = vars(parser.parse_args())
    return args


def main():
    args = get_arguments()
    echo_pin = int(args['echo'])

    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(echo_pin, gpio.IN)
    curr_status = gpio.input(echo_pin)
    state_time = time.time()
    print("{0} - {1}".format(time.strftime('%l:%M%p %Ss %f us'), curr_status))
    while True:
        new_status = gpio.input(echo_pin)
        print(new_status)
        time.sleep(0.5)
        if new_status != curr_status:
            print("{0} : {1} (Time since last: {2})".format(time.strftime('%l:%M%p %Ss %fus'), curr_status,
                                                            time.time() - state_time))
            state_time = time.time()

main()
