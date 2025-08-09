# import tkinter as tk
# from sklearn.neighbors import KNeighborsClassifier
# from tkinter import messagebox, Label, Button
# from PIL import Image, ImageTk
# import sqlite3
# import cv2
# import pickle
# import time
# from datetime import datetime,date
# import numpy as np

# # Place the mark_attendance function here
# def mark_attendance(user_id, name, timestamp, status="Present"):
#     today_date = date.today().strftime("%d-%m-%Y")

#     conn = sqlite3.connect('attendance.db')
#     c = conn.cursor()

#     c.execute("SELECT * FROM attendance WHERE id = ? AND date = ?", (user_id, today_date))
#     result = c.fetchone()

#     if result:
#         print(f"Attendance for {name} (ID: {user_id}) already marked today.")
#         if status == "Present":
#             speak(f"Attendance for {name} already marked today.")
#     else:
#         c.execute("INSERT INTO attendance (id, name, date, time, status) VALUES (?, ?, ?, ?, ?)", 
#                   (user_id, name, today_date, timestamp, status))
#         conn.commit()
#         print(f"Attendance marked for {name} (ID: {user_id}) at {timestamp}. Status: {status}.")
        
#         if status == "Present":
#             speak(f"Attendance marked for {name}")
    
#     conn.close()

# # Then, mark_attendance_frontend function goes below
# def mark_attendance_frontend():
#     try:
#         video = cv2.VideoCapture(0)
#         if not video.isOpened():
#             messagebox.showerror("Error", "Cannot open webcam")
#             return

#         facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
#         attendance_to_save = None

#         while True:
#             ret, frame = video.read()
#             if not ret:
#                 messagebox.showerror("Error", "Failed to capture video")
#                 break

#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             faces = facedetect.detectMultiScale(gray, 1.3, 5)
            
#             for (x, y, w, h) in faces:
#                 crop_img = frame[y:y+h, x:x+w, :]
#                 resized_img = cv2.resize(crop_img, (75, 75)).flatten().reshape(1, -1)
#                 output = knn.predict(resized_img)

#                 name = output[0]
#                 user_id = IDS[LABELS.index(name)]

#                 ts = time.time()
#                 timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                
#                 attendance_to_save = (user_id, name, timestamp)

#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
#                 cv2.putText(frame, f"Name: {name}", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
#                 cv2.putText(frame, f"Roll no: {user_id}", (x, y + h + 45), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

#             cv2.imshow("Attendance Window", frame)
#             k = cv2.waitKey(1)

#             if k == ord('o') and attendance_to_save:
#                 user_id, name, timestamp = attendance_to_save
#                 mark_attendance(user_id, name, timestamp, status="Present")
#                 messagebox.showinfo("Attendance", f"Attendance marked for {name} (ID: {user_id})")
#                 attendance_to_save = None
#                 break

#             if k == ord('q'):
#                 break

#         video.release()
#         cv2.destroyAllWindows()

#     except Exception as e:
#         messagebox.showerror("Error", f"An error occurred: {str(e)}")

# # Function to mark attendance
# def mark_attendance_frontend():
#     # Open the video capture and capture faces
#     video = cv2.VideoCapture(0)
#     facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#     with open('data/faces_data.pkl', 'rb') as f:
#         FACES = pickle.load(f)
#     with open('data/names.pkl', 'rb') as f:
#         LABELS = pickle.load(f)
#     with open('data/ids.pkl', 'rb') as f:
#         IDS = pickle.load(f)

#     knn = KNeighborsClassifier(n_neighbors=5)
#     knn.fit(FACES, LABELS)

#     attendance_to_save = None

#     while True:
#         ret, frame = video.read()
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = facedetect.detectMultiScale(gray, 1.3, 5)
        
#         for (x, y, w, h) in faces:
#             crop_img = frame[y:y+h, x:x+w, :]
#             resized_img = cv2.resize(crop_img, (75, 75)).flatten().reshape(1, -1)
#             output = knn.predict(resized_img)
            
#             name = output[0]
#             user_id = IDS[LABELS.index(name)]
            
#             ts = time.time()
#             timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            
#             # Prepare attendance details to save later
#             attendance_to_save = (user_id, name, timestamp)

#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
#             cv2.putText(frame, f"Name: {name}", (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
#             cv2.putText(frame, f"Roll no: {user_id}", (x, y + h + 45), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        
#         cv2.imshow("Attendance Window", frame)
#         k = cv2.waitKey(1)

#         if k == ord('o'):
#             if attendance_to_save:
#                 user_id, name, timestamp = attendance_to_save
#                 mark_attendance(user_id, name, timestamp, status="Present")
#                 messagebox.showinfo("Attendance", f"Attendance marked for {name} (ID: {user_id})")
#                 attendance_to_save = None
#             break
#         if k == ord('q'):
#             break

#     video.release()
#     cv2.destroyAllWindows()

# # GUI for viewing database entries
# def view_db():
#     conn = sqlite3.connect('attendance.db')
#     c = conn.cursor()
#     c.execute("SELECT * FROM attendance")
#     records = c.fetchall()

#     view_window = tk.Toplevel(root)
#     view_window.title("Attendance Records")

#     label = tk.Label(view_window, text="ID\tName\tDate\tTime\tStatus")
#     label.grid(row=0, column=0, padx=10, pady=10)

#     for i, record in enumerate(records):
#         record_label = tk.Label(view_window, text="\t".join(map(str, record)))
#         record_label.grid(row=i+1, column=0, padx=10, pady=5)

#     conn.close()

# # Tkinter Window Setup
# root = tk.Tk()
# root.title("Smart Attendance System")
# root.geometry("600x400")

# # Create a header
# header = Label(root, text="Smart Attendance System", font=("Arial", 24))
# header.pack(pady=20)

# # Button to Start Attendance
# btn_start_attendance = Button(root, text="Start Attendance", command=mark_attendance_frontend, font=("Arial", 14))
# btn_start_attendance.pack(pady=20)

# # Button to View Database
# btn_view_db = Button(root, text="View Attendance Records", command=view_db, font=("Arial", 14))
# btn_view_db.pack(pady=20)

# # Exit Button
# btn_exit = Button(root, text="Exit", command=root.quit, font=("Arial", 14))
# btn_exit.pack(pady=20)

# # Run the Tkinter loop
# root.mainloop()
