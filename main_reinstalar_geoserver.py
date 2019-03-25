# Script que re-instala un geoserver, a partir de archivos de respaldo.
import sys
import subprocess
import json
import os
import time

__author__="Raúl Medina Peña"

#Variables acceso del Geoserver
#Usuario del geoserver
USUARIO        = 'admin'
#Contraseña del usuario en el geoserver
PASSW          = 'geoserver'
#Direccion del geoserver
URL_GEOSERVER  = 'http://localhost:8080/geoserver_try'
#Direcciones de de nuestra informacion del GEOSERVER a respaldar
PATH_WORKSPACE = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredData/workspaces/'
PATH_LAYERS    = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredLayers/'
PATH_STYLES    = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredData/workspaces/cen/styles/'

#Funcion que limpia un geoserver, elimina los workspaces, stores, layers y styles por default.
def clean_geoserver(user, pwd, url_geoserver):
	#Sentencia para obtener los workspaces por default para despues borrarlos
	rest_get_workspaces = 'curl -u {usuario}:{password} -X GET {url}/rest/workspaces.json'.format(usuario=user, password=pwd, url=url_geoserver)
	#Sentencia para eliminar los workspaces
	prefix_rest_delete_ws = 'curl -u {usuario}:{password} -X DELETE {url}/rest/workspaces/'.format(usuario=user, password=pwd, url=url_geoserver)
	#recurse=true, forzamos a que se ejecute la peticion
	ext_recurse = '.json?recurse=true'

	#Ejecutamos la peticion, para obtener todos los workspaces por default del geoserver
	response = subprocess.check_output(rest_get_workspaces, shell=True)
	#El resultado de la peticion lo convertimos en un JSON
	ws_json = json.loads(response.decode())
	
	if ws_json['workspaces'] != '':
		#Borramos cada workspace 
		for ws in ws_json['workspaces']['workspace']:
			rest_delete = prefix_rest_delete_ws + ws['name'] + ext_recurse
			#print(rest_delete)
			subprocess.call(rest_delete, shell=True)

	#Variables para borrar styles
	#Sentencia para obtener los estilos por default
	rest_get_styles = 'curl -u {usuario}:{password} -X GET {url}/rest/styles.json'.format(usuario=user, password=pwd, url=url_geoserver)
	#Sentencia para eliminar los estilos por default
	prefix_rest_delete_styles = 'curl -u {usuario}:{password} -X DELETE {url}/rest/styles/'.format(usuario=user, password=pwd, url=url_geoserver)

	#Ejecutamos la peticion para obtener los estilos por default del geoserver
	response_sld = subprocess.check_output(rest_get_styles, shell=True)
	#Guardamos el resultado de la peticion en un JSON
	sld_json = json.loads(response_sld.decode())
	
	if sld_json['styles'] != '':
		#Iteramos sobre los estilos para ir eliminando uno por uno
		for sld in sld_json['styles']['style']:
			sld_delete = prefix_rest_delete_styles + sld['name'] + ext_recurse
			#print(sld_delete)
			subprocess.call(sld_delete, shell=True)

#Funcion que crea los workspaces a partir de la carpeta de un geoserver.
def create_workspaces_geoserver(user, pwd, url_geoserver, path_resource):
	#Sentencia que representa el xml para poder crear el workspace
	workspace_xml = '<workspace><name>{name}</name></workspace>'
	#Sentencia para crear un wrokspace
	rest_workspace = 'curl -v -u {usuario}:{password} -XPOST -H "Content-type: text/xml" -d "{xml}" {url}/rest/workspaces'
	#Obtenemos los directoriios que representan los workspace de nuestro repositorio local
	workspaces = next(os.walk(path_resource))[1]
	
	#Creamos cada workspace ene l geoserver
	for ws in workspaces:
		ws_xml = workspace_xml.format(name=ws)
		#print(ws_xml)
		rest_post = rest_workspace.format(usuario=user, password=pwd, xml=ws_xml, url=url_geoserver)
		#print(rest_post)
		subprocess.call(rest_post, shell=True)

#Funcion que carga las capas en el nuevo geoserver
def put_layers_geoserver(user, pwd, url_geoserver, path_layers):
	#Sentencia para poder crear layers en el geoserver
	rest_layer = 'curl -v -u admin:geoserver -XPUT -H "Content-type: text/plain" -d "file://{path_layers}{store}/{shape}" \
			      {url_geoserver}/rest/workspaces/cen/datastores/{store}/external.shp'
	#Obtenemos los directorios en donde se encuentran los shapefile de nuestro repositorio local
	stores = next(os.walk(path_layers))[1]
	#Creamos cada layer en el geoserver 
	#(NOTA: no se ha podido guardar la capa de fondo ya que es una piramide de mosaicos)
	for st in stores:
		shape = get_shapefile('{path_layers}{store}/'.format(path_layers=path_layers, store=st))
		if shape is not None:
			rest_put = rest_layer.format(path_layers=path_layers, store=st, shape=shape, url_geoserver=url_geoserver)
			print(rest_put)
			subprocess.call(rest_put, shell=True)

#Funcion que pone los estilos en el geoserver
def put_styles_geoserver(user, pwd, url_geoserver, path_styles):
	#Sentencia que representa el archivo XML para crear un nuevo "style"
	name_style     = '<style><name>{name}</name><filename>{name}.sld</filename></style>'
	#Sentencia para crear el nuevo "style" en el geoserver
	rest_style     = 'curl -v -u {usuario}:{password} -XPOST -H "Content-type: text/xml" -d "{archivo_xml}" \
	                 {url_geoserver}/rest/workspaces/cen/styles'
	#Sentencia para guardar el contenido del "style" 
	rest_contenido = 'curl -v -u {usuario}:{password} -XPUT -H "Content-type: application/vnd.ogc.sld+xml" -d @{path}{name_archivo}.sld \
	                 {url_geoserver}/rest/workspaces/cen/styles/{name_archivo}'
	
	#Obtenemos los nombres de los archivos .sld
	styles = get_all_styles(path_styles)
	
	#Creamos cada "style" en el geoserver
	for s in styles:
		xml_style = name_style.format(name=s.rstrip(".sld"))
		rest_post = rest_style.format(usuario=user, password=pwd, archivo_xml=xml_style, url_geoserver=url_geoserver)
		#print(rest_post)
		subprocess.call(rest_post, shell=True)
		
		rest_put = rest_contenido.format(usuario=user, password=pwd, path=path_styles, name_archivo=s.rstrip(".sld"), url_geoserver=url_geoserver)
		#print(rest_put)
		subprocess.call(rest_put, shell=True)


#Obtiene el archivo con extension .shp
def get_shapefile(path_resource):
	files = os.listdir(path_resource)
	for f in files:
		if f.endswith('.shp'):
			return f

#Obtiene todos los archivos .sld de un directorio
def get_all_styles(path_resource):
	styles = []
	files = os.listdir(path_resource)
	for f in files:
		if f.endswith('.sld'):
			styles.append(f)
	return styles


#Firma del metodo MAIN del programa
if __name__ == "__main__":
	clean_geoserver(USUARIO, PASSW, URL_GEOSERVER)
	create_workspaces_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_WORKSPACE)
	put_layers_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_LAYERS)
	put_styles_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_STYLES)
	
	
