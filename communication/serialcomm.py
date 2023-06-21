#!/usr/bin/env python3
import serial
import time
import cv2
import numpy as np
import os

from gui.pages import PORT_PATH, BAUD_RATE, MICRO_DELAY, STEP_SIZE, MAX_STEPS, MIN_STEPS
from typing import TYPE_CHECKING, Union

z_coordinate = 0

if TYPE_CHECKING:
    from gui.pages.scan import ScanCamFrame
    from gui.pages.manuelcalibration import ManualCamFrame


def get_arduino():
    return serial.Serial(PORT_PATH, BAUD_RATE, timeout=1)


def move_motor(arduino: serial.Serial, steps, axis, delay):
    global z_coordinate
    if steps < 0:
        direction = 0
        steps = abs(steps)
    else:
        direction = 1
    if not arduino:
        return

    arduino.reset_input_buffer()
    command = f"step{axis},{steps},{direction},{delay}\n"
    arduino.write(command.encode())

    while True:
        if arduino.in_waiting > 0:
            # print(arduino.in_waiting)
            # line = arduino.readline().decode('utf-8').rstrip()
            line = arduino.readline().decode('ascii')
            # arduino.read_until("\n")
            print(line)
            z_coordinate = int(line.split("\t")[2].split(": ")[-1])
            break

    time.sleep(0.01)


def tray_procedure(arduino, direction):
    if direction:
        move_motor(arduino, 0, "B", 0)
        print("backward")
    else:
        move_motor(arduino, 0, "F", 0)
        print("forward")


def calibration_procedure(arduino: serial.Serial):
    move_motor(arduino, 0, "Calibration", 0)


def scanning_procedure(cls: Union['ManualCamFrame', 'ScanCamFrame'], arduino, slide_indexes, step_size, min_steps,
                       max_steps):
    ## for example slide indexes = [0,1,2]
    slide_distance = 2200  # a number for steps for Y axis motor
    bottom_top_slide_distance = 600  # first lamel bottom to second lamel top distance as steps
    left_right_slide_distance = 0

    # first of all, motor calibration code run
    # assump that your frame is on the top-right corner
    # goes to first slide
    # move_motor(arduino, x_steps, "X", MICRO_DELAY)
    # move_motor(arduino, y_steps, "Y", MICRO_DELAY)

    # go to first index slide.
    # if slide_indexes[0] == 0, so the motor will be stable
    slide_index_temp, _ = slide_indexes[0]
    distance = slide_distance * slide_index_temp
    # print("distance: ", distance)
    # print(type(distance))
    # print("slide distance: ", slide_distance)
    # print("slide indexes[0]", slide_indexes[0])
    move_motor(arduino, -distance, "Y", MICRO_DELAY * 2)

    for (slide_index, slide_value) in (slide_indexes):
        if slide_index == slide_indexes[-1]:
            print(slide_value)
            slide_scan(cls, arduino, slide_index, slide_value, step_size, min_steps, max_steps)
            print("Scanning Procedure Finished")
            time.sleep(5)
            calibration_procedure()
        else:
            slide_scan(cls, arduino, slide_index, slide_value, step_size, min_steps, max_steps)
            move_motor(arduino, -bottom_top_slide_distance, "Y", MICRO_DELAY * 2)
            # if needed ->
            # move_motor(arduino, left_right_slide_distance, "X", MICRO_DELAY)


