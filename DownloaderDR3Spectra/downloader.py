from astroquery.simbad import Simbad #importa el modulo astroquery de la api de simbad
from astropy.table import Column, Table, join 
# se utilizan para trabajar con tablas de datos de una manera sencilla y eficiente.
import os
import numpy as np
from astroquery.gaia import Gaia #importa el modulo astroquery de la api de gaia
from bokeh.plotting import figure, output_file, save #importa libreria para generar graficos y guardarlos en formato html o svg.
from bokeh.models import ColumnDataSource, Label, LabelSet, Range1d
#se utilizan para trabajar con datos y crear elementos de gráficos específicos, como fuente de datos, etiquetas, conjuntos de etiquetas y límites de ejes en Bokeh.

def get_querys(file_name): # recibe un parametro que es un nombre de un archivo txt
	#se crean 3 listas vacias 
	names=[]
	querys=[]
	list_of_types_to_ignore=[]
	file=open(file_name,"r") # se abre el archivo en modo lectura 
	for line in file:#  itera a traves de cada linea de archivo
		if line[0]=='#':#si la linea comienza con un # ignora la linea
			continue
		else:
			data=line.split(" |& ") #cada linea se divide por un separador |&
			names.append(data[0]) #se agrega la primer parte de la linea a names 
			querys.append(data[1])#la segunda a querys 
			list_of_types_to_ignore.append(data[2])#la tercera a list of types
	file.close()#despues de leer todas las lineas este se cierra 
	return names, querys, list_of_types_to_ignore #la funcion retorna las listas y su resultado


def get_gaia_id(id, ids):#recibe dos ides 
	id_found=False #variable booleana
	id_gaia=id #se le asigna el id de gaia 
	if id_gaia.find('Gaia DR2')>=0: #busca en id_gaia si se encuentra la cadena "Gaia DR2"
		id_gaia=id_gaia[9:len(id_gaia)] #extrae y guarda en la variable
		id_found=True #se vuelve true 
		#find object
	else: #en caso de que no se encuentre 
		id_gaia=ids #se le asignan los ids 
		index=id_gaia.find('Gaia DR2') #busca de igual manera 
		if index>=0:
			id_gaia=id_gaia[index+9:len(id_gaia)] # y se guarda 
			index=id_gaia.find('|') #se busca el separador | en id_gaia y se elimina todo despues de ese separador
			if id_gaia.find('|')>=0:
				id_gaia=id_gaia[0:index]
			index=id_gaia.find(' ')
			if id_gaia.find('|')>=0:
				id_gaia=id_gaia[0:index]
				id_found=True
				#find object
	return id_found, id_gaia #al final la funcion retorna los valores del id 


def save_table(name, phase, object_list): #recibe los 3 parametros 
	if type(object_list)!=None: #Verifica si object_list es difernte de none
		object_list_to_save=object_list.copy()# si es diferente de none crea una copia 
		if(os.path.exists(name+'_phase_'+str(phase)+'.vot')):#comprueba si existe un archivo con el nombre name_phase_str(pahse).vot, si existe lo elimina
			os.remove(name+'_phase_'+str(phase)+'.vot')#elimina el archivo
		object_list_to_save.write(name+'_phase_'+str(phase)+'.vot', format='votable')#usando el metodo write escribe el contenido de object_list_to_save.

###############
def query_simbad(query): #toma un parametro llamada query
	custom_search=Simbad() #crea la instancia de la clse simbad llamada custom_search
	custom_search.TIMEOUT = 60*60#asigna un timeout de 60 min
	custom_search.add_votable_fields("id(Gaia)", "flux(J)", "flux(H)", "flux(K)", "flux(V)", "flux(B)", "ids", "otypes") #usando el metodo "add_votables_fields"  agrega los campos correspondientes a la consulta
	result=custom_search.query_criteria(query) #usando query_criteria realiza la consulta utilizando el argumento query y la asigna a result
	return result #rertornando el result 


