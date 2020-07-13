import shutil
import pathlib
import os
import time
import logging
import re


HEIGHT = 400
WIDTH = 800
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

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
pp_folder_td4 = 'preprocess_gen\\'
pp_folder_td5 = 'bld\\_incl\\'
work_folders = ['asw','bsw','aggr']
#Creating an object 
logger=logging.getLogger()
filepath = ""
base_path = ""
Input_folder_path = ""
pp_folder_path = ""
work_folder_path = ""
var = tk.IntVar()
v = tk.StringVar()
values = {"TD4" : "1", 
          "TD5" : "2"}

START_HEADER = "Data Definition"
ID = "Input Data\n"
CD = "Calibration Data\n"
GI = "General Information\n"
AC = "Application Conditions\n"
IA = "Import Actions\n"
CNFD = "Configuration Data\n"
AD = "Action Definitions\n"
ET = "Error treatment\n"

Data_Definition = []
Input_Data = []
Calibration_Data = []
Import_Actions = []
Action_Definitions = []
list_of_NC_to_fetch_frmPP = []
fetched_ncees = []
actions_dict = dict()

class Data:
    def __init__(self):
        self.name = ""
        self.mode = ""
        self.hexR = ""
        self.phyR = ""
        self.rsln = 0.0
        self.unit = ""
        self.desc = ""
        self.isNC = False
        self.isLV = False
        self.isAR = False
        self.dimn = 0
        self.size = []

def identify_DT(hexR):
    if (hexR.strip() == "F32"):
        return 'f32'
    elif(hexR.strip().find('\n') > 0):
        return 'u8'
    else:
        rnge = hexR.strip().split('... ')
        lr = int(rnge[0].strip(),16)
        ur = int(rnge[1].strip('[ H]'),16) 
        if lr>ur:
            if ur < 256:
                return 's8'
            elif ur < 65536:
                return 's16'
            elif ur < 4294967296:
                return 's32'
            else:
                return 's64'
        else:
            if ur < 256:
                return 'u8'
            elif ur < 65536:
                return 'u16'
            elif ur < 4294967296:
                return 'u32'
            else:
                return 'u64'

def update_list_if_stringdataEXIST(list):
    length = len(list)
    i=9;
    while i < length:
        if list[i].find('\n')>0:
            list.insert(i+1,'-')
        i = i+9
    return list

def fetch_NC_def_frmPP():
    nc_set = set()
    global list_of_NC_to_fetch_frmPP
    global pp_folder_path
    global fetched_ncees
    with open(os.path.join(pp_folder_path,'all_hash_defines.h'),'w') as wfh:
        for root, dirs, files in os.walk(pp_folder_path):
            for file in files:
                if file.endswith('.h') and (not file.endswith('_mcr.h')) and (not file.endswith('tmp_inp.h')) and (not file.endswith('all_actions.h')) and (not file.endswith('all_hash_defines.h')):
                    with open(os.path.join(root,file),'r') as rfh:
                        s = " "
                        while s:
                            s = rfh.readline()
                            if s.strip().startswith('#define'):
                                wfh.write(s.strip()+'\n')
    nc_set = set(list_of_NC_to_fetch_frmPP)
    with open(os.path.join(pp_folder_path,'all_hash_defines.h'),'r') as rfh:
        for ncees in nc_set:
            found = False
            rfh.seek(0)
            s = " "
            while s:
                s = rfh.readline()
                if s.startswith('#define '+ncees) or s.startswith('#define'+'\t'+ncees):
                    fetched_ncees.append(s)
                    found = True
                    break
            if not found:
                coment = '//NC not found in preprocess_gen. Dummy value here\n'
                def_nc = coment+'#define'+'\t'+ncees+'\t'+'(1)'
                fetched_ncees.append(def_nc)

