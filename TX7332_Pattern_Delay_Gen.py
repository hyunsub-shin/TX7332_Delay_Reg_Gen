#######################################################################
##                  Used for TX7332                                  ##
##                  channel delay calculator                         ##
#######################################################################
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

'''
Make exe file cmd
 - pyinstaller -w -F effect_control.py
modify effect_control.spec file
 - add ui & icon files
    # -*- mode: python ; coding: utf-8 -*-
    files = [('effect_control.ui','.'),('text2img.ico','.')] <===== add
    
 - change datas=[]
    a = Analysis(['control.py'],
                pathex=[],
                binaries=[],
                datas=[], =====>> change : datas=files,
                
 - Add icon file
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        icon='text2img.ico', <===== add icon
        
one more Make exe file cmd
 - pyinstaller effect_control.spec
'''

####################################################
app = QtWidgets.QApplication([])
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
ui = uic.loadUi(BASE_DIR + r'\TX7332_Pattern_Delay_Gen.ui')
ui.setWindowTitle("TX7332 Delay & Pattern Reg Generator")
####################################################


def Linear_Gen_Delay():
    delay_data = np.float16(np.zeros(32))
    delay_int = np.int16(np.zeros(32))
    df = pd.DataFrame(delay_data)
    
    clock = float(ui.lineEdit_clock.text())
    focus = float(ui.lineEdit_focus_L.text())/1000
    pitch = float(ui.lineEdit_pitch_L.text())/1000
    sound_speed = float(ui.lineEdit_sound_speed.text())
    ref_delay = float((np.sqrt(focus**2 + (pitch*15.5)**2))/sound_speed * (clock*1000000))
    
    for i in range(32):
        delay_data[i] = ref_delay - np.sqrt(focus**2 + (pitch*(i+1 - 16.5))**2)/sound_speed * clock*1000000
        delay_int[i] = int(round(delay_data[i]))
        # print(hex(delay_hex[i])[2:].zfill(4).upper())        
        df[i:] = str(hex(delay_int[i])[2:].zfill(4).upper())
    
    df1 = df.transpose()
    # print(df1)
    
    name = "Probe_Focus_" + ui.lineEdit_focus_L.text() + "mm_Linear"
    if ui.checkBox_file.isChecked():
        df1.to_excel(name + ".xlsx")  
        df1.to_csv(name + ".csv")
    
    Delay_count(delay_int)
    Delay_hex(delay_int)
    Gen_Delay_Table(delay_int, name, 0)
    display_plot(delay_int,delay_int,delay_int,delay_int)
    
    # plt.figure()
    # plt.title('channel delay_'+ui.lineEdit_focus_L.text()+"mm")
    # plt.xlabel('channel')
    # plt.ylabel("delay")
    # plt.plot(delay_int)
    # plt.grid()
    # plt.show()


def Convex_Gen_Delay():
    delay_data = np.float16(np.zeros(32))
    delay_int = np.int16(np.zeros(32))
    df = pd.DataFrame(delay_data)
    
    clock = float(ui.lineEdit_clock.text())
    focus = float(ui.lineEdit_focus_C.text())/1000
    pitch = float(ui.lineEdit_pitch_C.text())/1000
    sound_speed = float(ui.lineEdit_sound_speed.text())
    radius = float(ui.lineEdit_radius.text())
    view_angle = 32 * pitch / radius
    dtheta = pitch / radius
    start_angle = -view_angle/2 + 0.5*dtheta
    ref_delay = np.sqrt((radius*np.cos(start_angle)-radius-focus)**2 + 
                        (radius*np.sin(start_angle))**2)/sound_speed*(clock*1000000)
    
    for i in range(32):
        delay_data[i] = ref_delay - np.sqrt((radius*np.cos(start_angle+dtheta*((i+1)-1))-radius-focus)**2 + 
                                            (radius*np.sin(start_angle+dtheta*((i+1)-1)))**2)/sound_speed*(clock*1000000)
        delay_int[i] = int(round(delay_data[i]))
        # print(hex(delay_hex[i])[2:].zfill(4).upper())        
        df[i:] = str(hex(delay_int[i])[2:].zfill(4).upper())
    
    df1 = df.transpose()
    # print(df1)
    
    name = "Probe_Focus_" + ui.lineEdit_focus_C.text() + "mm_Convex" 
    if ui.checkBox_file.isChecked():
        df1.to_excel(name + ".xlsx")
        df1.to_csv(name + ".csv")
    
    Delay_count(delay_int)
    Delay_hex(delay_int)
    Gen_Delay_Table(delay_int, name, 0)
    display_plot(delay_int,delay_int,delay_int,delay_int)
    
    # plt.figure()
    # plt.title('channel delay_'+ui.lineEdit_focus_L.text()+"mm")
    # plt.xlabel('channel')
    # plt.ylabel("delay")
    # plt.plot(delay_int)
    # plt.grid()
    # plt.show()