def calculate_fluxes(table): #toma un argumento llamado table
	if(table['flux_v']>table['flux_k']):#si el valor de tablefluxv es mayor a tablefluxk
		table['flux_flag']=1 #agrega una nueva columa flux_flag con valor 1 en la tabla
	else:
		table['flux_flag']=0 # si no agrega una nueva columna flux_flag con valor 0 en la tabla 
	#agrega las siguientes columnas con los valores calculados como la diferencia entre las columnas correspondientes de flujos
	table['j_h']=table['flux_j']-table['flux_h'] 
	table['h_k']=table['flux_h']-table['flux_k']
	table['b_v']=table['flux_b']-table['flux_v']
	table['v_k']=table['flux_v']-table['flux_k']


def get_star_name(name):
	return name



def look_for_gaia_ids(result, ids_list):#toma 2 agrumentos anteriormente creados (en  query_simbad) 
	new_table=None
	for star in result: #itera cada elemento star en result
		id_found, id = get_gaia_id(star['ID_Gaia'], star['IDS']) #ejecuta la funcion get_gaia_id con sus respectivos argumentos
		if id_found: # si dicha funcion devuelve true entonces
			ids_list.append(id) #se agrega el valor del id retornado  por dicha funcion 
			if type(new_table)==type(None): #si new table es none entonces crea una nueva tabla usando la informacion de star y agrega las columnas "Source_id", "name" etc.
				new_table=Table(star)
				new_table.keep_columns(['FLUX_J', 'FLUX_H', 'FLUX_K', 'FLUX_V','FLUX_B'])
				new_table.add_column(np.int64('1111111111111111111'), name='source_id', index=0)
				new_table[0]['source_id']=np.int64(id)
				new_table.rename_column('FLUX_J', 'flux_j')
				new_table.rename_column('FLUX_H', 'flux_h')
				new_table.rename_column('FLUX_K', 'flux_k')
				new_table.rename_column('FLUX_V', 'flux_v')
				new_table.rename_column('FLUX_B', 'flux_b')
				a=Column( data=[' '*30],name='Name')
				new_table.add_column(a, index=1)
				new_table[0]['Name']=get_star_name(star['MAIN_ID'])
				a=Column(data=[0.00000000], name='j_h' )
				new_table.add_column(a)
				a=Column(data=[0.00000000], name='h_k' )
				new_table.add_column(a)
				a=Column(data=[0.00000000], name='b_v' )
				new_table.add_column(a)
				a=Column(data=[0.00000000], name='v_k' )
				new_table.add_column(a)
				c=Column(data=[-1], name='flux_flag' )
				new_table.add_column(c)
				calculate_fluxes(new_table[0]) #tambien se ejecuta la funcion  calculate_fluxes 
			else: #si new_table no es none entocnes 
				new_table.add_row([np.int64(id), get_star_name(star['MAIN_ID']), star['FLUX_J'], star['FLUX_H'],star['FLUX_K'],star['FLUX_V'],star['FLUX_B'], 0., 0., 0., 0., 0]) #agrega una nueva fila a new table con la infomacion de star y los valores predefinidos para las columnas asignadas
				calculate_fluxes(new_table[len(new_table)-1])# se ejecuta calculate fluxes con su respectivo argumento
	return new_table #finalmente retorna la tabla creada


def create_edr3_query(list_ids): #toma de argumento el list_ids
	query='' #vacia la query 
	if type(list_ids)!=type(None): #verifica si list_ids es diferente de none si es asi entonces
		#construye una consulta para seleccionar informacion de estrellas de la tabla gaia_source
		# en la base de datos de gaiaedr3 y gaiadr2 la consulta se une a ambas tables sobre
		# el source_id y se seleccionan solo las estrellas que tengan su sources id en la tabla
		# list_ids y agrega las columnas requeridas y las asigna a la variable query 
		""" query+='select g3.source_id,g3.ra,g3.ra_error,g3.dec,g3.dec_error,g3.parallax,g3.parallax_error,'
		query+='g3.parallax_over_error,g3.phot_g_mean_flux,g3.phot_g_mean_mag,g3.phot_bp_mean_flux,g3.phot_bp_mean_mag,'
		query+='g3.phot_rp_mean_flux,g3.phot_rp_mean_mag,g3.bp_rp,g3.bp_g,g3.g_rp,g3.dr2_radial_velocity,'
		query+='g3.dr2_radial_velocity_error, '
		query+='g2.phot_variable_flag, g2.teff_val, g2.a_g_val from gaiaedr3.gaia_source as g3 inner join '
		query+='gaiadr2.gaia_source as g2 on (g3.source_id=g2.source_id) where g3.source_id in '
		query +='('  """
		query+='SELECT * FROM gaiadr3.xp_summary where source_id in '
		query +='(' 
    
		for id in list_ids:
			query+=' '+id+', '
		query=query[:len(query)-2]

		query+=' )'
	return query #retorna el query


