FIELDS_SENSOR = ['id_sensor', 'guid_sensor', 'id_modulo', 'fe_registrado']

path = "main/img/sensores/"

CODES_SENSORES = {
    #    Aclaración para módulos:
    #        No cambiar los valores del significado de las claves, 
    #        lo que si se puede es cambiar los valores de las claves.

    # Atencion! Actualizar este valor cada vez que se agregue un nuevo sensor
    # Cantidad de Sensores = 19
    # Ver archivo indices sensores

    #####################################
    #      SENSORES DE TEMPERATURA      #
    #####################################
    "DHT11": {
        "clase": 1,
        "descripcion": "<p>El DHT11 es un sensor de temperatura y humedad digital de bajo costo. Utiliza un sensor capacitivo de humedad y un termistor para medir el aire circundante, y muestra los datos mediante una señal digital en el pin de datos (no hay pines de entrada analógica). Es bastante simple de usar, pero requiere sincronización cuidadosa para tomar datos. El único inconveniente de este sensor es que sólo se puede obtener nuevos datos una vez cada 2 segundos, así que las lecturas que se pueden realizar serán mínimo cada 2 segundos. En comparación con el DHT22, este sensor es menos preciso, menos exacto y funciona en un rango más pequeño de temperatura / humedad, pero su empaque es más pequeño y menos caro.</p><p>Características</p><ul><li>Alimentación: 3Vdc ≤ Vcc ≤ 5Vdc</li><li>Rango de medición de temperatura: 0 a 50 °C</li><li>Precisión de medición de temperatura: ±2.0 °C .</li><li>Resolución Temperatura: 0.1°C</li><li>Rango de medición de humedad: 20% a 90% RH.</li><li>Precisión de medición de humedad: 4% RH.</li><li>Resolución Humedad: 1% RH</li><li>Tiempo de sensado: 1 seg.</li></ul>",
        "fields": FIELDS_SENSOR + ['temperatura', 'humedad'],
        "modulos": {1: "TEMPERATURA", 2: "HUMEDAD"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img": path+'dht11.jpg',
        "de_unidad": {1: "º", 2: "%"},
    },

    "DS18B20": {
        "clase": 2,
        "descripcion": "<p>El sensor DS18B20 permite medir temperaturas de hasta 125ºC de forma fácil y además está sellado en un envoltorio estanco que permite sumergirlo en un líquido o pretegerlo de la intempérie. Dado que es un sensor digital, la señal leida no se degrada debido a la distancia del cableado. Puede funcionar en modo 1-Wire con una precisión de ±0.5°C con una resolución de 12 bits. También pueden utilizarse varios sensores sobre el mismo pin ya que internamente viene programado con un ID único de 64 bits para diferenciarlos. El rango de funcionamiento es de 3 a 5V por lo que se puede utilizar en practicamente cualquier sistema de que use microcontroladores.</p><p>Características del cable</p><ul><li>Tubo de acero inoxidable de 6mm de diámetro por 30mm de largo</li><li>Largo: 91cm</li><li>Diámetro: 4mm</li><li>Contiene un sensor de temperatura DS18B20</li></ul><p>Conexión:</p><p>En función de la producción, los cables del sensor pueden variar pero seguirán según estas especificaciones:</p><ul><li>Si tienes 4 cables: Rojo es Vcc (positivo), Negro es GND (negativo) y Blanco es el cable de datos. La malla es GND.</li><li>Si tienes 3 cables: Rojo es Vcc (positivo), Azul/Negro es GND (negativo) y Amarillo/Blanco es el cable de datos.</li></ul><p>Características del sensor DS18B20</p><ul><li>Rango de temperatura: -55 a 125°C</li><li>Resolución: de 9 a 12 bits (configurable)</li><li>Interfaz 1-Wire (Puede funcionar con un solo pin)</li><li>Identificador interno único de 64 bits</li><li>Multiples sensores puede compartir el mismo pin</li><li>Precisión: ±0.5°C (de -10°C a +85°C)</li><li>Tiempo de captura inferior a 750ms</li><li>Alimentación: 3.0V a 5.5V</li></ul>",
        "fields": FIELDS_SENSOR + ['temperatura'],
        "modulos": {1: "TEMPERATURA"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img": path+'DS18B20.png',
        "de_unidad": {1: "º"},
    },

    "HDC1080": {
        "clase": 13,
        "descripcion": "<p>El HDC1080 de Imagen de Sensor de humedad digital HDC1080 de Texas Instruments es un sensor de humedad digital con sensor de temperatura integrado que proporciona una precisión excelente de medición con un consumo de energía muy bajo. El HDC1080 opera en un amplio rango de oferta y es una alternativa de bajo costo, de bajo consumo a soluciones competitivas en una amplia gama de aplicaciones comunes. Los sensores de humedad y temperatura se calibran en fábrica.</p><p>Características</p><ul><li>Precisión de humedad relativa ±2% (típica)</li><li>Temperatura de precisión ±0. 2 ° C (típico)</li><li>Excelente estabilidad en alta humedad</li><li>Resolución de medidas de 14 bits</li><li>Corriente en modo de reposo de 100 nA</li><li>Voltaje de alimentación: 2.7 V a 5.5 V</li><li>Corriente de alimentación promedio: <p>- Medición de RH de 11 bits, de 710 nA a 1 sps</p></li> - Medición de temperatura y RH de 11 bits, de 1.3 µA a 1 sps</li><li>Huella de dispositivo pequeña de 3 x 3 mm</li><li>Interfaz I2C</li></ul>",
        "fields": FIELDS_SENSOR + ['temperatura'],
        "modulos": {1: "TEMPERATURA", 2: "HUMEDAD"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'HDC1080.jpg',
        "de_unidad": {1: "º", 2: "%"},
    },
    #####################################
    #        SENSORES MAGNETICOS        #
    #####################################
    "MAGNETICO": {
        "clase": 5,
        "descripcion": "Modulo de sensor magnético (apertura de puertas).",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "MAGNETICO"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img": path+'magenetico.jpg',
        "de_unidad": {1:"",},
    },

    "PESSL": {
        "clase": 6,
        "descripcion": "Pluviómetro Pessl",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img": path+'pessl.jpg',
        "de_unidad": None,
    },

    #####################################
    #              ACTUADORES           #
    #####################################
    "RELE": {
        "clase": 8,
        "descripcion": "<p>Los relé, permiten controlar cargas de alto voltaje con una señal pequeña. Esto nos permitirá controlar componentes de alto voltaje o alto amperaje, como bombillas o bombas de agua, etc.</p><p>El modulo posee 1 Relay de alta calidad, fabricado por Songle, con capacidad de manejar cargas de hasta 250V/10A. El módulo relay posee un led indicador de alimentación (rojo) y un led indicador de activación (vender). Este modulo a diferencia de los módulos relay de 2 o más canales no posee optoacopladores, en su lugar la activación del relay es mediante un transistor.  Este modulo Relay activa la salida normalmente abierta (NO: Normally Open) al recibir un '0' lógico (0 Voltios) y desactiva la salida con un '1' lógico (5 voltios).</p><p>Entre las cargas que se pueden manejar tenemos: bombillas de luz, luminarias, motores AC (220V), motores DC, solenoides, electroválvulas, calentadores de agua y una gran variedad de actuadores más. Se recomienda realizar y verificar las conexiones antes de alimentar el circuito, también es una buena practica proteger el circuito dentro de un case.</p>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img": path+'rele.jpg',
        "de_unidad": None,
    },

    #####################################
    #               RASPBERRY           #
    #####################################
    "RASPBERRY": {
        "clase": 21,
        "descripcion": "<p>Sensores disponibles para capturar diferentes parametros de una Raspberry</p>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "TEMPERATURA", 2:"PROCESADOR", 3:"USO DE DISCO"},
        "is_valid": True,
        "admite_monitoreo": True,
        "img":None,
        "de_unidad": {1:"ºC",2:"%",3:"%"},
    },
    #####################################
    #            OTROS SENSORES         #
    #####################################
    "FOTORESISTOR": {
        "clase": 3,
        "descripcion": "<p>Un LDR es un dispositivo cuya resistencia varía de acuerdo con la cantidad de luz que reciba. Son muy útiles para proyectos de control de iluminación, seguidores solares, interruptores crepusculares, etc.</p><p>Este módulo posee 2 salidas, una analógica que debes conectar a una entrada analógica y así utilizar el conversor ADC. La salida digital posee solo 2 estados: activo/apagado, el cambio de un estado a otro depende del umbral que se fije con el potenciómetro del módulo. La salida digital puede utilizarse para controlar un relay y asi realizar una acción dependiente de la intensidad de luz.</p><p>Especificaciones Técnicas</p><ul><li>Voltaje de Operación: 5V DC</li><li>Conexión de 4 cables: VCC, GND, DO, AO</li><li>Salida analógica y digital(comparador)</li><li>Opamp en modo comparador: LM393</li><li>Potenciometro para ajuste de comparador</li><li>Led rojo de encendido y verde de salida digital</li></ul>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'modulo-ldr.png',
        "de_unidad": None,
    },

    "MHRD": {
        "clase": 4,
        "descripcion": "<p>Modulo de sensor de precipitacion (lluvia) MH-RD analógico.</p><p>Los sensores de lluvia se utilizan en la detección de agua más allá de lo que un sensor de humedad puede detectar.</p><p>El sensor de lluvia detecta el agua que completa los circuitos en las pistas impresos de sus tarjetas de sensores. La tarjeta del sensor actúa como una resistencia variable que cambiará de 100kohm cuando está mojado a 2Mohm cuando está seco. En resumen, cuanto más húmedo sea el tablero, mayor será la corriente que se llevará a cabo.</p>",
        "fields": FIELDS_SENSOR + ['do', 'canal_0', 'canal_1', 'canal_2', 'canal_3'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'MHRD.jpg',
        "de_unidad": None,
    },

    "HCSR501": {
        "clase": 7,
        "descripcion": "<p>Modulo de sensor de movimiento, PIR (HC-SR501).</p><p>El módulo HC-SR501 tiene 3 pines de conexión +5v, OUT (3,3v) y GND, y dos resistencias variables de calibración (Ch1 y RL2).</p><ul><li>Ch1: Con esta resistencia podemos establecer el tiempo que se va a mantener activa la salida del sensor. Una de las principales limitaciones de este módulo es que el tiempo mínimo que se puede establecer es de más o menos 3s. Si cambiamos la resistencia por otra de 100K, podemos bajar el tiempo mínimo a más o menos 0,5 s.</li><li>RL2: Esta resistencia variable nos permite establecer la distancia de detección  que puede variar entre 3-7m.</li><li>La posibilidad de mantener activa la salida del módulo durante un tiempo determinado nos permite poder usarlo directamente para prácticamente cualquier aplicación sin necesidad de usar un microcontrolador.</li></ul><p>Características</p><ul><li>Sensor piroeléctrico (Pasivo) infrarrojo (También llamado PIR)</li><li>El módulo incluye el sensor, lente, controlador PIR BISS0001, regulador y todos los componentes de apoyo para una fácil utilización</li><li>Rango de detección: 3 m a 7 m, ajustable mediante trimmer (Sx)</li><li>Lente fresnel de 19 zonas, ángulo < 100º</li><li>Salida activa alta a 3.3 V</li><li>Tiempo en estado activo de la salida configurable mediante trimmer (Tx)</li><li>Redisparo configurable mediante jumper de soldadura</li><li>Consumo de corriente en reposo: < 50 μA</li></ul>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'HCSR501.jpg',
        "de_unidad": None,
    },

    "TSL2561": {
        "clase": 9,
        "descripcion": "<p>El TSL2561 es un sensor de luz muy preciso que mide en un rango de 0.1 a 40000 lux. A diferencia de otros sensores similares, tiene dos diodos que le permite medir tanto la luz ambiente en el espectro visible como la luz infrarroja. La placa está diseñada para funcionar tanto a 3.3 como a 5V así que lo puedes utilizar con tu microcontrolador favorito sin necesidad de componentes adicionales. Funciona mediante el bus I2C y por lo tanto es muy sencillo de hacer funcionar y puedes utilizarlo junto a otros sensores en un mismo bus.</p><p>Características:</p><ul><li>Rango muy similar el ojo humano</li><li>Medición precisa en diversos ambientes lumínicos</li><li>Temperatura de funcionamiento: -30 a 80 *C</li><li>Rango dinámico (Lux): 0.1 a 40,000 Lux</li><li>Alimentación: 2.7 - 3.6V</li><li>Interfaz: I2C (Dirección: 0x39, 0x29 o 0x49, seleccionable)</li></ul>",
        "fields": FIELDS_SENSOR + ['total', 'visible'],
        "modulos": {1: "TOTAL", 2: "VISIBLE"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'TSL2561.jpg',
        "de_unidad": None,
    },

    "MQ2": {
        "clase": 10,
        "descripcion": "<p>Este es un sensor muy sencillo de usar, ideal para medir concentraciones de gas natural en el aire. Puede detectar concentraciones desde 300 hasta 10000 ppm.El módulo posee una salida analógica que proviene del divisor de voltaje que forma el sensor y una resistencia de carga. También tiene una salida digital que se calibra con un potenciómetro, esta salida tiene un Led indicador. La resistencia del sensor cambia de acuerdo a la concentración del gas en el aire. El MQ-2 es sensible a LPG, i-butano, propano, metano, alcohol, hidrogeno y humo.</p><p>Especificaciones Técnicas</p><ul><li>Voltaje de Operación: 5V DC</li><li>Respuesta rápida y alta sensibilidad</li><li>Rango de detección: 300 a 10000 ppm</li><li>Gas característico: 1000ppm, Isobutano</li><li>Resistencia de sensado: 1KΩ 50ppm Tolueno a 20KΩ in</li><li>Tiempo de Respuesta: ≤ 10s</li><li>Tiempo de recuperación: ≤ 30s</li><li>Temperatura de trabajo: -20 ℃ ~ +55 ℃</li><li>Humedad: ≤ 95% RH</li><li>Contenido de oxigeno ambiental: 21%</li><li>Consume menos de 150mA a 5V.</li></ul>",
        "fields": FIELDS_SENSOR + ['do', 'Co', 'Humo'],
        "modulos": {1: "GENERICO", 2: "RO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'mq-2.jpg',
        "de_unidad": None,
    },

    "MQTT": {
        "clase": 11,
        "descripcion": "Sensor especifico del Tipo MQTT",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO MQTT"},
        "is_valid": False,
        "admite_monitoreo": False,
        "img": '',
        "de_unidad": None,
    },

    "ANEMOMETRO": {
        "clase": 12,
        "descripcion": "Anemometro, mide la dirección y velocidad del viento. El equipo base corresponde a la estación meteorológica WH1081, WS1081, TX81W yTX81D",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "VELOCIDAD", 2: "DIRECCION"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'Anemometer.jpg',
        "de_unidad": {1: "km/hs", 2: "º"},
    },

    "BMP280": {
        "clase": 14,
        "descripcion": "<p>Descripción:</p><p>El sensor de presión barométrica BMP280 diseñado especialmente para aplicaciones móviles. Sus pequeñas dimensiones y su bajo consumo de energía permite la implementación en distintos dispositivos. El sensor dispone de una excelente precisión relativa de ± 0,12 hPa, lo que equivale a ± diferencia 1 M en altitud. El coeficiente de temperatura muy bajo offset (TCO) de 1,5 Pa / K se traduce en una variación de temperatura de sólo 12,6 cm / K.<p>Nota: Debido a la alta sensibilidad de este sensor, evite tocarlo con los dedos.</p><p>Características:</p><ul><li>Voltaje de alimentación: 1.71-3.6V.</li><li>Corriente de trabajo 2.8uA.</li><li>Rango para la medida de la presión barométrica: 300hPa ~ 1100hPa</li><li>Precisión de la medida de la presión barométrica: ± 1hPa</li><li>Rango de Temperatura: - 40 ~ 85°C.</li><li>Precisión en la Temperatura: ± 1°C.</li><li>Interface: I2C y SPI</li></ul>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "PRESION"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'BMP280.jpg',
        "de_unidad": {1: "hPa", },
    },

    "PLUVIOMETRO": {
        "clase": 15,
        "descripcion": "<p>Descripción:</p><p>Los pluviómetros sirven para calcular la cantidad de lluvia que cae en una zona concreta durante un periodo de tiempo determinado.</p><p>El modelo base correesponde a uno de los sensores de la estación meteorológica WH1081, WS1081, TX81R</p>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'WS1081.jpg',
        "de_unidad": {1: 'mm/pulso', },
    },

    "AS3935": {
        "clase": 16,
        "descripcion": "<p>El AS3935 de ams es un CI de sensor de rayos programable que detecta la presencia y aproximación de actividad eléctrica potencialmente peligrosa en las inmediaciones. Detecta actividad dentro de la nube, así como relámpagos de nube a tierra, lo que permite que a menudo se puedan evaluar los riesgos de tormentas que se aproximan.</p><p>El AS3935 detecta la actividad eléctrica mientras ésta se aproxima desde una distancia de hasta 40 km. Además, el AS3935 identifica y rechaza las señales de interferencia desde fuentes artificiales comunes, tales como iluminación fluorescente, motores, hornos de microondas e interruptores.</p><p>Sobre la base de investigaciones científicas, se puede calcular estadísticamente la distancia de la tormenta a partir de las señales medidas. Esta información permite al usuario ajustar los niveles de alerta adecuados para una aplicación específica. La seguridad personal se puede establecer a un nivel prudencial, mientras que la protección de equipos debe contemplar fiabilidad, intensidad de señal y duración de la batería.</p><p>El CI flexible ofrece la capacidad de configuración que permite el funcionamiento de la pieza tanto en interiores como en exteriores con solo cambiar la configuración de ganancia en un registro.</p><p>Características y beneficios</p><ul>        <li>El detector de rayos advierte de la actividad de tormentas eléctricas en un radio de 40 km.</li><li>Cálculo de distancia a la cabeza de la tormenta de hasta 1 km en 14 pasos</li><li>Detecta tanto relámpagos nube a tierra como dentro de la nube (nube a nube)</li><li>Niveles de detección programables permiten la configuración del umbral para controles óptimos</li><li>Algoritmo integrado de rechazo de elemento perturbador artificial</li><li>Interfaz SPI e I2C para lectura de control y de registro</li><li>Ajuste de antena para compensar variaciones de componentes externos</li><li>Rango de voltaje de alimentación de 2.4 V a 5.5 V</li><li>Modo de apagado, escucha y activo</li><li>Paquete: 16LD MLPQ (4 mm x 4 mm)</li></ul>",
        "fields": FIELDS_SENSOR + ['valor'],
        "modulos": {1: "GENERICO"},
        "is_valid": True,
        "admite_monitoreo": False,
        "img": path+'AS3935.jpg',
        "de_unidad": {1: None, },
    },

    "FLUJO_PERSONAS": {
        "clase": 17,
        "descripcion": "Flujo de personas",
        "fields": FIELDS_SENSOR + ['entrada', 'salida'],
        "modulos": {1: "GENERICO"},
        "is_valid": False,
        "admite_monitoreo": False,
        "img": '',
        "de_unidad": {1: "", },
    },

    "CAM": {
        "clase": 18,
        "descripcion": "Cámara web USB",
        "fields": FIELDS_SENSOR,
        "modulos": {1: "CAM"},
        "is_valid": False,
        "admite_monitoreo": False,
        "img": '',
        "de_unidad": {1: "", },
    },

    "SC200": {
        "clase": 19,
        "descripcion": "Equipo inversor SC200 Eaton",
        "fields": FIELDS_SENSOR,
        "modulos": {1: "AC", 2: "BATERIA"},
        "is_valid": False,
        "admite_monitoreo": False,
        "img": path+'SC200.jpg',
        "de_unidad": {1: "V.",2: "V."},
    },

    "SNMPWEBSERVER": {
        "clase": 20,
        "descripcion": "Equipo Inversor SNMP Web Server",
        "fields": FIELDS_SENSOR,
        "modulos": {1: "AC", 2: "BATERIA"},
        "is_valid": False,
        "admite_monitoreo": False,
        "img": '',
        "de_unidad": {1: "V.",2: "V."},
    },
}

def get_codes():
    list_tuplas = []
    for key in CODES_SENSORES.keys():
        if CODES_SENSORES[key]["is_valid"]:
            list_tuplas.append((CODES_SENSORES[key]["clase"], key))
    return tuple(list_tuplas)


CODIGOS_SENSORES_CHOICE = get_codes()