def Gen_Delay_Table(data, name, isSector):
    # df = pd.DataFrame(data)
    # print("data : ", df.transpose())  
    
    print("Gen_delay table")
    print(data)
    
    delay_table = np.int16(np.zeros([128,32]))
    df_reg_data = pd.DataFrame(np.int16(np.zeros([128,16])))
    
    if (not isSector): # if Linear, Convex
        # delay_table = np.int16(np.zeros([128,32]))
        for i in range(128):
            delay = np.roll(data,-15+i)
            delay_table[i,:] = delay
        
        ######################## np array int to hex ########################
        delay_hex = np.array([[hex(int(x))[2:].zfill(4).upper() for x in y] for y in delay_table])
        #####################################################################
        print("delay_table", delay_hex)
        
        df1 = pd.DataFrame(delay_hex) 
        # print(df1) 
    else:
        print("############### sector ####################")
        
        # delay_table = np.int16(np.zeros([128,32]))
        delay_table = data
        
        ######################## np array int to hex ########################
        delay_hex = np.array([[hex(int(x))[2:].zfill(4).upper() for x in y] for y in delay_table])
        #####################################################################
        print("delay_table", delay_hex)
        
        df1 = pd.DataFrame(delay_hex.transpose()) 
        # print(df1)
        
        if ui.checkBox_file.isChecked():
            name = name + "_delay"
            df1.to_excel(name + ".xlsx")
            df1.to_csv(name + ".csv")
            # np.savetxt(csv_name + ".csv", delay_table, fmt='%g', delimiter=',')
    
    # print("################# 7332 Reg Data #################")
    # df_reg_data = pd.DataFrame(np.int16(np.zeros([128,16])))    
    df_reg_data.iloc[0:,0] = (df1.iloc[0:,31]) + (df1.iloc[0:,29]) 
    df_reg_data.iloc[0:,1] = (df1.iloc[0:,27]) + (df1.iloc[0:,25]) 
    df_reg_data.iloc[0:,2] = (df1.iloc[0:,23]) + (df1.iloc[0:,21]) 
    df_reg_data.iloc[0:,3] = (df1.iloc[0:,19]) + (df1.iloc[0:,17]) 
    df_reg_data.iloc[0:,4] = (df1.iloc[0:,30]) + (df1.iloc[0:,28]) 
    df_reg_data.iloc[0:,5] = (df1.iloc[0:,26]) + (df1.iloc[0:,24]) 
    df_reg_data.iloc[0:,6] = (df1.iloc[0:,22]) + (df1.iloc[0:,20]) 
    df_reg_data.iloc[0:,7] = (df1.iloc[0:,18]) + (df1.iloc[0:,16]) 
    df_reg_data.iloc[0:,8] = (df1.iloc[0:,15]) + (df1.iloc[0:,13]) 
    df_reg_data.iloc[0:,9] = (df1.iloc[0:,11]) + (df1.iloc[0:,9]) 
    df_reg_data.iloc[0:,10] = (df1.iloc[0:,7]) + (df1.iloc[0:,5]) 
    df_reg_data.iloc[0:,11] = (df1.iloc[0:,3]) + (df1.iloc[0:,1])     
    df_reg_data.iloc[0:,12] = (df1.iloc[0:,14]) + (df1.iloc[0:,12]) 
    df_reg_data.iloc[0:,13] = (df1.iloc[0:,10]) + (df1.iloc[0:,8]) 
    df_reg_data.iloc[0:,14] = (df1.iloc[0:,6]) + (df1.iloc[0:,4]) 
    df_reg_data.iloc[0:,15] = (df1.iloc[0:,2]) + (df1.iloc[0:,0]) 
    
    # ui.textEdit.clear()
    # ui.textEdit.setPlainText(str(df_reg_data))
    
    if ui.checkBox_file.isChecked():
        name = name + "_Reg_Table"
        df_reg_data.to_excel(name + ".xlsx")
        df_reg_data.to_csv(name + ".csv")
      

