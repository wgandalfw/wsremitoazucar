from suds.client import Client
import suds
import os
from configparser import ConfigParser
from xml.dom import minidom

configuracion = ConfigParser()
configuracion.read("wsaa.ini")
entrada = configuracion['archivos']['entrada']

def getAuth(estructura):
    auto=estructura.factory.create('ns0:AuthRequestType')
    tree = minidom.parse('TA_wsremazucar.xml')
    root = tree.getElementsByTagName('credentials')    
    for hijo in root:
        auto.token = hijo.getElementsByTagName('token')[0].firstChild.data
        auto.sign = hijo.getElementsByTagName('sign')[0].firstChild.data    
    return auto

def getIdReqCliente(estructura):
    remitoArchivo= minidom.parse(entrada)
    idrem = remitoArchivo.getElementsByTagName('idReqCliente')[0]
    idReqClient = idrem.firstChild.data
    return idReqClient

def getRemito(estructura):
    receptorNacional= estructura.factory.create('ns0:ReceptorNacionalComplexType') 
    remito= estructura.factory.create('ns0:RemitoBaseType') 
    viaje=estructura.factory.create('ns0:ViajeType') 
    tramo=estructura.factory.create('ns0:TramoComplexType')
    automotor=estructura.factory.create('ns0:AutomotorType')
    transporteNacional=estructura.factory.create('ns0:TransporteNacionalComplexType')
    arraymercaderias = estructura.factory.create('ns0:ArrayMercaderiasType')
    mercaderia= estructura.factory.create('ns0:MercaderiaAltaType')
    remitoArchivo= minidom.parse(entrada)

    nodo = remitoArchivo.getElementsByTagName('remito')
    for hijo in nodo:
        remito.esEntregaMostrador = hijo.getElementsByTagName('esEntregaMostrador')[0].firstChild.data
        remito.puntoEmision = hijo.getElementsByTagName('puntoEmision')[0].firstChild.data
        remito.cuitTitularMercaderia = hijo.getElementsByTagName('cuitTitularMercaderia')[0].firstChild.data
        remito.tipoTitularMercaderia = hijo.getElementsByTagName('tipoTitularMercaderia')[0].firstChild.data
        remito.numeroMaquila = hijo.getElementsByTagName('numeroMaquila')[0].firstChild.data
        remito.cuitAutorizadoRetirar = hijo.getElementsByTagName('cuitAutorizadoRetirar')[0].firstChild.data
        remito.importeCot = hijo.getElementsByTagName('importeCot')[0].firstChild.data
        nodoReceptor = remitoArchivo.getElementsByTagName('receptor')
        for hijoReceptor in nodoReceptor:
            remito.receptor.cuitPaisReceptor=hijoReceptor.getElementsByTagName('cuitPaisReceptor')[0].firstChild.data
            nodoReceptorNacional = remitoArchivo.getElementsByTagName('receptorNacional')
        for hijoReceptorNacional in nodoReceptorNacional:
            receptorNacional.cuitReceptor = hijoReceptorNacional.getElementsByTagName('cuitReceptor')[0].firstChild.data
            receptorNacional.codDomReceptor = hijoReceptorNacional.getElementsByTagName('codDomReceptor')[0].firstChild.data
            remito.receptor.receptorNacional=receptorNacional
        nodoviaje = remitoArchivo.getElementsByTagName('viaje')
        for hijoviaje in nodoviaje:
            viaje.fechaInicioViaje=hijoviaje.getElementsByTagName('fechaInicioViaje')[0].firstChild.data
            viaje.kmDistancia=hijoviaje.getElementsByTagName('kmDistancia')[0].firstChild.data
            remito.viaje=viaje
            nodoAuto = remitoArchivo.getElementsByTagName('automotor')
            for hijoAuto in nodoAuto:
                automotor.codPaisTransportista=hijoAuto.getElementsByTagName('codPaisTransportista')[0].firstChild.data
                automotor.dominioVehiculo=hijoAuto.getElementsByTagName('dominioVehiculo')[0].firstChild.data
                trasNac = remitoArchivo.getElementsByTagName('transporteNacional')
                for hijoTransNac in trasNac:
                    transporteNacional.cuitTransportista=hijoTransNac.getElementsByTagName('cuitTransportista')[0].firstChild.data
                    transporteNacional.cuitConductor=hijoTransNac.getElementsByTagName('cuitConductor')[0].firstChild.data
        automotor.transporteNacional=transporteNacional
        tramo.automotor=automotor
        remito.viaje.tramo=tramo
        
        merca = remitoArchivo.getElementsByTagName('mercaderia')
        for hijomerca in merca:
            mercaderia.orden=hijomerca.getElementsByTagName('orden')[0].firstChild.data
            mercaderia.anioZafra=hijomerca.getElementsByTagName('anioZafra')[0].firstChild.data
            mercaderia.cantidad=hijomerca.getElementsByTagName('cantidad')[0].firstChild.data
            mercaderia.tipoProducto=hijomerca.getElementsByTagName('tipoProducto')[0].firstChild.data
            mercaderia.unidadMedida=hijomerca.getElementsByTagName('unidadMedida')[0].firstChild.data
            mercaderia.tipoEmbalaje=hijomerca.getElementsByTagName('tipoEmbalaje')[0].firstChild.data

        arraymercaderias.mercaderia=mercaderia
        remito.arrayMercaderias=arraymercaderias
    return remito
   

if not os.path.isfile("wsaa.ini"):
    print("No se encontro el archivo de configuracion wsaa.ini")
    quit()


cuitRepresentada = configuracion['certificados']['rep']
servidor = configuracion['servidores']['remito']

req = Client(servidor)
authResquest = getAuth(req)
authResquest.cuitRepresentada = cuitRepresentada


idReqClient = getIdReqCliente(req)

remito = getRemito(req)

try:    
    salida = configuracion['archivos']['salida']
    resultado= req.factory.create('ns0:RemitoReturnType')     
    resultado=req.service.generarRemito(authResquest,idReqClient,remito)    
    print(resultado.resultado)
    with open(salida,"w") as archivo:
        archivo.write(resultado.resultado + '\n')
        print(resultado)
        if resultado.resultado == "R":
            error= req.factory.create('ns0:CodigoDescripcionType')
            error = resultado.arrayErrores[0]
            archivo.write(str(error[0].codigo) + '\t' + error[0].descripcion)
            print(error[0].codigo,'=',error[0].descripcion)
        else:
            autorizado = req.factory.create('ns0:RemitoDatosAutorizacionType')
            autorizado = resultado.remitoDatosAutorizacion
            archivo.write(str(autorizado.codigoRemito) + '\t' + str(autorizado.nroComprobante) + '\t' + str(autorizado.idTipoComprobante) + '\t' + str(autorizado.codigoAutorizacion) + '\t' + str(autorizado.fechaEmision) + '\t' + str(autorizado.fechaVencimiento) + '\t' + autorizado.estado),
            print(autorizado.codigoRemito,'=',autorizado.nroComprobante)
    archivo.close()
except suds.WebFault as error:
    print ("se ha producido un error: ",error)