import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from tkinter import messagebox
from datetime import datetime

# Set the file paths
known_faces_dir = "known_faces"
attendance_file_path = "attendance.xlsx"

# Load the known faces
known_face_encodings = []
known_face_names = []
for name in os.listdir(known_faces_dir):
    face_encodings = []
    for filename in os.listdir(f"{known_faces_dir}/{name}"):
        image = face_recognition.load_image_file(f"{known_faces_dir}/{name}/{filename}")
        face_encoding = face_recognition.face_encodings(image)
        if len(face_encoding) > 0:
            face_encodings.append(face_encoding[0])
    if len(face_encodings) > 0:
        known_face_encodings.append(face_encodings[0])
        known_face_names.append(name)

# Create the attendance dictionary
attendance_dict = {name: "Absent" for name in known_face_names}

# Initialize the GUI window
root = tk.Tk()
root.title("Student Attendance")
root.geometry("500x500")

# Create a frame for the camera feed
camera_frame = tk.Frame(root, width=200, height=300)
camera_frame.pack(side=tk.LEFT)

# Add a label for the student names
label = tk.Label(root, text="Student Names:")
label.pack()

# Add a checkbox for each student name
var_list = []
checkboxes = []
for name in known_face_names:
    var = tk.BooleanVar()
    var_list.append(var)
    checkbox = tk.Checkbutton(root, text=name, variable=var, font=("Arial", 20), state=tk.DISABLED)
    checkbox.pack(side=tk.TOP)
    checkboxes.append(checkbox)

# Create password window
password = "1234"  # set the password
password_window = tk.Toplevel(root)
password_window.title("Password")
password_window.geometry("200x100")
password_window.withdraw()

# Add password entry and button
password_label = tk.Label(password_window, text="Enter Password:")
password_label.pack()
password_entry = tk.Entry(password_window, show="*")
password_entry.pack(padx=10, pady=5)
password_button = tk.Button(password_window, text="Submit", command=lambda: check_password(password_entry.get()))
password_button.pack()

# Function to check the password
def check_password(entry):
    if entry == password:
        password_window.destroy()
        enable_checkboxes()
    else:
        password_entry.delete(0, tk.END)
        password_entry.insert(0, "Incorrect password")

# Function to enable checkboxes
def enable_checkboxes():
    for checkbox in checkboxes:
        checkbox.config(state=tk.NORMAL)

# Add a button to enable manual marking of attendance
manual_button = tk.Button(root, text="Manual Attendance", command=lambda: password_window.deiconify())
manual_button.pack(pady=10)

# Function to update attendance and show camera feed
def update_attendance():
    # Capture a live image from the camera
    ret, frame = cap.read()

    # Convert the live image to RGB format
    rgb_frame = frame[:, :, ::-1]

    # Detect the face in the live image
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Mark attendance for detected faces
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        # Find the closest match in the known face encodings
        face_distances = np.linalg.norm(np.subtract(known_face_encodings, face_encoding), axis=1)
        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] < 0.6:
            name = known_face_names[best_match_index]

            # Determine if the person is entering or exiting based on their position in the frame
            if left < (cap.get(3) // 2) and not var_list[best_match_index].get():
                # Person is entering from the left side
                attendance_dict[name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Present"
                var_list[best_match_index].set(True)
                checkboxes[best_match_index].config(bg="light green")
                print(f"{name} is present.")  # Print attendance record
            elif right > (cap.get(3) // 2) and var_list[best_match_index].get():
                # Person is exiting from the right side
                attendance_dict[name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Currently out"
                var_list[best_match_index].set(False)
                checkboxes[best_match_index].config(bg="yellow")
                print(f"{name} is currently out.")  # Print attendance record

    # Update attendance for manually marked checkboxes
    for i, var in enumerate(var_list):
        if var.get():
            name = known_face_names[i]
            if attendance_dict[name] == "Absent":
                attendance_dict[name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Present"
                print(f"{name} is present.")  # Print attendance record
                checkboxes[i].config(bg="light green")  # Set background to light green
        else:
            name = known_face_names[i]
            if attendance_dict[name] == "Present":
                attendance_dict[name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Absent"
                checkboxes[i].config(bg="white")  # Set background to white

    # Save the attendance file
    attendance_df = pd.DataFrame(list(attendance_dict.items()), columns=["Name", "Attendance"])
    attendance_df.to_excel(attendance_file_path, index=False)

    # Convert the image to a format suitable for displaying in tkinter
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    image = Image.fromarray(frame)
    image = ImageTk.PhotoImage(image)

    # Update the camera frame in the GUI window
    camera_label.config(image=image, bd=3, relief=tk.SUNKEN)
    camera_label.image = image
    root.after(10, update_attendance)


# Capture a live image from the camera
cap = cv2.VideoCapture(0)

# Create a label to display the camera feed
camera_label = tk.Label(camera_frame)
camera_label.pack()

# Call the update_attendance function
update_attendance()

# Run the GUI window
root.mainloop()

# Release the camera
cap.release()
cv2.destroyAllWindows()
