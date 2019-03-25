# Script que re-instala un geoserver, a partir de archivos de respaldo.
import sys
import subprocess
import json
import os
import time

__author__="Raúl Medina Peña"

# Funcion que elimina los workspaces, datastores, group layers, layers, y styles de un geoserver.
#variables acceso del Geoserver
USUARIO        = 'admin'
PASSW          = 'geoserver'
URL_GEOSERVER  = 'http://localhost:8080/geoserver_try'
PATH_WORKSPACE = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredData/workspaces/'
PATH_LAYERS    = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredLayers/'
PATH_STYLES    = '/home/rmedina/RESPALDOS/respaldo_ACTUAL/ServerData/GeoserverCenapredData/workspaces/cen/styles/'

#Funcion que limpia un geoserver, elimina los workspaces, stores, layers y styles por default.
def clean_geoserver(user, pwd, url_geoserver):
	#Variables para borrar workspaces
	rest_get_workspaces = 'curl -u {usuario}:{password} -X GET {url}/rest/workspaces.json'.format(usuario=user, password=pwd, url=url_geoserver)
	prefix_rest_delete_ws = 'curl -u {usuario}:{password} -X DELETE {url}/rest/workspaces/'.format(usuario=user, password=pwd, url=url_geoserver)
	ext_recurse = '.json?recurse=true'
	ext = '.json'

	#Obtenemos todos los workspaces por default del geoserver
	response = subprocess.check_output(rest_get_workspaces, shell=True)
	ws_json = json.loads(response.decode())
	
	if ws_json['workspaces'] != '':

		
		#Borramos cada workspace 
		for ws in ws_json['workspaces']['workspace']:
			rest_delete = prefix_rest_delete_ws + ws['name'] + ext_recurse
			#print(rest_delete)
			subprocess.call(rest_delete, shell=True)

	#Variables para borrar styles
	rest_get_styles = 'curl -u {usuario}:{password} -X GET {url}/rest/styles.json'.format(usuario=user, password=pwd, url=url_geoserver)
	prefix_rest_delete_styles = 'curl -u {usuario}:{password} -X DELETE {url}/rest/styles/'.format(usuario=user, password=pwd, url=url_geoserver)

	#Obtenemos los estilos por default del geoserver
	response_sld = subprocess.check_output(rest_get_styles, shell=True)
	sld_json = json.loads(response_sld.decode())
	
	if sld_json['styles'] != '':
		for sld in sld_json['styles']['style']:
			sld_delete = prefix_rest_delete_styles + sld['name'] + ext
			#print(sld_delete)
			subprocess.call(sld_delete, shell=True)

#Funcion que crea los workspaces a partir de la carpeta de un geoserver.
def create_workspaces_geoserver(user, pwd, url_geoserver, path_resource):
	workspace_xml = '<workspace><name>{name}</name></workspace>'
	rest_workspace = 'curl -v -u {usuario}:{password} -XPOST -H "Content-type: text/xml" -d "{xml}" {url}/rest/workspaces'
	workspaces = next(os.walk(path_resource))[1]
	
	for ws in workspaces:
		ws_xml = workspace_xml.format(name=ws)
		#print(ws_xml)
		rest_post = rest_workspace.format(usuario=user, password=pwd, xml=ws_xml, url=url_geoserver)
		print(rest_post)
		subprocess.call(rest_post, shell=True)

def put_layers_geoserver(user, pwd, url_geoserver, path_layers):
	rest_layer = 'curl -v -u admin:geoserver -XPUT -H "Content-type: text/plain" -d "file://{path_layers}{store}/{shape}" \
			      {url_geoserver}/rest/workspaces/cen/datastores/{store}/external.shp'
	stores = next(os.walk(path_layers))[1]
	for st in stores:
		shape = get_shapefile('{path_layers}{store}/'.format(path_layers=path_layers, store=st))
		if shape is not None:
			rest_put = rest_layer.format(path_layers=path_layers, store=st, shape=shape, url_geoserver=url_geoserver)
			print(rest_put)
			subprocess.call(rest_put, shell=True)

def put_styles_geoserver(user, pwd, url_geoserver, path_styles):
	name_style     = '<style><name>{name}</name><filename>{name}.sld</filename></style>'
	rest_style     = 'curl -v -u {usuario}:{password} -XPOST -H "Content-type: text/xml" -d "{archivo_xml}" \
	                 {url_geoserver}/rest/workspaces/cen/styles'
	rest_contenido = 'curl -v -u {usuario}:{password} -XPUT -H "Content-type: application/vnd.ogc.sld+xml" -d @{path}{name_archivo}.sld \
	                 {url_geoserver}/rest/workspaces/cen/styles/{name_archivo}'
	
	#Obtenemos los nombres de los archivos .sld
	styles = get_all_styles(path_styles)
	
	for s in styles:
		xml_style = name_style.format(name=s.rstrip(".sld"))
		rest_post = rest_style.format(usuario=user, password=pwd, archivo_xml=xml_style, url_geoserver=url_geoserver)
		#print(rest_post)
		subprocess.call(rest_post, shell=True)
		
		rest_put = rest_contenido.format(usuario=user, password=pwd, path=path_styles, name_archivo=s.rstrip(".sld"), url_geoserver=url_geoserver)
		#print(rest_put)
		subprocess.call(rest_put, shell=True)


def get_shapefile(path_resource):
	files = os.listdir(path_resource)
	for f in files:
		if f.endswith('.shp'):
			return f

def get_all_styles(path_resource):
	styles = []
	files = os.listdir(path_resource)
	for f in files:
		if f.endswith('.sld'):
			styles.append(f)
	return styles



if __name__ == "__main__":
	clean_geoserver(USUARIO, PASSW, URL_GEOSERVER)
	create_workspaces_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_WORKSPACE)
	put_layers_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_LAYERS)
	put_styles_geoserver(USUARIO, PASSW, URL_GEOSERVER, PATH_STYLES)
	
	