def slide_scan(cls: 'ScanCamFrame', arduino, slide_index, slide_value, step_size, min_steps, max_steps):
    global z_coordinate
    ## whole progress for scanning a slide
    # and saving the images

    x_step_size = 80  # it will be a frame length
    y_step_size = 100  # it will be a frame width
    y_steps = 16  # y axis motor run for 15 times
    x_steps = 23  # x axis motor run for 23 times

    # Starting at the top right corner of the surface
    x, y = x_steps - 1, 0

    # Assume the scan direction to the left initially
    direction = 'left'

    while y < y_steps:
        # Moving the scan head in the current direction
        while (direction == 'right' and x < x_steps) or (direction == 'left' and x >= 0):

            # At the end of scanning (at last x and y step), break the loop
            if x == x_steps - 1 and y == y_steps - 1 and direction == 'right':
                print("Scanning complete!")
                return

            # Scan current point here
            # print(f"Scanning point ({x}, {y})")

            # Move in the current direction
            if direction == 'right':
                if x < x_steps - 1:  # Ensure we don't move past the edge
                    x += 1

                    if not os.path.exists(f"images/scanning"):
                        os.makedirs(f"images/scanning")
                    filename = f"images/scanning/{slide_value}_{x}_{y}.png"
                    frame = cls.get_frame()
                    cv2.imwrite(filename, frame)

                    temp_coord = 160000 - z_coordinate
                    # print(temp_coord)
                    move_motor(arduino, -temp_coord, "Z", MICRO_DELAY * .005)

                    move_motor(arduino, x_step_size, "X", MICRO_DELAY)
                    autofocus(cls, arduino, STEP_SIZE * 64, MIN_STEPS, MAX_STEPS)
                    time.sleep(0.05)

                    # dont forget to use os.getcwd ..!

                else:  # If we're at the edge, don't move
                    break
            else:  # direction == 'left'
                if x > 0:  # Ensure we don't move past the edge
                    x -= 1

                    if not os.path.exists(f"images/scanning"):
                        os.makedirs(f"images/scanning")
                    filename = f"images/scanning/{slide_value}_{x}_{y}.png"
                    frame = cls.get_frame()
                    cv2.imwrite(filename, frame)
                    temp_coord = 160000 - z_coordinate
                    # print(temp_coord)
                    move_motor(arduino, -temp_coord, "Z", MICRO_DELAY * .005)
                    move_motor(arduino, -x_step_size, "X", MICRO_DELAY)
                    autofocus(cls, arduino, STEP_SIZE * 64, MIN_STEPS, MAX_STEPS)
                    time.sleep(0.05)

                else:  # If we're at the edge, don't move
                    break

        # At the end of a row, move down one row
        if y < y_steps - 1:  # Ensure we don't move past the bottom
            y += 1
            if not os.path.exists(f"images/scanning"):
                os.makedirs(f"images/scanning")

            filename = f"images/scanning/{slide_value}_{x}_{y}.png"
            frame = cls.get_frame()
            cv2.imwrite(filename, frame)
            temp_coord = 160000 - z_coordinate
            # print(temp_coord)
            move_motor(arduino, -temp_coord, "Z", MICRO_DELAY * .005)
            move_motor(arduino, -y_step_size, "Y", MICRO_DELAY)
            autofocus(cls, arduino, STEP_SIZE * 64, MIN_STEPS, MAX_STEPS)
            time.sleep(0.05)

        # Switch the scan direction for the next row
        direction = 'right' if direction == 'left' else 'left'

    print("Scanning complete!")


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def variance(image):
    return np.var(image)


def sobel(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img_sobel = cv2.Sobel(img_gray, cv2.CV_16U, 1, 1)
    return cv2.mean(img_sobel)[0]


def laplacian(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img_laplacian = cv2.Laplacian(img_gray, cv2.CV_16U)
    return cv2.mean(img_laplacian)[0]


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def autofocus(cls: Union['ManualCamFrame', 'ScanCamFrame'], arduino, step_size, min_steps, max_steps):
    # Move the motor to the initial position
    if not arduino:
        return

    def focus(step_size, min_steps, max_steps):
        max_focus_measure = 0
        best_step = min_steps

        move_motor(arduino, min_steps, "Z", MICRO_DELAY * .005)

        # Loop through possible motor positions
        for step in range(min_steps, max_steps, step_size):
            # Capture an image at the current position
            frame = cls.get_frame()

            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # median = cv2.medianBlur(frame, 5)
            # print(np.mean(gray))

            # Calculate the focus measure
            focus_measure = laplacian(frame)
            print(focus_measure)

            # Compare the focus measure to the previous best
            if focus_measure > max_focus_measure:
                max_focus_measure = focus_measure
                best_step = step

            # Move the motor to the next position
            move_motor(arduino, step_size, "Z", MICRO_DELAY * .005)
            time.sleep(0.01)

        return best_step

    # Rough Focusing
    best_step = focus(step_size, min_steps, max_steps)
    steps_to_move = max_steps - best_step

    move_motor(arduino, -steps_to_move, "Z", MICRO_DELAY * .005)
    # Fine tuning
    # best_step = focus(step_size // 8, min_steps // 8, max_steps // 8)
    # Move the motor back to the best focus position
    # steps_to_move = (max_steps // 8) - best_step

    # move_motor(arduino, -steps_to_move, "Z", MICRO_DELAY * .005)