def Sector_Gen_Delay():
    global ElementPitch, NofProbeElements, NofTXChannels
    global NofScanline, FOV, BfSync2Rxen, CK
    global TXResolution, SpeedofSound
    
    TXResolution = float(ui.lineEdit_clock.text()) * 1000000
    ElementPitch = float(ui.lineEdit_pitch_S.text()) / 1000
    NofProbeElements = 32
    NofTXChannels = 32
    SpeedofSound = float(ui.lineEdit_sound_speed.text())
    CK = TXResolution / SpeedofSound
    NofScanline = 128
    FOV = float(ui.lineEdit_fov.text()) # 90.0
    
    focus = float(ui.lineEdit_focus_S.text())
    print("focus", focus)
    
    Make_ProbeElementPosition()
    Make_TX_BF(focus)


def Make_ProbeElementPosition():
    global ele_x_pos, ele_y_pos
    global xinit, yinit, TXxinit, TXyinit, xinc, yinc

    ele_x_pos = ((np.array(range(1, NofProbeElements + 1)) - NofProbeElements / 2) - 0.5) * ElementPitch
    # print("ele_x_pos_hw", ele_x_pos) # pizzabox Test
    ele_y_pos = ele_x_pos * 0

    ele_x_pos_hw = np.round(ele_x_pos * CK * 4)  # s14.2
    ele_y_pos_hw = np.round(ele_y_pos * CK * 4)  # s14.2
    ele_x_pos_hw = np.uint32(np.uint16(ele_x_pos_hw))
    # print("ele_x_pos_hw", ele_x_pos_hw) # pizzabox Test
    ele_y_pos_hw = np.uint32(np.uint16(ele_y_pos_hw))
    # print("ele_y_pos_hw", ele_y_pos_hw) # pizzabox Test

    step = FOV/NofScanline
    angle = np.deg2rad(np.arange(-FOV/2,FOV/2,step, dtype=np.float64)+step/2)
    # print("angle", angle) # Pizzabox Test

    xinit = np.zeros(NofScanline)
    yinit = np.zeros(NofScanline)

    TXxinit = xinit
    TXyinit = yinit
    xinc = np.sin(angle)
    yinc = np.cos(angle)


def Make_TX_BF(focal_depth_mm):
    focal_depth = focal_depth_mm / 1000  # mm를 m로 변환

    xf = xinc * focal_depth
    yf = yinc * focal_depth

    TXdelay = np.zeros([NofTXChannels, NofScanline])
    TXdelay_init = np.zeros(NofScanline)

    for i in range(NofScanline):
        TXdelay_init[i] = np.sqrt((TXxinit[i] - xf[i]) ** 2 + (TXyinit[i] - yf[i]) ** 2)
        TXdelay[0:NofProbeElements, i] = np.sqrt((ele_x_pos - xf[i]) ** 2 + (ele_y_pos - yf[i]) ** 2) - TXdelay_init[i]
    # print("TXdelay_init", TXdelay_init)

    TXdelay = TXdelay * TXResolution / SpeedofSound
    # print("TXdelay = ", TXdelay)

    max_delay = np.max(abs(TXdelay))
    print("max_delay", max_delay) # Pizzabox test
    # min_delay = np.min(TXdelay) # Pizzabox test
    # print("min delay", min_delay) # Pizzabox test

    # np.savetxt('Sector_TX_Delay_{0}.csv'.format(focal_depth_mm), TXdelay, fmt='%g', delimiter=',') # Pizzabox test

    # TXdelay_hw = np.round(((BfSync2Rxen * 4) - TXdelay) * 2)
    # TXdelay_hw = np.round(((BfSync2Rxen ) - TXdelay) ) # Pizzabox Test
    # TXdelay_hw = np.round( (abs(max_delay) - TXdelay) ) # Pizzabox Test
    TXdelay_hw = np.round(max_delay - TXdelay) # Pizzabox Test
    print("TXdelay_hw", TXdelay_hw)
    
    df1 = pd.DataFrame(TXdelay_hw)
    # ui.textEdit.clear()
    # ui.textEdit.setPlainText(str(df1.transpose()))

    name = "Probe_Focus_" + ui.lineEdit_focus_S.text() + "mm_Sector" 
    Delay_count(np.int16(TXdelay_hw[:,0]))
    Delay_hex(np.int16(TXdelay_hw[:,0]))
    Gen_Delay_Table(TXdelay_hw, name, 1)
    
    # np.savetxt('Sector_TX_Delay_HW_{0}.csv'.format(focal_depth_mm), TXdelay_hw.transpose(), fmt='%g', delimiter=',')
    display_plot(TXdelay_hw[:,0],TXdelay_hw[:,63],TXdelay_hw[:,64],TXdelay_hw[:,127])  # Pizzabox test


