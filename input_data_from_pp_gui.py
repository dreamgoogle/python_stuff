import shutil
import pathlib
import os
import time
import logging

HEIGHT = 200
WIDTH = 700
import tkinter as tk
from tkinter import *
root = tk.Tk()
root.wm_title("Collect Inputs_V_1.0")
include = "#include"
action = "ACTION_"
decl = "extern"
decl_only_farm = "    extern"
functions = "extern void"
nc1 = "#define\tN"
nc2 = "#define N"
datatypes = ['boolean','u8','s8','u16','s16','u32','s32','u64','s64','flag','f32','f64','unsigned','signed','uint32','sint32','float','uint16','sint16','uint8','sint8','uint64','sint64','int','char']
pp_folder = 'preprocess_gen\\'
work_folders = ['asw','bsw','aggr']
#Creating an object 
logger=logging.getLogger()
filepath = ""
base_path = ""
Input_folder_path = ""
pp_folder_path = ""
work_folder_path = ""
var = tk.IntVar()

def copy_grls(entry2):
    global Input_folder_path
    global work_folder_path
    global var
    entry2 = entry2.lower()
    logger.debug("Proceeding to copy grl's by scanning checkbutton...")
    if var.get()==1:
        logger.debug("Checkbutton enabled. Looking for files...")
        for root,dirs,files in os.walk(work_folder_path):
            for file in files:
                if file.endswith('.grl') and file.startswith(entry2):
                    if entry2+'.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_confi.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_confi_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_confi0.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_confi0_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_nvdat.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry2+'_nvdat0.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
    for root,dirs,files in os.walk(work_folder_path):
        for file in files:
            if file == 'fcut.grl':
                logger.debug("Copying fcut grl file...")
                shutil.copyfile(os.path.join(root,'fcut.grl'),os.path.join(Input_folder_path,'fcut.grl'))
            if file == 'local_data_type.grl':
                logger.debug("Copying local_data_type grl file...")
                shutil.copyfile(os.path.join(root,'local_data_type.grl'),os.path.join(Input_folder_path,'local_data_type.grl'))


def collect_nc_data_n_actions():
    global pp_folder_path
    global base_path
    global work_folder_path
    global logger
    logger.debug("Proceeding to scan preprocess_gen folder...")
    for root, dirs, files in os.walk(pp_folder_path):
        logger.debug("Scan sucess !!\nProceeding to create temporay file(tmp_inp.h)..")
        with open(os.path.join(root,'tmp_inp.h'), "w") as wfh_tmp:
            logger.debug("tmp_inp.h created !!\nProceeding to filter out only needed files and then extract relevant part from them..")
            for file in files:
                if file.endswith('.h') and (not file.endswith('_mcr.h')) and (not file.endswith('tmp_inp.h')) and (not file.endswith('all_inputs.h')):
                    with open(os.path.join(root,file), "r") as rfh:
                        s = " "
                        while(s):
                            s = rfh.readline()
                            if s.startswith(nc1) or s.startswith(nc2):
                                wfh_tmp.write(s)
                            elif s.startswith(decl) and (not(s.startswith(functions) or s.endswith(");\n"))):
                                L = s.split()
                                size = len(L)
                                if (size > 2):
                                    if (L[1] in datatypes or L[2] in datatypes):
                                        wfh_tmp.write(s)
            logger.debug("All NC's and variables collected to tmp_inp.h.\nProceeding to sort...")
        #sorting NC's before variables into all_inputs.h
        with open(os.path.join(root,'tmp_inp.h'), "r") as rfh_var:
            with open(os.path.join(root,'all_inputs.h'), "w+") as wfh_var:
                s = " "
                while(s):
                    s = rfh_var.readline()
                    if s.startswith(nc1) or s.startswith(nc2):
                        wfh_var.write(s)
                rfh_var.seek(0)
                s = " "
                while(s):
                    s = rfh_var.readline()
                    if s.startswith(decl):
                        wfh_var.write(s)
                logger.debug("Sort complete and available in all_inputs.h!! \nProceeding to collect ACTIONS by scanning work folder...")
                #collecting actions
                work_folder_path = os.path.join(base_path,'work')
                for dirss in work_folders:
                    action_folder_path = os.path.join(work_folder_path,dirss)
                    for roott, dirrs, filess in os.walk(action_folder_path):
                        for file in filess:
                            if file.endswith('.h') and (not file.endswith('_mcr.h')):
                                with open(os.path.join(roott,file), "r") as rfhh:
                                    s = " "
                                    while(s):
                                        s = rfhh.readline()
                                        if s.startswith(decl) or s.startswith(decl_only_farm):
                                            L = s.split()
                                            size = len(L)
                                            if size>2:
                                                if ((L[1] in datatypes) or (L[1] == "void")) and L[2].startswith(action) and (s[-2] == ';'):
                                                    if L[1] == "void" :
                                                        wfh_var.write(s[:-2] + '{}' + '\n')
                                                    else:
                                                        definitn = s[:-2] + '{'+'return ({})0;'.format(L[1])+'}'
                                                        wfh_var.write(definitn + '\n')
                logger.debug("ACTION's collected!!")
            wfh_var.close()

