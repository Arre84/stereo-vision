"""stereo-vision.py

    This pythons script cmputes and reconstructs a point map with 30 
    points selected by the user on a right and left picture
    of the stereo camera with the mouse.

    Author:Emilio Arredondo Payán
    Organisation: Universidad de Monterrey
    Contact: Emilio.Arredondop@udem.edu
    First created: Wednesday 15 May 2024
    Last updated: Wednesday 15 May 2024

    EXAMPLE OF USAGE:
    python .\get-measurements.py -c 1 --z 30 --cal_file .\calibration_data.json
    
"""
import cv2
import numpy as np
import argparse as arg
from numpy.typing import NDArray
import os
import json
import matplotlib.pyplot as plt
import time

left_points = []
right_points = []
exit_flag = False

def user_interaction()-> arg.ArgumentParser:
    """
    Parse command-line arguments for images paths.
    Returns:
        argparse.ArgumentParser: The argument parser object configured with the paths of the images.
    """
    parser = arg.ArgumentParser(description='Images to perform the selection')
    parser.add_argument("-l",'--l_img', 
                        type=str,
                        help='Path to the left image picture')
    parser.add_argument("-r",'--r_img', 
                        type=str, 
                        help='Path to the left image picture')
    parser.add_argument('--cal_file', 
                        type=str, 
                        help='Path to the calibration JSON object')
    args = parser.parse_args()
    return args

def onclick(event, points_list):
    global exit_flag
    if event.button == 3:  # Si es clic izquierdo
        if event.xdata is not None and event.ydata is not None:
            points_list.append((event.xdata, event.ydata))
            print("Punto seleccionado:", event.xdata, event.ydata)
            plt.close()
        else:
            print("¡Punto fuera de los límites de la imagen!")

def on_key(event):
    global exit_flag
    if event.key == 'q':
        exit_flag = True

def select_points(left_image,right_image):
    fig = plt.figure()
    plt.imshow(left_image)
    plt.title('Imagen Izquierda')
    cid1 = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, left_points))
    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()
    fig = plt.figure()
    plt.imshow(right_image)
    plt.title('Imagen derecha')
    cid1 = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, right_points))
    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()
    

def pipeline()-> None:
    args = user_interaction()
    left_image = cv2.imread(args.l_img)
    right_image = cv2.imread(args.r_img)
    for i in range(30):
        select_points(left_image,right_image)
        if exit_flag:
            break
        print("Puntos izquierdos guardados hasta ahora:", left_points)
        print("Puntos derechos guardados hasta ahora:", right_points)
         # Salir del bucle si se presiona 'q'
    # Limpiar listas fuera del bucle
    return None



if __name__ == "__main__":
    pipeline()