def search_in_gaia(query): #argumento query
	job = Gaia.launch_job(query) # Utiliza la clase Gaia para crear un trabajo (job) con la query dada.
	result=job.get_results() #Recupera los resultados de dicho trabajo (job) y los asigna a la variable "result".
	if type(result)!=type(None): #Verifica si el resultado es distinto de "None"
		if len(result)==0: #si es así, se verifica si la longitud de resultado es cero si es asi
			result=None # se asigna none a la variable resultado 
	return result #devuelve result 


def merge_tables(simbad_table, gaia_table):
	merged_table=None #inicializa la varibale como none
	list_of_ids_in_gaia=[] # lista vacia 
	list_ids_to_remove=[] #lista vacia 
	new_simbad_table=simbad_table.copy() #crea una copia de simbad_table y la asigna a una nueva tabla
	if type(gaia_table)!=type(None): #verifica si "gaiatable" es diferente de none, si es asi entonces  
		for stars in gaia_table: #itera sobre cada estrella en gaia table y agrega su source id a "list of ids in gaia"
			list_of_ids_in_gaia.append(stars['source_id'])
		for i in range(len(simbad_table)-1,-1,-1): # itera cada fila en simbad table desde el ultimo elemento hasta el primero y verifica si el source id esta en list of ids in gaia
			if simbad_table[i]['source_id'] not in list_of_ids_in_gaia:
				list_ids_to_remove.append(i) #si no esta entonces agrega el indice de esa fila a list id to remove
		for id_to_remove in list_ids_to_remove:  #itera sobre list id to remove
			new_simbad_table.remove_row(id_to_remove) #elimina las dilas en new simbad table utilizando remove_row
		merged_table=join(gaia_table, new_simbad_table) # utiliza la funcion join para uni "gaia table" y new simbad table y lo asigna a merged_table
	return merged_table #retorna merged_table


def ignore_otypes(table, types_to_ignore):
	types_to_ignore=type_to_ignore.strip() # limpia el strig types_to ignore y se separa en una lista 
	if types_to_ignore!="": 
		ignore=types_to_ignore.split(' ')
		list_of_types_to_ignore=types_to_ignore.split("|")#utilizando el caracter | como separador
		for i in range(len(table)-1,-1,-1):#itera sobre cada tipo a ignorar en la lista 
			for ignore_type in ignore: 
				if table[i]['OTYPES'].find(ignore_type)>-1: #verifica los campos otypes en la fila actual contiene el tipo a ignorar utilizando el metodofind si se encuentra
					table.remove_row(i) #elimina la fila y se detiene el ciclo 
					break
	return table #retorna la tabla actualizada 

