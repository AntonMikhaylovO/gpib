import visa
import tkinter
import time
import threading
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure

class GPIB():
    def __init__(self):
        self.buf=0


    def connect(self):
        self.rm = visa.ResourceManager()
        self.inst = self.rm.open_resource("GPIB0::8::INSTR")


    def command(self,arg, key_word):
        if key_word=='CURR':self.inst.write("CURRent "+str(arg))
        elif key_word=='VOLT': self.inst.write("VOLTage "+str(arg))
        elif key_word=='CH': self.inst.write("CHANnel "+ str(arg))
        elif key_word=="ON": self.inst.write("OUTPut:STATe 1")
        elif key_word=="OFF": self.inst.write("OUTPut:STATe 0")
        elif key_word=="CURR?" : self.inst.write("CURRent?")
        elif key_word=='VOLT?': self.inst.write("VOLTage?")
        elif key_word=="CH?": self.inst.write("CHANnel?")
        elif key_word=="READ": self.buf=self.inst.read()

class GUI():
    def __init__(self, GPIB):
        self.c=0
        self.root=tkinter.Tk()
        self.root.resizable(False, False)
        self.reading_flag=False
        self.reading_graph_flag=False
        self.root.geometry('1050x700')
        self.root.title('INSTEK PPT-3615 Client v 0.0.0')
        self.GPIB=GPIB
        x=10
        y=10
        hx=185
        hy=25
        self.counter=0
        self.x_1=[]
        self.x_2=[]
        self.x_3=[]
        self.y_1=[]
        self.y_2=[]
        self.y_3=[]
        self.xa_1=[]
        self.xa_2=[]
        self.xa_3=[]
        self.current_state_name=GUI_stack(self.root)
        self.current_state_name.name_lable()
        self.current_state_name.place(x=x,y=y,height=25,width=270)
        self.channel_1=GUI_stack(self.root)
        self.channel_1.current_state()
        self.channel_1.place(x=x,y=y+hy,height=25,width=270)
        self.channel_2 = GUI_stack(self.root)
        self.channel_2.current_state()
        self.channel_2.place(x=x, y=y+2*hy, height=25, width=270)
        self.channel_3 = GUI_stack(self.root)
        self.channel_3.current_state()
        self.channel_3.place(x=x, y=y+3*hy, height=25, width=270)
        self.entry=GUI_stack(self.root)
        self.entry.Entry_state()
        self.entry.place(x=x+hx+90,y=y,height=50,width=270)
        self.period_entry=GUI_stack(self.root)
        self.connect_frame=tkinter.Frame(self.root)
        self.connect_frame.place(x=x+3*hx-10,y=y,height=50,width=270)
        self.connect_frame_inter=tkinter.Frame(self.root)
        self.connect_frame_inter.place(x=x+4*hx-115,y=y+hy+25,height=50,width=180)
        GUI.button(self)
        self.period_entry.Entry_period()
        self.period_entry.place(x=x+hx+90,y=y+2*hy,height=50,width=350)
        self.g_frame_1=tkinter.Frame(self.root)
        self.g_frame_2=tkinter.Frame(self.root)
        self.g_frame_3=tkinter.Frame(self.root)
        self.graph_1=Grpahics(self.g_frame_1)
        self.graph_2=Grpahics(self.g_frame_2)
        self.graph_3=Grpahics(self.g_frame_3)
        self.g_frame_1.place(x=x,y=y+5*hy-20, height=190,width=720)
        self.g_frame_2.place(x=x, y=y + 5 * hy+170, height=190, width=720)
        self.g_frame_3.place(x=x, y=y + 5 * hy+360, height=190, width=720)

        self.interval_flag=False


    def button(self):
        x=0
        y=0
        h=25
        w=80
        self.connect=tkinter.Button(self.connect_frame_inter,text='Подключить', relief='raised', command=lambda:self.GPIB.connect())
        self.read_b=tkinter.Button(self.connect_frame, text='Читать',relief='raised', command=lambda:GUI.reading_thread(self.read_b))
        self.write_b=tkinter.Button(self.connect_frame, text='Записать',relief='raised', command=lambda:GUI.write())
        self.onb=tkinter.Button(self.connect_frame, text='Output on',relief='raised', command=lambda:self.GPIB.command(0,'ON'))
        self.offb=tkinter.Button(self.connect_frame, text='Output off',relief='raised', command=lambda:self.GPIB.command(0,'OFF'))
        self.interval=tkinter.Button(self.connect_frame_inter,text='Период',relief='raised', command=lambda:self.start_inter(self.interval))
        self.reset_graph=tkinter.Button(self.connect_frame_inter,text='Сбросить', relief='raised', command=lambda:self.reset())
        self.set_count=tkinter.Button(self.connect_frame_inter,text='Промежуток', relief='raised', command=lambda:self.set_cnt())
        self.reset_graph.place(x=x+w, y=y, height=h,width=w)
        self.set_count.place(x=x+w,y=y+h,height=h,width=w)
        self.interval.place(x=x,y=y,height=h,width=w)
        self.connect.place(x=x, y=y+h,height=h, width=w )
        self.read_b.place(x=x+w, y=y, height=h, width=w)
        self.write_b.place(x=x, y=y, height=h, width=w)
        self.onb.place(x=x,y=y+h, height=h, width=w)
        self.offb.place(x=x+w,y=y+h, height=h,width=w)


    def reset(self):
        self.reading_graph_flag=False
        self.graph_1.f.clf()
        self.graph_2.f.clf()
        self.graph_3.f.clf()
        self.graph_3.f.draw()
        self.reading_graph_flag = True
        th = threading.Thread(target=lambda: self.graphics_mode(0))
        th.start()

    def set_cnt(self):
        self.reading_graph_flag=False
        self.graph_1.a.clear()
        self.graph_2.a.clear()
        self.graph_3.a.clear()
        self.graph_1.ax2.clear()
        self.graph_2.ax2.clear()
        self.graph_3.ax2.clear()
        count = int(self.period_entry.interval.get())
        self.reading_graph_flag = True
        th = threading.Thread(target=lambda: self.graphics_mode(count))
        th.start()

    def read(self):
        while (self.reading_flag):
            for i in  range(1,4):
                self.GPIB.command(i,'CH')
                self.GPIB.command(0,'VOLT?')
                self.GPIB.command(0,'READ')
                if i==1:
                    self.channel_1.voltage.set(GPIB.buf[0:len(GPIB.buf)-1] if GPIB.buf!='' else 0)
                elif i==2:
                    self.channel_2.voltage.set(GPIB.buf[0:len(GPIB.buf)-1] if GPIB.buf!='' else 0)
                elif i==3:
                    self.channel_3.voltage.set(GPIB.buf[0:len(GPIB.buf)-1] if GPIB.buf!='' else 0)
                time.sleep(1)
                self.GPIB.command(0,'CURR?')
                self.GPIB.command(0,'READ')
                if i==1:
                    self.channel_1.amperage.set(GPIB.buf[0:len(GPIB.buf)-1] if GPIB.buf!='' else 0)
                elif i==2:
                    self.channel_2.amperage.set(GPIB.buf[0:len(GPIB.buf)-1]if GPIB.buf!='' else 0)
                elif i==3:
                    self.channel_3.amperage.set(GPIB.buf[0:len(GPIB.buf)-1]if GPIB.buf!='' else 0)
                self.channel_1.power.set('{:.2e}'.format(float(self.channel_1.amperage.get())*float(self.channel_1.voltage.get())))
                self.channel_2.power.set('{:.2e}'.format(float(self.channel_2.amperage.get()) * float(self.channel_2.voltage.get())))
                self.channel_3.power.set('{:.2e}'.format(float(self.channel_3.amperage.get()) * float(self.channel_3.voltage.get())))
                if self.reading_graph_flag==False:
                    self.reading_graph_flag=True
                    th = threading.Thread(target=lambda: self.graphics_mode(0))
                    th.start()
                time.sleep(1)

    def reading_thread(self,bt):
        if self.reading_flag==False:
            bt.config(bg='PaleGreen3')
            self.reading_flag=True
            read_thread=threading.Thread(target=lambda:GUI.read())
            read_thread.start()
        else:
            self.reading_flag=False
            bt.config(bg='Grey')

    def write(self):
        voltage=self.entry.volt.get()
        amperage=self.entry.curr.get()
        channel=self.entry.chanel.get()
        if channel==0:
            for i in range(1,4):
                self.GPIB.command(str(i), 'CH')
                self.GPIB.command(str(voltage), 'VOLT')
                self.GPIB.command(str(amperage), 'CURR')
        self.GPIB.command(str(channel), 'CH')
        self.GPIB.command(str(voltage),'VOLT')
        self.GPIB.command(str(amperage),'CURR')

    def graphics_mode(self,count):
        while (self.reading_graph_flag):
            time.sleep(1)
            self.c+=1
            a=''
            self.x_1.append(self.channel_1.voltage.get())
            self.x_2.append(self.channel_2.voltage.get())
            self.x_3.append(self.channel_3.voltage.get())
            self.xa_1.append(self.channel_1.amperage.get())
            self.xa_2.append(self.channel_2.amperage.get())
            self.xa_3.append(self.channel_3.amperage.get())
            self.y_1.append(self.c)
            self.y_2.append(self.c)
            self.y_3.append(self.c)

            if count!=0:
                if len(self.x_1)>count:
                    self.counter+=1
                    self.x_1=self.x_1[self.counter::]
                    self.x_2=self.x_2[self.counter::]
                    self.x_3=self.x_3[self.counter::]
                    self.xa_1=self.xa_1[self.counter::]
                    self.xa_2=self.xa_2[self.counter::]
                    self.xa_3=self.xa_3[self.counter::]
                    self.y_1=self.y_1[self.counter::]
            self.graph_1.animate(self.y_1,self.xa_1,self.x_1)
            self.graph_2.animate(self.y_1,self.xa_2,self.x_2)
            self.graph_3.animate(self.y_1,self.xa_3,self.x_3)

    def interv(self):
        while(self.interval_flag):
            hight=self.period_entry.upper.get()
            low=self.period_entry.down.get()
            step=self.period_entry.step.get()
            count=self.period_entry.interval.get()
            chanel=self.entry.chanel.get()
            cur=int(low)
            while(cur<int(hight)):
                if ((chanel=='1')|(chanel=='2')|(chanel=='3')):
                    print(chanel)
                    self.GPIB.command(str(chanel), 'CH')
                    self.GPIB.command(str(cur), 'VOLT')
                time.sleep(int(count))
                cur+=int(step)
                print(cur)
            self.interval_flag=False

    def start_inter(self,bt):
        if self.interval_flag==False:
            self.interval_flag=True
            th=threading.Thread(target=self.interv)
            th.start()
            bt.config(bg='PaleGreen3')
        else:
            self.interval_flag=False
            bt.config(bg='Grey')


