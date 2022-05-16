from configparser import ConfigParser
import os
import sys
import json
from datetime import date, datetime
from datetime import timedelta as td
import xml.etree.ElementTree as ET
from suds.client import Client
import suds
'''
probando sinc con git
'''
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

def emitirRemito():
    try:
        iniciar = iniciar_proceso()
        tree = ET.parse(iniciar['entrada'])
        root = tree.getroot()
        for hijo in root.findall('./emitirRemito'):
            codigoRemito = hijo.find('codigoRemito').text
            cuitConductor = hijo.find('cuitConductor').text
            cedulaConductor = hijo.find('cedulaConductor').text
            nombreConductor = hijo.find('nombreConductor').text
            apellidoConductor = hijo.find('apellidoConductor').text
            dominioVehiculo = hijo.find('dominioVehiculo').text
            dominioAcoplado = hijo.find('dominioAcoplado').text
            fechaInicioViaje = hijo.find('fechaInicioViaje').text
        resultado = iniciar['cliente'].service.emitirRemito(authRequest={'token': iniciar['token'], 'sign': iniciar['sign'], 'cuitRepresentada': iniciar['cuitRepresentada']},
                                                            emitirRemito={'codigoRemito' : codigoRemito,
                                                                          'transporte' : {
                                                                              'conductor' : {
                                                                                  'conductorNacional' : {
                                                                                      'cuitConductor' : cuitConductor
                                                                                  },
                                                                              },   
                                                                              'dominioVehiculo' : dominioVehiculo,
                                                                              'dominioAcoplado' : dominioAcoplado
                                                                              }, 
                                                                          'fechaInicioViaje' : fechaInicioViaje
                                                                          })        
        archivo=open ('remSalida.txt','w')
        archivo.write(str(resultado[0])+'\n')
        resultado = resultado[1]        
        for a in resultado:
            for b in a[1] :
                archivo.write(str(b.codigo)+'\t'+b.descripcion+'\n')
        archivo.close()
    except suds.WebFault as error:
        print("se ha producido un error: ", error)

emitirRemito()