def generate_graph(name, phases, number_of_objects_per_phase): #recibe 3 agrumentos
	output_file(f'{name}_info.html') #especificar el nombre del archivo de salida que se guardara el grafico
	fig=figure(title=f'Number of objets for each phase \n{name}:', x_range=phases) #crea una figura y especifica el titulo del grafico y el rango del ejex
	source = ColumnDataSource(data=dict( # crea una fuente de datos utilizando la clase columndatasource lso datos para el grafico son espeficados como un diccionario  con 3 claves x y names
		x=phases, y=number_of_objects_per_phase, names=[f'{number_of_objects_per_phase[i]} objects' for i in range(len(number_of_objects_per_phase))])) #labelesSet para crear las etiquetas con numero de objetos encontrados que se mostaran
	labels = LabelSet(x='x', y='y', text='names', x_offset=0, y_offset=5, text_align='center', source=source, render_mode='canvas') #
	fig.vbar(x='x', top='y', width=0.9, color='red', source=source) #luego utiliza vbar para generar el grafico de las barras con las caracetristicas especificas 
	fig.xaxis[0].axis_label = 'phase' #utiliza xaxis y yaxis para etiquetar los ejes
	fig.yaxis[0].axis_label = 'Number of objects found'
	fig.y_range.start=0 
	fig.add_layout(labels)
	save(fig) #utilizando la funcion save para guardar el grafico en el archivo mencionado anterior mente
	number_of_objects_per_phase.clear()# por ultimpo limpia el contenido del argumento number of objects

def add_abs_gaia_magnitude(table):
	new_column=Column( data=[0.000000000],name='g_abs_mag')
	table.add_column(new_column, index=23)
	for star in table:
		star['g_abs_mag']=calculate_abs_gaia_magnitude(star['phot_g_mean_mag'], star['parallax'], star['a_g_val'])
	return table



def calculate_abs_gaia_magnitude(mag_g, parallax, ext, mag_err=None, parallax_err_mas=None):
	try:
		if type(parallax)!=type(np.float64('0.0')):
			return np.nan
		d_pc = np.abs(1000.0/parallax)
		if type(ext)==type(np.float32(1.0)):
			val = (5+mag_g-(5*np.log10(d_pc))+ext)
			return val
		else:
			val = (5+mag_g-(5*np.log10(d_pc)))
			return val
	except ZeroDivisionError:
		return np.nan





if __name__ == '__main__':
	names, querys, types_to_ignore=get_querys('query.txt') # Llama a la función get_querys que se encuentra en un archivo separado, pasando como argumento 'query.txt' y guarda el resultado en las variables
	Gaia.login(user='yhernand', password='Lilufifi1!')
	number_of_objects_per_phase=[]#crea una lista vacia que se utilizara mas adelante para guardar el numero de objetos encontrados en cada fase del proceso 
	phases=[f'phase_{i}' for i in range(1,6)] # crea una lista phases utilizando la compresion de listas con los nombres de cada fase del proceso 
	for i in range(len(names)): #utiliza un bucle for  para recorrer la lista names en cada iteracion se asignan las variables name query y type to ignore
		name=names[i]
		query=querys[i]
		type_to_ignore=types_to_ignore[i]
		result=query_simbad(query) #utiliza la funcion query simbad pasando como argumento query y guarda el resultado en una variable
		ids_list=[]
		if type(result)!=None: #utiliza un if statment para comprobar que existe el result y su longitud es mayor a 0 
			if len(result)>0:
				#Todos losa objetos que encuentra con la consulta
				save_table(name, 1, result)
				number_of_objects_per_phase.append(len(result))
				result2=ignore_otypes(result, type_to_ignore)
				#los objetos que encontró ignorando los tipos (que no estan clasificados como el objeto principal)
				save_table(name, 2, result2)
				number_of_objects_per_phase.append(len(result2))
				new_table=look_for_gaia_ids(result2, ids_list)
				#los objetos que tienen identificador GAIA
				save_table(name, 3, new_table)
				number_of_objects_per_phase.append(len(new_table))
		query_gaia=create_edr3_query(ids_list)
		#Genera el archivo que contiene la consulta
		archivotxt = open("GigantesR.txt", "w")
		archivotxt.write(query_gaia)
		gaia_table=search_in_gaia(query_gaia)
		#los objetos que encontró en GAIA dr3
		save_table(name, 4, gaia_table)
		number_of_objects_per_phase.append(len(gaia_table))
		merged_table=merge_tables(new_table, gaia_table)
		#merged_table=add_abs_gaia_magnitude(merged_table)
		#los objetos que tienen completo los colores y sus magnitudes
		save_table(name, 5, merged_table)
		number_of_objects_per_phase.append(len(merged_table))
		print(f'{name} finished...')
		generate_graph(name,phases,number_of_objects_per_phase)