def create_dummy_files():
    global pp_folder_path
    global base_path
    global work_folder_path
    global filepath
    global Input_folder_path
    namelist = []
    logger.debug("Opening the file to collect list of needed headers...!!")
    with open(filepath, "r") as rfh_1:
        s = " "
        while(s):
            s = rfh_1.readline()
            if s.startswith(include):
                L = s.split()
                size = len(L)
                if size>1:
                    name = L[1][1:-1]
                elif s.endswith('>\n'):
                    L = s.split('<')
                    name = L[1][:-2]
                namelist.append(name)
        finallist = set(namelist)
        logger.debug("List obtained!! \nProceeding to create Collect_Inputs folder and dummy headers...!!")
        try:
            Input_folder_path = os.path.join(pp_folder_path,'Collect_Inputs')
            f = [x[1] for x in os.walk(pp_folder_path)]
            if 'Collect_Inputs' in f[0]:
                shutil.rmtree(Input_folder_path)
                os.mkdir(Input_folder_path)
            else:
                os.mkdir(Input_folder_path)
            logger.debug("Collect_Inputs folder created !!\nCreating headers...!!")
            for names in finallist:
                with open(os.path.join(Input_folder_path,names), "w+") as wfh_1:
                    name = names.upper()
                    name = name.replace('.','_')
                    guard1 = '#ifndef '+name
                    guard2 = '#define '+name
                    guard3 = 'endif'
                    wfh_1.write(guard1 + '\n')
                    wfh_1.write(guard2)
                    wfh_1.write('\n'*10)
                    wfh_1.write(guard3)
            logger.debug("Headers created !!\nMoving all_inputs.h ...!!")
            shutil.move(os.path.join(pp_folder_path,'all_inputs.h'),os.path.join(Input_folder_path,'all_inputs.h'))
            logger.debug("Move complete!!")
        except OSError as error:
            logger.debug("Exception occoured while removing old Collect_Inputs folder and \nsubsequently creating dummy files!!")
            fail_message = "Exception occoured while removing old Collect_Inputs folder and \nsubsequently creating dummy files!!\nEnsure Collect_Inputs folder or its files are not in use."
            lo_label3.config(fg='#ff0000',text = fail_message)

def setuplogger():
    global pp_folder_path
    #Create and configure logger 
    logging.basicConfig(filename=os.path.join(pp_folder_path,"debug.log"), format='%(asctime)s %(message)s', filemode='w')   
    #Setting the threshold of logger to DEBUG 
    logger.setLevel(logging.DEBUG)