def display_plot(data1, data2, data3, data4):
    # figure 1 ..................................
    fig = plt.figure(num=2,dpi=80,facecolor='white')
        
    ################ Remove widget ################
    for i in range(ui.verticalLayout_graph.count()):
        ui.verticalLayout_graph.itemAt(i).widget().deleteLater()
    ###############################################
    plt.clf()
  
    plt.subplot(4,1,1)
    plt.title('Channel Delay H/W')
    plt.plot(data1,'b')    
    plt.xlim([0,32])
    # plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
    #             17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
    plt.ylabel('sc1')
    plt.grid()

    plt.subplot(4,1,2)
    plt.plot(data2,'r')   #  2* ???
    plt.xlim([0,32])
    # plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
    #             17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
    plt.ylabel('sc64')
    plt.grid()

    plt.subplot(4,1,3)
    plt.plot(data3,'c')   #  2* ???
    plt.xlim([0,32])
    # plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
    #             17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
    plt.ylabel('sc65')
    plt.grid()

    plt.subplot(4,1,4)
    plt.plot(data4,'g')   #  2* ???
    plt.xlim([0,32])
    # plt.xticks([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,
    #             17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])
    plt.ylabel('sc128')
    plt.grid()

    # plt.savefig("./test_figure2.png",dpi=300)
    # plt.show()
    
    ############### Add graph widget at layout ###############
    canvas = FigureCanvas(fig)
    ui.verticalLayout_graph.addWidget(canvas)
    ##########################################################


def Delay_count(delay_data):
    for i, value in enumerate(delay_data):
        getattr(ui, f"lineEdit_ch_{i+1}").setText(str(value))
        
    # ui.lineEdit_ch_1.setText(str(delay_data[0]))
    # ui.lineEdit_ch_2.setText(str(delay_data[1]))
    # ui.lineEdit_ch_3.setText(str(delay_data[2]))
    # ui.lineEdit_ch_4.setText(str(delay_data[3]))
    # ui.lineEdit_ch_5.setText(str(delay_data[4]))
    # ui.lineEdit_ch_6.setText(str(delay_data[5]))
    # ui.lineEdit_ch_7.setText(str(delay_data[6]))
    # ui.lineEdit_ch_8.setText(str(delay_data[7]))
    # ui.lineEdit_ch_9.setText(str(delay_data[8]))
    # ui.lineEdit_ch_10.setText(str(delay_data[9]))
    # ui.lineEdit_ch_11.setText(str(delay_data[10]))
    # ui.lineEdit_ch_12.setText(str(delay_data[11]))
    # ui.lineEdit_ch_13.setText(str(delay_data[12]))
    # ui.lineEdit_ch_14.setText(str(delay_data[13]))
    # ui.lineEdit_ch_15.setText(str(delay_data[14]))
    # ui.lineEdit_ch_16.setText(str(delay_data[15]))
    # ui.lineEdit_ch_17.setText(str(delay_data[16]))
    # ui.lineEdit_ch_18.setText(str(delay_data[17]))
    # ui.lineEdit_ch_19.setText(str(delay_data[18]))
    # ui.lineEdit_ch_20.setText(str(delay_data[19]))
    # ui.lineEdit_ch_21.setText(str(delay_data[20]))
    # ui.lineEdit_ch_22.setText(str(delay_data[21]))
    # ui.lineEdit_ch_23.setText(str(delay_data[22]))
    # ui.lineEdit_ch_24.setText(str(delay_data[23]))
    # ui.lineEdit_ch_25.setText(str(delay_data[24]))
    # ui.lineEdit_ch_26.setText(str(delay_data[25]))
    # ui.lineEdit_ch_27.setText(str(delay_data[26]))
    # ui.lineEdit_ch_28.setText(str(delay_data[27]))
    # ui.lineEdit_ch_29.setText(str(delay_data[28]))
    # ui.lineEdit_ch_30.setText(str(delay_data[29]))
    # ui.lineEdit_ch_31.setText(str(delay_data[30]))
    # ui.lineEdit_ch_32.setText(str(delay_data[31]))