def Parse_Inputs(rawdata):
    global list_of_NC_to_fetch_frmPP
    tmp_list = []
    lis = rawdata.split(chr(7))
    lis = update_list_if_stringdataEXIST(lis)
    length = len(lis)
    no_of_data = int((length - 7)/9)
    for i in range(0,no_of_data):
        dat = Data()
        dat.name = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[7+i*9])
        dat.mode = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[8+i*9])
        dat.hexR = re.sub(r'[\x00-\x06,\x08-\x09,\x0B-\x1F]+', '', lis[9+i*9])
        dat.phyR = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[10+i*9])
        dat.rsln = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[11+i*9])
        dat.unit = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[12+i*9])
        dat.desc = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', lis[14+i*9])
        if dat.name.count('[')>0:
            dat.isAR = True
            dat.dimn = dat.name.count('[')
            tmp_size = dat.name.split('[')
            for i in range(1,len(tmp_size)):
                if not tmp_size[i].strip('[ ];]').isnumeric():
                    dat.size.append(tmp_size[i].strip('[ ];]'))
            list_of_NC_to_fetch_frmPP+=dat.size
        tmp_list.append(dat)
    return tmp_list

def Parse_IA(rawdata):
    final_ac_list=[]
    tmp_str = rawdata
    tmp_str = re.sub(r'[\x00-\x06,\x08-\x1F]+', '', tmp_str)
    actions = tmp_str.split('\x07\x07ACTION_')
    tmp_actions = []
    final_ac_list = []
    for i in range(0,len(actions)):
        tmp_actions.append('ACTION_'*(i>0)+actions[i])
    for actns in tmp_actions:
        tmp = re.split('[{ ]',actns)
        final_ac_list.append(tmp[0])
    return final_ac_list

def fetch_ACTIONdefs_frmPP():
    global pp_folder_path
    global actions_dict
    with open(os.path.join(pp_folder_path,'all_actions.h'), "r") as rfh:
        s = " "
        while s:
            s = rfh.readline()
            l_split = re.split('[( ]',s)
            if len(l_split)>2:
                actions_dict.setdefault(l_split[2], []).append(s)

