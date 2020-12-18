#creador:   Juan Carlos Romero Chalco
#proposito: Accesibilidad a los modulos programados de acceso a web y estadisticas, sistema de conteo y clasificacion,
#           sistema de generacion de reportes con Reportlab a pdf, aplicativo de calibracion de la web cam integrada o web cam usb
#Requisitos previos para el funcionamiento
#version de python 3.7.3
#Sistem Op: Raspbian Boster 
#python -m pip install --upgrade pip
#sudo apt-get install python-tk
#liberar puertos ocupados
#netstat -tulpn -- verificar puertos ocupados
#ps -fA | grep python
#kill 12945
import subprocess
import tkinter as tk 
from tkinter import *

def abrir_programa1():
    subprocess.Popen(["python", "app.py"])

def abrir_programa2():
    #pass
    subprocess.call(['python', 'conteo_clasificacion_vehicular.py', '--display', '1', '--output', 'koper_highway.avi', '--mask', '210,260,630,420', '--resize', '640'])

def abrir_programa3():
    subprocess.Popen(['python', 'conteo_clasificacion_vehicular.py', '--input', 'videos/koper_highway.mp4', '--display', '1', '--output', 'koper_highway.avi', '--mask', '150,300,510,450', '--resize', '800'])

def abrir_programa4():
    subprocess.Popen(["python", "generar_reporte.py"])

def abrir_programa5():
    subprocess.Popen(["python", "Calibracion/calibracion_web_cam.py"])
def quit():
    global root
    root.destroy()
    
root = tk.Tk()
root.title("Sistema de Conteo y Clasificacion")
root.geometry("525x530")
Myframe = tk.Frame(root)
Myframe.pack(fill="both",expand=True)
Imagen=PhotoImage(file="assets/conteo.gif")
Imagen_2 =Label(Myframe, image=Imagen)
Imagen_2.place(x=0, y=0)

tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Iniciar Servidor WSGI", command=abrir_programa1).pack()
tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Iniciar Conteo y Clasifiacion Tiempo Real", command=abrir_programa2).pack()
tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Iniciar Conteo y Clasificacion de Ruta de Video", command=abrir_programa3).pack()
tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Generar ReportLab", command=abrir_programa4).pack()
tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Calibracion CAM", command=abrir_programa5).pack()
tk.Button(root, height=2, width=65, background = "black", foreground = "white", text="Salir", command=quit).pack()
root.resizable(0,0)
root.mainloop()
