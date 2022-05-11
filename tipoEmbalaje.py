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
    servidor = configuracion['servidores']['remito']
    entrada = configuracion['archivos']['entrada']
    salida = configuracion['archivos']['salida']

    tree = ET.parse('TA_wsremazucar.xml')
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
    result['entrada'] = entrada
    result['salida'] = salida
    return result

def consultarTiposEmbalaje():    
    try:
        iniciar = iniciar_proceso()
        with open(iniciar['entrada'],"r") as archivo:
            for linea in archivo:
                cuitTitula = linea
        resultado = iniciar['cliente'].service.consultarTiposEmbalaje(authRequest={'token': iniciar['token'], 'sign': iniciar['sign'], 'cuitRepresentada': iniciar['cuitRepresentada']})
        print(resultado)
        resultado = resultado[0]
        archivo=open (iniciar['salida'],'w')
        for a in resultado:
            for b in a[1] :
                archivo.write(str(b.codigo)+'\t'+str(b.descripcion)+'\n')
        archivo.close()
    except suds.WebFault as error:
        print("se ha producido un error: ", error)



consultarTiposEmbalaje()