def spec_parser(specpath):
    global START_HEADER
    global GI
    global IA
    global AD
    global CNFD
    global ET
    global Data_Definition
    global Input_Data
    global Calibration_Data
    global list_of_NC_to_fetch_frmPP
    global pp_folder_path
    global fetched_ncees
    global Import_Actions
    global fetched_actions
    global actions_dict
    OpD = False
    InD = False
    CaD = False
    CnD = False
    AcD = False
    ImA = False
    EtD = False
    GnI = False
    logger.debug("Accessing provided spec path : {}\n".format(specpath))
    with open(specpath,'r',encoding='ansi') as rfh:
        s = " "
        while s:
            s = rfh.readline()
            if s.startswith(START_HEADER):
                logger.debug("Start header found...\n")
                OpD = True
                break
        s = rfh.readline()
        while s:
            if (s.endswith(ID) or s.endswith(CD) or s.endswith(CNFD) or s.endswith(AD) or s.endswith(IA) or s.endswith(ET) or s.endswith(GI) or s.endswith(AC)):
                if s.endswith(ID):
                    logger.debug("Data_Definition string found...\nData_Definition string getting parsed...\n")
                    InD = True
                    Data_Definition_str = s
                    Data_Definition = Parse_Inputs(s)
                    logger.debug("Parse success\n")
                elif s.endswith(CD):
                    if InD is True:
                        logger.debug("Input_Data string found...\nInput_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\nData_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                    else:
                        pass
                    CaD = True
                elif s.endswith(CNFD):
                    if CaD is True:
                        #Calibration_Data = Parse_Inputs(s)
                        pass
                    elif InD is True:
                        logger.debug("Input_Data string found...\nInput_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\nData_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    else:
                        pass
                    CnD = True
                elif s.endswith(AD):
                    if CnD is True:
                        #Configuration_Data = Parse_Inputs(s)
                        pass
                    elif CaD is True:
                        #Calibration_Data = Parse_Inputs(s)
                        pass
                    elif InD is True:
                        logger.debug("Input_Data string found...\nInput_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\Data_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    else:
                        pass
                    AcD = True
                elif s.endswith(IA):
                    if AcD is True:
                        #Action_Definitions = Parse_Inputs(s)
                        pass
                    elif CnD is True:
                        #Configuration_Data = Parse_Inputs(s)
                        pass
                    elif CaD is True:
                        #Calibration_Data = Parse_Inputs(s)
                        pass
                    elif InD is True:
                        logger.debug("Input_Data string found...\Input_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\Data_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    else:
                        pass
                    ImA = True
                elif s.endswith(ET):
                    if ImA is True:
                        logger.debug("Import_Actions string found...\Import_Actions string getting parsed...\n")
                        Import_Actions_str = s
                        Import_Actions = Parse_IA(s)
                        logger.debug("Parse success\n")
                        pass
                    elif AcD is True:
                        #Action_Definitions = Parse_IA(s)
                        pass
                    elif CnD is True:
                        #Configuration_Data = Parse_Inputs(s)
                        pass
                    elif CaD is True:
                        #Calibration_Data = Parse_Inputs(s)
                        pass
                    elif InD is True:
                        logger.debug("Input_Data string found...\Input_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\Data_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    else:
                        pass
                    EtD = True
                elif s.endswith(GI) or s.endswith(AC):
                    if EtD is True:
                        #Error_Treatment = Parse_Inputs(s)
                        pass
                    elif ImA is True:
                        logger.debug("Import_Actions string found...\Import_Actions string getting parsed...\n")
                        Import_Actions_str = s
                        Import_Actions = Parse_IA(s)
                        logger.debug("Parse success\n")
                        pass
                    elif AcD is True:
                        #Action_Definitions = Parse_IA(s)
                        pass
                    elif CnD is True:
                        #Configuration_Data = Parse_Inputs(s)
                        pass
                    elif CaD is True:
                        #Calibration_Data = Parse_Inputs(s)
                        pass
                    elif InD is True:
                        logger.debug("Input_Data string found...\Input_Data string getting parsed...\n")
                        Input_Data_str = s
                        Input_Data = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    elif OpD is True:
                        logger.debug("Data_Definition string found...\Data_Definition string getting parsed...\n")
                        Data_Definition_str = s
                        Data_Definition = Parse_Inputs(s)
                        logger.debug("Parse success\n")
                        pass
                    else:
                        pass
                    GnI = True               
                else:
                    pass
                s = rfh.readline()
            else:
                s = s + rfh.readline()
    
            if GnI is True:
                break
        logger.debug("Spec Parse process over\n")
    logger.debug("Spec closed. \n")
    logger.debug("Data_Definition_str : {} \n".format(Data_Definition_str))
    logger.debug("Input_Data_str : {} \n".format(Input_Data_str))
    if ImA is True:
        logger.debug("Import_Actions_str : {} \n".format(Import_Actions_str))
    logger.debug("Creating module_inputs.h ...")
    with open(os.path.join(pp_folder_path,'module_inputs.h'),'w') as wfh:
        dl = []
        for data in Input_Data:
            logger.debug("Identifying data tyoe of {} ...".format(data.name))
            dt = identify_DT(data.hexR)
            logger.debug("Identified as {}..\n".format(dt))
            logger.debug("Creating declaration..\n")
            if data.name.startswith('NC') or data.name.startswith('NLC'):
                if data.name.find('[')>0:
                    name = data.name[0:data.name.find('[')].strip()+'(i)'
                else:
                    name = data.name.strip()
                list_of_NC_to_fetch_frmPP.append(name)
            elif data.name.startswith('LV_'):
                if data.name.find('[')>0:
                    name = data.name[0:data.name.find('[')].lower()+data.name[data.name.find('['):]
                else:
                    name = data.name.lower()
                dl.append('extern\tflag\t'+name+';\n')
            elif data.name.startswith('LC_') or data.name.startswith('C_') or data.name.startswith('CLF_'):
                if data.name.find('[')>0:
                    name = data.name[0:data.name.find('[')].lower()+data.name[data.name.find('['):]
                else:
                    name = data.name.lower()
                dl.append('extern\tconst\t'+dt+'\t'+name+';\n')
            else:
                if data.name.find('[')>0:
                    name = data.name[0:data.name.find('[')].lower()+data.name[data.name.find('['):]
                else:
                    name = data.name.lower()
                dl.append('extern\t'+dt+'\t'+name+';\n')
        logger.debug("Declaration creation process over..\nFetching collected NC's definition from PP folder\n")   
        fetch_NC_def_frmPP()
        logger.debug("Fetch complete in fetched_ncees = {}\nWritting it to module_inputs.h now\n".format(fetched_ncees))
        for nc in fetched_ncees:
            wfh.write(nc)
        logger.debug("Writting data declarations to module_inputs.h\n")
        for data in dl:
            wfh.write(data)
        try:
            logger.debug("Fetching needed action defs from PIS\n")
            fetch_ACTIONdefs_frmPP()
            logger.debug("Fetch completed in form of ACTION dictionary\nNow writting it to module_inputs.h\n")
            for actions in Import_Actions:
                if len(actions_dict[actions])>1:
                    comment = "/*Warning : {} declarations available. Choose one by commenting others*/\n".format(len(actions_dict[actions]))
                    wfh.write(comment)
                    for defs in actions_dict[actions]:
                        wfh.write(defs)
                else:
                    for defs in actions_dict[actions]:
                        wfh.write(defs)
        except:
            logger.debug("Exception occured while collecting or writting Actions - fn name - {}\n".format('fetch_ACTIONdefs_frmPP'))

def copy_grls(entry3):
    global Input_folder_path
    global work_folder_path
    global var
    entry3 = entry3.lower()
    logger.debug("Proceeding to copy grl's by scanning checkbutton...")
    if var.get()==1:
        logger.debug("Checkbutton enabled. Looking for files...")
        for root,dirs,files in os.walk(work_folder_path):
            for file in files:
                if file.endswith('.grl') and file.startswith(entry3):
                    if entry3+'.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_confi.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_confi_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_confi0.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_confi0_prj.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_nvdat.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
                    if entry3+'_nvdat0.grl' == file:
                        shutil.copyfile(os.path.join(root,file),os.path.join(Input_folder_path,file))
    for root,dirs,files in os.walk(work_folder_path):
        for file in files:
            if file == 'fcut.grl':
                logger.debug("Copying fcut grl file...")
                shutil.copyfile(os.path.join(root,'fcut.grl'),os.path.join(Input_folder_path,'fcut.grl'))
            if file == 'local_data_type.grl':
                logger.debug("Copying local_data_type grl file...")
                shutil.copyfile(os.path.join(root,'local_data_type.grl'),os.path.join(Input_folder_path,'local_data_type.grl'))


def collect_nc_data_n_actions(specpath):
    global pp_folder_path
    global base_path
    global work_folder_path
    global logger
    global work_folders
    global Input_folder_path
    work_folder_path = os.path.join(base_path,'work')
    
    logger.debug("Proceeding to collect ACTIONS...")
    with open(os.path.join(pp_folder_path,'all_actions.h'), "w") as wfh_var:
        wfh_var.write('#ifndef ALL_ACTIONS_H\n')
        wfh_var.write('#define ALL_ACTIONS_H\n')
        #collecting actions
        work_folder_path = os.path.join(base_path,'work')
        for dirss in work_folders:
            logger.debug("Scanning directory {} for action prototypes...".format(dirss))
            action_folder_path = os.path.join(work_folder_path,dirss)
            for roott, dirrs, filess in os.walk(action_folder_path):
                for file in filess:
                    if file.endswith('.h') and (not file.endswith('_mcr.h')):
                        logger.debug("{} scanning".format(file))
                        with open(os.path.join(roott,file), "r") as rfhh:
                            s = " "
                            while(s):
                                s = rfhh.readline()
                                if s.strip().startswith(decl):
                                    s = s.strip()
                                    L = s.split()
                                    size = len(L)
                                    if size>2:
                                        if ((L[1] in datatypes) or (L[1] == "void")) and L[2].startswith(action) and (s[-1] == ';'):
                                            brac = s.find('(')
                                            le = len(s)
                                            args = (s[brac+1:-2].strip()).split(',')
                                            if len(args)==1 and args[0]=='void':
                                                wfh_var.write(s+'\n')
                                            else:
                                                knwn = 1
                                                for each in args:
                                                    if knwn==1:
                                                        dt_par = each.split()
                                                        for ech in dt_par:
                                                            if (ech.strip()).strip('*') in datatypes:
                                                                knwn = 1
                                                                break
                                                            else:
                                                                knwn = 0
                                                    else:
                                                        break
                                                if knwn==1:
                                                        wfh_var.write(s+'\n')
        logger.debug("ACTION's collected!!")
        wfh_var.write('#endif\n')
    try:
        logger.debug("Spec parsing started for spec {}...\n".format(specpath)) 
        spec_parser(specpath)
        logger.debug("Spec parsing complete with out errors!!")
    except OSError as error:
        logger.debug("Exception occured while parsing spec\n")

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
                logger.debug("#include found in - {}".format(s))
                s = s.strip()
                L = s.split('<')
                size = len(L)
                if size>1:
                    name = L[1][:-1]
                namelist.append(name)
        finallist = set(namelist)
        path_split = str(filepath).split('\\')
        logger.debug("Path split...")
        path_split[len(path_split)-1] = path_split[len(path_split)-1].replace('.c','_im.h')
        logger.debug("Renamed...")
        imfile = path_split[len(path_split)-1]
        if imfile in finallist:
            logger.debug("module import header found...")
            ext_path = ""
            for dirt in path_split:
                ext_path = ext_path+dirt+'\\'
            logger.debug("new path : {}...".format(ext_path))
            ext_path = pathlib.Path(pathlib.PureWindowsPath(ext_path))
            namelist = []
            with open(ext_path, "r") as rfh_2:
                logger.debug("module import header opened for reading...")
                s = " "
                while(s):
                    s = rfh_2.readline()
                    if s.startswith(include):
                        logger.debug("#include found in - {}".format(s))
                        s = s.strip()
                        L = s.split('<')
                        size = len(L)
                        if size>1:
                            name = L[1][:-1]
                        namelist.append(name)
            for files in namelist:
                finallist.add(files)
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
                    guard3 = '#endif'
                    wfh_1.write(guard1 + '\n')
                    wfh_1.write(guard2)
                    wfh_1.write('\n'*10)
                    wfh_1.write(guard3)
            logger.debug("Headers created !!Moving module_inputs.h to Collect_Inputs folder\n")
            shutil.move(os.path.join(pp_folder_path,'module_inputs.h'),os.path.join(Input_folder_path,'module_inputs.h'))
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

def gen_file_api(entry,entry3,entry2):
    global base_path
    global Input_folder_path
    global work_folder_path
    global filepath
    global pp_folder
    global pp_folder_path
    global v
    start = time.time()
    filepath = pathlib.Path(pathlib.PureWindowsPath(entry))
    specpath = pathlib.Path(pathlib.PureWindowsPath(entry2))
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
        fols_in_PIS = os.listdir(base_path)
        try:
            if os.path.isdir(os.path.join(base_path,pp_folder_td4)):
                pp_folder_path = os.path.join(base_path,pp_folder_td4)
            else:
                for dirss in fols_in_PIS:
                    if dirss.startswith('_FS_'):
                        pp_folder_path = os.path.join(base_path,dirss,pp_folder_td5)
                        break
        except OSError as error:
            fail_message = "Exception occoured while finding preprocess_gen folder for selected build platform.\n Please use builded software."
            lo_label3.config(fg='#ff0000',text = fail_message)
            
        setuplogger()
        logger.debug("Logger setup...\nEntered path: <{}>\n".format(filepath)) 
        logger.debug("Proceeding to collect NC's, variables and ACTION's...\n") 
        try:
            collect_nc_data_n_actions(specpath)
            logger.debug("NC's, variables and ACTION's collected successfully !!\nProceeding to create dummy headers...\n") 
            try:
                create_dummy_files()
                logger.debug("Creation of Collect_Inputs folder and dummy headers successfull !!\nProceeding to copy grl's...\n") 
                try:
                    copy_grls(entry3)
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

    
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH,bg='#FAD15A' )
canvas.pack()
frame = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
frame.place(relx=0.008,rely=0.025,relwidth=0.984,relheight=0.115)
frame2 = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
frame2.place(relx=0.008,rely=0.155,relwidth=0.984,relheight=0.115)
label = tk.Label(frame, text="C-File:", font=('Times',15))
label.place(relx=0.0001,relwidth=0.08,relheight=1)
entry1 = tk.Entry(frame, bg='white',font=('Serif',12))
entry1.place(relx=0.090,relwidth=0.75,relheight=1)

label2 = tk.Label(frame2, text="Spec:", font=('Times',15))
label2.place(relx=0.0001,relwidth=0.08,relheight=1)
entry2 = tk.Entry(frame2, bg='white',font=('Serif',12))
entry2.place(relx=0.090,relwidth=0.91,relheight=1)

lower_frame = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
entry3 = tk.Entry(lower_frame, bg='white',font=("Serif",12))
lowerside_frame = tk.Frame(root, bd=5,highlightbackground="black",highlightthickness=1)
label_lsf = tk.Label(lowerside_frame, text="Build Platform :", font=('Serif',11,'bold'))

button = tk.Button(frame, text="Generate Files", bg='#c2c2a3', font=('Times',14), command=lambda: gen_file_api(entry1.get(),entry3.get(),entry2.get()))
button.place(relx=0.845,relwidth=0.1549,relheight=1)
button.config(state=DISABLED)

lower_frame.place(relx=0.008,rely=0.285,relwidth=0.5, relheight=0.205)
entry3.place(relx=0.08,rely=0.5,relwidth=0.15,relheight=0.39)
entry3.config(state=DISABLED)
#print(v.get())

def Rbuttoncheck():
    global v
    if v.get() == '1' or v.get() == '2':
        button.config(state=NORMAL)
    else:
        button.config(state=DISABLED)

lowerside_frame.place(relx=0.516,rely=0.285,relwidth=0.476, relheight=0.205)
label_lsf.place(relx=0.008,rely=0.1,relwidth=0.3,relheight=0.3)
for (text, value) in values.items(): 
    Radiobutton(lowerside_frame, text = text, variable = v, value = value, command=Rbuttoncheck).pack(side = TOP, ipady = 8)

def activateCheck():
    global var
    if var.get() == 1:
        entry3.config(state=NORMAL)
    elif var.get() == 0:
        entry3.config(state=DISABLED)

cb = tk.Checkbutton(lower_frame,text='Enable to copy aggr specific common grl files',font=('Serif',11,'bold'),variable=var,command=activateCheck,anchor='nw')
cb.place(rely=0.03,relwidth=1,relheight=0.45)

lower_frame2 = tk.Frame(root,bg='#f6f678', bd=3,highlightbackground="black",highlightthickness=1)
lower_frame2.place(relx=0.008,rely=0.505,relwidth=0.984,relheight=0.48)

lo_label3 = tk.Label(lower_frame2,font=('Serif',9,'bold'),anchor='nw', justify='left')
lo_label3.place(relx=0.0001,rely=0,relwidth=0.9998,relheight=1)

root.mainloop()