class Grpahics():
    def __init__(self,root):
        self.f = Figure()
        self.a = self.f.add_subplot(111)
        self.ax2 = self.a.twinx()
        canvas = FigureCanvasTkAgg(self.f, root)
        canvas.show()
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True,ipadx=10,ipady=1)
        self.r_t=True
        self.i = 0
        self.ii=[0]
        self.li,=self.a.plot(self.ii,self.ii, color='r', label='U, (В)')
        self.li2, = self.ax2.plot(self.ii, self.ii, color='b', label='I, (А)')
        legend = self.a.legend(loc='lower left', shadow=True, fontsize='x-small')
        legend2=self.ax2.legend(loc='upper left', shadow=True, fontsize='x-small')
        self.root = root

    def animate(self,x,y2,y):
        self.li.set_xdata(x)
        self.li.set_ydata(y)
        self.li2.set_xdata(x)
        self.li2.set_ydata(y2)
        self.a.relim(visible_only =True)
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.a.autoscale_view(True,True,True)
        self.f.canvas.draw()

class GUI_stack(tkinter.Frame):
    def __init__(self,root):
        super().__init__(root)

    def current_state(self):
        self.voltage = tkinter.StringVar()
        self.voltage.set(0.0)
        self.amperage = tkinter.StringVar()
        self.amperage.set(0.0)
        self.power=tkinter.StringVar()
        voltage_lable = tkinter.Label(self, textvariable=self.voltage, bd=1, relief='sunken')
        amperage_lable = tkinter.Label(self, textvariable=self.amperage, bd=1, relief='sunken')
        power_lable=tkinter.Label(self, textvariable=self.power,bd=1,relief='sunken')
        voltage_lable.place(x=0, y=0, height=25, width=90)
        amperage_lable.place(x=90, y=0, height=25, width=90)
        power_lable.place(x=180,y=0,height=25,width=90)

    def name_lable(self):
        curr_sign = tkinter.Label(self, text='Ток, (А)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        volt_sign = tkinter.Label(self, text='U, (В)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        pow_sign = tkinter.Label(self, text='W, (Вт)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        curr_sign.place(x=90, y=0, height=25, width=90)
        volt_sign.place(x=0, y=0, height=25, width=90)
        pow_sign.place(x=180, y=0, height=25, width=90)

    def Entry_state(self):
        self.curr = tkinter.Entry(self,relief='sunken')
        self.volt = tkinter.Entry(self,relief='sunken')
        self.chanel = tkinter.Entry(self,relief='sunken')
        self.chanel.insert(0, '0')
        self.curr.insert(0, '0.0')
        self.volt.insert(0, '0.0')
        curr_lbl = tkinter.Label(self, text='Ток, (А)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        volt_lbl = tkinter.Label(self, text='U, (В)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        chan_lbl = tkinter.Label(self, text='Канал', relief='sunken', bd=1, bg='DeepSkyBlue3')
        volt_lbl.place(x=90, y=0, height=25, width=90)
        curr_lbl.place(x=0, y=0, height=25, width=90)
        chan_lbl.place(x=180, y=0, height=25, width=90)
        self.curr.place(x=0, y=25, height=25, width=90)
        self.volt.place(x=90, y=25, height=25, width=90)
        self.chanel.place(x=180, y=25, height=25, width=90)

    def Entry_period(self):
        self.interval = tkinter.Entry(self,relief='sunken')
        self.upper = tkinter.Entry(self,relief='sunken')
        self.down = tkinter.Entry(self,relief='sunken')
        self.step = tkinter.Entry(self,relief='sunken')
        interval = tkinter.Label(self, text='Интервал, (с)',relief='sunken', bd=1, bg='DeepSkyBlue3')
        upper = tkinter.Label(self, text='Верх, (В)',relief='sunken', bd=1, bg='DeepSkyBlue3')
        down = tkinter.Label(self, text='Низ, (В)',relief='sunken', bd=1, bg='DeepSkyBlue3')
        step = tkinter.Label(self, text='Шаг, (В)', relief='sunken', bd=1, bg='DeepSkyBlue3')
        self.interval.insert(0, '0')
        self.upper.insert(0, '0.0')
        self.down.insert(0, '0.0')
        self.step.insert(0,'0.0')
        step.place(x=270,y=0,height=25,width=90)
        interval.place(x=0, y=0, height=25, width=90)
        upper.place(x=90, y=0, height=25, width=90)
        down.place(x=180, y=0, height=25, width=90)
        self.interval.place(x=0, y=25, height=25, width=90)
        self.upper.place(x=90, y=25, height=25, width=90)
        self.down.place(x=180, y=25, height=25, width=90)
        self.step.place(x=270,y=25,height=25,width=90)





GPIB=GPIB()
GUI=GUI(GPIB)
#Grpahics(GUI.gf,GUI)
GUI.root.mainloop()