# REINSTALCIÓN AUTOMATIZADA DE UN GEOSERVER

Esta reinstalación de geoserver se hace a partir de un repositorio local, en donde se encuentran las carpetas  
con la información de los _WORKSPACES_ , _LAYERS_, y _STYLES_.

Este repositorio con la información es un respaldo de la información principal del _GEOSERVER_ que se quiere respaldar.

### REQUERIMIENTOS
   * Lenguaje de programacion __PYTHON 3__
   * __GEOSERVER__ version 2.11.2

### EJECUCIÓN
   > _**python3** main_reinstalar_geoserver.py_

### DESCRIPCIÓN

El programa se compone de 4 funciones importantes:
   * Limpiar el GEOSERVER, esto lo hace por medio de la función __create_workspaces_geoserver__ 
   * Crear los _workspaces_ para después poder crear sus capas y sus estilos correspondientes  
     usando la función __create_workspaces_geoserver__
   * Poner las capas (layers), esto es por medio de la función __put_layers_geoserver__
   * Poner los estilos (styles) que afectan a cada capa, utilizando la función __put_styles_geoserver__
     (NOTA: aun no se pueden asignar los estilos directamente con una petición REST a GEOSERVER.
