from tkinter import *
import tkinter.messagebox
from PIL import ImageTk, Image
import cv2
import numpy as np
from time import sleep
import threading

root = Tk()
viewframe_1 = Frame(root, bg="white")
viewframe_1.grid()
label_1 = Label(viewframe_1, bg="black")
label_2 = Label(viewframe_1, bg="black")
label_3 = Label(viewframe_1, bg="black")
label_4 = Label(viewframe_1, bg="black")

label_1.grid(row=0, column=0)
label_2.grid(row=0, column=3)
label_3.grid(row=4, column=0)
label_4.grid(row=4, column=3)


def get_center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy, w, h


class ti(threading.Thread):
    def __init__(self, camera_id, label):
        threading.Thread.__init__(self)
        self.camera_id = camera_id
        self.label = label
        self.count = 0
        self.first_frame = None
        self.cap = cv2.VideoCapture(camera_id)
        self.detec = []

    def run(self):
        while(self.cap.isOpened()):
            self.view_cam()

    def view_cam(self):
        self.detec.clear()
        ret, frame = self.cap.read()
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        greygauss = cv2.GaussianBlur(grey, (21, 21), 0)
        if self.first_frame is None:
            self.first_frame = greygauss
        delta_frame = cv2.absdiff(self.first_frame, greygauss)
        retval, thresh_delta = cv2.threshold(
            delta_frame, 21, 255, cv2.THRESH_BINARY)
        thresh_delta = cv2.dilate(thresh_delta, np.ones((5, 5)))
        (cnts, _) = cv2.findContours(thresh_delta.copy(),
                                     cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in cnts:
            (x, y, w, h) = cv2.boundingRect(contour)
            if w > 75 and h > 75:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 5)
                center = get_center(x, y, w, h)
                self.detec.append(center)
                self.frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            y_min_offset = int(
                78.5/100*self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            y_max_offset = int(
                80.5/100*self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            x_min_offset = 0
            x_max_offset = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)

            cv2.rectangle(frame,
                          (x_min_offset, y_min_offset),
                          (x_max_offset, y_max_offset),
                          (100, 100, 255),
                          -1)
            for (x, y, w, h) in self.detec:
                if y < y_max_offset and y > y_min_offset and x < x_max_offset and (w > 75 or h > 75):
                    self.count += 1
                    cv2.rectangle(frame,
                                  (x_min_offset, y_max_offset+20),
                                  (x_max_offset, y_min_offset+20),
                                  (255, 100, 100),
                                  -1)
                    self.detec.remove((x, y, w, h))
            self.detec.clear()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        scale_percent = 30  # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)


class XCanvas():
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.canvas = Canvas(viewframe_1, width=45, height=125, bg="white")
        self.canvas.grid(row=self.row, column=self.column)
        self.oval_red = self.canvas.create_oval(5, 5, 40, 40, fill="red")
        self.oval_yellow = self.canvas.create_oval(5, 45, 40, 80, fill="white")
        self.oval_green = self.canvas.create_oval(5, 85, 40, 120, fill="white")

    def set_state(self, state):
        if state == "R":
            self.oval_red = self.canvas.create_oval(5, 5, 40, 40, fill="red")
            self.oval_yellow = self.canvas.create_oval(
                5, 45, 40, 80, fill="white")
            self.oval_green = self.canvas.create_oval(
                5, 85, 40, 120, fill="white")
        elif state == "Y":
            self.oval_red = self.canvas.create_oval(5, 5, 40, 40, fill="white")
            self.oval_yellow = self.canvas.create_oval(
                5, 45, 40, 80, fill="yellow")
            self.oval_green = self.canvas.create_oval(
                5, 85, 40, 120, fill="white")
        elif state == "G":
            self.oval_red = self.canvas.create_oval(5, 5, 40, 40, fill="white")
            self.oval_yellow = self.canvas.create_oval(
                5, 45, 40, 80, fill="white")
            self.oval_green = self.canvas.create_oval(
                5, 85, 40, 120, fill="green")


class XText():
    def __init__(self, countLabel_row, countLabel_column, timeLabel_row, timeLabel_column):
        self.countLabel_row = countLabel_row
        self.countLabel_column = countLabel_column
        self.timeLabel_row = timeLabel_row
        self.timeLabel_column = timeLabel_column
        self.countLabel = Label(viewframe_1, text="countLabel", bg="white")
        self.timeLabel = Label(viewframe_1, text="timeLabel", bg="white")
        self.countLabel.grid(row=self.countLabel_row,
                             column=self.countLabel_column)
        self.timeLabel.grid(row=self.timeLabel_row,
                            column=self.timeLabel_column)
        self.Xlock = "yes"

    def set_countLabel_Text(self, data):
        self.countLabel.configure(text=data)

    def set_timeLabel_Text(self, data):
        self.timeLabel.configure(text=data)


class XSpace():
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.space = Label(viewframe_1, text="\t\n", bg="white")
        self.space.grid(row=self.row, column=self.column)


canvas1 = XCanvas(0, 1)
canvas2 = XCanvas(0, 4)
canvas3 = XCanvas(4, 1)
canvas4 = XCanvas(4, 4)
canvas_cont = [canvas1, canvas2, canvas3, canvas4]

textLabel1 = XText(1, 0, 2, 0)
textLabel2 = XText(1, 3, 2, 3)
textLabel3 = XText(5, 0, 6, 0)
textLabel4 = XText(5, 3, 6, 3)
textLabel_cont = [textLabel1, textLabel2, textLabel3, textLabel4]

space1 = XSpace(0, 2)
space2 = XSpace(3, 0)
space3 = XSpace(3, 3)
space4 = XSpace(4, 2)
space5 = XSpace(7, 0)
space6 = XSpace(0, 5)
space7 = XSpace(4, 5)


def set_Canvas_State(state):
    for i in range(0, len(canvas_cont)):
        if i == state:
            canvas_cont[i].set_state("G")
        else:
            canvas_cont[i].set_state("R")


def main_PAAC():
    canvas1.set_state("Y")
    canvas2.set_state("G")
    canvas3.set_state("R")
    canvas4.set_state("Y")
    while True:
        sleep(0.1)
        for i in range(0, len(canvas_cont)):
            vehicle_count = arr[i].count
            print(str(i)+" : "+str(vehicle_count))
            wait_time = vehicle_count*2
            print("Wait time : "+str(wait_time))
            if wait_time < 1:
                set_Canvas_State(-1)
            else:
                if wait_time > 60:
                    wait_time = 60
                set_Canvas_State(i)
                display_counts_cont[i].Xlock = "locked"
                display_timer = display_counts_timer(
                    textLabel_cont[i], int(wait_time+5))
                display_timer.start()
                sleep(wait_time+5)
                display_counts_cont[i].Xlock = "unlocked"
                arr[i].count = 0
                print("Should be 0 :"+str(arr[i].count))


class display_counts(threading.Thread):
    def __init__(self, ti_var, xtext_var):
        threading.Thread.__init__(self)
        self.ti_var = ti_var
        self.xtext_var = xtext_var
        self.Xlock = "unlocked"

    def run(self):
        while True:
            sleep(0.1)
            if self.Xlock == "unlocked":
                self.xtext_var.set_countLabel_Text(
                    "Current Vehicle Count : "+str(self.ti_var.count))
                if self.ti_var.count > 0:
                    self.xtext_var.set_timeLabel_Text(
                        "Current Wait Time : "+str((self.ti_var.count*2)+5))
                else:
                    self.xtext_var.set_timeLabel_Text("Current Wait Time : 0")


class display_counts_timer(threading.Thread):
    def __init__(self, xtext_var, s):
        threading.Thread.__init__(self)
        self.xtext_var = xtext_var
        self.s = s

    def run(self):
        self.xtext_var.set_countLabel_Text("Remaining time to wait : ")
        time = int(self.s)
        while time != 0:
            sleep(1)
            time = time-1
            self.xtext_var.set_timeLabel_Text(str(time))


x = ti('Data/second/Lane1mod.mp4', label_1)
y = ti('Data/second/Lane2mod.mp4', label_2)
z = ti('Data/second/Lane3mod.mp4', label_3)
q = ti('Data/second/Lane4mod.mp4', label_4)
arr = [x, y, z, q]
for x in arr:
    x.daemon = TRUE
    x.start()

d = threading.Thread(target=main_PAAC)
d.daemon = TRUE
d.start()

dc1 = threading.Thread(target=display_counts, args=(x, textLabel1,))
display_counts_cont = []
for i in range(0, 4):
    dc = display_counts(arr[i], textLabel_cont[i])
    dc.daemon = TRUE
    dc.start()
    display_counts_cont.append(dc)
root.mainloop()
# sys.exit()
