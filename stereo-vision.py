"""stereo-vision.py

    This pythons script cmputes and reconstructs a point map with 30 
    points selected by the user on a right and left picture
    of the stereo camera with the mouse.

    Author:Emilio Arredondo Payán
    Organisation: Universidad de Monterrey
    Contact: Emilio.Arredondop@udem.edu
    First created: Wednesday May 15 2024
    Last updated: Wednesday May 16 2024

    EXAMPLE OF USAGE:
    python .\stereo-vision.py -l .\left_infrared_image.png -r .\right_infrared_image.png --cal_file .\calibration-parameters.txt
    
"""
import cv2
import numpy as np
import argparse as arg
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

left_points = []
right_points = []
points_panda = []
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

def read_calibration(file_path:str)->dict:
    """
    Reads camera calibration parameters from a plain text file.

    Args:
        file_path: path to the file with the calibration parameters.

    Returns:
        caliration_params: Dictionary containing the calibration parameters
    """
    calibration_params = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ":" in line:
                key, value = line.split(":")
                # Remover comillas, espacios adicionales y comas
                key = key.strip().replace('"', '')
                value = value.strip().replace(',', '').replace('"', '')
                # Convertir el valor a float si es posible
                try:
                    value = float(value)
                except ValueError:
                    pass
                calibration_params[key] = value
    return calibration_params

def onclick(event, points_list):
    """
    Handle mouse click events.

    Parameters:
    - event (Event): The event object representing the mouse click.
    - points_list (list): The list to which the clicked points will be appended.

    Returns:
    - None
    """

    if event.button == 3:  # Si es clic izquierdo
        if event.xdata is not None and event.ydata is not None:
            points_list.append((event.xdata, event.ydata))
            print("Punto seleccionado:", event.xdata, event.ydata)
            plt.close()
        else:
            print("¡Punto fuera de los límites de la imagen!")

def on_key(event):
    """
    Handle key press events for q key.

    Parameters:
    - event (Event): The event object representing the key press.

    Returns:
    - None
    """
    global exit_flag
    if event.key == 'q':
        exit_flag = True

def select_points(left_image: NDArray,right_image: NDArray):
    """
    Display left and right images for point selection, and select the points.

    Parameters:
    - left_image (array): The left image array.
    - right_image (array): The right image array.

    Returns:
    - None
    """
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
    
def selection(left_image:NDArray,right_image:NDArray,calibration:dict)->None:
    """
    Select points, compute distances, and show images.

    Parameters:
    - left_image (array): The left image array.
    - right_image (array): The right image array.
    - calibration (dict): A dictionary containing calibration parameters.

    Returns:
    - None
    """
    global exit_flag 
    for i in range(30):
        select_points(left_image,right_image)
        if exit_flag:
            exit_flag = False
            left_points.clear()
            right_points.clear()
            break
        if left_points:
            compute_real_distances(calibration)
        print("coordenadas guardados hasta ahora:", points_panda,"mm")
        left_points.clear()
        right_points.clear()
        # Salir del bucle si se presiona 'q'
    
def compute_real_distances(calibration:dict):
    """
    Compute real distances between selected points and appends them to a global variable.

    Parameters:
    - calibration (dict): A dictionary containing calibration parameters.

    Returns:
    - None
    """
    left = left_points[0]
    right = right_points[0]
    l_x = left[0]
    l_y = left[1]
    r_x = right[0]
    r_y = right[1]
    left_wrt = l_x - calibration['rectified_cx']
    right_wrt = r_x - calibration['rectified_cx']
    h_wrt = l_y - calibration['rectified_cy']
    d = left_wrt - right_wrt
    z = calibration['rectified_fx']*abs(calibration['baseline'])/d
    X = left_wrt*z/calibration['rectified_fx']
    Y = h_wrt*z/calibration['rectified_fy']
    points_panda.append((X,Y,z))

def plotting(Name: str)->None:
    """
    Plot 3D scatter plot of selected points.

    Parameters:
    - Name (str): The name of the plot.

    Returns:
    - None
    """
    fig = plt.figure()
 
# syntax for 3-D projection
    ax = plt.axes(projection ='3d')
    x = []
    y = []
    z = []
    # defining all 3 axis
    for point in points_panda:
        x.append(point[0])
        y.append(-point[1])
        z.append(point[2])
    # plotting
    ax.scatter(x, z, y)
    ax.set_title(Name)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('z', fontsize=12)
    ax.set_zlabel('y', fontsize=12)
    plt.show()
    return None

def pipeline()-> None:
    """
    Execute the entire pipeline.

    Returns:
    - None
    """
    args = user_interaction()
    left_image = cv2.imread(args.l_img)
    right_image = cv2.imread(args.r_img)
    params = read_calibration(args.cal_file)
    for i in range(3):
        selection(left_image,right_image,params)
        plotting(f"Plot {i+1}")
        points_panda.clear()
    # Limpiar listas fuera del bucle
    return None

if __name__ == "__main__":
    pipeline()