def gen_file_api(entry,entry2):
    global base_path
    global Input_folder_path
    global work_folder_path
    global filepath
    global pp_folder
    global pp_folder_path
    start = time.time()
    filepath = pathlib.Path(pathlib.PureWindowsPath(entry))
    split_fp = str(filepath).split('\\')
    base_path = ""
    valid_path = False
    for fols in split_fp:
        if fols != 'work':
            base_path = base_path+fols+'\\'
        else:
            valid_path = True
            break
    if valid_path is True:
        pp_folder_path = os.path.join(base_path,pp_folder)
        setuplogger()
        logger.debug("Logger setup...\nProceeding to collect NC's, variables and ACTION's...\n") 
        try:
            collect_nc_data_n_actions()
            logger.debug("NC's, variables and ACTION's collected successfully !!\nProceeding to create dummy headers...\n") 
            try:
                create_dummy_files()
                logger.debug("Creation of Collect_Inputs folder and dummy headers successfull !!\nProceeding to copy grl's...\n") 
                try:
                    copy_grls(entry2)
                    logger.debug("Copy successfull !!\nReady for next run...\n")
                    logger.debug("---------------------------------------------")
                    shutil.copyfile(os.path.join(pp_folder_path,'debug.log'),os.path.join(Input_folder_path,'debug.log'))
                    end = time.time()
                    tt = round((end-start),3)
                    pass_message = "Find all inputs in Collect_Inputs folder created at\n"+Input_folder_path+"\nTask finished in {a} secs.".format(a=tt)
                    lo_label3.config(fg='#000099',text = pass_message)
                except OSError as error:
                    fail_message = "Exception occoured while copying grl files!!"
                    lo_label3.config(fg='#ff0000',text = fail_message)
            except OSError as error:
                fail_message = "Exception occoured while creating dummy files!!\nPlease check the entered path\n{a}\nIdeally it should end with a c-file name available inside work folder".format(a=entry)
                lo_label3.config(fg='#ff0000',text = fail_message)
        except OSError as error:
            fail_message = "Exception occoured while collecting NC's, data and actions!!"
            lo_label3.config(fg='#ff0000',text = fail_message)
    else:
        fail_message = "Invalid path!! \nCopy the full file path"
        lo_label3.config(fg='#ff0000',text = fail_message)
    

    
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH,bg='#f6f678' )
canvas.pack()
frame = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
frame.place(relx=0.008,rely=0.03,relwidth=0.984,relheight=0.18)

label = tk.Label(frame, text="Path :", font=('Times',15))
label.place(relx=0.0001,relwidth=0.08,relheight=1)

entry1 = tk.Entry(frame, bg='white',font=('Serif',10))
entry1.place(relx=0.090,relwidth=0.73,relheight=1)
lower_frame = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
entry2 = tk.Entry(lower_frame, bg='white',font=("Serif",10))

button = tk.Button(frame, text="Generate Files", bg='#c2c2a3', font=('Times',13), command=lambda: gen_file_api(entry1.get(),entry2.get()))
button.place(relx=0.83,relwidth=0.1699,relheight=1)

lower_frame.place(relx=0.008,rely=0.24,relwidth=0.5, relheight=0.3)
entry2.place(relx=0.08,rely=0.5,relwidth=0.15,relheight=0.4)
entry2.config(state=DISABLED)

def activateCheck():
    global var
    if var.get() == 1:
        entry2.config(state=NORMAL)
    elif var.get() == 0:
        entry2.config(state=DISABLED)

cb = tk.Checkbutton(lower_frame,text='Enable to copy aggr specific common grl files',font=('Serif',10,'bold'),variable=var,command=activateCheck,anchor='nw')
cb.place(rely=0.001,relwidth=1,relheight=0.45)

lower_frame2 = tk.Frame(root,bg='#f6f678', bd=3,highlightbackground="black",highlightthickness=1)
lower_frame2.place(relx=0.008,rely=0.57,relwidth=0.984,relheight=0.40)

lo_label3 = tk.Label(lower_frame2,font=('Serif',9,'bold'),anchor='nw', justify='left')
lo_label3.place(relx=0.0001,rely=0,relwidth=0.9998,relheight=1)

root.mainloop()
