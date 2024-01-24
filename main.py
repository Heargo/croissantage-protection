import face_recognition
import cv2
import numpy as np
import os
import time
import ctypes

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load faces from the face folder andCreate arrays of known face encodings and their names
known_face_encodings = []
for filename in os.listdir("./face"):
    #if not image skip it
    if not filename.endswith(".jpg") or filename.endswith(".png"):
        continue
    #load the image
    image = face_recognition.load_image_file("./face/"+filename)
    #get the encoding
    encoding = face_recognition.face_encodings(image)[0]
    #append the encoding to the array
    known_face_encodings.append(encoding)


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
frame_rate_processed = 5
process_this_frame = True
i = 0
last_time_safe = time.time()

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        print("face locations: ", face_locations)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = "Safe"
                last_time_safe = time.time()

            # Or instead, use the known face with the smallest distance to the new face
            # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            # best_match_index = np.argmin(face_distances)
            # if matches[best_match_index]:
            #     name = known_face_names[best_match_index]

            face_names.append(name)

    i = (i+1) % frame_rate_processed
    process_this_frame = i==0


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        #green if name is safe red if not
        color = (0, 255, 0) if name == "Safe" else (0, 0, 255)
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # if the last time safe was more than 20 seconds ago then lock the screen (simulate windows + l keystroke)
    if time.time() - last_time_safe > 10:
        print("lock the screen")
        ctypes.windll.user32.LockWorkStation()


# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()