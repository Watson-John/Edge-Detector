import cv2
import numpy as np

def detect_squares(image_path, threshold_factor=1.0):
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

    # Filter small contours and sort by area
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:3]

    # Iterate over the contours and draw rectangles around them
    for i, c in enumerate(contours):
        # Approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, peri * 0.09, True)

        # Draw a rectangle around the contour
        x, y, w, h = cv2.boundingRect(approx)


        # Print the area of the contour
        print(f"Area of subset photo {i+1}: {cv2.contourArea(c)}")
        
        # Scale the rectangle coordinates back to the original image size and crop the image
        x = int(x / 0.1) 
        y = int(y / 0.1) 
        w = int(w / 0.1) 
        h = int(h / 0.1)
        cropped_image = image[y:y + h, x:x + w]

        # Save the cropped image
        cv2.imwrite(f"cropped_image_{i+1}.png", cropped_image)
        

        
    # 

if __name__ == "__main__":
    image_path = "Input\Scan007.tif"
    detected_rectangles = detect_squares(image_path, threshold_factor=1.2)  # You can adjust the threshold_factor as needed
