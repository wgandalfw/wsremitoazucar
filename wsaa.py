from configparser import ConfigParser
import os
import sys
from xml.etree.ElementTree import parse,Element
from datetime import date, datetime
from datetime import timedelta as td
from suds.client import Client
import suds

if not os.path.isfile("wsaa.ini"):
    print("No se encontro el archivo de configuracion wsaa.ini")
    quit()

configuracion=ConfigParser()

configuracion.read("wsaa.ini")

csr=os.getcwd() + "\\certificados\\" + configuracion['certificados']['csr']
pem=os.getcwd() + "\\certificados\\" + configuracion['certificados']['pem']
key=os.getcwd() + "\\certificados\\" + configuracion['certificados']['key']
xml=os.getcwd() + "\\certificados\\" + configuracion['certificados']['xml']
cms=os.getcwd() + "\\certificados\\" + configuracion['certificados']['cms']
bat=os.getcwd() + "\\" + configuracion['bat']['bat']
tiempo=configuracion['duracion']['minutos']
servidor=configuracion['servidores']['wsaa']

#capturamos el parametro si el parametro es nulo consideramos que se quiere consultar un alta de inscripcion

if len(sys.argv) == 1:
    permiso=configuracion['Autorizaciones']['RM']
else:
    permiso=configuracion['Autorizaciones'][sys.argv[1]]

#procedemos a modificar el archivo xml
doc_xml=parse(xml)
root= doc_xml.getroot()

#en una lista obtenemos la fecha de inicio y expiracion del permiso
for hijo in root.findall('./header'):
    expira=hijo.find('expirationTime').text.split('T')

#obtengo la fecha de expiracion
fecha_expiracion= datetime.strptime(expira[0]+' '+expira[1],'%Y-%m-%d %H:%M:%S')

#verifico si el vertificado esta expirado

if fecha_expiracion< datetime.now():
    print("se debe regenerar el xml y volver a crear el csm")
    fecha_inicio=datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
    fecha_fin=datetime.strftime(datetime.now()+td(minutes=int(tiempo)),'%Y-%m-%d %H:%M:%S')
    fecha_inicio=fecha_inicio.replace(' ','T')
    fecha_fin=fecha_fin.replace(' ','T')
    print(fecha_inicio)
    print(fecha_fin)
    for hijo in root.findall('./header'):
        hijo.find('generationTime').text=fecha_inicio
        hijo.find('expirationTime').text=fecha_fin

    root.find('service').text=permiso

    doc_xml.write(xml)
    
    try:
        os.system('"'+bat+' '+os.getcwd()+"\\openssl\\bin "+xml+' '+cms+' '+pem+' '+key+'"')
    except:
        print('Ha ocurrido un error al intentar generar el archivo csm revisar los argumentos del bat')

        print("Archivo csm generado exitosamente")

    #Se procede a pedir la autorizacion en el servidor de autorizacion

cliente=Client(servidor)

archivo_cms=open(cms,"r")
texto=archivo_cms.readlines()

cadena=""
texto.remove(texto[len(texto)-1])
texto.remove(texto[0])

for index in texto:
    cadena=cadena+index

#print(cadena)

try:
    resultado=cliente.service.loginCms(cadena)
    archivo=open ('TA'+"_"+permiso+".XML",'w')
    archivo.write(resultado)
    archivo.close()
except suds.WebFault as error:
    print ("se ha producido un error: ",error)
    archivo=open("Error_WSAA.txt",'w')
    archivo.write(str(datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'))+' = '+ str(error))
    archivo.close()

