import os
status = ""
HEIGHT = 200
WIDTH = 600
import tkinter as Collect_data_TK
from tkinter import font
root = Collect_data_TK.Tk()
decl = "extern"
nc = "#define\tN"
def gen_file_api(entry):
	try:
		for root, dirs, files in os.walk(entry):
			with open(os.path.join(root,'all_inputs.h'), "w") as wfh_var:
				for file in files:
					if file.endswith('.h') and (not file.endswith('_mcr.h')) and (not file.endswith('all_inputs.h')):
						with open(os.path.join(root,file), "r") as rfh:
							s = " "
							while(s):
								s = rfh.readline()
								if s.startswith(decl) or s.startswith(nc):
									wfh_var.write(s)
			lo_label['text'] = "all_inputs.h created at \n" + root
	except:
		lo_label['text'] = "Path Incorrect !! Please check."

canvas = Collect_data_TK.Canvas(root, height=HEIGHT, width=WIDTH )
canvas.pack()

frame = Collect_data_TK.Frame(root, bg='#f6f678', bd=5)
frame.place(relwidth=1,relheight=0.2)

label = Collect_data_TK.Label(frame, text="Path :", font=('Times',15))
label.place(relx=0.0001,relwidth=0.08,relheight=1)

entry = Collect_data_TK.Entry(frame, bg='white',font=('Times',15))
entry.place(relx=0.090,relwidth=0.73,relheight=1)

button = Collect_data_TK.Button(frame, text="Generate File", bg='gray', font=('Times',13), command=lambda: gen_file_api(entry.get()))
button.place(relx=0.83,relwidth=0.1699,relheight=1)

lower_frame = Collect_data_TK.Frame(root, bg='#f6f678',bd=5)
lower_frame.place(rely=0.18,relwidth=1, relheight=0.80)

lo_label = Collect_data_TK.Label(lower_frame,font=('Courier',12,'bold'),anchor='nw', justify='left')
lo_label.place(relx=0.0001,relwidth=0.9998,relheight=1)

root.mainloop()
