from configparser import ConfigParser
import os
import sys
import json
from datetime import date, datetime
from datetime import timedelta as td
import xml.etree.ElementTree as ET
from suds.client import Client
import suds

def iniciar_proceso():
    if not os.path.isfile("wsaa.ini"):
        print("No se encontro el archivo de configuracion wsaa.ini")
        quit()

    configuracion = ConfigParser()

    configuracion.read("wsaa.ini")

    csr = os.getcwd() + "\\certificados\\" + configuracion['certificados']['csr']
    pem = os.getcwd() + "\\certificados\\" + configuracion['certificados']['pem']
    key = os.getcwd() + "\\certificados\\" + configuracion['certificados']['key']
    xml = os.getcwd() + "\\certificados\\" + configuracion['certificados']['xml']
    cms = os.getcwd() + "\\certificados\\" + configuracion['certificados']['cms']
    cuitRepresentada = configuracion['certificados']['rep']
    bat = os.getcwd() + "\\" + configuracion['bat']['bat']
    tiempo = configuracion['duracion']['minutos']
    servidor = configuracion['servidores']['constancia']

    tree = ET.parse('TA_ws_sr_constancia_inscripcion.xml')
    root = tree.getroot()
    for hijo in root.findall('./credentials'):
        token = hijo.find('token').text
        sign = hijo.find('sign').text
    cliente = Client(servidor)
    result = dict()
    result['token'] = token
    result['sign'] = sign
    result['cliente'] = cliente
    result['cuitRepresentada'] = cuitRepresentada
    return result

def getPersona_v2():
    try:
        iniciar = iniciar_proceso()
        resultado = iniciar['cliente'].service.getPersona_v2(iniciar['token'], iniciar['sign'],iniciar['cuitRepresentada'],
                                                             20203032723)
        print(resultado[0][0],'-',resultado[0][2],'-',resultado[0][3],'-',resultado[0][4],'-',resultado[0][5],'-',resultado[0][6],'-',resultado[0][7])
        resultado = resultado[0]        
        '''archivo=open ('remSalida.txt','w')
        for a in resultado:
            for b in a[1] :
                archivo.write(str(b.codigo)+'\t'+b.descripcion+'\n')
        archivo.close()'''
    except suds.WebFault as error:
        print("se ha producido un error: ", error)

getPersona_v2()        