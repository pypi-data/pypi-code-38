# Actualmente el sistema permite guardar los siguientes tipos de datos en los modelos
#     AutoField
#     CharField
#     TextField (RichText can have some issues)
#     IntegerField
#     FloatField
#     BooleanField
#     DateTimeField
#     FileField (Pero el archivo fisico no)
#
#     Funciona con:
#         RegularField
#         ForeingKey
#         ManyToMany
# Deberiamos encontrar una forma de hacer batch saves

#Import python
import csv
import codecs
#Import django
from django.db import transaction
from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime

#Import personales
from .functions import get_fields

# Create your views here.
def select_app(request):
    lista_apps = []
    models = []
    for x in apps.all_models:
        lista_apps.append(x)
        for y in apps.all_models[x]:
            if apps.all_models[x][y]._meta.auto_created is False:
                models.append(y)
    return render(request, 'select_app.html', {'apps': lista_apps, 'models': models, })

def select_models(request, app_name):
    lista_apps = []
    models = []
    for x in apps.all_models:
        if x == app_name:
            lista_apps.append(x)
            for y in apps.all_models[x]:
                if apps.all_models[x][y]._meta.auto_created is False:
                    models.append(y)
    return render(request, 'select_models.html', {'apps': lista_apps, 'models': models, })

def download(request, app_name):
    if request.method == "POST":
        models = []
        for x in apps.all_models:
            if x == app_name:#Si es nuestra app
                for y in apps.all_models[x]:
                    if y in request.POST.getlist('models'):#Si fue marcado
                        if apps.all_models[x][y]._meta.auto_created is False:
                            models.append(apps.all_models[x][y])
        #Configuramos la salida
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + app_name + '.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response, delimiter=';', lineterminator='\n', quoting=0)
        #Creamos la primera linea:
        writer.writerow(['A', app_name])
        #Recorremos los modelos
        for model in models:
            writer.writerow(['M', model._meta.model_name])
            #Obtenemos campos y Generamos la cabecera
            fields = get_fields(model)
            writer.writerow(['F']+fields)

            #Obtenemos todos los objetos del modelo
            items = model.objects.all()
            #recorrremos los campos del registro
            for item in items:
                linea = []
                for field in fields:
                    fname = field[0]
                    ftype = field[1]
                    if ftype == 'RegularField':
                        linea.append(str(getattr(item, fname)).replace(";", ",").replace("\r\n", "<nwline>"))
                    if ftype == 'ForeingKey':
                        dest = getattr(item, fname)
                        if dest is not None:
                            linea.append(dest.id)
                        else:
                            linea.append('')
                    if ftype == 'ManyToMany':
                        many = getattr(item, fname)
                        if many is not None:
                            linea.append([m.id for m in many.all()])
                        else:
                            linea.append('[]')
                writer.writerow(['R']+linea)
        return response
    else:
        return select_models(request, app_name)


