from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import os
import time
import sqlite3
from win32com.client import Dispatch
from datetime import datetime, date
def create_db():# Function to initialize the SQLite database and create the required tables
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id TEXT PRIMARY KEY, name TEXT)''')# Create table for students (if it doesn't exist)
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id TEXT, name TEXT, date TEXT, time TEXT, status TEXT)''')
    conn.commit()
    conn.close()
def speak(str1):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str1)
def mark_attendance(user_id, name, timestamp, status="Present"):# Function to mark attendance in the database
    today_date = date.today().strftime("%d-%m-%Y")
    conn = sqlite3.connect('attendance.db')# Connect to SQLite database
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE id = ? AND date = ?", (user_id, today_date))
    result = c.fetchone() # Check if attendance has already been marked today
    if result:
        print(f"Attendance for {name} (ID: {user_id}) already marked today.")
        if status == "Present":
            speak(f"Attendance for {name} already marked today.")
    else:# Insert attendance if not already present
        c.execute("INSERT INTO attendance (id, name, date, time, status) VALUES (?, ?, ?, ?, ?)", 
                  (user_id, name, today_date, timestamp, status))
        conn.commit()
        print(f"Attendance marked for {name} (ID: {user_id}) at {timestamp}. Status: {status}.")
        if status == "Present":# Only call speak for 'Present' students
            speak(f"Attendance marked for {name}")
    conn.close()
def mark_absent_students():# Function to mark absent students
    today_date = date.today().strftime("%d-%m-%Y")
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    all_students = c.fetchall()
    for student in all_students:# Check which students have not been marked as present today
        student_id, name = student
        c.execute("SELECT * FROM attendance WHERE id = ? AND date = ?", (student_id, today_date))
        result = c.fetchone()
        if not result:# Mark the student as absent
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            mark_attendance(student_id, name, timestamp, status="Absent")
    
    conn.close()
create_db() # Initialize the database
def add_student(user_id, name):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO students (id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()
with open('data/names.pkl', 'rb') as w: # Load face data, names, and IDs
    LABELS = pickle.load(w)
with open('data/ids.pkl', 'rb') as i:
    IDS = pickle.load(i)
for i in range(len(IDS)): # Adding all students from pickle files to the database
    user_id = IDS[i]
    name = LABELS[i]
    add_student(user_id, name)
print("All students have been added to the database.")
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)
print('Shape of Faces matrix --> ', FACES.shape)
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)
imgBackground = cv2.imread("bg.png")
attendance_to_save = None  # To hold the attendance details until 'o' is pressed
while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (75, 75)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        name = output[0]
        user_id = IDS[LABELS.index(name)]
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        attendance_to_save = (user_id, name, timestamp)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.putText(frame, "Name:" + str(name), (x, y + h + 20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, "Roll no:" + str(user_id), (x, y + h + 45), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame", imgBackground)
    k = cv2.waitKey(1)
    if k == ord('o'): # Save attendance as Present when 'o' is pressed
        if attendance_to_save:
            user_id, name, timestamp = attendance_to_save
            mark_attendance(user_id, name, timestamp, status="Present") 
            speak("Attendance saved.")
            attendance_to_save = None  # Reset after saving
    if k == ord('q'): # Before exiting, mark absent students
        mark_absent_students()
        break
video.release()
cv2.destroyAllWindows()

