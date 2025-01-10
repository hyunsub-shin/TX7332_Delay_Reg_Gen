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

from TX7332_ui import Ui_MainWindow

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
    # 채널 매핑 패턴을 정의
    channel_pairs = [
        (31,29), (27,25), (23,21), (19,17),
        (30,28), (26,24), (22,20), (18,16),
        (15,13), (11,9),  (7,5),   (3,1),
        (14,12), (10,8),  (6,4),   (2,0)
    ]
    
    # 한번에 모든 채널 매핑 수행
    for i, (ch1, ch2) in enumerate(channel_pairs):
        df_reg_data.iloc[0:,i] = df1.iloc[0:,ch1] + df1.iloc[0:,ch2]
       
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

    TXdelay_hw = np.round(max_delay - TXdelay) # Pizzabox Test
    print("TXdelay_hw", TXdelay_hw)
    
    df1 = pd.DataFrame(TXdelay_hw)

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


def Delay_hex(delay_int):
    for i, value in enumerate(delay_int):
        getattr(ui, f"lineEdit_ch_{i+1}_hex").setText(hex(value)[2:].zfill(4).upper())


def Pattern_Gen():
    # 상수 정의
    LEVEL_CODES = {
        "HIGH_Z": "000",
        "HV_M": "001",
        "HV_P": "010",
        "GND": "011",
        "END_of_Pattern": "111"
    }
    
    # LVL과 PER 값 읽기
    LVL = [getattr(ui, f"comboBox_LVL_{i+1}").currentText() for i in range(16)]
    PER = [getattr(ui, f"lineEdit_PER_{i+1}").text() for i in range(16)]
    
    # LVL 코드 변환
    LVL_ = [LEVEL_CODES[level] for level in LVL]
    
    # PER 값 계산
    clock = int(ui.lineEdit_clock.text())
    PER_ = [str(bin(max(0, int(int(per) * clock / 1000) - 2))[2:].zfill(5)) for per in PER]
    
    # 레지스터 값 계산
    regs = []
    for i in range(4):  # Reg120 ~ Reg123
        reg_values = []
        for j in range(4):
            idx = i * 4 + (3 - j)  # 역순으로 인덱스 계산
            reg_values.append(hex(int('0b' + PER_[idx] + LVL_[idx], 2))[2:].zfill(2))
        regs.append(''.join(reg_values))
    
    # UI에 결과 표시
    for i, reg in enumerate(regs):
        getattr(ui, f"lineEdit_R{120+i}").setText("0x" + reg)


ui.pushButton_L_cal.clicked.connect(Linear_Gen_Delay)
ui.pushButton_C_cal.clicked.connect(Convex_Gen_Delay)
ui.pushButton_S_cal.clicked.connect(Sector_Gen_Delay)
ui.pushButton_P_Gen.clicked.connect(Pattern_Gen)

ui.show()
app.exec()