@transaction.atomic
def restore(request, app_name):
    titulo = "Carga de " + app_name
    message = "Se cargaron con exito los modelos"
    if request.method == "GET":
        return render(request, "restore_csv.html", {'titulo': titulo, })
    else:#Si subieron un archivo
        # if not GET, then proceed
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            message = 'El archivo no es de tipo csv'
            return render(request, "restore_csv.html", {'titulo': titulo, 'message': message, })
        #if file is too large, return
        if csv_file.multiple_chunks():
            message = "El archivo es demasiado Grande (%.2f MB)."%(csv_file.size/(1000*1000))
            return render(request, "restore_csv.html", {'titulo': titulo, 'message': message, })
        #Preparamos el archivo csv
        file_data = csv_file.read().decode("utf-8-sig")
        lineas = file_data.split("\n")

        ready_models = {}#Limpiamos la lista de registros
        #empezamos el procesamiento
        for linea in lineas:
            if not linea == '':
                tipo_linea = linea[0]
                valores = linea[2:].split(';')
                #APPS
                if tipo_linea == 'A':#Checkeamos la app en la primer linea del documento
                    if valores[0] == app_name:
                        print("Iniciamos la restauracion de la app: " + app_name)
                    else:
                        message = "El archivo pertence a otra APP"
                        break

                #MODEL
                elif tipo_linea == 'M':#Si es linea que define modelo
                    for x in apps.all_models:#Recorremos los modelos
                        if x == app_name:
                            for y in apps.all_models[x]:
                                if apps.all_models[x][y]._meta.model_name == valores[0]:
                                    model = apps.all_models[x][y]
                                    ready_models[model._meta.model_name] = {}#Creamos sub dict para poner todos los items
                    print("Comenzamos a cargar el modelo: " + str(model))
                #FIELDS
                elif tipo_linea == 'F':#Si es la linea en que definimos los campos
                    field_list = []
                    for item in valores:
                        field_list.append(item.replace("(", "").replace(")", "").replace("'", "").replace(" ", "").split(","))
                    for index in range(len(field_list)):
                        field = field_list[index]
                        if len(field) == 5:
                            for x in apps.all_models:
                                if x == field[3]:
                                    for y in apps.all_models[x]:
                                        if y == field[4]:
                                            field[4]= apps.all_models[x][y]
                #RECORDS
                elif tipo_linea == 'R':#Procesamos los records
                    new_item = model()#instanciamos un nuevo registro
                    index = 0
                    for field in field_list:
                        fname = field[0]
                        ftipo = field[1]
                        fclase = field[2]
                        if len(field) == 5:
                            fdest = field[4]
                        #Procesamos segun el tipo de campo
                        if ftipo == 'RegularField':
                            if field[0] == 'id' and field[2] == 'AutoField':
                                try:
                                    new_item = model.objects.get(pk=valores[index])#Obtenemos el ya existente
                                except:
                                    pass#Al no hacer nada dejamos la id vacia para que le genere una nueva
                                #Lo disponibilizamos por si llega a ser foreignkey de otro modelo
                                ready_models[model._meta.model_name][valores[index]] = new_item
                            else:#Si no es un campo ID
                                if fclase in ('CharField', 'TextField'):
                                    setattr(new_item, fname, valores[index].replace("<nwline>","\r\n"))
                                elif fclase == 'IntegerField':
                                    setattr(new_item, fname, int(valores[index]))
                                elif fclase == 'FloatField':
                                    setattr(new_item, fname, float(valores[index]))
                                elif fclase == 'BooleanField':
                                    if valores[index] == "True":
                                        setattr(new_item, fname, True)
                                    else:
                                        setattr(new_item, fname, False)
                                elif fclase == 'DateTimeField':
                                    setattr(new_item, fname, parse_datetime(valores[index]))
                                elif fclase == 'FileField':
                                    #Deberiamos hacer algo mas respecto al archivo fisico
                                    setattr(new_item, fname, valores[index])
                        elif ftipo == 'ForeingKey':
                            if valores[index] != '':
                                try:
                                    dest = ready_models[fdest._meta.model_name][valores[index]]
                                    setattr(new_item, fname, dest)
                                except:
                                    try:
                                        dest = fdest.objects.get(pk=valores[index])
                                        setattr(new_item, fname, dest)
                                    except:
                                        message = "Inconsistencia en foreignkey"
                                        message+= "Linea" + str(linea)
                                        break
                        elif ftipo == 'ManyToMany':
                            new_item.save()#Tiene que tener idea antes de cargarle los many2many
                            item_set = getattr(new_item, fname)
                            for m2m_id in valores[index][1:][:-1].split(','):
                                try:
                                    dest = ready_models[fdest._meta.model_name][m2m_id.replace(" ", "")]
                                    item_set.add(dest)
                                except:
                                    try:
                                        dest = fdest.objects.get(pk=m2m_id)
                                        item_set.add(dest)
                                    except:
                                        message = "Inconsistencia en ManyToMany"
                                        message+= "Linea" + str(linea)
                                        break                              
                        index += 1
                    #Una vez procesada la linea de registro:
                    new_item.save()#Preparamos para guardar
        return render(request, "restore_csv.html", {'titulo': titulo, 'message': message, })