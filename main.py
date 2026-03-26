"""
Name: main.py
Author: Asante Frye
Description: A surveillance application to detect changes in a scene captured via camera stream.
"""

# Import required libraries
import cv2  # Computer Vision library for camera capture analysis
from dotenv import (
    load_dotenv,
)  # Import function to load envionment variables from env file
from time import sleep  # To establish delays between captures
import os  # To read environment variables
from datetime import datetime
from EnvException import EnvException
from google.cloud import vision


def load_environment() -> str | None:
    # Load environment variables
    env_found: bool = load_dotenv()

    # Attempt to Read API key
    try:
        if not env_found or not os.environ.get("API_KEY"):
            raise EnvException(
                "Could not load the environment... "
                "Please ensure a valid '.env' file is present "
                "with your GCP API_KEY defined."
            )
        else:
            API_KEY: str | None = os.environ.get("API_KEY")  # Get the user's API_KEY
            return API_KEY
    except EnvException as e:
        print(e)


def capture_image_objects(cam: cv2.VideoCapture, fname: str, cv_client):
    for _ in range(5):
        cam.grab()

    ret, frame = cam.read()  # Capture a frame from the camera
    if not ret:
        raise IOError("Could not capture a frame from the camera")

    # Write the frame to image directory
    if not os.path.exists("./images"):
        os.mkdir("./images")

    cv2.imwrite(fname, frame)
    print(f"Saving image capture to '{fname}'")

    # Read the image file to analyze with GCVision client
    with open(fname, "rb") as image_file:
        image_content = image_file.read()

    image = vision.Image(content=image_content)  # Analyze the image

    # Get the recognized objects from the image capture
    objects = cv_client.object_localization(image=image).localized_object_annotations

    return objects


def main() -> None:
    API_KEY = load_environment()  # (Attempt) Load the enviroment

    num_captures: int = 5  # Total number of captures to take before exiting the program

    # Connect to the default camera on the system
    camera: cv2.VideoCapture = cv2.VideoCapture(0)

    # Initiate a connection to the Image Annotator client using user's API key
    vision_client = vision.ImageAnnotatorClient(client_options={"api_key": API_KEY})

    # List of recognized objects
    objects: list[str] = []

    while num_captures > 0:
        capture_objects = capture_image_objects(
            camera, f"./images/capture{abs(num_captures - 5)}.jpg", vision_client
        )

        for obj in capture_objects:
            if (obj.score >= 0.50) and (obj.name not in objects):
                print(
                    f"Recognized new object '{obj.name}'"
                    f" at location {obj.bounding_poly}"
                    f" with {obj.score:.2f} confidence.\n"
                )
                objects.append(obj.name)
            else:
                print("No changes detected in scene...\n")
        num_captures -= 1
        print(
            f"Image taken at time: {datetime.now()}.\n",
            "Taking next capture in 30 seconds...\n",
            "=" * 60 + "\n",
        )
        sleep(30)

    # Release camera resource back to Operating System
    camera.release()


if __name__ == "__main__":
    main()
