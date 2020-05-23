import os
status = ""
HEIGHT = 200
WIDTH = 600
import tkinter as tk
from tkinter import font
root = tk.Tk()

def gen_file_api(entry):
	try:
		for root, dirs, files in os.walk(entry):
			with open(os.path.join(root,'all_inputs.h'), "w") as wfh:
				for file in files:
					if file.endswith('.h'):
						with open(os.path.join(root,file), "r") as rfh:
							word = "extern"
							s = " "
							while(s):
								s = rfh.readline()
								L=s.split()
								if(word in L) or ('#define' in L):
									wfh.write(s)
			lo_label['text'] = "all_inputs.h created at \n" + root
	except:
		lo_label['text'] = "Path Incorrect !! Please check."

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH )
canvas.pack()

frame = tk.Frame(root, bg='#f6f678', bd=5)
frame.place(relwidth=1,relheight=0.2)

label = tk.Label(frame, text="Path :", font=('Times',15))
label.place(relx=0.0001,relwidth=0.08,relheight=1)

entry = tk.Entry(frame, bg='white',font=('Times',15))
entry.place(relx=0.090,relwidth=0.73,relheight=1)

button = tk.Button(frame, text="Generate File", bg='gray', font=('Times',13), command=lambda: gen_file_api(entry.get()))
button.place(relx=0.83,relwidth=0.1699,relheight=1)

lower_frame = tk.Frame(root, bg='#f6f678',bd=5)
lower_frame.place(rely=0.18,relwidth=1, relheight=0.80)

lo_label = tk.Label(lower_frame,font=('Courier',12,'bold'),anchor='nw', justify='left')
lo_label.place(relx=0.0001,relwidth=0.9998,relheight=1)

root.mainloop()
