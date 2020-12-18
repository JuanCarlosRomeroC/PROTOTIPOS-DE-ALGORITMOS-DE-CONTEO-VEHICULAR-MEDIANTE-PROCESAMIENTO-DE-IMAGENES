import cv2,time
#1. crear objeto para camara externa
video=cv2.VideoCapture(0)
#8 variable a
a=0
while True:
    a = a + 1
    #3. Crear frame de objetos
    check, frame = video.read()
    print(check)
    print(frame)# Representa a la imagen

    #convertir a escala de grises
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    #4. mostrar frames
    #cv2.imshow('Captura',frame)
    cv2.imshow("Captura",gray)
    #5. presinar una tecla para salir (en milisigundos)
    #cv2.waitKey(0)
    #7. para play
    key=cv2.waitKey(1)
    if key == ord ('q'):
        break
print(a)
    #2. apagar camara
video.release()
cv2.destroyAllWindows
