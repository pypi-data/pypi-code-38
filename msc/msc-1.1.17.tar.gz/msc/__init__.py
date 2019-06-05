import os,sys,inspect
from kafka import KafkaConsumer
from kafka import KafkaProducer
import _thread
import json,datetime
from flask import Flask
import logging
from pymongo import MongoClient
import base64,pprint,time
from colorama import init, Fore, Back, Style
import copy
import asyncio
from concurrent import futures
from threading import Thread
import redis
import hashlib

#from concurrent.futures import ThreadPoolExecutor,futures,ProcessPoolExecutor
class db():
    __mongo_uri = ""

    def __init__(self,mongo_uri = ""):
        self.__mongo_uri = mongo_uri
        
    def conexion(self):
        conexion = None
        try:        
            conexion = MongoClient(self.__mongo_uri)
            return conexion
        except:
            return None

class microservice(db):

    loop = asyncio.get_event_loop()
    variable_entorno = "MQ"
    loopito = None
    _debug = False
    service_app = ""
    service_name = ""
    service_topic_name = ""
    service_version = ""
    server_cola_mensajeria = ""
    servers_mensajeria = []
    service_es_worker = None
    __sincrono = False
    __conexion_redis = None
    __producer = None
    __consumer = None
    __flujo = []
    __flujoPrincipal = {}
    __functionWorkerCambiarData = None
    __errores = {}
    __config_serv = {}
    __respuesta_asincronos = []
    __tiene_asincronos = False
    __validar_llave_repetida = False
    __pool_redis = None

    def __init__(self,configuracion):
        self._debug  = configuracion["_debug"]

        self.service_app = configuracion["_appName"]
        self.service_name = configuracion["_actionName"]
        self.service_es_worker = True if configuracion["_type"].upper() == "WORKER" else False
        if configuracion["_appName"] == "appcoppel" and configuracion["_versionName"] == "v1":
            self.service_topic_name = configuracion["_actionName"]
        else:
            self.service_topic_name = configuracion["_appName"]+"_"+configuracion["_versionName"]+"_"+configuracion["_actionName"]
        self.service_version = configuracion["_versionName"]

        if os.environ.get("DEBUG"):
            if os.environ.get("DEBUG") == "1":
                self._debug = True
            else:
                self._debug = False

        #Reviso que existan las variables de entorno
        f = self.__obtener_vars_entorno()
        if not f:
            if configuracion["_zookeeperServer"] != "":
                self.server_cola_mensajeria = configuracion["_zookeeperServer"]
                self.__servers_m_q()
            else:
                print("No se definio el servidor de messagequeue")
                sys.exit(0)
        else:
            self.__servers_m_q()

    def health_check(self):
        app = Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.logger.disabled = True
        @app.route("/")
        def check():
            errorProducer = False
            msj = self.__json_to_b64({'data': {'smoketest': 1}, 'headers': {'Asynchronous': False, 'Authorizacion': ''}, 'metadata': {'id_operacion': '0', 'id_transaction': '0', 'intents': 0, 'callback': '0', 'owner': '0', 'uowner': '0', 'uworker': '0', 'worker': 'pruebita2', 'asynchronous': False, 'mtype': 'input', 'bifurcacion': False, 'time': '0', 'from': '0'}})
            
            """*****************************
                Revisar conexion del PRODUCER
            *****************************"""
            try:
                #Revisar si puedo escribir y escribir el topico con data health_ckeck
                future = self.__producer.send(self.service_topic_name,key=str.encode(str("test")),value=msj)
                #revisar si responde en menos de 15 segundos si no esto producira un error y regresara UNHEALTY
                result = future.get(timeout=15)
            except:
                errorProducer = True
            
            if errorProducer:
                print("error producer : ",errorProducer)
                return "error", 500
            else:
                print("producer OK!")
                return "healthy!",200
        try:
            app.run(host="0.0.0.0",port=80,threaded=True)
        except :
            print("ya esta acorriendo por este puerto health check")

    def __servers_m_q(self):
        var = self.server_cola_mensajeria.split(",")
        arr = []
        for item in var:
            if item[len(item)-4:len(item)] == "2181":
                modif = item[0:len(item)-4] + "9092"
                arr.append(modif)
            else:
                arr.append(item)
        self.servers_mensajeria = arr

    def __obtener_vars_entorno(self):
        self.server_cola_mensajeria = os.environ.get(self.variable_entorno)
        return True if self.server_cola_mensajeria else False
    
    def setErrors(self,obj):
        self.__errores = obj

    def start(self,function = object,flujo=[]):
        if self.service_es_worker == None:
            print("No se ha definido tipo de microservicio")
            sys.exit(0)
        else:
            if self.service_es_worker:
                print("start Worker")
                self.__config_serv = flujo
                self.__funcion_worker(function,flujo)
            else:
                print("start Bifurcacion")
                flujito = self.__modificarFlujo(flujo)

                self.__funcion_bifurcacion(function,flujito)
            
    def __modificarFlujo(self,flujo):

        self.__flujoPrincipal = flujo
        reconstruido = []    
        modificado = []
        if len(flujo) > 0:
            modificado.append({
                "_appName":self.service_app,
                "_actionName":self.service_name,
                "_versionName":self.service_version
            })
            
            for item3 in flujo:
                modificado.append(item3)


            objetos = len(modificado)
            count = 0

            for item in modificado:
                objeto = {}
                objInsertar = []
                if type(item) is dict:
                    # ! Owner_Conf
                    if count == 0:
                        objeto["grabar_metadata"] = True
                        if item["_versionName"] == "v1" and item["_appName"] == "appcoppel":
                            objeto["owner_conf"] = item["_actionName"]
                        else:
                            objeto["owner_conf"] = item["_appName"]+"_"+item["_versionName"]+"_"+item["_actionName"]
                    else:

                        if modificado[count]["_appName"] == "appcoppel" and modificado[count]["_versionName"] == "v1":
                            objeto["owner_conf"] = modificado[count]["_actionName"]
                        else:
                            objeto["owner_conf"] =  modificado[count]["_appName"]+"_"+ modificado[count]["_versionName"]+"_"+ modificado[count]["_actionName"]
                    
                    # ! Worker_Conf
                    if (count + 1) < objetos:
                        if type(modificado[count+1]) is list:
                            self.__tiene_asincronos = True
                            worker_conf = ""
                            total = len(modificado[count+1])
                            for item2 in modificado[count+1]:
                                worker_conf += item2["_appName"]+"_"+item2["_versionName"]+"_"+item2["_actionName"] + ","
                                try:
                                    objInsertar.append({
                                        "end": False,
                                        "async":True,
                                        "paralelos":total,
                                        "owner_conf": item2["appName"]+"_"+item2["_versionName"]+"_"+item2["_actionName"],
                                        "worker_conf": modificado[count + 2]["_appName"]+"_"+modificado[count + 2]["_versionName"]+"_"+modificado[count + 2]["_actionName"]
                                    })
                                except:
                                    objInsertar.append({
                                        "end": True,
                                        "async":True,
                                        "paralelos":total,
                                        "owner_conf": item2["_appName"]+"_"+item2["_versionName"]+"_"+item2["_actionName"],
                                        "worker_conf": ""
                                    })

                            worker_conf = worker_conf[:len(worker_conf) - 1]
                           
                            objeto["worker_conf"] = worker_conf
                        else:
                            if  modificado[count+1]["_appName"] == "appcoppel" and  modificado[count+1]["_versionName"] == "v1":
                                objeto["worker_conf"] = modificado[count+1]["_actionName"]
                            else:
                                objeto["worker_conf"] = modificado[count+1]["_appName"]+"_"+modificado[count+1]["_versionName"]+"_"+modificado[count+1]["_actionName"]
                    else:
                        objeto["worker_conf"] = ""
                        
                    # ! End
                    if "end" in item:
                        objeto["end"] = item["end"]
                    else:
                        if (count + 1) < objetos :
                            objeto["end"] = False
                        else:
                            objeto["end"] = True

                    reconstruido.append(objeto)
                    if len(objInsertar) > 0:
                        for objetito in objInsertar:
                            reconstruido.append(objetito)
                

                count = count + 1
                
        else:
            print("no tiene flujo")

        print(json.dumps(reconstruido,sort_keys=True,indent=4)) if self._debug else self._debug
        self.__flujoMod = reconstruido
        return reconstruido

    def __funcion_bifurcacion(self,function,flujo):
        self.__functionWorkerCambiarData = function
        if len(inspect.getargspec(function).args) == 0:
            print("")
            print("")
            print("La funcion (startBifurcacion) recibe un objeto funcion")# debera recibir 2 argumentos no : "+str(countArgs))
            print("*****************************************************************************")
        else:
            countArgs = len(inspect.getargspec(function).args)
            if countArgs != 5:
                print("*****************************************************************************")
                print("la funcion de entrada debera recibir 5 argumentos no : "+str(countArgs))
                print("funcionalidad de la funcion : modificar la data de entrada del siguiente worker")
                print("Argumentos:")
                print("    1 argumento  = para recibir Nombre del worker que respondio")
                print("    2 argumento  = para recibir Id_transaction")
                print("    3 argumento  = para recibir Configuracion general del Microservicio")
                print("    4 argumento  = para recibir Data inicial de la transaccion")
                print("    5 argumento  = para recibir Respuesta del Worker anterior")
                print("*****************************************************************************")
            else:
                if len(flujo) == 0:
                    print("****************************************")
                    print("No se recibio el flujo del a bifurcacion")
                    print("****************************************")
                else:
                    self.__flujo = flujo
                    self.__startConsumer(self.__functionBifurcacion)

    def __funcion_worker(self,function,config={}):
        if len(inspect.getargspec(function).args) == 0:
            print("")
            print("")
            print("La funcion (del worker) recibe un objeto funcion")# debera recibir 2 argumentos no : "+str(countArgs))
            print("*****************************************************************************")
        else:
            try:
                countArgs = len(inspect.getargspec(function).args)
                if countArgs == 3:
                    self.__startConsumer(function,config)
                else:
                    print("*****************************************************************************")
                    print("la funcion de entrada debera recibir 3 argumentos no : "+str(countArgs))
                    print("Argumentos:")
                    print("    1 argumento  = para recibir los datos de configuracion del microservicio")
                    print("    2 argumento  = para recibir los datos de entrada al servicio")
                    print("    3 argumento  = para recibir funcion escribirWorkerAsincrono")
                    print("La funcion  debe retornar una tupla ejemplo :  (0 =int,{} =json)")
                    print("*****************************************************************************")
            except Exception as e:
                print(e)
                print("la funcion debe retornar una tupla ejm.: return (0,{})")
        
    def __conecctMQ(self):
        ret = False
        try:
            self.__producer = KafkaProducer(bootstrap_servers=self.servers_mensajeria)
            self.__consumer = KafkaConsumer(self.service_topic_name,bootstrap_servers=self.servers_mensajeria,group_id=str(self.service_topic_name))
            ret = True
        except Exception as e:
            print(e)
            ret = False
        return ret
    
    def __json_to_b64(self,json_in):
        return base64.b64encode(str.encode(json.dumps(json_in)))

    def __b64_to_json(self,encoded):
        decoded = base64.b64decode(encoded)
        return json.loads(decoded.decode('utf-8'))

    def f(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def validarLlaveRepetida(self,datos):
        llave = ""
        llave = hashlib.md5(str(datos).encode()).hexdigest() +"_"+hashlib.sha256(str(datos).encode()).hexdigest()
        datos = self.__conexion_redis.get(llave)
        if datos:
            return True
        else:
            self.__conexion_redis.set(llave,1,ex=(10 * 60))#10 minutos
            return False

    def __startConsumer(self,function,config={}):
        if os.environ.get("REDIS"):
            try:
                self.__pool_redis = redis.ConnectionPool(host=os.environ.get("REDIS"), port=6379)
                self.__conexion_redis = redis.Redis(connection_pool=self.__pool_redis)
                self.__validar_llave_repetida = True
            except:
                print("no conecto a redis")

        if self.__conecctMQ() == True:
            _thread.start_new_thread(self.health_check,())
            if self.__tiene_asincronos == True:
                _thread.start_new_thread(self.__hilo_limpiar,())
                
            print(" * Running Daemon on : " + str(self.servers_mensajeria) + " servicio: " + self.service_topic_name)
            try:
                for message in self.__consumer:
                    try:

                        if self.__validar_llave_repetida:
                            if self.validarLlaveRepetida(message.value) == False:
                                _thread.start_new_thread(self.__functionBridge,(function,config,message.value,self.__llamar_worker_asincrono,))
                        else:
                            _thread.start_new_thread(self.__functionBridge,(function,config,message.value,self.__llamar_worker_asincrono,))
                    except Exception as e:
                        print(e)
                        pass
            except Exception as e:
                print("se desconecto la cola de mensajeria (reconectar)")
                time.sleep(180)
                self.__startConsumer(function)

        else:
            print("Error:\n############################\nNo esta activo el Message Queue\n############################\n")
            time.sleep(10)
            self.__startConsumer(function)



    def __functionBridge(self,function,*args):
        objeto = self.__b64_to_json(args[1])

        if "data" in objeto and ("smoketest" in objeto["data"]):

            metadata = objeto["metadata"]
            data = objeto["data"]
            headers = objeto["headers"]
            respuesta = {}
            respuesta["meta"] = {}
            respuesta["data"] = {}
            respuesta["meta"]["id_transaction"] = ""
            respuesta["meta"]["status"] = "SUCCESS"


            self.__config_serv["container_id"] = os.environ.get("HOSTNAME")
            respuesta["data"]["response"] = self.__config_serv
            respuesta["data"]["response"]["errorCode"] = "0"
            respuesta["data"]["response"]["userMessage"] = "smoketest ok"
            
            respuestax = {}                                                                                                                                                                                                                                                  																																																														
            respuestax["metadata"] = metadata                                                                                                                                                                                                                                            
            respuestax["headers"] = headers                                                                                                                                                                                                                                              
            respuestax["data"] = data     
            respuestax["response"] = respuesta
            respuestax["metadata"]["time"] = datetime.datetime.now().isoformat()[:19]+"Z"
            respuestax["metadata"]["worker"]  = respuestax["metadata"]["owner"]                                                                                                                                                                                                           
            respuestax["metadata"]["owner"]  = self.service_name
            respuestax["metadata"]["mtype"] = "output"                                                                                                                                                                                                                                   
            if("uowner" in respuestax["metadata"]):                                                                                                                                                                                                                                      
                uowner = respuestax["metadata"]["uowner"]                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                        
            if("uworker" in respuestax["metadata"]):                                                                                                                                                                                                                                     
                uworker = respuestax["metadata"]["uworker"]                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                        
            respuestax["metadata"]["uworker"] = uowner                                                                                                                                                                                                                                   
            respuestax["metadata"]["uowner"] = uworker 


            if(metadata["bifurcacion"] == True):                                                                                                                                                                                                                                        
                metadata["bifurcacion"] = False                                                                                                                                                                                                                                     
                TOPICO = respuestax["metadata"]["callback"]
                self.__escribirColaMensajeria(TOPICO,respuestax,metadata["id_transaction"])
            else:
                TOPICO = "respuesta_"+metadata["owner"]
                respuesta2 = {"_id":respuestax["metadata"]["id_transaction"],"response":respuestax["response"],"metadata":respuestax["metadata"]}
                self.__escribirColaMensajeria(TOPICO,respuesta2,metadata["id_transaction"])
        else:

            """
            hora_msj = objeto["metadata"]["time"]
            actual = None
            hora_mensaje = None
            hora_actual = datetime.datetime.strptime(datetime.datetime.now().isoformat()[:19]+"Z","%Y-%m-%dT%H:%M:%SZ")

            try: 
                bus = hora_msj.index("Z")
                #trae formato nuevo de las librerias
                hora_mensaje = datetime.datetime.strptime(hora_msj,"%Y-%m-%dT%H:%M:%SZ")
            except:
                #trae formato viejo de las librerias
                hora_mensaje =  datetime.datetime.strptime(hora_msj,"%Y-%m-%d %H:%M:%S.%f")


            #si el time del mensaje ya tiene 5 minutos de retraso ignoro el mensaje
            if (hora_actual - hora_mensaje).seconds > 300:
                print("______________")
                print("SEGUNDOS RETRASO",":",(hora_actual - hora_mensaje).seconds)
                print("______________")
            """
            
            if self.service_es_worker == True:
                configuracion_entrada = args[0]
                mensaje_entrada = copy.copy(objeto)
                funcion_entrada = args[2]
                code = 0
                datax = {}
                try:
                    code,datax = function(configuracion_entrada,mensaje_entrada,funcion_entrada)
                except Exception as e:
                    code,datax  = -99,{}
                    error = {"_id":objeto["metadata"]["id_transaction"],"servicio":self.service_topic_name,"error":str(e)}
                    self.__escribirColaMensajeria("Errores_criticos",error,mensaje_entrada["metadata"]["id_transaction"])

                metadata = mensaje_entrada["metadata"]
                data = mensaje_entrada["data"]
                headers = mensaje_entrada["headers"]
                if "headers" not in   mensaje_entrada or "data" not in mensaje_entrada or "metadata" not in   mensaje_entrada:
                    print("No contiene datos correctos")
                else:
                    respuesta = self.__response(code,datax,metadata)
                    respuestax = {}                                                                                                                                                                                                                                                              																																																														
                    respuestax["metadata"] = metadata                                                                                                                                                                                                                                            
                    respuestax["headers"] = headers                                                                                                                                                                                                                                              
                    respuestax["data"] = data                                                                                                                                                                                                                                              
                    respuestax["response"] = respuesta                                                                                                                                                                                                                                      
                    respuestax["metadata"]["time"] = datetime.datetime.now().isoformat()[:19]+"Z"
                    respuestax["metadata"]["worker"]  = respuestax["metadata"]["owner"]                                                                                                                                                                                                           
                    respuestax["metadata"]["owner"]  = self.service_topic_name
                    respuestax["metadata"]["mtype"] = "output"                                                                                                                                                                                                                        
                    if("uowner" in respuestax["metadata"]):                                                                                                                                                                                                                                      
                        uowner = respuestax["metadata"]["uowner"]                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                
                    if("uworker" in respuestax["metadata"]):                                                                                                                                                                                                                                     
                        uworker = respuestax["metadata"]["uworker"]                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                
                    respuestax["metadata"]["uworker"] = uowner                                                                                                                                                                                                                                   
                    respuestax["metadata"]["uowner"] = uworker    

                    if(metadata["bifurcacion"] == True):                                                                                                                                                                                                                                        
                        metadata["bifurcacion"] = False                                                                                                                                                                                                                                     
                        TOPICO = respuestax["metadata"]["callback"]
                        self.__escribirColaMensajeria(TOPICO,respuestax,respuestax["metadata"]["id_transaction"])
                    else:
                        TOPICO = "respuesta_"+metadata["owner"]                                                                                                                                                                                                                             
                        respuesta2 = {"_id":respuestax["metadata"]["id_transaction"],"response":respuestax["response"],"metadata":respuestax["metadata"]}                                                                                                                                                                                                                                                                                                                             
                        self.__escribirColaMensajeria(TOPICO,respuesta2,respuestax["metadata"]["id_transaction"])

            else:
                TOPICO,respuesta = function(args[0],objeto)
                if TOPICO != "":
                    self.__escribirColaMensajeria(TOPICO,respuesta,objeto["metadata"]["id_transaction"])


    def __llamar_worker_asincrono(self,topico,respuesta,id_transaction = ""):
        _thread.start_new_thread(self.__escribir,(topico,respuesta,id_transaction,))

    def __escribir(self,topico,respuesta,idTransaction):
        if respuesta != {}:
            msj = self.__json_to_b64(respuesta)
            self.__producer.send(topico,key=str.encode(str(idTransaction)),value=msj)
            #self.__producer.flush()
            
            if topico[:9] == "respuesta":
                print(Fore.RED+"*****************   SALIDA FINAL  *****************"+Fore.WHITE) if self._debug else self._debug
                print(Fore.YELLOW+"[ "+idTransaction+" ] -  SALIDA - ["+topico+"]") if self._debug else self._debug
                print(json.dumps(respuesta["response"],sort_keys=True,indent=4)) if self._debug else self._debug
                print(" "+Fore.WHITE) if self._debug else self._debug
            else:
                print(Fore.RED+"********************   SALIDA   *******************"+Fore.WHITE) if self._debug else self._debug
                #print("[ "+idTransaction+" ] -  SALIDA - ["+topico+"]\n"+str(respuesta)) if self._debug else self._debug
                print("[ "+idTransaction+" ] -  output - ["+topico+"]\n"+str(respuesta)) if self._debug else self._debug
    
    def __escribirColaMensajeria(self,topico,respuesta,idTransaction = ""):
        self.__escribir(topico,respuesta,idTransaction)

    def __response(self,code,data = None,metadata = None):
        response = {}
        response["meta"] = {}
        response["data"] = {}

        response["meta"]["id_transaction"] = metadata["id_transaction"]
        
        if code == 0:
            response["meta"]["status"] = "SUCCESS"    
            response["data"]["response"] = data
        else:
            if type(data) is str:
                response["meta"]["status"] = "ERROR"
                response["data"]["response"] = {
                    "errorCode":str(code),
                    "userMessage":str(data)
                }
            else:
                response["meta"]["status"] = "ERROR"
                response["data"]["response"] = {
                    "errorCode":str(code),
                    "userMessage":self.__buscarMensaje(str(code))
                }
        return response

    def __buscarMensaje(self,id):
        res = ""
        if str(id) in self.__errores:
            res = self.__errores[str(id)]

        else:
            if str(id) == "-99":
                res = "Ocurrio algo inesperado, favor de intentarlo de nuevo."
            else:
                res = "Error No Definido"
        return res

    def __hilo_limpiar(self):
        while(True):
            print("Limpiar datos asincronos "+str(datetime.datetime.now()))
            #print(self.__respuesta_asincronos)
            self.__borrarAsincrono()
            time.sleep(60)

    def __borrarAsincrono(self):
        index2 = 0
        date_format = "%Y-%m-%d %H:%M:%S"
        fechaActual = datetime.datetime.strptime(str(datetime.datetime.now())[:19],date_format)
        # borrar viejos
        tmpArr = copy.copy(self.__respuesta_asincronos)

        for item in self.__respuesta_asincronos:
            fechaGuardado = datetime.datetime.strptime(item["time"],date_format)
            delta = fechaActual - fechaGuardado
            #si ya tiene mas de 3 minutos lo borro
            if delta.seconds > 180:
                tmpArr.remove(item)
            index2 += 1

        self.__respuesta_asincronos = tmpArr

    def __functionBifurcacion(self,configService,jsonArguments):
        log = print
        if jsonArguments == {}:
            return "",{}
        else:
            """Retorna topico a responder y json a __escribir"""
            metadata = jsonArguments["metadata"]
            data = jsonArguments["data"]
            headers = jsonArguments["headers"]
            response = {}
            if "response" in jsonArguments:
                response = jsonArguments["response"]
            OWNER = metadata["owner"]
            ID_TRANSACCION = metadata["id_transaction"]
            try:
                print(Fore.GREEN+"********************   ENTRADA  ********************"+Fore.WHITE) if self._debug else self._debug
                log("[ "+ID_TRANSACCION + " ] - ENTRADA - ["+metadata["owner"]+"] \nHeaders : "+str(headers) +"\nData : "+ str(data) +"\nResponse : "+ str(response)) if self._debug else self._debug
                metadata["mtype"] = "input"
                metadata["time"] = datetime.datetime.now().isoformat()[:19]+"Z"
                metadata["bifurcacion"] = True
                
                cursor_conf = self.__buscar(metadata["owner"])
                asyncronos = cursor_conf["worker_conf"].split(",")
                worker_conf = ""

                if "async" in cursor_conf:
                    print("Respondio asyncrono :",metadata["owner"]) if self._debug else self._debug
                    self.__respuesta_asincronos.append({
                        "time": str(datetime.datetime.now())[0:19],
                        "id_transaction" : metadata["id_transaction"],
                        "worker":metadata["owner"],
                        "response":jsonArguments["response"]
                    })
                    data_inicial,metadata_inicial = jsonArguments["metadata"]["inicial_bifurcacion"]["data"],jsonArguments["metadata"]["inicial_bifurcacion"]["metadata"]
                    if jsonArguments["response"]["meta"]["status"] == "SUCCESS":
                        count_respuestas = 0
                        respuestas_pegadas = {}
                        for iteracion in self.__respuesta_asincronos:
                            if iteracion["id_transaction"] == metadata["id_transaction"]:
                                respuestas_pegadas[str(iteracion["worker"])] = iteracion["response"]["data"]["response"]
                                count_respuestas += 1

                            if count_respuestas == 3:
                                break                        
                        if count_respuestas == cursor_conf["paralelos"]:
                            if cursor_conf["end"] == False:
                                worker_conf = cursor_conf["worker_conf"]
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" NO ES SERVICIO FINAL") if self._debug else self._debug
                                uWorker_async = metadata["uworker"]
                                string = str(time.time()).replace('.', '')
                                jsonArguments["metadata"]["id_operacion"] = int(string)
                                jsonArguments["metadata"]["uowner"] = uWorker_async
                                jsonArguments["metadata"]["worker"] = worker_conf
                                jsonArguments["metadata"]["uworker"] = metadata["worker"]+"_"+str(metadata["id_operacion"])
                                jsonArguments["metadata"]["owner"] = self.service_topic_name
                                responseAnterior = {}
                                if "data" in jsonArguments["response"]:
                                    jsonArguments["response"]["data"]["response"] = respuestas_pegadas
                                    responseAnterior = jsonArguments["response"]["data"]["response"]
                                else:
                                    responseAnterior = jsonArguments["data"]

                                worker_respondio = OWNER.split("_")
                                OWNER_MOD = OWNER
                                if len(worker_respondio) > 1:
                                    if len(worker_respondio) == 2:
                                        OWNER_MOD = OWNER
                                    else:
                                        OWNER_MOD = worker_respondio[2]
                                data_mod = self.__functionWorkerCambiarData(OWNER_MOD,ID_TRANSACCION,{},data_inicial,responseAnterior)
                                
                                if data_mod != {}:
                                    jsonArguments["data"] = data_mod
                                jsonArguments["response"] = {}
                                return jsonArguments["metadata"]["worker"],jsonArguments
                            else:
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" ES SERVICIO FINAL") if self._debug else self._debug
                                JSON_RESPUESTA_FIN = {}
                                if JSON_RESPUESTA_FIN == {}:
                                    jsonArguments["response"]["data"]["response"] = respuestas_pegadas
                                    JSON_RESPUESTA_FIN = jsonArguments["response"]
                                
                                msj = {"_id":metadata["id_transaction"],"response":JSON_RESPUESTA_FIN,"metadata":metadata_inicial}
                                
                                return "respuesta_"+metadata["callback"],msj
                        else:
                            return "",{}
                    else:
                        log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" ES SERVICIO FINAL") if self._debug else self._debug
                        JSON_RESPUESTA_FIN = {}
                        if JSON_RESPUESTA_FIN == {}:
                            JSON_RESPUESTA_FIN = jsonArguments["response"]
                        msj = {"_id":metadata["id_transaction"],"response":JSON_RESPUESTA_FIN,"metadata":metadata_inicial}
                        return "respuesta_"+metadata["callback"],msj
                    
                else:
                    # ? validar si es llamado a workers asincronos
                    if len(asyncronos) <=  1:
                        worker_conf = cursor_conf["worker_conf"]
                        if "grabar_metadata" in cursor_conf:
                            # ? gurdo la metadata y data inicial para cuando la necesite
                            inicial = {}
                            inicial["data"] = copy.copy(jsonArguments["data"])
                            inicial["metadata"] = copy.copy(jsonArguments["metadata"])

                            jsonArguments["metadata"]["inicial_bifurcacion"] = inicial
                            uWorker_async = metadata["uworker"]
                            string = str(time.time()).replace('.', '')
                            jsonArguments["metadata"]["id_operacion"] = int(string)
                            jsonArguments["metadata"]["uowner"] = uWorker_async
                            jsonArguments["metadata"]["worker"] = worker_conf
                            jsonArguments["metadata"]["uworker"] = metadata["worker"]+"_"+str(metadata["id_operacion"])
                            jsonArguments["metadata"]["owner"] = self.service_topic_name
                            worker_respondio = OWNER.split("_")
                            OWNER_MOD = OWNER
                            if len(worker_respondio) > 1:
                                if len(worker_respondio) == 2:
                                    OWNER_MOD = OWNER
                                else:
                                    OWNER_MOD = worker_respondio[2]
                            data_mod = self.__functionWorkerCambiarData(OWNER_MOD,ID_TRANSACCION,{},jsonArguments["data"],jsonArguments["data"])
                            if data_mod != {}:
                                jsonArguments["data"] = data_mod
                            jsonArguments["response"] = {}
                            return jsonArguments["metadata"]["worker"],jsonArguments
                        else:
                            data_inicial,metadata_inicial = jsonArguments["metadata"]["inicial_bifurcacion"]["data"],jsonArguments["metadata"]["inicial_bifurcacion"]["metadata"]
                            success =True

                            #Reviso la respuesta del servicio entrante
                            if "response" in jsonArguments and jsonArguments["response"]["meta"]["status"] == "ERROR":
                                success = False
                            
                            # si success y  servicio es fin y  envio al servicio que sigue
                            if success == True:
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" SUCCESS") if self._debug else self._debug
                                if cursor_conf["end"] == False:
                                    log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" NO ES SERVICIO FINAL") if self._debug else self._debug
                                    uWorker_async = metadata["uworker"]
                                    string = str(time.time()).replace('.', '')
                                    jsonArguments["metadata"]["id_operacion"] = int(string)
                                    jsonArguments["metadata"]["uowner"] = uWorker_async
                                    jsonArguments["metadata"]["worker"] = worker_conf
                                    jsonArguments["metadata"]["uworker"] = metadata["worker"]+"_"+str(metadata["id_operacion"])
                                    jsonArguments["metadata"]["owner"] = self.service_topic_name
                                    responseAnterior = {}
                                    if "data" in jsonArguments["response"]:
                                        responseAnterior = jsonArguments["response"]["data"]["response"]
                                    else:
                                        responseAnterior = jsonArguments["data"]

                                    worker_respondio = OWNER.split("_")
                                    OWNER_MOD = OWNER
                                    if len(worker_respondio) > 1:
                                        if len(worker_respondio) == 2:
                                            OWNER_MOD = OWNER
                                        else:
                                            OWNER_MOD = worker_respondio[2]
                                    data_mod = self.__functionWorkerCambiarData(OWNER_MOD,ID_TRANSACCION,{},data_inicial,responseAnterior)
                                    
                                    if data_mod != {}:
                                        jsonArguments["data"] = data_mod
                                    jsonArguments["response"] = {}
                                    if "worker_tmp" in data_mod:
                                        w_tmp = ""
                                        for wo in self.__flujoPrincipal:
                                            if wo["_actionName"] == data_mod["worker_tmp"]:
                                                w_tmp = wo["_appName"]+"_"+wo["_versionName"]+"_"+wo["_actionName"]
                                                break
                                        return w_tmp,jsonArguments
                                    else:
                                        return jsonArguments["metadata"]["worker"],jsonArguments
                                else:
                                    log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" ES SERVICIO FINAL") if self._debug else self._debug
                                    JSON_RESPUESTA_FIN = {}
                                    if JSON_RESPUESTA_FIN == {}:
                                        JSON_RESPUESTA_FIN = jsonArguments["response"]

                                    msj = {"_id":metadata["id_transaction"],"response":JSON_RESPUESTA_FIN,"metadata":metadata_inicial}
                                    return "respuesta_"+metadata["callback"],msj
                            else:
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" ERROR") if self._debug else self._debug
                                msj = {"_id":metadata["id_transaction"],"response":jsonArguments["response"],"metadata":metadata_inicial}
                                return "respuesta_"+metadata["callback"],msj
                    else:
                        data_inicial,metadata_inicial = jsonArguments["metadata"]["inicial_bifurcacion"]["data"],jsonArguments["metadata"]["inicial_bifurcacion"]["metadata"]
                        success =True

                        #Reviso la respuesta del servicio entrante
                        if "response" in jsonArguments and jsonArguments["response"]["meta"]["status"] == "ERROR":
                            success = False
                        
                        if success == True:
                            for work in asyncronos:
                                # si success y  servicio es fin y  envio al servicio que sigue
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" SUCCESS") if self._debug else self._debug
                                log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" NO ES SERVICIO FINAL") if self._debug else self._debug
                                uWorker_async = metadata["uworker"]
                                string = str(time.time()).replace('.', '')
                                jsonArguments["metadata"]["id_operacion"] = int(string)
                                jsonArguments["metadata"]["uowner"] = uWorker_async
                                jsonArguments["metadata"]["worker"] = work
                                jsonArguments["metadata"]["uworker"] = metadata["worker"]+"_"+str(metadata["id_operacion"])
                                jsonArguments["metadata"]["owner"] = self.service_topic_name
                                responseAnterior = {}
                                if "data" in jsonArguments["response"]:
                                    responseAnterior = jsonArguments["response"]["data"]["response"]
                                else:
                                    responseAnterior = jsonArguments["data"]

                                worker_respondio = OWNER.split("_")
                                OWNER_MOD = OWNER
                                if len(worker_respondio) > 1:
                                    if len(worker_respondio) == 2:
                                        OWNER_MOD = OWNER
                                    else:
                                        OWNER_MOD = worker_respondio[2]

                                data_mod = self.__functionWorkerCambiarData(OWNER_MOD,ID_TRANSACCION,{},data_inicial,responseAnterior)
                                
                                if data_mod != {}:
                                    jsonArguments["data"] = data_mod
                                jsonArguments["response"] = {}
                                self.__escribirColaMensajeria(jsonArguments["metadata"]["worker"],jsonArguments,jsonArguments["metadata"]["id_transaction"])
                        else:
                            log("[ "+ID_TRANSACCION + " ] - "+metadata["owner"] +" ERROR") if self._debug else self._debug
                            msj = {"_id":metadata["id_transaction"],"response":jsonArguments["response"],"metadata":metadata_inicial}
                            return "respuesta_"+metadata["callback"],msj

            except Exception as e:            
                error = {"_id":jsonArguments["metadata"]["id_transaction"],"servicio":self.service_topic_name,"error":str(e)}
                self.__escribirColaMensajeria("Errores_criticos",error,jsonArguments["metadata"]["id_transaction"])

            return self.service_topic_name,{}

    def __buscar(self,microservicio):
        ret = { "end":True,"worker_conf":""}
        for item in self.__flujo:
            if item["owner_conf"] == microservicio:
                ret = item
                break
        return ret