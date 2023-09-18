import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog




# Function to get the current numbering value from a file
def get_current_number():
    try:
        with open("numbering.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 1

# Function to save the current numbering value to a file
def save_current_number(number):
    with open("numbering.txt", "w") as file:
        file.write(str(number))

def order_rect(points):
    # initialize result -> rectangle coordinates (4 corners, 2 coordinates (x,y))
    res = np.zeros((4, 2), dtype=np.float32)

    left_to_right = points[points[:, 0].argsort()] # Sorted by x

    left_points = left_to_right[:2,:]
    left_points = left_points[left_points[:, 1].argsort()] # Sorted by y
    right_points = left_to_right[2:,:]
    right_points = right_points[right_points[:, 1].argsort()] # Sorted by y

    res[0] = left_points[0]
    res[1] = right_points[0]
    res[2] = right_points[1]
    res[3] = left_points[1]

    return res

def four_point_perspective_transform(img, points):
    # Create an empty array for the destination points (rectangle corners)
    rect = np.zeros((4, 2), dtype=np.float32)

    # Order the input points in clockwise order
    ordered_points = order_rect(points)

    # Calculate the width and height of the destination rectangle
    widthA = np.sqrt(((ordered_points[3][0] - ordered_points[2][0]) ** 2) + ((ordered_points[3][1] - ordered_points[2][1]) ** 2))
    widthB = np.sqrt(((ordered_points[1][0] - ordered_points[0][0]) ** 2) + ((ordered_points[1][1] - ordered_points[0][1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((ordered_points[1][0] - ordered_points[3][0]) ** 2) + ((ordered_points[1][1] - ordered_points[3][1]) ** 2))
    heightB = np.sqrt(((ordered_points[0][0] - ordered_points[2][0]) ** 2) + ((ordered_points[0][1] - ordered_points[2][1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Set the destination points (rectangle corners)
    rect[0] = [0, 0]
    rect[1] = [maxWidth - 1, 0]
    rect[2] = [maxWidth - 1, maxHeight - 1]
    rect[3] = [0, maxHeight - 1]

    # Compute the perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(ordered_points, rect)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warped


# Function to detect the squares in the image and crop them
def detect_squares(image_path, output_path, threshold_factor=1.0, num_subsets=3):
    # Load the image
    image = cv2.imread(image_path)

    # Add a white border around the image
    image_with_border = cv2.copyMakeBorder(image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # Downscale image
    down_image = cv2.resize(image, (0, 0), fx=0.1, fy=0.1)

    # Convert image to grayscale
    gray = cv2.cvtColor(down_image, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding to create a binary image
    _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Find all contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Reject all contours that are too small
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]

    # Filter small contours and sort by area
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]

    # Get the current numbering value
    current_number = get_current_number()

    # Iterate over the contours and draw rectangles around them
    for i, c in enumerate(contours):
        # Approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, peri * 0.02, True)  # Adjust the parameter as needed

        # Get the rectangle coordinates from the approximated contour
        rect = cv2.minAreaRect(approx)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # Find the longest side of the box
        side1 = np.linalg.norm(box[0] - box[1])
        side2 = np.linalg.norm(box[0] - box[3])
        side_long = max(side1, side2)

        if side_long == side1:
            # Calculate the slope of side 1
            x1, y1 = box[0]
            x2, y2 = box[1]
            slope = (y2 - y1) / (x2 - x1)
            angle = np.arctan(slope) * 180 / np.pi
        else:
            # Calculate the slope of side 2
            x1, y1 = box[0]
            x2, y2 = box[3]
            slope = (y2 - y1) / (x2 - x1)
            angle = np.arctan(slope) * 180 / np.pi

          # Rotate the image to the nearest 90 degrees
        if angle < 0:
            angle = -angle

        angle_list = [0, 90, 180, 270]

        # Find the closest angle to the current angle
        closest_angle = min(angle_list, key=lambda x: abs(x - angle))

        # Calculate the corrective angle
        corrective_angle = abs(closest_angle - angle)

        # Print the corrective angle
        print(f"Corrective Angle: {corrective_angle}")
        print(f"Closest Angle: {closest_angle}")
        print(f"Angle: {angle}")

        # Apply the perspective transform to the rotated square
        warped_square = four_point_perspective_transform(down_image, box)

        # Save the image with the rotated rectangle
        cv2.imwrite(f"{output_path}/{current_number}-warped.png", warped_square)


        print(f"Current Number: {current_number}")



        # Increment the current number
        current_number += 1

    # Save the updated numbering value
    save_current_number(current_number)




# Function to browse and select the input file
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.tif")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# Function to browse and select the output folder
def browse_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, folder_path)

# Function to process the image using the input parameters
def process_image():
    image_path = entry_file.get()
    output_path = entry_output.get()
    if not image_path or not output_path:
        return

    threshold_factor = float(entry_threshold.get())
    num_subsets = int(entry_num_subsets.get())

    detect_squares(image_path, output_path, threshold_factor, num_subsets)
    print("Image processing completed.")

# Create the GUI window
root = tk.Tk()
root.title("Image Processing GUI")
root.geometry("300x450")

# Title label
title_label = tk.Label(root, text="Image Processing", font=("Helvetica", 20, "bold"))
title_label.pack(pady=20)

# Input fields and labels
label_file = tk.Label(root, text="Input File:")
label_file.pack()
entry_file = tk.Entry(root)
entry_file.pack(pady=5)
button_browse = tk.Button(root, text="Browse", command=browse_file)
button_browse.pack()

label_threshold = tk.Label(root, text="Threshold Factor:")
label_threshold.pack()
entry_threshold = tk.Entry(root)
entry_threshold.pack(pady=5)
entry_threshold.insert(0, "1.5")

label_num_subsets = tk.Label(root, text="Number of Subsets:")
label_num_subsets.pack()
entry_num_subsets = tk.Entry(root)
entry_num_subsets.pack(pady=5)
entry_num_subsets.insert(0, "3")

label_output = tk.Label(root, text="Output File Path:")
label_output.pack()
entry_output = tk.Entry(root)
entry_output.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=browse_output_folder)
browse_button.pack(pady=5)


# Process Image button
button_process = tk.Button(root, text="Process Image", command=process_image, bg="green", fg="white", font=("Helvetica", 14, "bold"))
button_process.pack(pady=20)

root.mainloop()