def Delay_hex(delay_int):
    for i, value in enumerate(delay_int):
        getattr(ui, f"lineEdit_ch_{i+1}_hex").setText(hex(value)[2:].zfill(4).upper())
        
    # ui.lineEdit_ch_1_hex.setText(str(hex(delay_int[0])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_2_hex.setText(str(hex(delay_int[1])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_3_hex.setText(str(hex(delay_int[2])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_4_hex.setText(str(hex(delay_int[3])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_5_hex.setText(str(hex(delay_int[4])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_6_hex.setText(str(hex(delay_int[5])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_7_hex.setText(str(hex(delay_int[6])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_8_hex.setText(str(hex(delay_int[7])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_9_hex.setText(str(hex(delay_int[8])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_10_hex.setText(str(hex(delay_int[9])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_11_hex.setText(str(hex(delay_int[10])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_12_hex.setText(str(hex(delay_int[11])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_13_hex.setText(str(hex(delay_int[12])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_14_hex.setText(str(hex(delay_int[13])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_15_hex.setText(str(hex(delay_int[14])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_16_hex.setText(str(hex(delay_int[15])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_17_hex.setText(str(hex(delay_int[16])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_18_hex.setText(str(hex(delay_int[17])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_19_hex.setText(str(hex(delay_int[18])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_20_hex.setText(str(hex(delay_int[19])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_21_hex.setText(str(hex(delay_int[20])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_22_hex.setText(str(hex(delay_int[21])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_23_hex.setText(str(hex(delay_int[22])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_24_hex.setText(str(hex(delay_int[23])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_25_hex.setText(str(hex(delay_int[24])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_26_hex.setText(str(hex(delay_int[25])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_27_hex.setText(str(hex(delay_int[26])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_28_hex.setText(str(hex(delay_int[27])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_29_hex.setText(str(hex(delay_int[28])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_30_hex.setText(str(hex(delay_int[29])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_31_hex.setText(str(hex(delay_int[30])[2:].zfill(4).upper()))
    # ui.lineEdit_ch_32_hex.setText(str(hex(delay_int[31])[2:].zfill(4).upper())) 


def Pattern_Gen():
    HZ = "000"
    HV_M = "001"
    HV_P = "010"
    GND = "011"
    EOP = "111"

    global LVL, PER, LVL_, PER_
    LVL = [None] *16
    PER = [None] *16
    LVL_ = [None] *16
    PER_ = [None] *16    

    Read_LVL()    
    for i in range(16):
        if LVL[i] == "HIGH_Z":
            LVL_[i] = HZ
        elif LVL[i] == "HV_P":
            LVL_[i] = HV_P
        elif LVL[i] == "HV_M":
            LVL_[i] = HV_M
        elif LVL[i] == "GND":
            LVL_[i] = GND
        elif LVL[i] == "END_of_Pattern":
            LVL_[i] = EOP
    print("LVL_", LVL_)

    Read_PER()    
    for i in range(16):
        temp = (int(PER[i]) * int(ui.lineEdit_clock.text()) / 1000) - 2
        if temp < 0:
            PER_[i] = str(bin(0)[2:].zfill(5))
        else:
            PER_[i] = str(bin(int(temp))[2:].zfill(5))
    print("PER_", PER_)
    
    Reg120 = [None]*4
    Reg121 = [None]*4
    Reg122 = [None]*4
    Reg123 = [None]*4
    
    Reg120[3] = '0b' + PER_[3] + LVL_[3]
    Reg120[2] = '0b' + PER_[2] + LVL_[2] 
    Reg120[1] = '0b' + PER_[1] + LVL_[1] 
    Reg120[0] = '0b' + PER_[0] + LVL_[0]

    Reg121[3] = '0b' + PER_[7] + LVL_[7]
    Reg121[2] = '0b' + PER_[6] + LVL_[6]
    Reg121[1] = '0b' + PER_[5] + LVL_[5]
    Reg121[0] = '0b' + PER_[4] + LVL_[4]

    Reg122[3] = '0b' + PER_[11] + LVL_[11]
    Reg122[2] = '0b' + PER_[10] + LVL_[10]
    Reg122[1] = '0b' + PER_[9] + LVL_[9]
    Reg122[0] = '0b' + PER_[8] + LVL_[8]

    Reg123[3] = '0b' + PER_[15] + LVL_[15]
    Reg123[2] = '0b' + PER_[14] + LVL_[14]
    Reg123[1] = '0b' + PER_[13] + LVL_[13]
    Reg123[0] = '0b' + PER_[12] + LVL_[12]
    print(Reg120, Reg121, Reg122, Reg123)
    
    Reg_120 = str(hex(int(Reg120[3],2))[2:].zfill(2)) + str(hex(int(Reg120[2],2))[2:].zfill(2)) + str(hex(int(Reg120[1],2))[2:].zfill(2)) + str(hex(int(Reg120[0],2))[2:].zfill(2))
    Reg_121 = str(hex(int(Reg121[3],2)))[2:].zfill(2) + str(hex(int(Reg121[2],2)))[2:].zfill(2) + str(hex(int(Reg121[1],2)))[2:].zfill(2) + str(hex(int(Reg121[0],2)))[2:].zfill(2)
    Reg_122 = str(hex(int(Reg122[3],2)))[2:].zfill(2) + str(hex(int(Reg122[2],2)))[2:].zfill(2) + str(hex(int(Reg122[1],2)))[2:].zfill(2) + str(hex(int(Reg122[0],2)))[2:].zfill(2)
    Reg_123 = str(hex(int(Reg123[3],2)))[2:].zfill(2) + str(hex(int(Reg123[2],2)))[2:].zfill(2) + str(hex(int(Reg123[1],2)))[2:].zfill(2) + str(hex(int(Reg123[0],2)))[2:].zfill(2)
    print(Reg_120, Reg_121, Reg_122, Reg_123)
    
    ui.lineEdit_R120.setText("0x" + Reg_120)
    ui.lineEdit_R121.setText("0x" + Reg_121)
    ui.lineEdit_R122.setText("0x" + Reg_122)
    ui.lineEdit_R123.setText("0x" + Reg_123)


