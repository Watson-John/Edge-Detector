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
        print("")

        # Rotate the image counter-clockwise by the corrective angle
        rows, cols = down_image.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        rotated_image = cv2.warpAffine(down_image, M, (cols, rows))

        # Rotate the box points by the corrective angle
        center = (cols / 2, rows / 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_box = cv2.transform(np.array([box]), rot_mat)[0]


        # crop the image to the rotated rectangle
        # get the min and max points, then crop
        x_min = np.min(rotated_box[:, 0])
        x_max = np.max(rotated_box[:, 0])
        y_min = np.min(rotated_box[:, 1])
        y_max = np.max(rotated_box[:, 1])

        # crop the image to the rotated rectangle
        cropped_image = rotated_image[y_min:y_max, x_min:x_max]
        
        # Save the image
        cv2.imwrite(f"{output_path}/{current_number}.png", cropped_image)

        # Get the bounding rectangle of the rotated box
        # x, y, w, h = cv2.boundingRect(rotated_box)

        # Scale the points up to the original image size
        # x = x * 10
        # y = y * 10
        # w = w * 10
        # h = h * 10

        # # Crop the image
        # cropped_image = image_with_border[y:y + h, x:x + w]

        # Save the image
        # cv2.imwrite(f"{output_path}/{current_number}.png", cropped_image)

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