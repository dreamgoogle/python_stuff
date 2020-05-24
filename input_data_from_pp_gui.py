import os
import time
start = time.time()
status = ""
HEIGHT = 200
WIDTH = 600
import tkinter as Collect_data_TK
from tkinter import font
root = Collect_data_TK.Tk()
decl = "extern"
functions = "extern void"
nc = "#define\tN"
datatypes = ['boolean','u8','s8','u16','s16','u32','s32','u64','s64','flag','f32','f64','unsigned','signed','uint32','sint32','float','uint16','sint16','uint8','sint8','uint64','sint64','int','char']
def gen_file_api(entry):
    try:
        for root, dirs, files in os.walk(entry):
            start = time.time()
            with open(os.path.join(root,'tmp_inp.h'), "w") as wfh_tmp:
                for file in files:
                    if file.endswith('.h') and (not file.endswith('_mcr.h')) and (not file.endswith('tmp_inp.h')) and (not file.endswith('all_inputs.h')):
                        with open(os.path.join(root,file), "r") as rfh:
                            s = " "
                            while(s):
                                s = rfh.readline()
                                if s.startswith(nc):
                                    wfh_tmp.write(s)
                                elif s.startswith(decl) and (not(s.startswith(functions) or s.endswith(");\n"))):
                                    L = s.split()
                                    size = len(L)
                                    if (size > 2):
                                        if (L[1] in datatypes or L[2] in datatypes):
                                            wfh_tmp.write(s)
            with open(os.path.join(root,'tmp_inp.h'), "r") as rfh_var:
                with open(os.path.join(root,'all_inputs.h'), "w+") as wfh_var:
                    s = " "
                    while(s):
                        s = rfh_var.readline()
                        if s.startswith(nc):
                            wfh_var.write(s)
                    rfh_var.seek(0)
                    s = " "
                    while(s):
                        s = rfh_var.readline()
                        if s.startswith(decl):
                            wfh_var.write(s)
            end = time.time()
            tt = round((end-start),3)
            lo_label['text'] = "all_inputs.h created at\n" + root
            lo_label2['text'] = "Task finished in {a} secs.".format(a=tt)
    except:
        lo_label3 = Collect_data_TK.Label(lower_frame,font=('Courier',10,'bold'),anchor='nw', justify='left',fg='#ff0000')
        lo_label3.place(relx=0.0001,rely=0,relwidth=0.9998,relheight=0.3)
        lo_label3['text'] = "Exception occoured !!"

canvas = Collect_data_TK.Canvas(root, height=HEIGHT, width=WIDTH )
canvas.pack()

frame = Collect_data_TK.Frame(root, bg='#f6f678', bd=5)
frame.place(relwidth=1,relheight=0.2)

label = Collect_data_TK.Label(frame, text="Path :", font=('Times',15))
label.place(relx=0.0001,relwidth=0.08,relheight=1)

entry = Collect_data_TK.Entry(frame, bg='white',font=('Times',14))
entry.place(relx=0.090,relwidth=0.73,relheight=1)

button = Collect_data_TK.Button(frame, text="Generate File", bg='gray', font=('Times',13), command=lambda: gen_file_api(entry.get()))
button.place(relx=0.83,relwidth=0.1699,relheight=1)

lower_frame = Collect_data_TK.Frame(root, bg='#f6f678',bd=5)
lower_frame.place(rely=0.18,relwidth=1, relheight=0.80)

lo_label = Collect_data_TK.Label(lower_frame,font=('Courier',10,'bold'),anchor='nw', justify='left',fg='#0000ff')
lo_label.place(relx=0.0001,rely=0,relwidth=0.9998,relheight=0.3)

lo_label2 = Collect_data_TK.Label(lower_frame,font=('Courier',10,'bold'),anchor='nw', justify='left',fg='#0000ff')
lo_label2.place(relx=0.0001,rely=0.3,relwidth=0.9998,relheight=0.7)

root.mainloop()