def Read_LVL():
    for i in range(16):
        LVL[i] = getattr(ui, f"comboBox_LVL_{i+1}").currentText()
        
    # LVL[0] = ui.comboBox_LVL_1.currentText()
    # LVL[1] = ui.comboBox_LVL_2.currentText()
    # LVL[2] = ui.comboBox_LVL_3.currentText()
    # LVL[3] = ui.comboBox_LVL_4.currentText()
    # LVL[4] = ui.comboBox_LVL_5.currentText()
    # LVL[5] = ui.comboBox_LVL_6.currentText()
    # LVL[6] = ui.comboBox_LVL_7.currentText()
    # LVL[7] = ui.comboBox_LVL_8.currentText()
    # LVL[8] = ui.comboBox_LVL_9.currentText()
    # LVL[9] = ui.comboBox_LVL_10.currentText()
    # LVL[10] = ui.comboBox_LVL_11.currentText()  
    # LVL[11] = ui.comboBox_LVL_12.currentText() 
    # LVL[12] = ui.comboBox_LVL_13.currentText() 
    # LVL[13] = ui.comboBox_LVL_14.currentText() 
    # LVL[14] = ui.comboBox_LVL_15.currentText() 
    # LVL[15] = ui.comboBox_LVL_16.currentText()      
    # print(LVL)


def Read_PER():
    for i in range(16):
        PER[i] = getattr(ui, f"lineEdit_PER_{i+1}").text()
        
    # PER[0] = ui.lineEdit_PER_1.text()
    # PER[1] = ui.lineEdit_PER_2.text()
    # PER[2] = ui.lineEdit_PER_3.text()
    # PER[3] = ui.lineEdit_PER_4.text()
    # PER[4] = ui.lineEdit_PER_5.text()
    # PER[5] = ui.lineEdit_PER_6.text()
    # PER[6] = ui.lineEdit_PER_7.text()
    # PER[7] = ui.lineEdit_PER_8.text()
    # PER[8] = ui.lineEdit_PER_9.text()
    # PER[9] = ui.lineEdit_PER_10.text()
    # PER[10] = ui.lineEdit_PER_11.text()
    # PER[11] = ui.lineEdit_PER_12.text()
    # PER[12] = ui.lineEdit_PER_13.text()
    # PER[13] = ui.lineEdit_PER_14.text()
    # PER[14] = ui.lineEdit_PER_15.text()
    # PER[15] = ui.lineEdit_PER_16.text()
    # print(PER)    


ui.pushButton_L_cal.clicked.connect(Linear_Gen_Delay)
ui.pushButton_C_cal.clicked.connect(Convex_Gen_Delay)
ui.pushButton_S_cal.clicked.connect(Sector_Gen_Delay)
ui.pushButton_P_Gen.clicked.connect(Pattern_Gen)


ui.show()
app.exec()