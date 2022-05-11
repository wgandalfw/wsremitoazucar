from suds.client import Client
import suds
import os
from configparser import ConfigParser
from xml.etree.ElementTree import parse,Element
import xml.etree.ElementTree as ET



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
bat = os.getcwd() + "\\" + configuracion['bat']['bat']
tiempo = configuracion['duracion']['minutos']
servidor = configuracion['servidores']['remito']

url = "https://fwshomo.afip.gov.ar/wsremazucar/RemAzucarService?wsdl"

req = Client(url)

#asigno el formato de las variables directamente como me indica el webservice
authResquest = req.factory.create('ns0:AuthRequestType')
cuilSimple = req.factory.create('ns0:CuitSimpleType')

#print(authResquest)
#print(cuilSimple)

tree = ET.parse('TA_wsremazucar.xml')
root = tree.getroot()
for hijo in root.findall('./credentials'):
    token = hijo.find('token').text
    sign = hijo.find('sign').text

cliente = Client(servidor)

###cargo las variables########
authResquest.token = token
authResquest.sign = sign
authResquest.cuitRepresentada = 20282222303

cuilSimple=  30708772964


try:
    resultado = cliente.service.consultarCodigosDomicilio(authResquest,cuilSimple)
    print(resultado)   
except suds.WebFault as error:
    print("se ha producido un error: ", error)