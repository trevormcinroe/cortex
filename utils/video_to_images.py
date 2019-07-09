# Program To Read video
# and Extract Frames
import cv2


# Function to extract frames
def FrameCapture(path):
    # Path to video file
    vidObj = cv2.VideoCapture(path)

    # Used as counter variable
    count = 0

    # checks whether frames were extracted
    success = 1

    while success:
        # vidObj object calls read
        # function extract frames
        success, image = vidObj.read()

        base_path = "E:\\nick\\"
        # Saves the frames with frame-count
        cv2.imwrite(f"{base_path}frame{count}.jpg", image)

        count += 1


# Driver Code
if __name__ == '__main__':
    # Calling the function
    FrameCapture(r"C:\Users\nick_simmons\NY Yankees vs BOS Red Sox ( LONDON SERIES ) Full Game #1 June 29 ,2019-KuoXq71nXN4.mp4")
