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

    # add a white border around image
    image = cv2.copyMakeBorder(image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # Downscale image
    down_image = cv2.resize(image, (0, 0), fx=0.1, fy=0.1)

    # Convert image to grayscale
    gray = cv2.cvtColor(down_image, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding to create a binary image
    _, binary_image_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Adjust the threshold value by the specified factor
    threshold_value = threshold_factor * cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)[0]
    _, binary_image = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Find all contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #reject all contours that are too small
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
        approx = cv2.approxPolyDP(c, peri * 0.09, True)

        #minimize the contour to a rectangle
        rect = cv2.minAreaRect(approx)

        # Get the rectangle coordinates and dimensions
        x, y, w, h = cv2.boundingRect(approx)

        # Print the area of the contour
        print(f"Area of subset photo {i+1}: {cv2.contourArea(c)}")
        
        # Scale the rectangle coordinates back to the original image size and crop the image
        x = int(x / 0.1) 
        y = int(y / 0.1) 
        w = int(w / 0.1) 
        h = int(h / 0.1)

        cropped_image = image[y:y + h, x:x + w]


        # Save the cropped image with the numbered filename
        output_filename = f"{output_path}/cropped_image_{current_number}.png"
        cv2.imwrite(output_filename, cropped_image)

        # Increment the current numbering value
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