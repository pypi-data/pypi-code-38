# Datos de entrenamiento para modelo de detección de drogas.
# Ejemplos tageados por Gaston Mignone.
# src=https://github.com/GastonSm/Drug_Train

TRAIN_DATA = [
    ("Muy buena hierba", {
        'entities': [(10, 16, 'DRUG')]
    }),

    ("Buenas tardes Jose", {
        'entities': [(14,18,'PER')]
    }),

    ("Linda maria me fume en Roma", {
        'entities': [(6, 11, 'DRUG'), (23,27,'LOC')]
    }),

    ("Google tiene una oficina en Buenos Aires", {
        'entities': [(0,6,'ORG'),(28,40,'LOC')]
    }),

    ("Jose fue a la escuela a las 8am", {
        'entities': [(0, 4, 'PER'),(14,21,'MISC')]
    }),

    ("¿Cuanto la marihuana?", {
        'entities': [(11, 20, 'DRUG')]
    }),

    ("alto faso el de Jose", {
        'entities': [(5, 9, 'DRUG'),(16,20,'PER')]
    }),

    ("weed se la llama internacionalmente", {
        'entities': [(0, 4, 'DRUG')]
    }),

    ("ganya para todos!, aclamaron con un grito", {
        'entities': [(0, 5, 'DRUG')]
    }),

    ("Hachís o polen, como quieras decirle, tambien chocolate. Todas estas palabras son utilizadas", {
        'entities': [(0, 6, 'DRUG'),(9, 14, 'DRUG'),(46, 55, 'DRUG')]
    }),
    
    ("Distintas formas de llamar al porro: por ejemplo, canuto, purito, cañon, fino, faso o un puro", {
        'entities': [(30, 35, 'DRUG'),(50, 56, 'DRUG'),(58, 64, 'DRUG'), (66, 71, 'DRUG'),(73, 77, 'DRUG'),(79, 83, 'DRUG'),(89, 93, 'DRUG')]
    }),
    
    ("A la cocaína, también conocida como 'merca', le dicen 'la porquería', 'falopa', 'cameruza' o 'camer'.", {
        'entities': [(5, 12, 'DRUG'),(37, 42, 'DRUG'),(55, 67, 'DRUG'),(71, 77, 'DRUG'),(81, 88, 'DRUG'),(93, 98, 'DRUG')]
    }),
    
    ("La pasta base es el deshecho de la  cocaína y también se la llama 'paco'. En la jerga, los dealers denominan a cada dosis de cocaína como 'camisa' y a la dosis de paco 'pantalón'", {
        'entities': [(3, 13, 'DRUG'),(36, 43, 'DRUG'),(67, 71, 'DRUG'), (66, 71, 'DRUG'),(125, 132, 'DRUG'),(139, 145, 'DRUG'),(163, 167, 'DRUG'), (169, 177, 'DRUG')]
    }),
    
    ("Vendiendo merca en la plaza me hice rico", {
        'entities': [(10, 15, 'DRUG'), (22,27,'LOC')]
    }),

    ("Android tiene una aplicación que permite validar archivos", {
        'entities': [(0, 7, 'MISC')]
    }),

    ("aguante el paco estaba escrito en el mural del parque, en frente a Carrefour", {
        'entities': [(11, 15, 'DRUG'),(47,53,'LOC'),(67,76,'ORG')]
    }),

    ("Fueron secuestradas 4 toneladas de cocaina en Mendoza", {
        'entities': [(35, 42, 'DRUG'),(46, 53, 'LOC')]
    }),
    
    ("Gustavo viaja a China dentro de un mes para ver el nuevo prototipo de autos electricos", {
        'entities': [(0, 7, 'PER'),(16, 21, 'LOC')]
    }),
    
    ("La code, o codeina se popularizó gracias a la nueva tendencia musical", {
        'entities': [(3, 7, 'DRUG'),(11, 18, 'DRUG')]
    }),
    
    ("Linda tarde para ir de visita al museo de Mar del Plata", {
        'entities': [(33, 38, 'LOC'),(42, 55, 'LOC')]
    }),
    
    ("Maria compra Coca-Cola en el camino", {
        'entities': [(0, 5, 'PER'),(13, 22,'MISC')]
    }),

    ("Buenas tardes Raul", {
        'entities': [(14,18,'PER')]
    }),

    ("Acaba de decir que se fumó un cañon", {
        'entities': [(30, 35, 'DRUG')]
    }),

    ("Gastón no va a terminar de escribir esto nunca?", {
        'entities': [(0, 6, 'PER')]
    }),

    ("El nuevo Ford Focus dicen que funciona muy bien", {
        'entities': [(9, 13, 'ORG'), (14, 19, 'MISC')]
    }),

    ("Florencia quiere ir a la playa, pero Manu no la deja", {
        'entities': [(0, 9, 'PER'),(25, 30, 'LOC'),(37, 41, 'PER')]
    }),

    ("Avisame a que hora vas al banco x que haora no estoi en casa asi yo voy para casa y te acompaño yegua", {
        'entities': [(32, 33, 'ME'),(38, 43,'ME'),(47, 52, 'ME'),(56, 60, 'MISC'),(77, 81, 'MISC')]
    }),

    ("Gordi mañana te alcansa la plata la maga x que yo no voy a estar besos mi amor", {
        'entities': [(16, 23, 'ME'),(36, 40, 'PER'), (41, 42, 'ME')]
    }),

    ("Bien amiga aca estoy en neco tomandoo un vinito con jose caceres jaaa", {
        'entities': [(24, 28, 'ME'),(29, 37, 'ME'),(41, 47, 'DRUG'),(52, 64, 'PER'),(65, 69, 'ME')]
    }),

    ("No ay ninguna amiga para el cabezita jaaaaaa", {
        'entities': [(3, 5, 'ME'),(28, 36, 'ME'),(37, 44, 'ME')]
    }),

    ("aaaaa es de balcarceeeee", {
        'entities': [(0, 5, 'ME'),(12, 20, 'LOC'), (12, 24, 'ME')]
    }),

    ("Hola ma estas en tu kasa", {
        'entities': [(5, 7, 'ME'),(20, 24, 'ME')]
    }),
    
    ("Si iria pero sola no da si a magali no la dejan entrar", {
        'entities': [(29, 35, 'PER')]
    }),
    
    ("Tengo un puro excelente", {
        'entities': [(9, 13, 'DRUG')]
    }),
    
    ("En Youtube hay videos de lo que gustes", {
        'entities': [(3, 10, 'MISC')]
    }),
    
    ("SpaCy debe entrenarse para poder detectar las drogas", {
        'entities': [(0, 5, 'MISC'),(46, 52, 'DRUG')]
    }),

    ("Carlos tiene una chala tatuada", {
        'entities': [(0, 6, 'PER'), (17, 23, 'DRUG')]
    }),

    ("Audi es de Alemania", {
        'entities': [(0,4,'ORG'),(11, 19, 'LOC')]
    }),

    ("Lindo canuto me fume en el bosque", {
        'entities': [(6, 12, 'DRUG'), (27,33,'LOC')]
    }),

    ("Fasta cierra a las 3pm", {
        'entities': [(0, 5, 'ORG')]
    }),

    ("Fumando weed todo el dia, asi dice la canción", {
        'entities': [(8, 12, 'DRUG')]
    }),

    ("Holanda posee en su bandera los colores azul, blanco y rojo", {
        'entities': [(0, 7, 'LOC')]
    }),

    ("Cuando hablamos de hierba nos referimos a droga en este contexto", {
        'entities': [(19, 25, 'DRUG'),(42, 47, 'DRUG')]
    }),
    
    ("La casa de Olivia queda a la vuelta de la mia", {
        'entities': [(3, 7, 'LOC'),(11, 17, 'PER')]
    }),
    
    ("Google posee una aplicación para android que permite localizar los mejores lugares turisticos", {
        'entities': [(0, 6, 'ORG'),(33, 4, 'MISC')]
    }),
    
    ("Hablemos de comprar cameruza", {
        'entities': [(20, 28, 'DRUG')]
    }),

    ("Incendiaron una plantación de marihuana en Misiones", {
        'entities': [(30, 39, 'DRUG'),(43, 51, 'LOC')]
    }),

    ("Estados Unidos tiene como presidente a Donald Trump", {
        'entities': [(0,14,'LOC'),(39, 51, 'PER')]
    }),

    ("Te llevo una ensalada", {
        'entities': [(13, 21, 'DRUG')]
    }),

    ("un gramo pa' la peda", {
        'entities': [(3, 8, 'DRUG'),(16, 20, 'DRUG')]
    }),

    ("Iremos al baile", {
        'entities': [(10, 15, 'MISC')]
    }),

    ("Marcha a favor de la legalización de la marihuana", {
        'entities': [(0, 49, 'MISC'),(40, 49, 'DRUG')]
    }),

    ("Jose Lopez fue el primero en entrar a la iglesia", {
        'entities': [(0, 10, 'PER'),(41, 48, 'MISC')]
    }),
    
    ("En Octubre sale un nuevo juego de Konami para la PlayStation 4", {
        'entities': [(34, 40, 'ORG'),(49, 62, 'MISC')]
    }),
    
    ("Gabriel es adicto a la cocaina", {
        'entities': [(0, 7, 'PER'),(23, 30, 'DRUG')]
    }),
    
    ("mreca .. escribo mal la palabra ", {
        'entities': [(0, 5, 'DRUG')]
    }),

    ("El festival de cine se hace en Mar del Plata", {
        'entities': [(3, 19, 'MISC'),(31, 44, 'LOC')]
    }),

    ("Me gustaria entrenar, pero debo seguir escribiendo oraciones para SpaCy", {
        'entities': [(68,74,'MISC')]
    }),

    ("Maria se fumo una maria, muy gracioso lo de Maria", {
        'entities': [(0, 5, 'PER'), (18,23,'DRUG'), (44, 49, 'PER')]
    }),

    ("Entre la lista de drogas estimulantes están:", {
        'entities': [(18, 24, 'DRUG')]
    }),

    ("Éxtasis también llamado pepas", {
        'entities': [(0, 7, 'DRUG'), (24, 29, 'DRUG'), (24, 28, 'DRUG')]
    }),

    ("Sustancias de tipo anfetaminico (anfetamínico), asi cubro ambas ", {
        'entities': [(0, 10, 'DRUG'), (19, 31, 'DRUG'), (33, 45, 'DRUG')]
    }),

    ("Como la efedrina o la pseudoefedrina", {
        'entities': [(8, 16, 'DRUG'),(22, 36, 'DRUG')]
    }),
    
    ("Se decia que Jonathan tomaba esteroides", {
        'entities': [(13, 21, 'PER'),(29, 39, 'DRUG')]
    }),
    
    ("rivotril triene efecto depresor.", {
        'entities': [(0, 8, 'DRUG')]
    }),
    
    ("La pasta base es el deshecho de la  cocaína y también se la llama 'paco'. En la jerga, los dealers denominan a cada dosis de cocaína como 'camisa' y a la dosis de paco 'pantalón'", {
        'entities': [(3, 13, 'DRUG'),(36, 43, 'DRUG'),(67, 71, 'DRUG'), (66, 71, 'DRUG'),(125, 132, 'DRUG'),(139, 145, 'DRUG'),(163, 167, 'DRUG'), (169, 177, 'DRUG')]
    }),

    ("el xanax y el valium tambien son depresores", {
        'entities': [(3, 8, 'DRUG'), (14, 20, 'DRUG')]
    }),

    ("popper, ladys, dick, boxer (gale, galuche, sacol) son inhalables", {
        'entities': [(0, 6, 'DRUG'),(8, 13, 'DRUG'),(15, 19, 'DRUG'), (21, 26, 'DRUG'),(28, 32, 'DRUG'),(34, 41, 'DRUG'),(43, 48, 'DRUG')]
    }),

    ("morfina, heroina, codeina, metadone y el opio son narcoticos (narcóticos)", {
        'entities': [(0, 7, 'DRUG'),(9, 16, 'DRUG'),(18, 25, 'DRUG'), (27, 35, 'DRUG'),(41, 45, 'DRUG'),(50, 60, 'DRUG'),(62, 72, 'DRUG')]
    }),

    ("Alucinógenos: LSD (tripis, acidos)", {
        'entities': [(0, 12, 'DRUG'),(14 , 17, 'DRUG'),(19 , 25, 'DRUG'),(27 , 33, 'DRUG')]
    }),

    ("En Irlanda consumen mucha ketamina (keta, k, ketacet entre otros) ", {
        'entities': [(0, 7, 'MISC'),(23, 31, 'DRUG'),(33, 37, 'DRUG'), (39, 40, 'DRUG'),(42, 49, 'DRUG')]
    }),

    ("Lautaro vendia GHB en la escuela", {
        'entities': [(0, 7, 'PER'),(15, 18, 'DRUG'),(25, 32, 'DRUG')]
    }),

    ("Jorge esta yendo a Polonia de vacaciones", {
        'entities': [(0, 5, 'PER'),(19, 26, 'MISC')]
    }),
    
    ("Ines Montani recomienda entrenar con minimo 100 oraciones", {
        'entities': [(0, 12, 'PER')]
    }),
    
    ("Dejemos de lado la falopa y escribamos sobre la playa de Corea del Sur", {
        'entities': [(19, 25, 'DRUG'),(48, 53, 'MISC'),(57, 70, 'MISC')]
    }),
    
    ("Ramiro y Guido saben que soy el mejor jugando", {
        'entities': [(0, 6, 'PER'),(9, 14, 'PER')]
    }),

    ("Facebook, Google, Amazon, y Microsoft son organizaciones", {
        'entities': [(0, 8, 'ORG'),(10, 16, 'ORG'),(18, 24, 'ORG'),(28, 37, 'ORG')]
    }),

    ("El dealer que solo tenia hachis", {
        'entities': [(25,31,'DRUG')]
    }),

    ("Emiliano fue al Tomorrowland", {
        'entities': [(0, 8, 'PER'), (16,28,'MISC')]
    }),

    ("De Alemania, de Croacia, de Brasil. Habie gente de todos lados!", {
        'entities': [(3, 11, 'LOC'),(16, 23, 'LOC'),(28, 34, 'LOC')]
    }),

    ("Que no pare la fiesta", {
        'entities': [(15, 21, 'MISC')]
    }),

    ("Esto no aporta en nada, solo en randomizar", {
        'entities': []
    }),

    ("Y la otra mitad la dividio para la moni y romina", {
        'entities': [(35, 39, 'PER'),(42, 48, 'PER')]
    }),
    
    ("En casa pero no entre a la comisaria y tuve que llamar a la madre que estava llendo para alla", {
        'entities': [(3, 7, 'MISC'),(27, 36, 'MISC'),(70, 76, 'ME'),(77, 83, 'ME')]
    }),

    ("Jaja. Buen kuando la veas avisale. Td bien x ai?", {
        'entities': [(0, 5, 'ME'),(11, 17, 'ME'),(35, 37, 'ME'),(43, 44, 'ME'),(45, 47, 'ME')]
    }),

    ("Besos cuidensen", {
        'entities': [(6, 15, 'ME')]
    }),

    ("Estoi con la abuela llamala a  mi cel ahora", {
        'entities': [(0, 5, 'ME'),(34, 37, 'ME')]
    }),

    ("Pone la pava, estoy esperando al camion", {
        'entities': []
    }),

    ("8 años de carcel para Fausto por la venta de sustancias", {
        'entities': [(22, 28, 'PER'),(45, 55, 'DRUG')]
    }),
    
    ("Me gustaria tener un texto con todos los datos juntos", {
        'entities': []
    }),
    
    ("en Rio de Janeiro se consume mucha merca, especialmente en las favelas", {
        'entities': [(3, 17, 'LOC'),(35, 40, 'DRUG'),(63, 70, 'MISC')]
    }),
    
    ("Gaston y Gerardo se quedan en Fasta hasta las 3pm", {
        'entities': [(0, 6, 'DRUG'),(9, 16, 'DRUG'),(30, 35, 'ORG')]
    }),

    ("Solamente quedan 20 oraciones", {
        'entities': []
    }),

    ("Le dieron 20 gramos de cocaina", {
        'entities': [(23,30,'DRUG')]
    }),

    ("Linda maria se fumo el Jony", {
        'entities': [(6, 11, 'DRUG'), (23,27,'PER')]
    }),

    ("¿Cuanto la caminsa?", {
        'entities': [(11, 18, 'DRUG')]
    }),

    ("pepa se le dice al LSD", {
        'entities': [(0, 4, 'DRUG'),(19, 22, 'DRUG')]
    }),

    ("zona ganya es una banda de chile", {
        'entities': [(5, 10, 'DRUG'), (27, 32, 'LOC')]
    }),

    ("vamos a escribir todo mal, por ejemplo: kiero kokaina", {
        'entities': [(46, 53, 'DRUG')]
    }),
    
    ("Bruno nos va a traer las conversaciones", {
        'entities': [(0, 5, 'PER')]
    }),
    
    ("Me tengo que ir a mi casa", {
        'entities': [(21, 25, 'MISC')]
    }),
    
    ("Me siento por las nubes", {
        'entities': []
    }),

    ("Vendian porro en la plaza San Martin", {
        'entities': [(8, 13, 'DRUG'), (20,36,'MISC')]
    }),

    ("Buenas tardes Luca", {
        'entities': [(14,18,'PER')]
    }),

    ("Linda maria me fume en Roma", {
        'entities': [(6, 11, 'DRUG'), (23,27,'LOC')]
    }),

    ("Volkswagen proviene al igual que Audi de Alemania", {
        'entities': [(0, 10, 'ORG'),(33, 37, 'ORG'), (41, 49, 'LOC')]
    }),

    ("Mario la denomina frula", {
        'entities': [(0, 5, 'PER'), (18, 23, 'DRUG')]
    }),

    ("Nicolás no consume estimulantes", {
        'entities': [(0, 7, 'PER'),(19, 31, 'DRUG')]
    }),

    ("Es hora de prender el faso", {
        'entities': [(22, 26, 'DRUG')]
    }),
    
    ("Las canciones modernas hacen apologia de las drogas", {
        'entities': [(45, 51, 'DRUG')]
    }),
    
    ("Mientras Gaston genera el nuevo modelo sigue escribiendo", {
        'entities': [(9, 15, 'PER')]
    }),
    
    ("si toy labuarando y me vengo máqana xk recien comense desde el lunes y toy cm una semana en Jujuy", {
        'entities': [(3, 6, 'ME'),(7, 17, 'ME'),(29, 35, 'ME'), (36, 38, 'ME'), (46, 53, 'ME'), (71, 74, 'ME'),(75, 77, 'ME'),(92,97,'LOC')]
    }),

    ("yo aka en ksa trab ,,,terminando lo k falta de est porrito", {
        'entities': [(3, 6, 'ME'),(10, 13, 'ME'),(14, 18, 'ME'),(19, 22, 'ME'),(36, 37, 'ME'),(47, 50, 'ME'),(51,58,'DRUG')]
    }),

    ("A ree bien primo que tal el clima aya en Tandil", {
        'entities': [(2, 5, 'ME'),(34, 37, 'ME'),(41, 47, 'LOC')]
    }),

    ("dale capas k venga por un poco de merca luego te aviso okey", {
        'entities': [(11, 12, 'ME'),(34, 39, 'DRUG')]
    }),

    ("Jajaja gil mi vieja no me deja LSD tomar en casa", {
        'entities': [(0, 6, 'ME'),(31, 34, 'DRUG'),(44, 48, 'MISC')]
    }),

    ("de última tomamos coca fue jejeje", {
        'entities': [(18, 22, 'DRUG')]
    }),

    ("bien aka yendo pa mi ksa xq recien salí del trabajo?", {
        'entities': [(5, 8, 'ME'),(15, 17, 'ME'),(21, 24, 'ME'),(25, 27, 'ME'),(44, 51, 'MISC')]
    }),
    
    ("Mm nada aca en mi casa escuchando ganya y vos??", {
        'entities': [(0, 2, 'ME'),(34, 39, 'DRUG')]
    }),
    
    ("eh primo hoy dijo ah romenco recien me llamó Julio?", {
        'entities': [(21, 28, 'LOC'),(45, 50, 'PER')]
    }),
    
    ("todas son lindas ,,,ta pa partírles cm un queso,,,se ponen unas calzas pero mal?", {
        'entities': [(17, 22, 'ME'),(23, 25, 'ME'),(36, 38, 'ME'),(47, 50, 'ME')]
    }),

    ("fumando porro, hola cm taz k hacías", {
        'entities': [(8, 13, 'DRUG'),(20, 22, 'ME'),(23, 27, 'ME'),(28, 29, 'ME')]
    }),

    ("si si la próxima bailamos hasta k salga el sol eaaa jeje", {
        'entities': [(32, 33, 'ME'),(47, 51, 'ME'),(52, 56, 'ME')]
    }),

    ("eh wacho pasame algún num de tus dilers asi los wasapeo jeje?", {
        'entities': [(3, 8, 'ME'),(22, 25, 'ME'),(33, 39, 'DRUG'),(48, 55, 'ME'),(56, 60, 'ME'),]
    }),

    ("wueno Nico te dejo xq voy ah comensar ah drogarme?", {
        'entities': [(0, 5, 'ME'),(6, 10, 'PER'),(19, 21, 'ME'),(29, 37, 'ME'),(41, 49, 'DRUG')]
    }),

    ("y aka andamos más k bien en Google?", {
        'entities': [(2, 5, 'ME'),(18, 19, 'ME'),(28, 34, 'ORG')]
    }),

    ("Si si estbmos d asado jejej si Saul :)", {
        'entities': [(6, 13, 'ME'),(14, 15, 'ME'),(22, 27, 'ME'),(30, 34, 'PER')]
    }),

    ("yo bien aka disfrutando del paco?", {
        'entities': [(8, 11, 'ME'),(28, 32, 'DRUG')]
    }),
    
    ("vs sos de Bolivia no?", {
        'entities': [(0, 2, 'ME'),(10, 17, 'LOC')]
    }),
    
    ("che vs no lo tns mi billetera xk no lo encuentro", {
        'entities': [(4, 6, 'ME'),(13, 16, 'ME'),(30, 32, 'ME')]
    }),
    
    ("y yo aka en lo de Rudy vine ah vicitar xk ya tuvo ah su hija su mujer?", {
        'entities': [(5, 8, 'ME'),(18,22,'PER'),(39, 41, 'ME')]
    }),

    ("k hiciste en el fin de semana", {
        'entities': [(0, 1, 'ME')]
    }),

    ("asta k no empiece a vender el faso", {
        'entities': [(0, 4, 'ME'),(5, 6, 'ME'),(29,33,'DRUG')]
    }),

    ("Alas 8 juego ala pelota. Por Polonia", {
        'entities': [(0, 4, 'ME'),(13, 16, 'ME'),(29, 36, 'LOC')]
    }),

    ("che y al final ahi joda en abruzece o no?", {
        'entities': [(27, 35, 'MISC')]
    }),

    ("tamos en la cumbre festejando el cumple de Elvira?", {
        'entities': [(12, 18, 'MISC'),(43, 49, 'PER')]
    }),

    ("No pasa qe ya estoy en mi trabajo xeso estoy mal", {
        'entities': [(8, 10, 'ME'),(26, 33, 'MISC'),(34, 38, 'ME')]
    }),

    ("ah wueno me imagino k taz re turbina?", {
        'entities': [(3, 8, 'ME'),(20, 21, 'ME'),(22, 25, 'ME'),(29, 36, 'DRUG')]
    }),
    
    ("ahi liyo pal compa", {
        'entities': [(4, 9, 'DRUG'),(9, 12, 'ME'),(13, 18, 'ME')]
    }),
    
    ("le di a la pasta guacho", {
        'entities': [(11, 16, 'DRUG'),(17, 23, 'ME')]
    }),
    
    ("Julio tiene cristales", {
        'entities': [(0,5,'PER'),(12,21,'DRUG')]
    }),

    ("bazuco? en el trabajo", {
        'entities': [(0, 6, 'DRUG'), (14,21,'MISC')]
    }),

    ("En Toyota no venden acido", {
        'entities': [(3,9,'ORG'),(20,25,'DRUG')]
    }),

    ("Ah xq jaja no ay polvo pero", {
        'entities': [(3, 5, 'ME'),(6, 10, 'ME'),(14, 16, 'ME'),(17, 22, 'DRUG')]
    }),

    ("Bn bn aca cocinando perico, va terminando ejje", {
        'entities': [(0, 2, 'ME'),(3, 5, 'ME'),(20, 26, 'DRUG'),(42, 46, 'ME')]
    }),

    ("Carlo la denomina hash", {
        'entities': [(0, 5, 'PER'), (18, 22, 'DRUG')]
    }),

    ("Nicolás no consume estimulantes", {
        'entities': [(0, 7, 'PER'),(19, 31, 'DRUG')]
    }),

    ("dale arrancate un verde y pinta la fiesta", {
        'entities': [(18, 23, 'DRUG')]
    }),
    
    ("tambien tenemos kush", {
        'entities': [(16, 20, 'DRUG')]
    }),
    
    ("alta blancanieves", {
        'entities': [(5, 17, 'DRUG')]
    }),
    
    ("Mabel deja de darle al carton", {
        'entities': [(0, 5, 'PER'),(23, 29, 'DRUG')]
    }),

    ("Q andas haciendo x Facebook? Estas laburando aya?", {
        'entities': [(0, 1, 'ME'),(17, 18, 'ME'),(19, 27, 'ORG'),(45, 48, 'ME')]
    }),
    
    ("Me imagino jeje pero cuand t vs a t casa", {
        'entities': [(11, 15, 'ME'),(27, 28, 'ME'),(29, 31, 'ME'),(34, 35, 'ME'),(36, 40, 'MISC')]
    }),
    
    ("De una no queda otra q laburar la anfeta ", {
        'entities': [(21, 22, 'ME'),(34, 40, 'DRUG')]
    }),

    ("y k me contas de wueno prima", {
        'entities': [(2, 3, 'ME'),(17, 22, 'ME'),]
    }),

    ("Manhattan es una locación", {
        'entities': [(0,9,'LOC')]
    }),

    ("Anita se fumo una kenke, muy gracioso lo de Maria", {
        'entities': [(0, 5, 'PER'), (18,23,'DRUG'), (44, 49, 'PER')]
    }),

    ("jazmin y jamon son denominaciones para lo que buscamos", {
        'entities': [(0, 6, 'DRUG'), (9, 14, 'DRUG')]
    }),

    ("extasis también llamado maka", {
        'entities': [(0, 7, 'DRUG'), (24, 28, 'DRUG')]
    }),

    ("choco, has, goma, ful, china, todas encontradas en Google ", {
        'entities': [(0, 5, 'DRUG'), (7, 10, 'DRUG'), (12, 16, 'DRUG'), (18, 21, 'DRUG'), (23, 28, 'DRUG'), (51, 57, 'ORG')]
    }),

    ("se consigue hongos en la plaza", {
        'entities': [(12, 18, 'DRUG'),(25, 30, 'MISC')]
    }),
    
    ("el elixir de la otra vez", {
        'entities': [(3, 9, 'DRUG')]
    }),
    
    ("rohypnol triene efecto depresor.", {
        'entities': [(0, 8, 'DRUG')]
    }),
    
    ("el valium viene recetado", {
        'entities': [(3, 9, 'DRUG')]
    }),

    ("Marcos consume tachielas", {
        'entities': [(0, 6, 'PER'), (9, 18, 'DRUG')]
    }),

    ("mota, kenke, que mas hay en el campo?", {
        'entities': [(0, 4, 'DRUG'),(6, 11, 'DRUG'),(31, 36, 'MISC')]
    }),

    ("Pablo consumia rulas y mdma", {
        'entities': [(0, 5, 'PER'),(15, 20, 'DRUG'),(23, 27, 'DRUG')]
    }),

    ("se rien del chulas pops", {
        'entities': [(12, 23, 'DRUG')]
    }),

    ("En Francia consumen polen y tate ", {
        'entities': [(3, 10, 'LOC'),(20, 25, 'DRUG'),(28, 32, 'DRUG')]
    }),

    ("Lautaro vendia ful en la escuela", {
        'entities': [(0, 7, 'PER'),(15, 18, 'DRUG'),(25, 32, 'DRUG')]
    }),

    ("un pastel de alta costura", {
        'entities': [(3, 9, 'DRUG'),(18, 25, 'DRUG')]
    }),
    
    ("Ines usa pegamento", {
        'entities': [(0, 4, 'PER'), (9,18,'DRUG')]
    }),

    ("Drogas o sustancias lícitas: se ocupan libremente de acuerdo a los deseos de cada consumidor. Por ejemplo, las bebidas alcohólicas y el tabaco.", {
        'entities': [(0, 6, 'DRUG'), (9, 19, 'DRUG'), (111, 130, 'DRUG'), (136, 142, 'DRUG')]
    }),

    ("Drogas que se utilizan principalmente como medicamento: generalmente se obtienen mediante prescripción médica.", {
        'entities': [(0, 6, 'DRUG'),(43, 54, 'DRUG')]
    }),

    ("En Occidente, su uso va ligado al tratamiento de trastornos del ánimo, trastornos del sueño, enfermedades dolorosas o con el fin de lograr mayor lucidez o concentración (nootrópicos).", {
        'entities': [(170, 181, 'DRUG')]
    }),
    
    ("Por ejemplo, los psicofármacos, estimulantes menores y la metadona.", {
        'entities': [(17, 30, 'DRUG'),(32, 44, 'DRUG'),(58, 66, 'DRUG')]
    }),
    
    ("Drogas o sustancias ilícitas: varían de acuerdo a la legislación de cada país.", {
        'entities': [(0, 6, 'DRUG'),(9, 28, 'DRUG')]
    }),
    
    ("Son aquellas cuyo comercio se considera ilegal, como los derivados cannabis, la heroína y la cocaína.", {
        'entities': [(67, 75, 'DRUG'),(80, 87, 'DRUG'),(93, 100, 'DRUG')]
    }),

    ("Existen convenciones internacionales que han establecido como prohibido el uso no médico de opiáceos, cannabis, alucinógenos, cocaína y muchos otros estimulantes, al igual que de los hipnóticos y sedantes. ", {
        'entities': [(92, 100, 'DRUG'), (102, 110, 'DRUG'), (112, 124, 'DRUG'), (126, 133, 'DRUG'), (149, 161, 'DRUG'), (183, 193, 'DRUG'), (196, 204, 'DRUG')]
    }),
    
    ("Una droga depresora es aquella que ralentiza o inhibe las funciones o la actividad de alguna región del cerebro.", {
        'entities': [(4, 9, 'DRUG')]
    }),
    
    ("Este grupo se subdivide a su vez en varios grupos: antihistamínicos, antipsicóticos, disociativos, GABAnérgicos, glicinérgicos, narcóticos y simpatológicos. ", {
        'entities': [(51, 67, 'DRUG'), (69, 83, 'DRUG'), (85, 97, 'DRUG'), (99, 111, 'DRUG'), (113, 126, 'DRUG'), (128, 138, 'DRUG'), (141, 155, 'DRUG')]
    }),

    ("Una droga estimulante es aquella que produce mejoras temporales de la actividad neurológica o física.", {
        'entities': [(4, 9, 'DRUG')]
    }),

    ("Psicodélicos: producen una alteración en la cognición y la percepción.", {
        'entities': [(0,12,'DRUG')]
    }),

    ("Los psicodélicos suelen agruparse en lisergamidas (destaca el LSD), feniletilaminas, piperazina, triptaminas y otros.", {
        'entities': [(4, 16, 'DRUG'), (37,49,'DRUG'), (62, 65, 'DRUG'), (68, 83, 'DRUG'), (85,95,'DRUG'), (97, 108, 'DRUG')]
    }),

    ("Disociativos: producen un bloqueo de las señales de la mente consciente hacia otras partes del cerebro produciendo alucinaciones, privación sensorial, disociación y trance. ", {
        'entities': [(0, 12, 'DRUG')]
    }),

    ("Se dividen en adamantanos, arilciclohexilaminas y morfinanos.", {
        'entities': [(14, 25, 'DRUG'), (27, 47, 'DRUG'), (50, 60, 'DRUG')]
    }),

    ("Delirantes: producen delirios, a diferencia de los alucinógenos psicodélicos y disociativos en el que se mantiene cierto estado de consciencia ", {
        'entities': [(0, 10, 'DRUG'), (51, 76, 'DRUG'), (79, 91, 'DRUG')]
    }),

    ("Se dividen en anticolinérgicos, antihistamínicos y GABA-agonistas.", {
        'entities': [(14, 30, 'DRUG'),(32, 48, 'DRUG'),(51, 65, 'DRUG')]
    }),
    
    ("Los opioides son las drogas que se unen a receptores opioides situados principalmente en el sistema nervioso central y en el tracto gastrointestinal.", {
        'entities': [(4, 12, 'DRUG'),(21, 27, 'DRUG'),(53, 61, 'DRUG')]
    }),
    
    ("Hay tres grandes clases de sustancias opiáceas: alcaloides del opio, como morfina y codeína;", {
        'entities': [(27, 46, 'DRUG'),(48, 67, 'DRUG'),(74, 81, 'DRUG'),(84, 91, 'DRUG')]
    }),
    
    ("opiáceos semi-sintéticos, tales como heroína y oxicodona", {
        'entities': [(0, 24, 'DRUG'),(37, 44, 'DRUG'),(47, 56, 'DRUG')]
    }),

    ("opioides completamente sintéticos, tales como petidina y metadona", {
        'entities': [(0, 8, 'DRUG'), (46, 54, 'DRUG'), (57, 63, 'DRUG')]
    }),

    ("Para dolores de intensidad fuerte se utilizan opioides fuertes como la morfina, la hidromorfona, la metadona, el fentanilo, etc.?", {
        'entities': [(46, 54, 'DRUG'),(71, 78, 'DRUG'),(83, 95, 'DRUG'),(100, 108, 'DRUG'),(113, 122, 'DRUG')]
    }),

    ("Para el alivio de dolores de intensidad moderada se utilizan opioides débiles, de distribución no libre, como el tramadol, la codeína o la hidrocodona.", {
        'entities': [(61, 69, 'DRUG'),(113, 121, 'DRUG'),(126, 133, 'DRUG'),(139, 150, 'DRUG')]
    }),

    ("Este grupo se divide en subgrupos: etéreos, haloalcanos, opioides y esteroides neuroactivos; inyectables o inhalables.", {
        'entities': [(35, 42, 'DRUG'),(44, 55, 'DRUG'),(57, 65, 'DRUG'),(68, 78, 'DRUG')]
    }),

    ("En Francia consumen polen y tate ", {
        'entities': [(3, 10, 'LOC'),(20, 25, 'DRUG'),(28, 32, 'DRUG')]
    }),

    ("Lautaro vendia ful en la escuela", {
        'entities': [(0, 7, 'PER'),(15, 18, 'DRUG'),(25, 32, 'DRUG')]
    }),

    ("un pastel de alta costura", {
        'entities': [(3, 9, 'DRUG'),(18, 25, 'DRUG')]
    }),
    
    ("Ines usa pegamento", {
        'entities': [(0, 4, 'PER'), (9,18,'DRUG')]
    }),

    ("En ese grupo de mierda que parecia yerba brava o volcan;", {
        'entities': [(35, 40, 'DRUG')]
    }),
    
    ("Quiero ponerme a vivir y un alto faso fumar", {
        'entities': [(33, 37, 'DRUG')]
    }),

    ("no estoy triste no es mi llanto es el humo de este fasito que me hace llorar", {
        'entities': [(51, 57, 'DRUG')]
    }),

    ("Si la plantita se muere por que ya se la fumaron", {
        'entities': [(6, 14, 'DRUG')]
    }),

    ("Mira que loco que quede del churro que me fume", {
        'entities': [(28, 34, 'DRUG')]
    }),

    ("Mira como me has dejado si no me mata la droga me mata tu amor tu amor", {
        'entities': [(41, 46, 'DRUG')]
    }),

    ("Desde que no estas conmigo todo el día tomo vino y no puedo dejar de fumanchar ", {
        'entities': [(69, 78, 'DRUG')]
    }),

    ("Pasame la geringa juana estamos de carabana", {
        'entities': [(10, 17, 'DRUG')]
    }),

    ("qe la banda me responda qe no se acabe la milonga", {
        'entities': [(42, 49, 'DRUG')]
    }),
    
    ("Yo no puedo seguir todo el dia tomando coca que vamo a tomar?", {
        'entities': [(39, 43, 'DRUG')]
    }),

    ("¿Cuánto sale un ladrillo? preguntó un intermediario", {
        'entities': [(16, 24, 'DRUG')]
    }),
    
    (" Nada de pollos ni helados. Es que algunos narcos ni siquiera se preocupan por las posibles grabaciones.", {
        'entities': [(9, 15, 'DRUG'),(19, 16, 'DRUG')]
    }),

    ("Los narcos negocian el abastecimiento de marihuana, pero no se animan a mencionar esa droga para evitar allanamientos.", {
        'entities': [(4, 10, 'DRUG'),(41, 50, 'DRUG'),(86, 91, 'DRUG')]
    }),

    ("Voy a tener que conseguir un poco de lechuga porque me andan pidiendo un montón", {
        'entities': [(37, 44, 'DRUG')]
    }),

    ("Con el Bocha muerto se acabó la buena merca", {
        'entities': [(7,12, 'PER' ),(38, 43, 'DRUG')]
    }),

    ("Cocaína: se puede tomar normalmente por la nariz (inhalado), inyectado con jeringa o por inhalación del humo. ", {
        'entities': [(0, 7, 'DRUG'),(75, 82, 'DRUG')]
    }),

    ("También conocida como: coca, crak, bazuco, perico. ", {
        'entities': [(23, 27, 'DRUG'),(29, 33, 'DRUG'),(35, 41, 'DRUG'), (43, 49, 'DRUG')]
    }),

    ("Si una persona toma Éxtasis, su cuerpo se puede calentar excesiva y peligrosamente mientras baila o practica cualquier otra actividad física.", {
        'entities': [(20, 27, 'DRUG')]
    }),

    ("El Éxtasis se ha convertido en una de las drogas ilegales que más se vende en la calle.", {
        'entities': [(3, 10, 'DRUG'),(42, 48, 'DRUG')]
    }),
    
    ("También se puede llamar:	XTC, E, Eva, Adán, pastillas del amor, X.?", {
        'entities': [(25, 28, 'DRUG'),(30, 31, 'DRUG'),(33, 36, 'DRUG'),(38, 62, 'DRUG'),(64, 66, 'DRUG')]
    }),

    ("El Éxtasis es una droga estimulante que puede provocar alucinaciones.", {
        'entities': [(3, 10, 'DRUG'),(18, 35, 'DRUG')]
    }),
    
    ("Como el Éxtasis, el uso de GHB está muy extendido en los clubs nocturnos y en las fiestas de rave y de música tecno, a las que pueden asistir adolescentes y adultos jóvenes.", {
        'entities': [(8, 18, 'DRUG'),(27, 30, 'DRUG')]
    }),

    ("El GHB provoca tanto un subidón de euforia (intenso incremento de la sensación de felicidad) como alucinaciones.", {
        'entities': [(3, 6, 'DRUG')]
    }),

    ("El GHB ha hecho que mucha gente joven necesite recibir cuidados médicos de urgencia.", {
        'entities': [(3, 6, 'DRUG')]
    }),

    ("La mariguana se fuma como un cigarrillo hecho a mano o envuelto (lo que recibe el nombre de porro o canuto).", {
        'entities': [(3, 12, 'DRUG'),(92, 97, 'DRUG'),(100, 106, 'DRUG')]
    }),

    ("La mariguana dificulta la conciencia del paso del tiempo y la concentración.", {
        'entities': [(3, 12, 'DRUG')]
    }),

    ("Rafael Nadal, máximo favorito al título, se retira de Melbourne Park tras ser eliminado del Abierto de Australia", {
        'entities': [(0, 12, 'PER'),(54, 68,'MISC'),(92, 112, 'MISC')]
    }),

    ("Sólo dos pertenecen al grupo de 10 primeros del ránking ATP, que son Roger Federer, N°2, y Marin Cilic, N°6", {
        'entities': [(69,82, 'PER' ),(91, 102, 'PER')]
    }),

    ("México: especialistas revelaron el verdadero significado de Teotihuacán ", {
        'entities': [(0, 6, 'LOC'),(60, 71, 'MISC')]
    }),

    ("Donald Trump apuntó contra el FBI por la pérdida de miles de mensajes de un funcionario que lo investigaba ", {
        'entities': [(0, 12, 'PER'),(30, 33, 'MISC')]
    }),

    ("Un estudio del Instituto Nacional de Antropología e Historia (INAH) de México reveló que el nombre de la urbe prehispánica de Teotihuacán", {
        'entities': [(15, 77, 'MISC'),(126, 137, 'MISC')]
    }),

    ("El mandatario estadounidense consideró que no haber preservado los intercambios entre Peter Strzok y su pareja, Lisa Page, durante uno de los períodos clave de las pesquisas por la injerencia rusa, es una de las mayores noticias en mucho tiempo", {
        'entities': [(86, 98, 'PER'),(112, 121, 'PER')]
    }),
    
    ("El Frente Renovador va a la Justicia por la inconstitucionalidad del megadecreto de Mauricio Macri", {
        'entities': [(84, 98, 'PER')]
    }),

    ("Mauricio es el presidente de Argentina", {
        'entities': [(0, 8, 'PER'),(29, 38, 'LOC')]
    }),
    
    ("La divisa de EEUU se vende a $19,61 en bancos del microcentro porteño", {
        'entities': [(13, 17, 'LOC'),(39, 69, 'MISC')]
    }),

    ("Sebastián Piñera presentó el gabinete para su segundo mandato al frente de Chile", {
        'entities': [(0, 16, 'PER'),(75, 80, 'LOC')]
    }),

    ("Éste es el caso de Andrés Chadwick en una de las carteras más importantes del gabinete, la de ministro del Interior", {
        'entities': [(19, 34, 'PER'),(94, 115, 'MISC')]
    }),

    ("La mariguana se fuma como un cigarrillo hecho a mano o envuelto (lo que recibe el nombre de porro o canuto).", {
        'entities': [(3, 12, 'DRUG'),(92, 97, 'DRUG'),(100, 106, 'DRUG')]
    }),

    ("La mariguana dificulta la conciencia del paso del tiempo y la concentración.", {
        'entities': [(3, 12, 'DRUG')]
    }),

    ("Ooooja k pasho jeje", {
        'entities': [(0, 6, 'ME'),(7, 8, 'ME'),(9, 14, 'ME'),(15, 19, 'ME')]
    }),

    ("vs si k la pasas re bien cambiando num ehhh ?", {
        'entities': [(0, 2, 'ME'),(6, 7, 'ME'),(35, 38, 'ME'),(39, 43, 'ME')]
    }),

    ("Jajjaja lo blokee sin kerer keriendo jaj", {
        'entities': [(0, 7, 'ME'),(11, 17, 'ME'),(22, 27, 'ME'),(28, 35, 'ME'),(36, 39, 'ME')]
    }),

    ("Jjaja wuen dia primith jaja ", {
        'entities': [(0, 5, 'ME'),(6, 10, 'ME'),(15, 22, 'ME'),(23, 27, 'ME')]
    }),

    ("Mmmm me hces um favore xfavor jajaj", {
        'entities': [(0, 4, 'ME'),(8, 12, 'ME'),(9, 11, 'ME'), (12, 18, 'ME'), (19, 25, 'ME'), (26, 31, 'ME')]
    }),

    ("Ajajja cuango lo pued bajr te dig iwual mchas gracias", {
        'entities': [(0, 6, 'ME'),(7, 13, 'ME'), (17, 21, 'ME'), (22, 26, 'ME'), (30, 33, 'ME'), (34, 39, 'ME'), (40, 44, 'ME')]
    }),
    
    ("Siiiii yege jajja si te envie un maj", {
        'entities': [(0, 6, 'ME'), (7,11,'ME'), (22, 27, 'ME'), (33, 36, 'ME')]
    }),

    ("Ooooh mmm noce xk llego tarde seguro xk no abia colectiv", {
        'entities': [(0, 5, 'ME'),(6, 9, 'ME'),(9, 13, 'ME'), (14,16,'ME'),(37, 39, 'ME'), (43, 47, 'ME'), (48, 56, 'ME')]
    }),
    
    ("Jugamos a las 14:00 aya en Balcarce", {
        'entities': [(20, 23, 'ME'),(27, 35, 'LOC')]
    }),

    ("contam k isiste hoy primita?", {
        'entities': [(0, 6, 'ME'), (7,8,'ME'), (9, 15, 'ME')]
    }),

    ("claro xk ahi días k toy mal y aburrido y noc en kien desaugarme,,", {
        'entities': [(6, 8, 'ME'), (18,19,'ME'), (20, 23, 'ME'), (41, 44, 'ME'), (48,52,'ME'), (53, 63, 'ME'), (63, 65, 'ME')]
    }),

    ("Primo k haces.... todo tranca.?", {
        'entities': [(6, 4, 'ME'), (13,17,'ME'), (23, 29, 'ME')]
    }),

    ("Pero stoy cn diana", {
        'entities': [(5, 9, 'ME'),(10, 12, 'ME'), (13, 18, 'PER')]
    }),

    ("Asta batan voy en remis de ahi me llevas ", {
        'entities': [(0, 4, 'ME'), (5, 10, 'LOC')]
    }),

    ("Ke corta manbos stos borrachos", {
        'entities': [(0, 2, 'ME'), (9,15,'ME'), (16, 20, 'ME')]
    }),

    ("Stoy yebando a mi papa a la cancha despues tengo ke ir a terminar de invitar", {
        'entities': [(0, 4, 'ME'), (5,12,'ME'), (49, 51, 'ME')]
    }),
    
    ("Ke viento se lebanto biento ahora?", {
        'entities': [(0, 2, 'ME'), (13,20,'ME'), (21, 27, 'ME')]
    }),

    ("Mañana voy a pagar la lus y yego un rato si no ay mucha jente", {
        'entities': [(22, 25, 'ME'), (28,32,'ME'), (47, 49, 'ME'), (56, 61, 'ME')]
    }),
    
    (" 123 y sigo voi al hospital a vuscar mi medicacion aver si me la dan", {
        'entities': [(12, 15, 'ME'), (30,36,'ME'), (51, 55, 'ME')]
    }),

    ("Voi x el puemte ya no doi mas", {
        'entities': [(0, 3, 'ME'), (4,5,'ME'), (9, 15, 'ME'), (22, 25, 'ME')]
    }),

    ("Si se vino hoi hace un rato y ya andamos en la calle de transa las dos ji", {
        'entities': [(11, 14, 'ME'), (56,62,'DRUG'), (71, 73, 'ME')]
    }),

    ("Que vas a fumar vos nenA me queda un vagullo solo", {
        'entities': [(20,24, 'ME' ),(37, 44, 'DRUG')]
    }),

    ("No no se recupera mas juan ya dijo el medico anoche estaba agrecibo mal ni los calmante lo paran ", {
        'entities': [(22, 26, 'PER'),(59, 67, 'ME')]
    }),

    ("Viste parece mas joben ", {
        'entities': [(17, 23, 'ME')]
    }),

    ("Ke ases ? Ase frio ahora", {
        'entities': [(0, 2, 'ME'), (3,7,'ME'), (10, 13, 'ME')]
    }),

    ("Y te dava para el escavio", {
        'entities': [(5, 9, 'ME'),(18, 25, 'DRUG')]
    }),
    
    ("Yo tomo un remis y voi para alla x que estoi esperando a sofia", {
        'entities': [(19, 22, 'ME'), (33,34,'ME'), (39, 46, 'ME')]
    }),

    ("El Éxtasis es una droga estimulante que puede provocar alucinaciones.", {
        'entities': [(3, 10, 'DRUG'),(18, 35, 'DRUG')]
    }),
    
    ("Como el Éxtasis, el uso de GHB está muy extendido en los clubs nocturnos y en las fiestas de rave y de música tecno, a las que pueden asistir adolescentes y adultos jóvenes.", {
        'entities': [(8, 18, 'DRUG'),(27, 30, 'DRUG')]
    }),

    ("El GHB provoca tanto un subidón de euforia (intenso incremento de la sensación de felicidad) como alucinaciones.", {
        'entities': [(3, 6, 'DRUG')]
    }),

    ("El GHB ha hecho que mucha gente joven necesite recibir cuidados médicos de urgencia.", {
        'entities': [(3, 6, 'DRUG')]
    }),

    ("La mariguana se fuma como un cigarrillo hecho a mano o envuelto (lo que recibe el nombre de porro o canuto).", {
        'entities': [(3, 12, 'DRUG'),(92, 97, 'DRUG'),(100, 106, 'DRUG')]
    }),

    ("La mariguana dificulta la conciencia del paso del tiempo y la concentración.", {
        'entities': [(3, 12, 'DRUG')]
    }),

    ("Rafael Nadal, máximo favorito al título, se retira de Melbourne Park tras ser eliminado del Abierto de Australia", {
        'entities': [(0, 12, 'PER'),(54, 68,'MISC'),(92, 112, 'MISC')]
    }),

    ("Sólo dos pertenecen al grupo de 10 primeros del ránking ATP, que son Roger Federer, N°2, y Marin Cilic, N°6", {
        'entities': [(69,82, 'PER' ),(91, 102, 'PER')]
    }),

    ("México: especialistas revelaron el verdadero significado de Teotihuacán ", {
        'entities': [(0, 6, 'LOC'),(60, 71, 'MISC')]
    }),

    ("Donald Trump apuntó contra el FBI por la pérdida de miles de mensajes de un funcionario que lo investigaba ", {
        'entities': [(0, 12, 'PER'),(30, 33, 'MISC')]
    }),

    ("Un estudio del Instituto Nacional de Antropología e Historia (INAH) de México reveló que el nombre de la urbe prehispánica de Teotihuacán", {
        'entities': [(15, 77, 'MISC'),(126, 137, 'MISC')]
    }),

    ("El mandatario estadounidense consideró que no haber preservado los intercambios entre Peter Strzok y su pareja, Lisa Page, durante uno de los períodos clave de las pesquisas por la injerencia rusa, es una de las mayores noticias en mucho tiempo", {
        'entities': [(86, 98, 'PER'),(112, 121, 'PER')]
    }),
    
    ("El Frente Renovador va a la Justicia por la inconstitucionalidad del megadecreto de Mauricio Macri", {
        'entities': [(84, 98, 'PER')]
    }),

    ("Mauricio es el presidente de Argentina", {
        'entities': [(0, 8, 'PER'),(29, 38, 'LOC')]
    }),
    
    ("La divisa de EEUU se vende a $19,61 en bancos del microcentro porteño", {
        'entities': [(13, 17, 'LOC'),(39, 69, 'MISC')]
    }),

    ("Sebastián Piñera presentó el gabinete para su segundo mandato al frente de Chile", {
        'entities': [(0, 16, 'PER'),(75, 80, 'LOC')]
    }),

    ("Éste es el caso de Andrés Chadwick en una de las carteras más importantes del gabinete, la de ministro del Interior", {
        'entities': [(19, 34, 'PER'),(94, 115, 'MISC')]
    }),

    ("La mariguana se fuma como un cigarrillo hecho a mano o envuelto (lo que recibe el nombre de porro o canuto).", {
        'entities': [(3, 12, 'DRUG'),(92, 97, 'DRUG'),(100, 106, 'DRUG')]
    }),

    ("La mariguana dificulta la conciencia del paso del tiempo y la concentración.", {
        'entities': [(3, 12, 'DRUG')]
    }),

    ("Estamos las dos con Candela, vamos a comer a tu casa", {
        'entities': [(20, 27, 'PER'), (48, 52, 'MISC')]
    }),

    ("Ah mira ke bueno... Xke c volvio? Mandale salu2 a las 2... Ke bonita la gorda. Cm c yama?", {
        'entities': [(8, 10, 'ME'),(20, 23, 'ME'),(24, 25, 'ME'),(42, 47, 'ME'),(59, 61, 'ME'),(79, 81, 'ME'),(82, 83, 'ME'),(84, 88, 'ME')]
    }),
    
    ("Y c... Pobre negra.. Y la meli n volvio todavia?? Ke lindo nobre. Es re parecida a la agustina d chikita. Tienen whasapp las chikas?", {
        'entities': [(2, 6, 'ME'),(26, 30, 'PER'),(31, 32, 'ME'),(50, 52, 'ME'),(59, 64, 'ME'),(86, 94, 'PER'),(95, 96, 'ME'),(97, 104, 'ME'),(103, 120, 'ME'),(125, 131, 'ME')]
    }),

    ("Preparate mañana para hacer el tuco, que yo hago los ñoquis", {
        'entities': []
    }),

    ("Queres alitas de pollo o carne?", {
        'entities': []
    }),

    ("Hola tia muy feliz cumple no pude ir a saludarte no hai plata y con las manos vacias no voy ni mamada espero que la pases lindo feliz cumple.", {
        'entities': [(52, 55, 'DRUG')]
    }),

    ("Pero voy a comer con la aBUELA ME BAS ACOMPAÑAR AL BANCO TENGO KE RETIRAR EL PIN", {
        'entities': [(24, 80, 'ME')]
    }),

    ("Ete mi numero nuev ja", {
        'entities': [(0, 3, 'ME'),(14, 18, 'ME'),(19, 21, 'ME')]
    }),

    ("naaa acabo de llegar del trab y no pude ver el partido", {
        'entities': [(0, 4, 'ME'),(25, 29,'ME')]
    }),

    ("Jajjja gracias estab re llenooo encina estabams los 4 na mas xk laro se fue a mar del plata ja", {
        'entities': [(0, 7, 'ME'),(15, 20, 'ME'),(24, 31, 'ME'),(32, 38, 'ME'),(39, 47, 'ME'),(54, 56, 'ME'),(57, 61, 'PER'),(78, 91, 'LOC'),(92, 94, 'ME')]
    }),

    ("mmm k raro k llegue tan tarde mmm ya me imagina xk llegó tarde después dice k nooo ", {
        'entities': [(0, 3, 'ME'),(4, 5, 'ME'),(11, 12, 'ME'),(30, 33, 'ME'),(48, 50, 'ME'),(76, 77, 'ME'),(78, 82, 'PER')]
    }),

    ("Che el domingo se juega si o si contra la gloria. ", {
        'entities': [(42, 48, 'MISC')]
    }),

    ("dale okey ,,pero no me dijo naa ever xk me dijo k me iva llamar y también ah rudy?", {
        'entities': [(10, 12, 'ME'),(28, 31, 'ME'),(32, 36, 'PER'),(37, 39, 'ME'),(48, 49, 'ME'),(53, 56, 'ME'),(74, 76, 'ME'),(77, 81, 'PER')]
    }),

    ("Van a venir pajas no?", {
        'entities': []
    }),
    
    ("Toda tu sangre, tus lagrimas, y tu vida.", {
        'entities': []
    }),

    ("Y tambien que envíes miles de mensajes con chistes, los cuales se riegan como pólvora", {
        'entities': []
    }),
    
    ("mmm noooo xk cuando llegue pa mi ksa no taban ,,asi agarré mis kosas y me fui ah jugar", {
        'entities': [(0, 3, 'ME'),(4, 9, 'ME'),(10, 12, 'ME'),(27, 29, 'ME'),(33, 36, 'ME'),(40, 45, 'ME'),(46, 48, 'ME'),(63, 68, 'ME'),(78, 80, 'ME')]
    }),
    
    ("aparte no saben todavia también de lo k choke", {
        'entities': [(38, 39, 'ME'),(40, 45, 'ME')]
    }),
    
    ("Si lo ves a jhoner desile ke me resp los msjs ke le mande", {
        'entities': [(12, 18, 'PER'),(19, 25, 'ME'),(26, 28, 'ME'),(32, 36, 'ME'),(41, 45, 'ME'),(46, 48, 'ME')]
    }),

    ("buenoo para mii sii hauiii qe tenerles respeto es la tribuu urbanaa mas popular yy famosa ", {
	'entities':  [(0, 6, 'ME'),(12, 15, 'ME'),(16, 19, 'ME'),(20, 26, 'ME'),(27, 29, 'ME'),(53, 59, 'ME'),(60, 67, 'ME'),(80, 82, 'ME')]
    }),

    ("ehh buenoo igual no haii qe trataarlos asiii osea porqe ", {
            'entities':  [(0, 3, 'ME'),(4, 10, 'ME'),(20, 24, 'ME'),(25, 27, 'ME'),(28, 38, 'ME'),(39, 44, 'ME'),(50, 55, 'ME')]
    }),

    ("ellos no nos hacen nada ii apartee los tratan como sii fueran unas mierdad iin no es asii ", {
            'entities':  [(24, 26, 'ME'),(27, 34, 'ME'),(51, 54, 'ME'),(67, 74, 'ME'),(75, 78, 'ME'),(85, 89, 'ME')]
    }),

    ("yo sii tengoo qe elegiir entre un flogeer oo un emoo preferiiriia se un flogger antes de cortarrme la s venass eso es de un taradoo cortarcee las vennas arreh forra noo mentiira peroprefiero ser floggerr", {
            'entities':  [(3, 6, 'ME'),(7, 13, 'ME'),(14, 16, 'ME'),(17, 24, 'ME'),(34, 41, 'ME'),(42, 44, 'ME'),(48, 52, 'ME'),(53, 65, 'ME'),(89, 98, 'ME'),(102, 103, 'ME'),(104, 110, 'ME'),(124, 131, 'ME'),(132, 141, 'ME'),(146, 152, 'ME'),(153, 158, 'ME'),(165, 168, 'ME'),(169, 177, 'ME'),(178, 190, 'ME'),(195, 203, 'ME')]
    }),

    ("adiozz", {
            'entities':  [(0, 6, 'ME')]
    }),

    ("El presidente Mauricio Macri recorrió esta mañana las obras de reconstrucción de la localidad jujeña Volcán, que en 2017 fue afectada por un alud de barro que dejó un saldo de cuatro muertos y pérdidas millonarias.", {
            'entities':  [(14, 28, 'PER'),(101, 107, 'LOC')]
    }),

    ("Macri fue recibido por el gobernador de la provincia Gerardo Morales que lo acompañó en el recorrido por Volcán, un pequeño conglomerado de 31 manzanas y 1200 habitantes, ubicado a 41 kilómetros de la capital provincial.", {
            'entities':  [(0, 5, 'PER'),(43, 52, 'MISC'),(53, 68, 'PER'),(105, 111, 'LOC'),(201, 219, 'MISC')]
    }),

    ("Al mediodía, el mandatario estuvo en un Centro de Desarrollo Infantil de Humahuaca, y luego depositó una ofrenda floral a la Virgen de la Candelaria, patrona de esa ciudad, que este año celebra sus 50 años del templo.", {
            'entities':  [(40, 69, 'MISC'),(73, 82, 'LOC'),(125, 148, 'MISC')]
    }),

    ("En tanto, el jefe de Estado tenía previsto participar de un partido de fútbol en una cancha del club Independencia, que es la de mayor altura del país y a las 16 encabezará en la ciudad de Perico, a 35 kilómetros de la capital provincial de Jujuy, el acto de restitución de la zona franca, que se prevé va a generar una nueva actividad económica en la región norteña.", {
            'entities':  [(96, 114, 'MISC'),(189, 195, 'LOC'),(241, 246, 'LOC'),(277, 288, 'MISC')]
    }),

    ("El 4 de febrero los Patriots de Nueva Inglaterra se enfrentan a los Eagles de Filadelfia en el acontecimiento deportivo más importante de los Estados Unidos: el Super Bowl.", {
            'entities':  [(32, 48, 'LOC'),(68, 74, 'MISC'),(78, 88, 'LOC'),(142, 156, 'LOC'),(161, 171, 'MISC')]
    }),

    ("Hong Kong sigue siendo el país con la economía más libre del mundo, según la edición 2018 del Índice de Libertad Económica que elabora desde hace 22 años The Heritage Foundation. Esta región administrativa especial de China, que tiene más de 7 millones de habitantes en una superficie que apenas supera los 1.000 kilómetros cuadrados, tiene un puntaje de 90,2 sobre 100.", {
            'entities':  [(0, 9, 'LOC'),(154, 177, 'ORG'),(218, 223, 'LOC')]
    }),

    ("Los dos países que completan el podio también pertenecen a la región de Asia-Pacífico. Uno es Singapur, que sumó 88,8, y el otro es Nueva Zelanda, con 84,2. Junto con Suiza (81,7), Australia (80,9) e Irlanda (80,4), son los únicos que el think tank con sede en Washington DC considera plenamente libres desde el punto de vista económico.", {
            'entities':  [(72, 85, 'MISC'),(94, 102, 'LOC'),(132, 145, 'LOC'),(167, 172, 'LOC'),(181, 190, 'LOC'),(200, 207, 'LOC'),(261, 274, 'LOC')]
    }),

    ("Los cuatro que completan el top ten están por debajo de los 80 puntos, lo que significa que califican como *mayormente libres*. Se trata de Estonia (78,8), Reino Unido (78), Canadá (77,7) y Emiratos Árabes (77,6).", {
            'entities':  [(140, 147, 'LOC'),(156, 167, 'LOC'),(174, 180, 'LOC'),(190, 205, 'LOC')]
    }),

    ("El país menos libre del planeta es Corea del Norte, que apenas suma 5,8 puntos. El régimen de Nicolás Maduro logró hundir a Venezuela al penúltimo lugar, con 25,2. Entre los diez menos libres hay otros dos latinoamericanos, que conviven junto con seis africanos: Cuba (31,9), República del Congo (38,9), Eritrea (41,7), Guinea Ecuatorial (42), Zimbabwe (44), Bolivia (44,1), Argelia (44,7) e Yibuti (45,1).", {
            'entities':  [(35, 50, 'LOC'),(94, 108, 'PER'),(124, 133, 'LOC'),(263, 267, 'LOC'),(276, 295, 'LOC'),(304, 311, 'LOC'),(320, 337, 'LOC'),(344, 352, 'LOC'),(359, 366, 'LOC'),(375, 382, 'LOC'),(392, 398, 'LOC')]
    }),

    ("La única nación de América Latina considerada *mayormente libre* es Chile. Con 75,2, ocupa el puesto 20 a nivel mundial. Bastante más lejos, en el 38, se encuentra Uruguay. Con 69,2 puntos, baja a la categoría *moderadamente libre*. El top 5 regional lo completan Colombia (68,9), Perú (68,7) y Panamá (67), que ocupan respectivamente los puestos 42, 43 y 54.", {
            'entities':  [(19, 33, 'LOC'),(68, 73, 'LOC'),(164, 171, 'LOC'),(264, 272, 'LOC'),(281, 285, 'LOC'),(295, 301, 'LOC')]
    }),

    ("En la región hay varios que están en rojo. *Mayormente no libres* son Nicaragua (58,9), Guyana (58,7), Haití (55,8), la Argentina (52,3) y Brasil (51,4). Todos ellos oscilan entre los lugares 100 y 153.", {
            'entities':  [(70, 79, 'LOC'),(88, 94, 'LOC'),(103, 108, 'LOC'),(120, 129, 'LOC'),(139, 145, 'LOC')]
    }),

    ("Bueno q les puedo dcir, no tngo nada en contra de ellos pero me parecn giles, se nota q no tienen nada q hacr q estar sakndose fotos y dspues subirlas a internet. Pero buenoq le vams hacr. Yo tngo amigos q son re floggers y son pilisimas, ojala todos fueran asi", {
            'entities':  [(6, 7, 'ME'),(18, 22, 'ME'),(64, 70, 'ME'),(86, 87, 'ME'),(103, 104, 'ME'),(105, 109, 'ME'),(110, 111, 'ME'),(118, 126, 'ME'),(168, 174, 'ME'),(178, 182, 'ME'),(183, 187, 'ME'),(192, 196, 'ME'),(204, 205, 'ME'),(228, 237, 'ME')]
    }),

    ("vs crees en eso?", {
            'entities':  [(0, 2, 'ME'),(6, 10, 'ME'),(9, 24, 'LOC'),(14, 17, 'ME'),(19, 24, 'ME'),(25, 27, 'ME')]
    }),

    ("holaaa", {
            'entities':  [(0, 6, 'ME')]
    }),

    ("k haces perdida todo bien?", {
            'entities':  [(0, 1, 'ME')]
    }),

    ("Y yo me estoi x ir de casa me sacaron las chapas tu hermanito", {
            'entities':  [(8, 13, 'ME'),(14, 15, 'ME')]
    }),

    ("Resulta que yo compraba digamos 'yerba mate' a un colombiano en capital.", {
            'entities':  [(33, 43, 'DRUG'),(64, 71, 'LOC')]
    }),

    ("y k haces lokito?", {
            'entities':  [(2, 3, 'ME'),(10, 16, 'ME')]
    }),

    ("holaaa", {
            'entities':  [(0, 6, 'ME')]
    }),

    ("eh Dieguito dond pinta hoy?", {
            'entities':  [(3, 11, 'PER'),(12, 16, 'ME')]
    }),

    ("Aaaa ke hino de puta", {
            'entities':  [(0, 4, 'ME'),(5, 7, 'ME'),(8, 12, 'ME')]
    }),

    ("Ooolu men!!", {
            'entities':  [(0, 5, 'ME'),(6, 9, 'ME')]
    }),

    ("Y es tu hermanito que le vamos hacer me voi si me prestan una casa ahora y que dios los ayude me preocupa la abuela nada mas", {
            'entities':  [(40, 43, 'ME')]
    }),

    ("Vuscalo yegua", {
            'entities':  [(0, 7, 'ME')]
    }),

    ("Oka oka", {
            'entities':  [(0, 3, 'ME'),(4, 7, 'ME')]
    }),

    ("Siii !!! Prii aka cn las chikas !!!", {
            'entities':  [(0, 4, 'ME'),(9, 13, 'ME'),(14, 17, 'ME'),(18, 20, 'ME'),(25, 31, 'ME')]
    }),

    ("Chateando con la culona no sabes como la estoi vardeando a ella y el marido jijiji", {
            'entities':  [(17, 23, 'ME'),(41, 46, 'ME'),(47, 56, 'ME'),(76, 82, 'ME')]
    }),

    ("y k andan haciendo ?", {
            'entities':  [(2, 3, 'ME')]
    }),

    ("Naaaa !! Mas abuu !!!", {
            'entities':  [(0, 5, 'ME'),(13, 17, 'ME')]
    }),

    ("Guachin!!! Como anda eso mi amigo?", {
            'entities':  [(0, 7, 'ME')]
    }),

    ("Pero che y la vieja ke dis sabe ke te vas ?", {
            'entities':  [(20, 22, 'ME'),(23, 26, 'ME'),(32, 34, 'ME')]
    }),

    ("ahi ando aka en mi ksa viendo k puedo hacer?", {
            'entities':  [(9, 12, 'ME'),(19, 22, 'ME'),(30, 31, 'ME')]
    }),

    ("Jo que chusma laaaaaaas", {
            'entities':  [(0, 2, 'ME'),(14, 23, 'ME')]
    }),

    ("Cuando me decia en una esquina tenia que estar ahi en punto. ", {
            'entities':  [(23, 30, 'MISC')]
    }),

    ("Ezte viejo ke no se keda kieto", {
            'entities':  [(0, 4, 'ME'),(11, 13, 'ME'),(20, 24, 'ME'),(25, 30, 'ME')]
    }),

    ("Tengo q esperar q me manden el email", {
            'entities':  [(6, 7, 'ME'),(16, 17, 'ME')]
    }),

    ("Si esta llorando como loca x que me voi", {
            'entities':  [(27, 28, 'ME'),(36, 39, 'ME')]
    }),

    ("Resulta que una vez unas amigas me pidieron que les consiga 6 cartoncitos de acido para ir a bariloche. ", {
            'entities':  [(62, 73, 'DRUG'),(77, 82, 'DRUG'),(93, 102, 'LOC')]
    }),

    ("mal xq no juego máqana ?", {
            'entities':  [(4, 6, 'ME'),(16, 22, 'ME')]
    }),

    ("Y desile ke te saco las chapas", {
            'entities':  [(2, 8, 'ME'),(9, 11, 'ME')]
    }),

    ("no sabes si ahi joda en batan?", {
            'entities':  [(24, 29, 'LOC')]
    }),

    ("Bien el mono ni aparecio y mi marido sigue durmiendo jijiji", {
            'entities':  [(53, 59, 'ME')]
    }),

    ("Jijijiji", {
            'entities':  [(0, 8, 'ME')]
    }),

    ("Decile a tu nico q no anda el celu", {
            'entities':  [(17, 18, 'ME'),(30, 34, 'ME')]
    }),

    ("*No,ni idea pa'!!! Estoy en Mar del Plata desde el Jueves,y no se nada*", {
            'entities':  [(12, 14, 'ME'),(28, 41, 'LOC')]
    }),

    ("Como siempre, lo llamo, quedamos en una esquina cerca de calle santa fe, y encaro en el subte. ", {
            'entities':  [(40, 71, 'MISC')]
    }),

    ("A lo rompiste vos si andava yegua", {
            'entities':  [(21, 27, 'ME')]
    }),

    ("Y como siempre se quiere lavar las manos y quedar como la mejor pero x que estava mama", {
            'entities':  [(69, 70, 'ME'),(75, 81, 'ME')]
    }),

    ("Le compre el chip al dope", {
            'entities':  [(21, 25, 'ME')]
    }),

    ("Jajajajajaja si lo provamos anoche y andava lo mas bien", {
            'entities':  [(0, 12, 'ME'),(19, 27, 'ME'),(37, 43, 'ME')]
    }),

    ("y k haces aka en mdp desd el jueves cm decis?", {
            'entities':  [(2, 3, 'ME'),(10, 13, 'ME'),(17, 20, 'LOC'),(21, 25, 'ME'),(36, 38, 'ME')]
    }),

    ("Cuando llego a la esquina, me pongo a esperar. ", {
            'entities':  [(18, 25, 'MISC')]
    }),

    ("Jijijijiji", {
            'entities':  [(0, 10, 'ME')]
    }),

    ("Hola primo qe hces? =)", {
            'entities':  [(11, 13, 'ME'),(14, 18, 'ME'),(20, 22, 'ME')]
    }),

    ("Enserio perra", {
            'entities':  [(0, 7, 'ME')]
    }),

    ("hola resp cuando kieras noo?", {
            'entities':  [(5, 9, 'ME'),(17, 23, 'ME'),(24, 27, 'ME')]
    }),

    ("Okaty", {
            'entities':  [(0, 5, 'ME')]
    }),

    ("cm se nota k te tiene cortito tuma noo?", {
            'entities':  [(0, 2, 'ME'),(11, 12, 'ME'),(30, 34, 'ME'),(35, 38, 'ME')]
    }),

    ("Yyy como va todo", {
            'entities':  [(0, 3, 'ME')]
    }),

    ("De un momento para otro, caen dos chabones y uno me pregunta si yo era (digamos por aca, aunque mi cuenta no es muy anonima) Pepito. ", {
            'entities':  [(125, 131, 'PER')]
    }),

    ("yo aka en mi ksa acostado ?", {
            'entities':  [(3, 6, 'ME'),(13, 16, 'ME')]
    }),

    ("Quien me tiene cortit", {
            'entities':  [(15, 21, 'ME')]
    }),

    ("Jijiji", {
            'entities':  [(0, 6, 'ME')]
    }),

    ("Qe bien", {
            'entities':  [(0, 2, 'ME')]
    }),

    ("Jajaja na estaba limpiando abajo para mañana", {
            'entities':  [(0, 6, 'ME'),(7, 9, 'ME')]
    }),

    ("X tomi", {
            'entities':  [(0, 1, 'ME')]
    }),

    ("A que celosa la flaca deja esas chicas en paz jijij", {
            'entities':  [(46, 51, 'ME')]
    }),

    ("Mi nombre es Pepito posta, asi que era imposible que pase algo raro, no tenia otra respuesta que no sea, si, soy yo.", {
            'entities':  [(13, 19, 'PER')]
    }),

    ("La voy a casar del cogote", {
            'entities':  [(9, 14, 'ME')]
    }),

    ("Tal cual como el colombiano hacia conmigo, estos pibes me dijeron veni caminemos mientras hacemos la transa. ", {
            'entities':  [(101, 107, 'DRUG')]
    }),

    ("A todo esto el flaco saca un frasquito con banda de merca y me dice aca esta lo tuyo. ", {
            'entities':  [(52, 57, 'DRUG')]
    }),

    ("Yo le digo: no vieja, pero yo queria 6 pepas, no merca. El loco dice uh bueno, guarda el frasquito, pela la billetera, y corta 6 pepas de una marca que nunca habia visto y me las da y me cobra. ", {
            'entities':  [(39, 44, 'DRUG'),(49, 54, 'DRUG'),(129, 134, 'DRUG')]
    }),

    ("Me voy, encaro para el subte con los acidos cuando me llama el colombiano. ", {
            'entities':  [(37, 43, 'DRUG')]
    }),

    ("Y me dice: DONDE ESTAS!!!! y yo le digo pero vos soo loco!! le acabo de comprar a unos flacos que sabian mi nombre, me dijeron que trabajan con vos... ", {
            'entities':  [(49, 52, 'ME')]
    }),

    ("Discutimos un rato y bueno, cuestion, termine comprandole a dos flacos que sabian mi nombre y me querian vender merca.", {
            'entities':  [(112, 117, 'DRUG')]
    }),

    ("Un pepito fue a comprar merca a la misma esquina que este pepito a la misma hora.", {
            'entities':  [(3, 9, 'PER'),(24, 29, 'DRUG'),(41, 48, 'MISC'),(58, 64, 'PER')]
    }),

    ("EDIT: Las pepas eran una pija, segun las minas nunca pegaron. Esto paso en 2010, todavia tengo la duda de que mierda paso.", {
            'entities':  [(10, 15, 'DRUG')]
    }),

    ("CIUDAD DE MÉXICO.- Que la violencia del narcotráfico no entre en las escuelas, o si lo hace, saber cómo actuar.", {
	'entities':  [(0, 16, 'LOC'),(40, 52, 'DRUG'),(69, 77, 'MISC')]
}),

("Ese es el objetivo de la Secretaría de Educación Pública (SEP) de México, que este año distribuirá al inicio del curso escolar un manual con protocolos de actuación en caso de tiroteo o irrupción de un comando en el centro educativo.", {
	'entities':  [(25, 62, 'ORG'),(66, 72, 'LOC')]
}),

("Entre otras cosas, la SEP recomienda a los alumnos: *Recostarse en el piso boca abajo, lejos de puertas y ventanas, así como permanecer en silencio y apagar el celular.", {
	'entities':  [(22, 25, 'ORG')]
}),

("En el año más violento que se vivió en México desde hace dos décadas, hace tiempo que la violencia del crimen organizado no respeta tampoco ni horarios, ni chicos, ni escuelas.", {
	'entities':  [(39, 45, 'LOC')]
}),

("Desde 2010, la SEP había instruido a su personal sobre la forma de actuación ante la violencia, pero por primera vez incluirá a los planteles de bachillerato.", {
	'entities':  [(15, 18, 'ORG')]
}),

("Para los casos de riñas con armas de fuego o el despliegue de un operativo militar o policial en las inmediaciones, se recomienda resguardarse en lugares seguros como aulas, bibliotecas, talleres o laboratorios.", {
	'entities':  [(167, 172, 'MISC'),(174, 185, 'MISC'),(187, 195, 'MISC'),(198, 210, 'MISC')]
}),

("El manual también incluye indicaciones sobre cómo actuar en caso de que haya una persona armada dentro del colegio, sea un alumno, maestro o personal ajeno a la escuela.", {
	'entities':  [(107, 114, 'MISC'),(161, 168, 'MISC')]
}),

("A los docentes y directivos se les pide permanecer dentro de las aulas, ordenar a los estudiantes que se recuesten en el suelo boca abajo, que apaguen las luces del establecimiento y permitan con precaución la entrada de los alumnos que estaban fuera en el momento en que se avisó de la contingencia.", {
	'entities':  [(65, 70, 'MISC')]
}),

("Ante el repunte en la ola de violencia que se vive en todo el país, en otras zonas del país se suman a las recomendaciones por escrito de la SEP los simulacros con policías reales equipados con armas sin balas para enseñar a los alumnos cómo comportarse.", {
	'entities':  [(141, 144, 'ORG')]
}),

("Estos simulacros no son siempre bien vistos por los padres, quienes denuncian que aquellos ejercicios crean alarma entre la comunidad educativa, como sucedió en Baja California Sur en octubre pasado, en una escuela de primaria.", {
	'entities':  [(161, 180, 'LOC'),(207, 214, 'MISC')]
}),

("Según cifras oficiales del Instituto Nacional para la Evaluación de la Educación (INEE), el 13% de los alumnos no se sienten seguros en sus colegios.", {
	'entities':  [(27, 80, 'ORG'),(82, 86, 'ORG')]
}),

("El informe presentado en diciembre por este organismo autónomo señala que el 25% de los docentes presenciaron en el último año la venta o el consumo de drogas y alcohol dentro de las escuelas y el 49% de los directores vieron hurtos y violaciones en las inmediaciones de sus centros.", {
	'entities':  [(152, 158, 'DRUG'),(161, 168, 'DRUG'),(183, 191, 'MISC')]
}),

("El año pasado se convirtió en el más violento en México en las últimas dos décadas, con 23.101 homicidios de enero a noviembre, según datos oficiales difundidos en diciembre pasado.", {
	'entities':  [(49, 55, 'LOC')]
}),

("El número de homicidios se incrementó notablemente desde que a fines de 2006 el gobierno del entonces presidente Felipe Calderón lanzó una controvertida ofensiva militar contra el crimen organizado.", {
	'entities':  [(80, 88, 'MISC'),(113, 128, 'PER')]
}),

("Cerrar la puerta del aula con llave o bloquearla con el escritorio o sillas en caso de un ataque al establecimiento; hacer un pase de lista de los alumnos que se encuentren en el salón", {
	'entities':  [(21, 25, 'MISC')]
}),

("Los gobiernos autoritarios suelen purgar, de tanto en tanto, a sus más altos cuadros políticos.", {
	'entities':  [(4, 13, 'MISC')]
}),

("Nicolás Maduro acaba, con ese marco, de destituir nada menos que a Rafael Ramírez Carreño, quien se desempeñaba desde el año 2014 como embajador de Venezuela ante las Naciones Unidas.", {
	'entities':  [(0, 14, 'PER'),(67, 89, 'PER'),(148, 157, 'LOC'),(167, 182, 'ORG')]
}),

("Lo hizo luego de decapitar, horas antes, a la cúpula de CITGO, la filial norteamericana de PDVSA, por presunta corrupción, pecado calificado de mortal que también ahora se esgrime contra el mencionado Rafael Ramírez, a quien además se acusa de lavado de dinero.", {
	'entities':  [(56, 61, 'ORG'),(91, 96, 'ORG'),(201, 215, 'PER')]
}),

("Ramírez se había desempeñado en el pasado también en lo más alto de petrolera estatal venezolana PDVSA.", {
	'entities':  [(0, 7, 'PER'),(97, 102, 'ORG')]
}),

("De uno de los dirigentes que en su momento estuviera entre los más cercanos a Hugo Chávez.", {
	'entities':  [(78, 89, 'PER')]
}),

("De un ex poderoso vicepresidente de Venezuela.", {
	'entities':  [(36, 45, 'LOC')]
}),

("De una de los cuatro únicos líderes del chavismo que, a fines de 2012, decidieran en La Habana que Nicolás Maduro sería el sucesor en el poder de Hugo Chávez, luego de su muerte.", {
	'entities':  [(85, 94, 'LOC'),(99, 113, 'PER'),(146, 157, 'PER')]
}),

("Si lo destituyen intempestivamente, mientras se encuentre físicamente en los Estados Unidos, Ramírez podría hasta perder su inmunidad diplomática y ser inmediatamente detenido por las autoridades locales con relación a sus probables vinculaciones con la corrupción y el narcotráfico.", {
	'entities':  [(77, 91, 'LOC'),(93, 100, 'PER'),(270, 282, 'DRUG')]
}),

("Se estima Ramírez que podría de pronto haber *desviado* en su favor una cifra impactante: nada menos que unos 11 billones de dólares originados en PDVSA.", {
	'entities':  [(10, 17, 'PER'),(147, 152, 'ORG')]
}),

("En las últimas semanas, a manera de anuncio de sus disidencias, Rafael Ramírez había de pronto publicado notas sumamente críticas acerca de la situación económica de su país, contra lo que el gobierno de Nicolás Mauro reaccionó airadamente desde las redes sociales.", {
	'entities':  [(64, 78, 'PER'),(204, 217, 'PER')]
}),

("Aparentemente, la purga dispuesta por Nicolás Maduro, que coincide con la repentina militarización del sector petrolero venezolano, es una señal más de la profunda división que se habría producido en lo más alto del chavismo.", {
	'entities':  [(38, 52, 'PER')]
}),

("Esto sucede, claro está, en momentos en los que el perimido *modelo* económico mismo del chavismo, el colectivista, ha sumido a Venezuela en la pobreza y destruido el que alguna vez fuera un elevado -y envidiado- nivel de vida de su pueblo.", {
	'entities':  [(128, 137, 'LOC')]
}),

("Pese a todo, Nicolás Maduro buscará seguramente obtener un segundo mandato presidencial en los comicios nacionales previstos para diciembre de 2018, que podrían de pronto adelantarse.", {
	'entities':  [(13, 27, 'PER')]
}),

("Alan Funes cruzó hace pocos meses el umbral de la mayoría de edad, con varios crímenes sobre su espalda.", {
	'entities':  [(0, 10, 'PER')]
}),

("Y se transformó durante los últimos días en el delincuente más buscado de Rosario, desde que arrancó un 2018 sangriento en esta ciudad, con 14 asesinatos en la primera quincena, varios originados por enfrentamientos entre dos nuevos clanes vinculados con la venta de drogas que juran exterminarse por las redes sociales y lo cumplen en las calles.", {
	'entities':  [(74, 81, 'LOC')]
}),

("A muy temprana edad, Alan, hijo de Jorge, un veterano pirata del asfalto que fue blanco de un ataque a balazos el 1° de enero, se transformó junto con su hermano Lautaro, de 20 años, en asesinos en potencia, con una sed de venganza incontenible, luego de que los Caminos mataran a su madre.", {
	'entities':  [(21, 25, 'PER'),(35, 40, 'PER'),(162, 169, 'PER')]
}),

("Disparó una ráfaga de 15 tiros al aire con una ametralladora FMK3 mientras estaba con prisión domiciliaria en la casa de su abuela en el sur de Rosario.", {
	'entities':  [(113, 117, 'MISC'),(144, 151, 'LOC')]
}),

("El 1° de mayo de 2016, Alan, en ese momento de 17 años, entró al pasillo de casas precarias de Ayacucho al 4300, apuntó su mirada y la pistola 9 milímetros contra Julio Solano, conocido como Pupi, y lo acribilló.", {
	'entities':  [(23, 27, 'PER'),(95, 111, 'LOC'),(163, 175, 'PER'),(191, 195, 'PER')]
}),

("Unos meses después, el muchacho fue detenido y enviado al Instituto de Rehabilitación del Adolescente (IRAR), y la causa judicial tuvo varias idas y venidas en el Juzgado de Menores N° 3 con recurrentes pedidos de nulidades de sus abogados hasta que acordaron con la fiscalía en octubre pasado que fuera enviado a la casa de su abuela en el barrio La Tablada.", {
	'entities':  [(58, 101, 'ORG'),(103, 107, 'ORG'),(163, 186, 'ORG'),(267, 275, 'MISC'),(317, 321, 'MISC'),(341, 358, 'LOC')]
}),

("Alexis Caminos, contemporáneo y principal enemigo de Alan y Lautaro, fue acusado por el asesinato de la madre de los Funes y de Claudio Fernández, a quien mataron de 11 disparos en el barrio Municipal.", {
	'entities':  [(0, 14, 'PER'),(53, 57, 'PER'),(60, 67, 'PER'),(117, 122, 'PER'),(128, 145, 'PER'),(184, 200, 'LOC')]
}),

("Alexis era menor cuando cometió el crimen.", {
	'entities':  [(0, 6, 'PER')]
}),

("El Juzgado de Menores enfrentó varias nulidades del abogado Marcos Cella -quien estuvo preso, como partícipe secundario de un asesinato- hasta que la Cámara Penal confirmó el procesamiento de Alexis recién en marzo de 2016.", {
	'entities':  [(3, 21, 'MISC'),(60, 72, 'PER'),(150, 162, 'MISC'),(192, 198, 'PER')]
}),

("Actualmente está preso en la cárcel de Coronda.", {
	'entities':  [(29, 35, 'MISC'),(39, 46, 'LOC')]
}),

("En 2013, la amistad entre las familias Funes y Caminos, que desde hace tiempo habían cultivado Jorge Funes y Roberto Caminos, alias Pimpi, histórico líder de la barra de Newell's, y aliado de la banda de Los Monos, se rompió con la generación siguiente, la de sus hijos, que se habían criado juntos en las torres de Fonavi del barrio Municipal, en la zona sur de Rosario.", {
	'entities':  [(39, 44, 'PER'),(47, 54, 'PER'),(95, 106, 'PER'),(109, 124, 'PER'),(132, 137, 'PER'),(170, 178, 'ORG'),(192, 213, 'ORG'),(306, 343, 'LOC'),(351, 370, 'LOC')]
}),

("*El problema con los Caminos empezó en 2012 y 2013.", {
	'entities':  [(21, 28, 'PER')]
}),

("Mis hermanos Alan y Ulises iban a la escuela.", {
	'entities':  [(13, 17, 'PER'),(20, 26, 'PER'),(37, 44, 'MISC')]
}),

("Para llegar tenían que pasar por el barrio Municipal.", {
	'entities':  [(36, 52, 'LOC')]
}),

("En ese barrio, la familia Caminos controlaba todo lo que pasaba.", {
	'entities':  [(26, 33, 'PER')]
}),

("Ellos querían que mis hermanos sean sus sicarios y empiecen a matar gente para ellos*, declaró Lautaro en la causa del crimen de Maximiliano Nota, según publicó el portal Cruz del Sur.", {
	'entities':  [(129, 145, 'PER'),(171, 183, 'LOC')]
}),

("El domingo pasado, Marcela Díaz, hermana de Tubi Segovia, aliado del clan Caminos, fue asesinada desde una camioneta VW Suran mientras se desplazaba en moto con un amigo, quien confesó a la policía que en el vehículo desde el cual los atacaron estaba Alan Funes, quien había anticipado que pretendía vengar la muerte de su hermano Ulises.", {
	'entities':  [(19, 31, 'PER'),(44, 56, 'PER'),(74, 81, 'PER'),(117, 119, 'ORG'),(251, 261, 'PER'),(331, 337, 'PER')]
}),

("Los Funes les habían advertido que se tenía que ir de Rosario porque la iban a matar, contó ayer la abogada de la víctima, Romina Bedetti.", {
	'entities':  [(4, 9, 'PER'),(54, 61, 'LOC'),(123, 137, 'PER')]
}),

("Alan Funes exhibió en un video una ametralladora FMK3, utilizada por unidades menores de diferentes cuerpos policiales y una de las armas preferidas de los narcos rosarinos", {
	'entities':  [(0, 10, 'PER'),(156, 162, 'DRUG')]
}),

("Alan Funes festeja el Año Nuevo con disparos de ametralladora; el joven de 18 años estaba en prisión domiciliaria por un homicidio cometido cuando era menor.", {
	'entities':  [(0, 10, 'PER')]
}),

("Jorge Funes, padre de Alan, fue baleado en la localidad santafecina de Alvear", {
	'entities':  [(0, 11, 'PER'),(22, 26, 'PER'),(71, 77, 'LOC')]
}),

("Tras difundirse un video con los disparos efectuados por Alan, la Justicia decidió enviarlo a la cárcel; se escapó antes de la llegada de la policía", {
	'entities':  [(57, 61, 'PER'),(97, 103, 'MISC')]
}),

("Fue asesinado Ulises Funes, hermano de Alan", {
	'entities':  [(14, 26, 'PER'),(39, 43, 'PER')]
}),

("Alan Funes promete matar *a todas las generaciones* del clan Caminos.", {
	'entities':  [(0, 10, 'PER'),(61, 68, 'PER')]
}),

("Lautaro Funes, hermano de Alan y preso por homicidio, también anticipa una venganza", {
	'entities':  [(0, 13, 'PER'),(26, 30, 'PER')]
}),

("Fue asesinada Marcela Díaz, hermana de Ariel Segovia, integrante del clan Caminos", {
	'entities':  [(14, 26, 'PER'),(39, 52, 'PER'),(74, 81, 'PER')]
}),

("Fue asesinado Leandro Rafatti, cuñado de Marcela Díaz", {
	'entities':  [(14, 29, 'PER'),(41, 53, 'PER')]
}),

("ROSARIO.- El cuerpo apareció flotando en el río Paraná, a la altura de Granadero Baigorria, ciudad vecina a Rosario , envuelto en una sábana, como si fuera una mortaja, y en el cráneo tenía rastros de haber muerto de un disparo.", {
	'entities':  [(0, 7, 'LOC'),(44, 54, 'LOC'),(71, 90, 'LOC'),(91, 98, 'MISC'),(108, 115, 'LOC')]
}),

("Su nombre era Maciel Amantino Wagner, un brasileño de 45 años que estaba prófugo desde 2014 en Ciudad del Este, Paraguay, y que había sido un miembro importante de la organización brasileña Primer Comando Capital (PCC).", {
	'entities':  [(14, 36, 'PER'),(95, 110, 'LOC'),(112, 120, 'LOC'),(190, 212, 'ORG'),(214, 217, 'ORG')]
}),

("Durante las últimas horas, según informaron a LA NACION desde la fiscalía de Rosario, familiares de Wagner arribaron a esta ciudad desde Paraguay para reconocer el cuerpo.", {
	'entities':  [(46, 55, 'ORG'),(65, 73, 'MISC'),(77, 84, 'LOC'),(100, 106, 'PER'),(137, 145, 'LOC')]
}),

("Llamó la atención a los funcionarios del Ministerio Público de la Acusación cómo se enteraron de que era Wagner quien había aparecido el 7 de noviembre pasado muerto, con un disparo en la cabeza, flotando en el río Paraná.", {
	'entities':  [(41, 75, 'ORG'),(105, 112, 'PER'),(211, 221, 'LOC')]
}),

("Se estima que el crimen se produjo entre la 1 y las 3 del 7 de noviembre, en las inmediaciones de una guardería náutica en Granadero Baigorria.", {
	'entities':  [(102, 119, 'MISC'),(123, 142, 'LOC')]
}),

("Los parientes del hombre asesinado dijeron que Wagner había arribado hacía pocos días a Rosario para realizar inversiones inmobiliarias.", {
	'entities':  [(47, 53, 'PER'),(88, 95, 'LOC')]
}),

("No hay pistas certeras sobre quién asesinó al miembro del Primer Comando Capital.", {
	'entities':  [(58, 80, 'ORG')]
}),

("¿Qué hacía en Rosario un prófugo vinculado a una de las organizaciones narcocriminales más importantes de América del Sur?", {
	'entities':  [(14, 21, 'LOC'),(71, 86, 'DRUG'),(106, 121, 'LOC')]
}),

("En agosto de 2014, la policía paraguaya difundió fotos y un listado de diez nombres de miembros del PCC que habían financiado y planeado un robo espectacular a la bóveda de la empresa Prosegur en Ciudad del Este.", {
	'entities':  [(100, 103, 'ORG'),(163, 169, 'MISC'),(176, 183, 'MISC'),(184, 192, 'ORG'),(196, 211, 'LOC')]
}),

("Wagner, conocido como Juninho, junto a otros integrantes de la organización que nació en San Pablo en 1993 en la prisión de Piranhao, en San Pablo, planificó el robo a través de un túnel de más de 350 metros, desde la casa de un abogado, que terminaba en la bóveda de Prosegur, donde estaban guardados en ese momento US$ 100.000.000.", {
	'entities':  [(0, 6, 'PER'),(22, 29, 'PER'),(89, 98, 'LOC'),(113, 120, 'MISC'),(124, 132, 'LOC'),(137, 146, 'LOC'),(218, 222, 'MISC'),(268, 276, 'ORG')]
}),

("El líder de este grupo era José Francisco da Silva, quien alquiló la casa donde se inició el túnel el 12 de noviembre del 2013.", {
	'entities':  [(27, 50, 'PER'),(69, 73, 'MISC')]
}),

("Los diez miembros del grupo nunca fueron atrapados, aunque la policía paraguaya descubrió el plan para ingresar en la empresa a través del túnel que construyeron durante más de ocho meses.", {
	'entities':  [(118, 125, 'MISC')]
}),

("El golpe a Prosegur en 2014 terminó en un fracaso.", {
	'entities':  [(11, 19, 'ORG')]
}),

("Pero en abril pasado un comando del PCC logró concretarlo en un asalto fulminante a la sede de la empresa en Ciudad del Este, donde tras un espectacular ataque con explosivos y armas largas los ladrones lograron llevarse unos US$ 8.000.000.", {
	'entities':  [(36, 39, 'ORG'),(98, 105, 'MISC'),(109, 124, 'LOC')]
}),

("En junio pasado, efectivos de Gendarmería Nacional detuvieron en Ituzaingó, Corrientes, a Néstor Palma, de 43 años, acusado de ser uno de los financistas del PCC, organización narcocriminal que en abril pasado se atribuyó el ataque a la empresa de caudales Prosegur de Ciudad del Este.", {
	'entities':  [(30, 50, 'ORG'),(65, 74, 'LOC'),(76, 86, 'LOC'),(90, 102, 'PER'),(158, 161, 'ORG'),(176, 189, 'DRUG'),(257, 265, 'ORG'),(269, 284, 'LOC')]
}),

("El operativo en el que apresaron a Palma fue concretado por efectivos de los escuadrones 47 y 50 de la Gendarmería Nacional, tras un trabajo de inteligencia de las unidades que operan en Misiones y Corrientes.", {
	'entities':  [(35, 40, 'PER'),(103, 123, 'ORG'),(187, 195, 'LOC'),(198, 208, 'LOC')]
}),

("Palma está imputado en una causa por la justicia nacional de Paraguay, acusado de haber asesinado a un efectivo de la Policía Nacional de ese país, y también es señalado como responsable de la planificación del asalto en el que unos 30 hombres atacaron con explosivos la entidad financiera internacional de la ciudad fronteriza del norte paraguayo.", {
	'entities':  [(0, 5, 'PER'),(61, 69, 'LOC'),(118, 134, 'ORG'),(310, 347, 'LOC')]
}),

("El financista estaba alojado en una hostería de Ituzaingó.", {
	'entities':  [(48, 57, 'LOC')]
}),

("Llegó a la Argentina desde mediados de abril pasado cuando ingresó en forma clandestina para viajar a la provincia de Buenos Aires.", {
	'entities':  [(11, 20, 'LOC'),(118, 130, 'LOC')]
}),

("Durante las primeras semanas de mayo, Palma habría estado en Buenos Aires, donde los grupos de inteligencia de la Gendarmería lo detectaron, pero aguardaron a que se presentaran las condiciones propicias para atraparlo.", {
	'entities':  [(38, 43, 'PER'),(61, 73, 'LOC'),(114, 125, 'ORG')]
}),

("Durante los últimos días de mayo circuló la información de que había salido de territorio bonaerense con destino a Corrientes, con la clara intención de permanecer en una zona poco poblada, para planificar su vuelta a tierra paraguaya.", {
	'entities':  [(115, 125, 'LOC')]
}),

("En esos días todas las fuerzas de seguridad desplegadas en ese lugar fueron alertadas de la presencia del sospechoso financista del PCC, por lo que se intensificaron los controles en las vías de tránsito terrestre.", {
	'entities':  [(132, 135, 'ORG')]
}),

("En Corrientes y Misiones, provincias fronterizas con Paraguay y Brasil, aparecen desde hace un tiempo lo que los investigadores llaman *lobos solitarios* ligados al PCC y a otra organización brasileña de peso como es el Comando Vermelho.", {
	'entities':  [(3, 13, 'LOC'),(16, 24, 'LOC'),(53, 61, 'LOC'),(64, 70, 'LOC'),(165, 168, 'ORG'),(220, 236, 'ORG')]
}),

("Las rutas por las que se mueven son la 12, que va desde Corrientes hasta Puerto Iguazú, y la 11, que llega hasta el límite con Paraguay, y la 86, que llega bordeando el límite con Paraguay hasta el norte argentino.", {
	'entities':  [(56, 66, 'LOC'),(73, 86, 'LOC'),(127, 135, 'LOC'),(180, 188, 'LOC'),(198, 213, 'LOC')]
}),

("Por allí, según las fuentes, se traslada cocaína que tiene como destino Brasil.", {
	'entities':  [(72, 78, 'LOC')]
}),

("Impostaba la voz y repetía las frases más conocidas de Pablo Escobar Gaviria, el líder del desaparecido cartel de Medellín.", {
	'entities':  [(55, 76, 'PER'),(114, 122, 'LOC')]
}),

("En un brazo y en una pierna tenía tatuados el rostro del capo narco colombiano y la entrada a la Hacienda Nápoles, el lugar donde el fallecido delincuente pasaba sus días de descanso.", {
	'entities':  [(62, 67, 'DRUG'),(97, 113, 'LOC')]
}),

("Se hacía llamar *el Patrón*, pero en la zona oeste del conurbano, a Héctor Peruchena todos lo conocían como *Gordo Chon*.", {
	'entities':  [(40, 64, 'LOC'),(68, 84, 'PER'),(109, 119, 'PER')]
}),

("En las últimas horas fue detenido por la policía bonaerense acusado de liderar una banda que fraccionaba droga y la vendía al menudeo en el partido de Merlo.", {
	'entities':  [(151, 156, 'LOC')]
}),

("Así lo informaron a LA NACION calificadas fuentes policiales y judiciales.", {
	'entities':  [(20, 29, 'ORG')]
}),

("Le rendía culto a Escobar Gaviria, era su modelo a seguir.", {
	'entities':  [(18, 33, 'PER')]
}),

    ("Era tan fanático de él que se recortó el bigote como el capo narco*, afirmó un detective que participó de la investigación.", {
	'entities':  [(61, 66, 'DRUG')]
}),

("*Hay escuchas telefónicas en las que el principal sospechoso hablaba e impostaba la voz como Escobar Gaviria*, explicaron.", {
	'entities':  [(93, 108, 'PER')]
}),

("El detenido tenía grabada en un brazo la imagen del fallecido jefe del cartel de Medellín y en una pierna, la entrada de la hacienda de ese narco colombiano", {
	'entities':  [(81, 89, 'LOC'),(124, 132, 'MISC'),(140, 145, 'DRUG')]
}),

("El escondite donde fue atrapado Alan Funes, el joven de 19 años que estaba prófugo, era un departamento de dos ambientes, enclavado en el barrio Itatí, en el sur de Rosario, donde vive su novia, Jorgelina Selerpe, nieta de Jorge, un histórico narco de Rosario que fue asesinado en febrero de 2010 a cinco cuadras de allí, tras instalar una de las primeras cocinas de cocaína en Rosario.", {
	'entities':  [(32, 42, 'PER'),(91, 103, 'MISC'),(138, 150, 'LOC'),(165, 172, 'LOC'),(195, 212, 'PER'),(223, 228, 'PER'),(243, 248, 'DRUG'),(251, 259, 'LOC'),(367, 374, 'DRUG'),(378, 385, 'LOC')]
}),

("Los efectivos de Gendarmería y la policía sorprendieron al amanecer a Alan durmiendo con su pareja, y lejos de la pistola calibre 9 mm que escondía debajo del bidet.", {
	'entities':  [(17, 28, 'ORG'),(70, 74, 'PER')]
}),

("La imagen se viralizó por las redes sociales y su historia también, en un contexto de recrudecimiento de la violencia en Rosario, donde en 15 días se produjeron 14 homicidios, muchos de ellos relacionados con una pelea territorial de la banda que lidera Alan y su hermano Lautaro Funes, alias *Lamparita*, con el clan Caminos, que gobernó históricamente la barra brava de Newell's.", {
	'entities':  [(121, 128, 'LOC'),(254, 258, 'PER'),(272, 285, 'PER'),(294, 303, 'PER'),(313, 325, 'ORG'),(372, 380, 'ORG')]
}),

("En este encadenamiento de homicidios que volvió a sacudir a Rosario los protagonistas son la segunda o tercera generación de personas nacidas y criadas en un territorio atravesado por la violencia.", {
	'entities':  [(60, 67, 'LOC')]
}),

("Alan vivía en la clandestinidad desde hacía 15 días.", {
	'entities':  [(0, 4, 'PER')]
}),

("Se movilizaba en un Audi, y se mostraba con una ametralladora, y esas imágenes no iban dirigidas a los periodistas, sino a sus enemigos, a quienes les señalaba por las redes sociales el poder de fuego que tenía.", {
	'entities':  [(20, 24, 'ORG')]
}),

("En las próximas horas, Alan y su novia, Jorgelina Selerpe, alias *Chipi*, serán imputados del asesinato de Marcela Díaz, hermana de Ariel Segovia, quien está sindicado como autor intelectual de tres asesinatos en el contexto de la guerra entre los dos clanes en los barrios La Tablada, Municipal y República de la Sexta.", {
	'entities':  [(23, 27, 'PER'),(40, 57, 'PER'),(66, 71, 'PER'),(107, 119, 'PER'),(132, 145, 'PER'),(274, 284, 'LOC'),(286, 295, 'LOC'),(298, 319, 'LOC')]
}),

("Ulises, uno de los hermanos de Alan, fue asesinado el 7 de enero pasado por dos sicarios que le dispararon desde un automóvil.", {
	'entities':  [(0, 6, 'PER'),(31, 35, 'PER')]
}),

("Alan y su hermano Lautaro juraron *matar a todas las generaciones de los Camino*.", {
	'entities':  [(0, 4, 'PER'),(18, 25, 'PER'),(69, 79, 'ORG')]
}),

("Las amenazas por Facebook de los Funes se cumplían en las calles.", {
	'entities':  [(17, 25, 'ORG'),(33, 38, 'PER')]
}),

("Al principio el gobierno de Santa Fe le trató de restar gravedad al problema, pero se empezó a preocupar al incrementarse los homicidios.", {
	'entities':  [(28, 36, 'LOC')]
}),

("El ministro de Seguridad de Santa Fe, Maximiliano Pullaro, se reunió con sus pares de la Nación para buscar estrategias para tratar de apaciguar la violencia.", {
	'entities':  [(28, 36, 'LOC'),(38, 57, 'PER'),(86, 95, 'ORG')]
}),

("La ministra de Seguridad, Patricia Bullrich, recibirá hoy al gobernador Miguel Lifschitz.", {
	'entities':  [(26, 43, 'PER'),(72, 88, 'PER')]
}),

("El detenido Alan es hijo de Jorge Funes, quien fue baleado el 1° de enero pasado en la localidad de Alvear, a 20 kilómetros de Rosario.", {
	'entities':  [(12, 16, 'PER'),(28, 39, 'PER'),(100, 106, 'LOC'),(126, 134, 'LOC')]
}),

("Este hombre es un veterano pirata del asfalto que se refugió en ese pueblo para eludir la batalla que protagonizaban sus hijos contra el clan liderado por Alexis Camino, preso en la cárcel de Coronda, hijo de Roberto, alias *Pimpi*, histórico líder de la barra brava de Newell's y amigo del padre de Alan, quien también tenía peso en esa hinchada.", {
	'entities':  [(155, 168, 'PER'),(182, 188, 'MISC'),(192, 199, 'LOC'),(209, 216, 'PER'),(225, 230, 'PER'),(270, 278, 'ORG'),(300, 304, 'PER')]
}),

("Jorgelina, pareja de Alan, es la nieta de Jorge Selerpe, asesinado en febrero de 2010.", {
	'entities':  [(0, 9, 'PER'),(21, 25, 'PER'),(42, 55, 'PER')]
}),

("Fue uno de los precursores de las cocinas de cocaína en Rosario, donde fue detenido en 2008 por la Policía de Seguridad Aeroportuaria (PSA) en un laboratorio en la zona sur donde tenían capacidad para producir 50 kilos de cocaína al mes, que tenían como destino el mercado europeo.", {
	'entities':  [(45, 52, 'DRUG'),(56, 63, 'LOC'),(99, 139, 'ORG'),(146, 157, 'MISC'),(222, 229, 'DRUG'),(265, 280, 'MISC')]
}),

("La detención de la pareja se produjo en medio de un megaoperativo conjunto de las fuerzas federales y de la policía de Santa Fe, que rodearon el edificio de Callao al 3900 para atrapar a Funes y Selerpe.", {
	'entities':  [(119, 127, 'LOC'),(145, 171, 'MISC'),(187, 192, 'PER'),(195, 202, 'PER')]
}),

("El ministro Pullaro contó a la prensa que los efectivos trazaron como estrategia detenerlo por la mañana, porque querían evitar un enfrentamiento: *El arresto se produjo en las primeras horas de la mañana porque entendíamos que la nocturnidad podía beneficiar a este delincuente.", {
	'entities':  [(12, 19, 'PER')]
}),

("Una banda narco integrada por ciudadanos peruanos fue desmantelada por la policía de Buenos Aires tras varios allanamientos realizados en el barrio porteño de Chacarita y en el partido bonaerense de San Martín.", {
	'entities':  [(10, 15, 'DRUG'),(85, 97, 'LOC'),(159, 168, 'LOC'),(199, 209, 'LOC')]
}),

("En esos operativos fueron decomisados 10 kilos de cocaína.", {
	'entities':  [(50, 57, 'DRUG')]
}),

("Los procedimientos fueron coordinados por efectivos de la Superintendencia de Investigaciones del Tráfico de Drogas Ilícitas y Crimen Organizado, delegación Zárate-Campana.", {
	'entities':  [(58, 144, 'ORG'),(109, 115, 'DRUG'),(157, 171, 'LOC')]
}),

("Según informó la policía bonaerense, esa organización criminal acopiaba y distribuía las drogas en distintos barrios de la ciudad de Buenos Aires, además de tener contactos con vendedores minoristas en el conurbano y localidades del interior bonaerense.", {
	'entities':  [(123, 145, 'LOC'),(205, 214, 'LOC'),(233, 252, 'LOC')]
}),

("En el caso interviene el Juzgado de Primera Instancia de Campana, a cargo de Adrián González Charvay.", {
	'entities':  [(25, 64, 'ORG'),(57, 64, 'LOC'),(77, 100, 'PER')]
}),

("En tanto, otras dos personas fueron arrestadas por personal de la Gendarmería al detectarse el transporte de algo más de cuatro kilos de cocaína.", {
	'entities':  [(66, 77, 'ORG'),(137, 144, 'DRUG')]
}),

("Ese procedimiento fue realizado en Salta por efectivos del Escuadrón 20 Orán, que efectuaba tareas de patrullaje en el paso fronterizo no habilitado denominado Los Gomones.", {
	'entities':  [(35, 40, 'LOC'),(59, 76, 'ORG'),(160, 171, 'LOC')]
}),

("Al verificarse los equipajes fueron encontrados 25 paquetes que contenían una *sustancia blanca*, la cual al ser sometida a las pruebas de campo narcotest, arrojaron resultado positivo para cocaína.", {
	'entities':  [(79, 95, 'DRUG'),(145, 154, 'DRUG'),(190, 197, 'DRUG')]
}),

("Un total de 4,345 kilos de esa droga fue decomisado en ese procedimiento y quedaron arrestados los dos sospechosos.", {
	'entities':  [(31, 36, 'DRUG')]
}),

("Pero en la única habitación del departamento 1 de Arribeños 2731, en Belgrano, no había ninguna cama.", {
	'entities':  [(17, 46, 'MISC'),(50, 64, 'LOC'),(69, 77, 'LOC')]
}),

("Nadie dormía en la vivienda.", {
	'entities':  [(19, 27, 'MISC')]
}),

("A los habitantes de las dos otras unidades funcionales nada les había llamado la atención hasta hoy a la madrugada, cuando se sorprendieron con la irrupción de personal de la Policía Federal Argentina (PFA), que descubrió un centro de acopio y distribución de pastillas de efedrina.", {
	'entities':  [(175, 206, 'ORG'),(260, 281, 'DRUG')]
}),

("Así lo informó el jefe de la PFA, comisario general Néstor Roncaglia, en una conferencia de prensa.", {
	'entities':  [(29, 32, 'ORG'),(52, 68, 'PER')]
}),

("En el departamento 1 de Arribeños 2731 los detectives policiales secuestraron 41.000 pastillas de una sustancia hecha a base de efedrina, que se sospecha llegaban a la Argentinas desde Paraguay por medio de encomiendas.", {
	'entities':  [(6, 20, 'MISC'),(24, 38, 'LOC'),(85, 94, 'DRUG'),(102, 111, 'DRUG'),(128, 136, 'DRUG'),(168, 178, 'LOC'),(185, 193, 'LOC')]
}),

("Además, hubo otros 11 allanamientos, entre ellos en un local comercial de la ciudad pueblo Nordelta, en Tigre.", {
	'entities':  [(55, 70, 'MISC'),(91, 99, 'LOC'),(104, 109, 'LOC')]
}),

("En los 12 procedimientos, ordenados por el juez federal Marcelo Martínez de Giorgi, se detuvo a seis sospechosos", {
	'entities':  [(56, 82, 'PER')]
}),

("Entre los detenidos hay un ciudadano español que ya había estado imputado en una causa de narcotráfico cuando la PFA descubrió un laboratorio de drogas sintéticas en un departamento de Viamonte al 800, en pleno centro porteño.", {
	'entities':  [(90, 102, 'DRUG'),(113, 116, 'ORG'),(130, 141, 'MISC'),(145, 162, 'DRUG'),(169, 181, 'MISC'),(185, 200, 'LOC'),(211, 225, 'LOC')]
}),

("Se trata de Francisco Ribas Rocher y que había sido sobreseído porque las pastillas secuestradas en dicha vivienda el 26 de septiembre de 2013, que en principio se pensaron que eran de éxtasis, pero el peritaje determinó que en realidad era metilona, que en esa época no figuraba en la lista de sustancias prohibidas de la ley de drogas.", {
	'entities':  [(12, 34, 'PER'),(74, 83, 'DRUG'),(106, 114, 'MISC'),(185, 192, 'DRUG'),(241, 249, 'DRUG'),(295, 316, 'DRUG'),(330, 336, 'DRUG')]
}),

("Según explicó Roncaglia, Ribas Rocher era parte de la banda desbaratada en las últimas horas.*Desarticulamos y detuvimos a los miembros de una organización narco criminal dedicada a la venta de drogas de síntesis como la efedrina, la metanfetamina, la metacualona y el metinol*, sostuvo el jefe de la PFA.", {
	'entities':  [(14, 23, 'PER'),(25, 37, 'PER'),(156, 161, 'DRUG'),(194, 212, 'DRUG'),(221, 229, 'DRUG'),(234, 247, 'DRUG'),(252, 263, 'DRUG'),(269, 276, 'DRUG'),(301, 304, 'ORG')]
}),

("En la investigación participó la Procuraduría de Narcocriminalidad (Procunar), a cargo del fiscal federal Diego Iglesias.", {
	'entities':  [(33, 77, 'ORG'),(106, 120, 'ORG')]
}),

("*Muchas de las sustancias que incautamos en el día de hoy, especialmente la efedrina, sirven de precursor para la metanfetamina*, sostuvo Martín Verrier, subsecretario de Lucha contra el Narcotráfico del Ministerio de Seguridad.", {
	'entities':  [(15, 25, 'DRUG'),(76, 84, 'DRUG'),(114, 127, 'DRUG'),(138, 152, 'PER'),(187, 199, 'DRUG'),(204, 227, 'ORG')]
}),

("El funcionario agregó:*Este tipo de droga puede generar problemas cardíacos, una súbita suba de la temperatura en el cuerpo humano y fallas tanto renales como hepáticas*.", {
	'entities':  [(36, 41, 'DRUG')]
}),

("La ministra de Seguridad, Patricia Bullrich , aseguró que sigue de cerca los casos de violencia narco en la región para evitar su repetición en la Argentina.", {
	'entities':  [(26, 43, 'PER'),(96, 101, 'DRUG'),(147, 156, 'LOC')]
}),

("Si bien las luchas entre clanes narco se dirimen aquí en sangrientos ajustes de cuentas, las autoridades esperan que esos enfrentamientos no lleguen a los niveles que actualmente se visualizan en Brasil y Colombia.", {
	'entities':  [(32, 37, 'DRUG'),(196, 202, 'LOC'),(205, 213, 'LOC')]
}),

("*En Colombia hubo dos ataques que sufrió la policía por bandas de narcotraficantes, lo mismo en Brasil*, ejemplificó la ministra, quien añadió: *Por eso nosotros estamos muy atentos a que en nuestro país podamos seguir dando lucha contra el narcotráfico sin que eso implique aumento de la violencia*.", {
	'entities':  [(4, 12, 'LOC'),(66, 82, 'DRUG'),(96, 102, 'LOC'),(241, 253, 'DRUG')]
}),

("Bullrich destacó, además, que en el primer mes de 2018 se registraron mejores resultados en operativos antidrogas que en los primeros 30 días del año pasado.", {
	'entities':  [(0, 8, 'PER')]
}),

("Este mes ha sido un redoblar el esfuerzo en la lucha contra el narcotráfico*, sostuvo Bullrich en una conferencia de prensa realizada ayer en el Olivos Golf Club.", {
	'entities':  [(63, 75, 'DRUG'),(86, 94, 'PER'),(145, 161, 'ORG')]
}),

("La funcionaria expuso detalles del operativo que derivó el viernes pasado en la desarticulación de una banda que operaba en ese tradicional country.", {
	'entities':  [(140, 147, 'MISC')]
}),

("Ese procedimiento culminó con la detención de seis personas acusadas de integrar una red de laboratorios narco en la zona metropolitana.", {
	'entities':  [(92, 104, 'MISC'),(105, 110, 'DRUG'),(117, 135, 'LOC')]
}),

("El presunto líder alquilaba dos propiedades en el Olivos Golf Club, mientras que la preparación de la cocaína estaba en manos de químicos colombianos.", {
	'entities':  [(32, 43, 'MISC'),(50, 66, 'ORG'),(102, 109, 'DRUG')]
}),

("*Esta fue una operación de enorme importancia para nuestro país porque en esta casa alquilada funcionaba un laboratorio de mejoramiento de la calidad de la cocaína para hacer rendir más el producto*, aseguró Bullrich, según consignó la agencia Télam.", {
	'entities':  [(108, 119, 'MISC'),(156, 163, 'DRUG'),(208, 216, 'PER'),(244, 249, 'ORG')]
}),

("*Hay un elemento que utilizan en la industria de la alimentación, el sorbato de potasio, que se encontró en un operativo en España en 2014.", {
	'entities':  [(69, 87, 'DRUG'),(124, 130, 'LOC')]
}),

("Esto sirve para perfeccionar la calidad del producto y así responder al público que tiene esta demanda*, precisó el jefe de la Gendarmería, comandante general Gerardo Otero.", {
	'entities':  [(126, 138, 'ORG'),(159, 172, 'PER')]
}),

("La técnica utilizada por ese grupo narco obtenía un 20% más de rendimiento en cada kilo de cocaína, sin disminuir demasiado la calidad de ese producto ilegal.", {
	'entities':  [(35, 40, 'DRUG'),(91, 98, 'DRUG')]
}),

("Para desbaratar esa organización criminal se efectuaron, además, allanamientos en los barrios de Belgrano, Palermo y Villa del Parque, y en la localidad bonaerense de Villa Luzuriaga, partido de La Matanza.", {
	'entities':  [(86, 93, 'MISC'),(86, 93, 'MISC'),(97, 105, 'LOC'),(107, 114, 'LOC'),(117, 133, 'LOC'),(167, 182, 'LOC'),(184, 205, 'LOC')]
}),

("El procedimiento estuvo a cargo juez federal de Lomas de Zamora, Federico Villena, y la investigación de la Gendarmería contó con la colaboración de la oficina antidrogas de los estados Unidos (DEA, en su sigla en inglés) y la Agencia Federal de Inteligencia (AFI).", {
	'entities':  [(48, 63, 'LOC'),(65, 81, 'PER'),(108, 119, 'ORG'),(152, 192, 'ORG'),(194, 197, 'ORG'),(227, 264, 'ORG')]
}),

("ROSARIO.- Un megaoperativo de la Policía Federal se realizó desde la madrugada de anteayer en el barrio Las Flores, la zona que dominan Los Monos en Rosario.", {
	'entities':  [(0, 7, 'LOC'),(0, 7, 'ORG'),(33, 48, 'ORG'),(97, 114, 'LOC'),(136, 145, 'ORG'),(149, 156, 'LOC')]
}),

("Un centenar de efectivos de esta fuerza llevaron adelante 28 allanamientos por una seguidilla de homicidios que se produjeron entre junio y julio pasado luego de que fuera asesinada Petrona Cantero, la hermana de Ariel, histórico líder de la organización narcocriminal.", {
	'entities':  [(182, 197, 'PER'),(182, 197, 'PER'),(213, 218, 'PER'),(255, 268, 'DRUG')]
}),

("El operativo se concretó mientras se realiza en Rosario el juicio contra 25 integrantes de la banda de los Monos, acusados por asociación ilícita y cinco homicidios.", {
	'entities':  [(48, 55, 'LOC'),(103, 112, 'ORG')]
}),

("Ramón Machuca, uno de los líderes de la organización, quien acusó en su declaración al gobierno socialista, a la Justicia y a la policía de Santa Fe de armar una causa contra la familia Cantero.", {
	'entities':  [(0, 13, 'PER'),(140, 148, 'LOC'),(186, 193, 'PER')]
}),

("La Policía Federal detuvo a cinco personas y secuestró cocaína, marihuana y armas durante el operativo que dejó desiertas las calles del barrio de la zona sur de Rosario.", {
	'entities':  [(3, 18, 'ORG'),(55, 62, 'DRUG'),(64, 73, 'DRUG'),(126, 169, 'MISC')]
}),

("Las órdenes de detención fueron libradas por la Fiscalía de Rosario, donde se investigan siete crímenes ligados a las venganzas de la familia Cantero.", {
	'entities':  [(48, 67, 'ORG'),(142, 149, 'PER')]
}),

("El operativo tiene relación con la investigación por el crimen de Isabel Petrona Cantero, ocurrido el 16 de junio pasado.", {
	'entities':  [(66, 88, 'PER')]
}),

("Como publicó LA NACION el 24 de julio pasado, se produjeron siete asesinatos como respuesta a la muerte de la hermana del líder de Los Monos.", {
	'entities':  [(13, 22, 'ORG'),(131, 140, 'ORG')]
}),

("Chabela Cantero fue asesinada por otro clan -los Schneider- que pretende dominar a balazos ese barrio.", {
	'entities':  [(0, 15, 'PER'),(45, 58, 'ORG'),(95, 101, 'MISC')]
}),

("La mujer, de 56 años, fue blanco de la ira de los Schneider y murió de un disparo en el abdomen, mientras que resultaron heridas su nieta y otra joven.", {
	'entities':  [(46, 59, 'ORG')]
}),

("Al ataque lo tramaron, según los investigadores, Patricia Schneider, alias *Pato*, y su marido, David Díaz, alias *Nango*.", {
	'entities':  [(49, 67, 'PER'),(76, 80, 'PER'),(96, 106, 'PER'),(115, 120, 'PER')]
}),

("Las mujeres del clan de Los Monos volvían a su casa cuando Patricia salió de un almacén situado a pocos metros y las increpó.", {
	'entities':  [(24, 33, 'ORG'),(59, 67, 'PER')]
}),

("Dos hombres salieron en defensa de Schneider y otros atacantes descendieron de una camioneta.", {
	'entities':  [(35, 44, 'PER')]
}),

("A Chabela Cantero le dispararon con un arma calibre 38 y murió casi en el acto.", {
	'entities':  [(2, 17, 'PER')]
}),

("La venganza no se hizo esperar en Las Flores.", {
	'entities':  [(34, 44, 'LOC')]
}),

("Los Cantero quemaron la casa de María de los Ángeles Schneider, hija de Patricia, la supuesta instigadora del crimen.", {
	'entities':  [(0, 11, 'ORG'),(32, 62, 'PER'),(72, 80, 'PER')]
}),

("Mientras esta espiral de violencia en esa parte de Rosario recrudecía, fue detenida en ese barrio Celestina Contreras, la madre de Claudio Cantero, líder de Los Monos asesinado el 26 de mayo de 2013.", {
	'entities':  [(51, 58, 'LOC'),(91, 97, 'MISC'),(98, 117, 'PER'),(131, 146, 'PER'),(157, 166, 'ORG')]
}),

("Esta mujer, conocida como la *Cele*, tenía pedido de captura por la causa narco conocida como Los Patrones, que desmanteló parte de este grupo a fines de 2015.", {
	'entities':  [(30, 34, 'PER'),(74, 79, 'DRUG'),(94, 106, 'ORG')]
}),

("El 11 de julio pasado, Gustavo Díaz, de 40 años, fue asesinado dentro de su casa, y su hijo de 10 años resultó herido.", {
	'entities':  [(23, 35, 'PER')]
}),

("Este hombre es el hermano de David, la pareja de Schneider, quien se había refugiado allí, en Uriburu y Acceso Sur, porque sabía que los Cantero lo buscaban para matarlo.", {
	'entities':  [(29, 34, 'PER'),(49, 58, 'PER'),(94, 114, 'LOC'),(133, 144, 'ORG')]
}),

("José Schneider, de 40 años, miembro del clan homónimo, fue ejecutado de un tiro en la nuca el 24 de julio.", {
	'entities':  [(0, 14, 'PER')]
}),

("Tres días después ocurrió otro crimen en ese barrio, que estaría vinculado a esta trama violenta.", {
	'entities':  [(45, 51, 'MISC')]
}),

("Jesús Fernández, de 23 años, fue asesinado en un presunto intento de robo.", {
	'entities':  [(0, 15, 'PER')]
}),

("Más allá del arresto de Marco Antonio Estrada González, la organización criminal liderada por ese jefe narco conocido como Marcos mantiene sus operaciones de venta de droga en la villa 1-11-14.", {
	'entities':  [(24, 54, 'PER'),(103, 108, 'DRUG'),(123, 129, 'PER'),(167, 172, 'DRUG'),(179, 192, 'LOC')]
}),

("Cinco de los integrantes de esa banda fueron arrestados anteayer tras allanamientos realizados por la Policía Federal en el Bajo Flores.", {
	'entities':  [(102, 117, 'ORG'),(124, 135, 'LOC')]
}),

("Fueron incautados 270 kilos de marihuana y 10 kilos de cocaína.", {
	'entities':  [(31, 40, 'DRUG'),(55, 62, 'DRUG')]
}),

("Según detalló el sitio oficial de noticias judiciales fiscales.gob.ar, la investigación se había iniciado en la Procuraduría de Narcocriminalidad (Procunar) al detectarse en la villa 1-11-14 la presencia de *soldaditos* que alertaban sobre los patrullajes realizados allí por las fuerzas de seguridad federales.", {
	'entities':  [(54, 69, 'ORG'),(112, 156, 'ORG'),(177, 190, 'LOC'),(280, 310, 'ORG')]
}),

("Se informó que el Departamento Unidad Federal de Investigaciones Especiales de la Policía Federal pudo comprobar que estas personas custodiaban la venta que la organización narcocriminal desarrollaba sobre una de las calles del barrio.", {
	'entities':  [(18, 97, 'ORG'),(173, 186, 'DRUG'),(217, 234, 'MISC')]
}),

("*La venta de drogas se desplazó especialmente a la calle Bolívar, entre la avenida Riestra y la calle Savigny, en inmediaciones de las manzanas 20, 23, 24 y 25, al igual que en cercanías de la iglesia San Antonio y en el punto habitualmente conocido como el Córner de Lalo*, se indicó en la página Web que comunica la actividad de las fiscalías federales.", {
	'entities':  [(13, 19, 'DRUG'),(51, 64, 'LOC'),(75, 90, 'LOC'),(96, 109, 'LOC'),(135, 159, 'LOC'),(193, 212, 'MISC'),(257, 272, 'LOC')]
}),

("La pesquisa fue seguida por el Juzgado Federal N° 12, a cargo de Sergio Torres, quien tiene a su cargo la causa vinculada con la organización comandada por el peruano Marcos.", {
	'entities':  [(31, 52, 'ORG'),(65, 78, 'PER'),(167, 173, 'PER')]
}),

("*Conforme surge de las tareas desplegadas y la información obtenida por la Procuraduría de Narcocriminalidad, se ha logrado corroborar la continuidad en el tiempo de la organización narcocriminal tradicionalmente liderada por Marco Antonio Estada González, Silvana Alejandra Salazar y Fernando Estrada González (alias «Pity»), enquistada en el interior de la villa 1-11-14 de esta ciudad, con dominio territorial de espacios específicos -hoy mudados a otros sectores de aquel barrio-, y relacionada con distintas actividades de corte delictivo, especialmente con el tráfico ilícito de sustancias estupefacientes, su comercialización y el acopio de armas de fuego y municiones*, indicaron los fiscales Diego Iglesias y Juan Pedro Zoni.", {
	'entities':  [(75, 108, 'ORG'),(182, 195, 'DRUG'),(226, 255, 'PER'),(257, 282, 'PER'),(285, 310, 'PER'),(319, 323, 'PER'),(359, 372, 'LOC'),(476, 482, 'MISC'),(585, 611, 'DRUG'),(701, 715, 'PER'),(718, 733, 'PER')]
}),

("Y agregaron que las detenciones de González, Salazar, Lily Lucila Enríquez Alarcón y, en el exterior, *Pity* Estrada González *no han sido motivos suficientes como para lograr culminar con las diferentes actividades ilícitas que estos venían llevando adelante*.", {
	'entities':  [(35, 43, 'PER'),(45, 52, 'PER'),(54, 82, 'PER'),(103, 107, 'PER'),(109, 125, 'PER')]
}),

("Cuatro sospechosos fueron detenidos ayer como parte de una organización criminal dedicada al narcomenudeo en el barrio porteño de Liniers.", {
	'entities':  [(93, 105, 'DRUG'),(112, 137, 'LOC')]
}),

("Fuentes policiales aseguraron que fueron decomisados cuatro kilogramos de cocaína durante los allanamientos.", {
	'entities':  [(74, 81, 'DRUG')]
}),

("El operativo estuvo a cargo de efectivos de la Dirección de Narcocriminalidad de la Policía de la Ciudad y la pesquisa se inició tras varias denuncias anónimas realizadas al 911 por vecinos de Liniers, señalándose en esos contactos que varias personas vendían droga en las inmediaciones de las calles José León Suárez, entre Ramón Falcón e Ibarrola.", {
	'entities':  [(47, 104, 'ORG'),(193, 200, 'LOC'),(260, 265, 'DRUG'),(301, 317, 'LOC'),(325, 337, 'LOC'),(340, 348, 'LOC')]
}),

("Los investigadores lograron dar con los responsables de esa red de comercialización de drogas y el fiscal Federal Federico Delgado ordenó que se efectuaran diversas diligencias para determinar si efectivamente en esa zona operaba una banda dedicada al narcomenudeo.", {
	'entities':  [(87, 93, 'DRUG'),(114, 130, 'PER'),(252, 264, 'DRUG')]
}),

("En el marco de la pesquisa, se estableció que la banda estaba liderada por un hombre apodado *Sami*, quien en complicidad con dos mujeres y un hombre se dedicaban a vender cocaína.", {
	'entities':  [(94, 98, 'PER'),(172, 179, 'DRUG')]
}),

("Por orden del juez Federal Rodolfo Canicoba Corral, la policía realizó 12 allanamientos en los domicilios identificados en la investigación y vinculados a la red delictiva.", {
	'entities':  [(19, 50, 'PER')]
}),

("Para desarticular a esa organización criminal, los agentes utilizaron filmaciones con cámaras ocultas en las que se observaría el sistema de comercialización de las drogas que llevaba adelante esta banda.", {
	'entities':  [(165, 171, 'DRUG')]
}),

("ROSARIO.- El ministro de Justicia de Santa Fe, Ricardo Silberstein, se mostró molesto y lanzó duras críticas contra el tribunal que enjuicia a la banda Los Monos, luego de que los jueces avalaron un reclamo de los líderes de la organización que se niegan a permanecer en calabozos en el subsuelo del edificio donde se realizan las audiencias.", {
	'entities':  [(0, 7, 'LOC'),(37, 45, 'LOC'),(47, 66, 'PER'),(152, 161, 'ORG'),(300, 308, 'MISC')]
}),

("Anteayer comenzó el juicio contra esa banda narcocriminal y se citará a 280 testigos.", {
	'entities':  [(44, 57, 'DRUG')]
}),

("*Si los imputados deciden sobre dónde estar alojados, hay un paso a un crimen organizado que construye su propia cárcel, como en Colombia*, aseguró Silberstein.", {
	'entities':  [(113, 119, 'MISC'),(129, 137, 'LOC'),(148, 159, 'PER')]
}),

("El ministro no lo recordó, pero no es la primera vez que ocurre algo similar en la causa de Los Monos.", {
	'entities':  [(92, 101, 'ORG')]
}),

("Carlos Varela cuestionó los dichos de Silberstein al señalar: *Como persona del derecho me indigna que un ministro de justicia quiera llevar contra el alambrado a un tribunal para que varíe su decisión.", {
	'entities':  [(0, 13, 'PER'),(38, 49, 'PER'),(166, 174, 'MISC')]
}),

("El 26 de enero de 2016 LA NACION publicó una crónica en la que el comisario Rubén Pereyra, alias *Gula Gula*, quien forma parte de los 25 imputados en el juicio, se construyó su propio calabozo en la Unidad de Seguridad Zona Rural, situada en la ruta 21 y la AO12, a unos 10 kilómetros esta ciudad.", {
	'entities':  [(23, 32, 'ORG'),(76, 89, 'PER'),(98, 107, 'PER'),(200, 230, 'ORG'),(246, 253, 'MISC'),(259, 263, 'MISC')]
}),

("*Me construyo mi propio calabozo*, le propuso Pereyra al juez de instrucción Juan Carlos Vienna, quien había ordenado su detención por considerarlo un infiltrado de la banda Los Monos en la Secretaría de Delitos Complejos, del Ministerio de Seguridad.", {
	'entities':  [(24, 32, 'MISC'),(46, 53, 'PER'),(77, 95, 'PER'),(174, 183, 'ORG'),(174, 183, 'PER'),(190, 250, 'ORG')]
}),

("Todo salió de mi bolsillo*, se jactó ese comisario en diálogo con LA NACION.", {
	'entities':  [(66, 75, 'ORG')]
}),

("El Ejecutivo estableció un mecanismo de seguridad planificando los lugares que son mucho mejores que las celdas de Piñero y, sin embargo, sólo por haberse desnudado logran imponer el lugar de detención estas personas a las que se está juzgando por amenazar jueces y a testigos e incluso por matarlos*, sostuvo Silberstein.", {
	'entities':  [(115, 121, 'PER'),(310, 321, 'PER')]
}),

("En los barrios humildes la penetración del narcomenudeo es visible para los vecinos.", {
	'entities':  [(43, 55, 'DRUG')]
}),

("El puesto de venta de droga está ahí, a la vista.", {
	'entities':  [(22, 27, 'DRUG')]
}),

("Alrededor de esos puntos de comercialización se construye la simbología narco, su demostración de fuerza.", {
	'entities':  [(72, 77, 'DRUG')]
}),

("Por eso se procura derrumbar al mismo tiempo las paredes de un búnker de drogas y la imagen de control territorial que emerge de esos lugares.", {
	'entities':  [(63, 69, 'MISC'),(73, 79, 'DRUG')]
}),

("*Los demolemos para demostrar que ahí no se va a vender más droga.", {
	'entities':  [(60, 65, 'DRUG')]
}),

("La persona que venda droga va a quedar detenida y así vamos a poder liberar a los vecinos que los sufren*, dijo a LA NACION el ministro Cristian Ritondo.", {
	'entities':  [(21, 26, 'DRUG'),(114, 123, 'ORG'),(136, 152, 'PER')]
}),

("El comercio de droga estaba localizado en la calle Manuel Rosetti al 3200, a pocas cuadras de la autopista Panamericana, en la villa Borges.", {
	'entities':  [(15, 20, 'DRUG'),(45, 73, 'LOC'),(97, 119, 'LOC'),(127, 139, 'LOC')]
}),

("Allí, dentro de un casilla, operaba *la Banda del Hacha*, que se ganó ese nombre porque en la puerta del búnker, en forma de amenaza, tenía clavada un hacha.", {
	'entities':  [(37, 55, 'ORG'),(105, 111, 'MISC')]
}),

("*Es un mensaje claro: no vamos a permitir que sigan con ese negocio mafioso de la venta de droga ni contaminando a nuestros chicos.", {
	'entities':  [(91, 96, 'DRUG')]
}),

("Muchas veces, los búnkeres se hacen en barrios muy humildes, como este, donde someten al vecino*, dijo Ritondo.", {
	'entities':  [(18, 26, 'MISC'),(103, 110, 'PER')]
}),

("Y agregó: *La medida que tomamos con la gobernadora [por María Eugenia Vidal] es que los lugares para venta de drogas hay que demolerlos.", {
	'entities':  [(57, 76, 'PER'),(111, 117, 'DRUG')]
}),

("Ese fue el caso de un búnker instalado en Mar del Plata, ubicado en el barrio Libertad, al noreste de la ciudad balnearia.", {
	'entities':  [(22, 28, 'MISC'),(42, 55, 'LOC'),(71, 86, 'LOC'),(105, 121, 'MISC')]
}),

("Un ejemplo diferente es lo que pasó con el búnker conocido como *del rey Arturo*, ubicado en el partido bonaerense de Esteban Echeverría.", {
	'entities':  [(43, 49, 'MISC'),(65, 79, 'ORG'),(96, 114, 'MISC'),(118, 136, 'LOC')]
}),

("Ese punto de venta de drogas fue entregado por la Justicia a la organización Madres contra el Paco y por la Vida.", {
	'entities':  [(22, 28, 'DRUG'),(50, 112, 'ORG'),(94, 98, 'DRUG')]
}),

("Se transformó así en un centro de rehabilitación de drogas y se construyeron canchas de fútbol y piletas.", {
	'entities':  [(52, 58, 'DRUG')]
}),

("En el caso presentado ayer en Olivos, Ritondo estuvo acompañado por el intendente de Vicente López, Jorge Macri, la plana mayor de la policía bonaerense y la fiscal a cargo de la investigación, Marcela Semería.", {
	'entities':  [(30, 36, 'LOC'),(38, 45, 'PER'),(85, 98, 'LOC'),(100, 111, 'PER'),(194, 209, 'PER')]
}),

("En el operativo se secuestraron dosis de paco, casi mil envoltorios de cocaína, 400 gramos de marihuana (los búnkeres se abastecen en forma diaria), balanzas de precisión y dinero producto de la venta de la droga.", {
	'entities':  [(41, 45, 'DRUG'),(71, 78, 'DRUG'),(94, 103, 'DRUG'),(109, 117, 'MISC'),(207, 212, 'DRUG')]
}),

("La identidad de los acusadas se encuentra en reserva porque la investigación sobre la Banda del Hacha continúa.", {
	'entities':  [(86, 101, 'ORG')]
}),

("El objetivo de la Justicia es llegar ahora a los narcotraficantes que facilitaban las sustancias para la venta minorista en esa zona del norte del conurbano.", {
	'entities':  [(49, 65, 'DRUG'),(86, 96, 'DRUG'),(128, 156, 'MISC')]
}),

("Durante ese tiempo, agentes de la policía bonaerense se infiltraron entre la gente del barrio y así vieron cómo funcionaba la banda.", {
	'entities':  [(87, 93, 'MISC')]
}),

("Hasta tenemos filmado al dueño de la casa corriendo por el pasillo con el hacha en las manos amedrentando a unos chicos*, contó a LA NACION una fuente calificada que participó de la pesquisa.", {
	'entities':  [(37, 41, 'MISC'),(130, 139, 'ORG')]
}),

("La Delegación de San Isidro de la Superintendencia de Investigaciones del Tráfico de Drogas Ilícitas y Crimen Organizado tomó la posta y una vez que tuvimos todos los elementos necesarios se pidió la orden de allanamiento al juez de garantías y acá estamos*, dijo la fiscal Semería.", {
	'entities':  [(3, 120, 'ORG'),(274, 281, 'PER')]
}),

("En referencia a si ese era el único *quiosco* de droga que actuaba en ese barrio humilde, el intendente de Vicente López, Jorge Macri, dijo: *Que nosotros sepamos, sí.", {
	'entities':  [(49, 54, 'DRUG'),(107, 120, 'LOC'),(122, 133, 'PER')]
}),

("En la misma sintonía, el jefe de la policía de la provincia de Buenos Aires, comisario general Fabián Perroni, detalló a LA NACION: *La lucha contra el narcotráfico es una pelea que no se puede abandonar y para eso hay que trabajar en conjunto con la gobernación, intendentes y la Justicia*.", {
	'entities':  [(50, 75, 'LOC'),(95, 109, 'PER'),(121, 130, 'ORG'),(152, 164, 'DRUG')]
}),

("Para el comisario Perroni el saneamiento de la fuerza policial es vital para encarar la lucha contra el narcotráfico.", {
	'entities':  [(18, 25, 'PER'),(104, 116, 'DRUG')]
}),

("El comisario Perroni consideró que ese sistema puede dar buenos resultados: *El buen policía ya no siente miedo al realizar una denuncia contra otro agente por algún delito que este cometa.", {
	'entities':  [(13, 20, 'PER')]
}),

("Para hacer funcionar la ruta a África, el cartel aspiraba a tener un puerto propio en Rosario.", {
	'entities':  [(31, 37, 'LOC'),(86, 93, 'LOC')]
}),

("En las escuchas telefónicas de la causa, Guillermo Heisinger, Aldo Corizzo y Carlos Yorelmy Duarte Díaz hablaban de la posibilidad de adquirir uno en la vecina Fray Luis Beltrán, donde desde 1941 está la fábrica de armas de Fabricaciones Militares.", {
	'entities':  [(41, 60, 'PER'),(62, 74, 'PER'),(77, 103, 'PER'),(160, 177, 'PER'),(204, 220, 'MISC'),(224, 247, 'ORG')]
}),

("Su predio costero es el único vacante en la ribera del Paraná, en una zona estratégica del polo industrial del Gran Rosario, por donde se exporta el 85% de la soja argentina.", {
	'entities':  [(44, 50, 'MISC'),(55, 61, 'LOC'),(111, 123, 'LOC')]
}),

("Según aquellas conversaciones, se inician tratativas con el ex Ministerio del Interior y Transporte de la Nación, que tenía jurisdicción sobre los puertos y era encabezado por Florencio Randazzo.", {
	'entities':  [(63, 112, 'ORG'),(176, 194, 'PER')]
}),

("En la transcripción de la escucha telefónica del 12 de septiembre de 2014, *una voz masculina que llama a Guillermo [Heisinger] le cuenta que está avanzando mucho con la gente del Ministerio del Interior en la campaña de [Florencio] Randazzo*.", {
	'entities':  [(106, 115, 'PER'),(117, 126, 'PER'),(180, 203, 'ORG'),(222, 231, 'PER'),(233, 241, 'PER')]
}),

("Seis días después, Duarte Díaz insistía en que *lo de los puertos va muy bien, y lo de Randazzo, también*.", {
	'entities':  [(19, 30, 'PER'),(58, 65, 'MISC'),(87, 95, 'PER')]
}),

("Voceros del ex ministro negaron que Randazzo hubiera tenido algún contacto con representantes de este cartel.", {
	'entities':  [(36, 44, 'PER')]
}),

("Randazzo estuvo a cargo de los puertos hasta el 1º de abril de 2015, cuando, a través de los decretos 441/2015 y 442/2015, la entonces presidenta Cristina Kirchner decidió que las terminales quedaran bajo el ala del Ministerio de Economía, que conducía Axel Kicillof.", {
	'entities':  [(0, 8, 'PER'),(31, 38, 'MISC'),(146, 163, 'PER'),(216, 238, 'ORG'),(253, 266, 'PER')]
}),

("En la causa 7650/2014 consta que Corizzo le avisó a Heisinger el 22 de noviembre de 2014: *González va mañana a las 10 al ministerio con un americano por un tema para Randazzo*.", {
	'entities':  [(33, 40, 'PER'),(52, 61, 'PER'),(91, 99, 'PER'),(167, 175, 'PER')]
}),

("Y agregó: *En este momento está haciendo el estudio de los accesos Vialidad Nacional*.", {
	'entities':  [(67, 84, 'ORG')]
}),

("El ministro de Seguridad bonaerense, Cristian Ritondo, supervisó hoy la quema de 450 kilos de cocaína y marihuana incautados por la Policía provincial.", {
	'entities':  [(37, 53, 'PER'),(94, 101, 'DRUG'),(104, 113, 'DRUG'),(132, 150, 'ORG')]
}),

("Ante esto, destacó: *El eje central de la gestión, además de garantizar la prevención del delito, es combatir a un crimen organizado y un narcotráfico que ya no cuentan con garantías y que saben que acá hay un Estado presente que, fiel a sus principios, pone todo a disposición para derrumbarlo*.", {
	'entities':  [(138, 150, 'DRUG')]
}),

("Respecto a la quema de la droga secuestrada en distintos puntos del conurbano y la Capital Federal, el ministro dijo que *se trata de una cadena de procedimientos donde la destrucción de la droga forma parte del último eslabón en la lucha contra el narcotráfico*.", {
	'entities':  [(26, 31, 'DRUG'),(68, 77, 'LOC'),(83, 98, 'LOC'),(249, 261, 'DRUG')]
}),

("La incineración de las drogas tuvo lugar en el crematorio Burzaco, ubicado en la calle Luis María Drago 2090 esquina Guido de esa localidad del partido de Almirante Brown, actividad en la que también estuvieron presentes autoridades ministeriales y policiales.", {
	'entities':  [(23, 29, 'DRUG'),(58, 65, 'LOC'),(81, 122, 'LOC'),(155, 170, 'LOC')]
}),

("Los estupefacientes fueron incautados en dos procedimientos realizados en marzo y junio de 2016 en diversos puntos de la Provincia (Avellaneda, Esteban Echeverría, Lomas de Zamora y Moreno) y la Ciudad de Buenos Aires.", {
	'entities':  [(121, 130, 'LOC'),(132, 142, 'LOC'),(144, 162, 'LOC'),(164, 179, 'LOC'),(182, 188, 'LOC'),(195, 217, 'LOC')]
}),

("La cocaína incinerada es producto del operativo *Cochera Blanca*, donde se incautaron 33 kilos de esta sustancia que era distribuida en forma de ladrillos y escondida en el interior de un auto.", {
	'entities':  [(3, 10, 'DRUG'),(103, 112, 'DRUG'),(145, 154, 'DRUG')]
}),

("Esta investigación permitió detener a tres personas -una de ellas de nacionalidad peruana- y establecer que la droga provenía del norte de nuestro país, para ser comercializada en la vía pública y en varios domicilios del conurbano bonaerense y la Capital Federal.", {
	'entities':  [(111, 116, 'DRUG'),(130, 151, 'LOC'),(183, 194, 'MISC'),(207, 217, 'MISC'),(222, 242, 'LOC'),(248, 263, 'LOC')]
}),

("El otro operativo incluyó la intercepción de un cargamento con más de 400 kilos de marihuana que provenía de la Capital Federal y tenía como destino la localidad de Lomas de Zamora.", {
	'entities':  [(83, 92, 'DRUG'),(112, 127, 'LOC'),(165, 180, 'LOC')]
}),

("Allí, gracias a tareas de inteligencia y vigilancias encubiertas realizadas por los uniformados, se logró la detención de dos sujetos -uno de nacionalidad paraguaya- y la intercepción del vehículo que transportaba la droga al barrio 9 de Abril del partido de Esteban Echeverría.", {
	'entities':  [(217, 222, 'DRUG'),(226, 243, 'LOC'),(259, 277, 'LOC')]
}),

("El ministerio de Seguridad bonaerense informó que desde principios de 2016 a la fecha fueron secuestradas alrededor de 25 toneladas de marihuana, más de 1.027 kilos de cocaína, 45 kilos de pasta base, casi 369.000 dosis de paco, 145.000 de LSD y 8.150 pastillas de éxtasis.", {
	'entities':  [(3, 37, 'ORG'),(135, 144, 'DRUG'),(168, 175, 'DRUG'),(189, 199, 'DRUG'),(223, 227, 'DRUG'),(240, 243, 'DRUG'),(252, 272, 'DRUG')]
}),

("Agencia Télam", {
	'entities':  [(0, 13, 'ORG')]
}),

("La Argentina tiene una de las tasas de detenciones más baja de la región: hay 175 presos cada 100.000 habitantes.", {
	'entities':  [(3, 12, 'LOC'),(66, 72, 'MISC')]
}),

("Así surge del último informe del Sistema Nacional de Estadísticas sobre Ejecución de la Pena (Sneep 2016), publicado por el Ministerio de Justicia de la Nación.", {
	'entities':  [(33, 92, 'ORG'),(94, 99, 'ORG'),(124, 159, 'ORG')]
}),

("La población penitenciaria se distribuye en 290 unidades penitenciarias, de las cuales 33 pertenecen al Servicio Penitenciario Federal, y 54 al Servicio de la Provincia de Buenos Aires.", {
	'entities':  [(104, 134, 'ORG'),(144, 184, 'ORG')]
}),

("*Entendemos que es muy importante dar a conocer la información y lo hacemos en formato abierto*, explicó a LA NACION Juan José Benitez, subsecretario de Política Criminal del Ministerio de Justicia.", {
	'entities':  [(107, 116, 'ORG'),(117, 134, 'PER'),(153, 197, 'ORG')]
}),

("Por su parte, Carlos Gonzalez Guerra, director de Política Criminal, destacó que *el SNEEP es una fuente de información muy importante incluso para las modificaciones en el Código Penal*.", {
	'entities':  [(14, 36, 'PER'),(50, 67, 'ORG'),(85, 90, 'ORG')]
}),

("*Es importante tomar decisiones en base a datos precisos, no en el aire como solía ocurrir en esta materia en Argentina.", {
	'entities':  [(110, 119, 'LOC')]
}),

("Este cambio significativo permitió valorizar a la Dirección de Política Criminal en su estructura y profesionalismo para aportar ideas concretas a la hora de tomar decisiones en derecho penal y procesal.", {
	'entities':  [(50, 80, 'ORG')]
}),

("A continuación, algunos de los datos más destacados del informe, analizado por LA NACION DATA:", {
	'entities':  [(79, 88, 'ORG')]
}),

("Algunas cárceles del país ofrecen diversas formas de capacitación laboral y educativa.", {
	'entities':  [(8, 16, 'MISC')]
}),

("En el caso de las capacitaciones laborales, el Sneep destaca que en 2016 sólo el 21% de la población penitenciaria participó.", {
	'entities':  [(47, 52, 'ORG')]
}),

("Unas 131 mujeres conviven con sus hijos dentro de los penales argentinos.", {
	'entities':  [(54, 61, 'MISC')]
}),

("Es la cifra más baja desde que se realizan los informes Sneep.", {
	'entities':  [(56, 61, 'ORG')]
}),

("En algunos penales de la provincia de Buenos Aires se comenzó a implementar un sistema de *casitas* dentro del predio penitenciario, para generar un ambiente más propicio para la crianza.", {
	'entities':  [(11, 18, 'MISC'),(25, 50, 'LOC'),(91, 98, 'MISC'),(111, 131, 'MISC')]
}),

("Sobre este punto, Benitez destaó el uso de pulseras electrónicas y el impacto que tuvo en el índice de mujeres presas con niños.", {
	'entities':  [(18, 25, 'PER')]
}),

("*Detectamos que tenemos menos mujeres presas con sus hijos en unidades carcelarias y en eso tiene un fuerte impacto el programa de pulseras electrónicas que impulsa en Ministerio de Justicia de la Nación y de la provincia*, señaló el funcionario.", {
	'entities':  [(62, 82, 'MISC'),(168, 221, 'ORG')]
}),

("Apenas el 8% de los detenidos tiene o tuvo la posibilidad de acceder a las salidas transitorias según el Sneep 2016.", {
	'entities':  [(105, 110, 'ORG')]
}),

("Personal de la Gendarmería incautó unos 5000 kilos de marihuana en un control vial ubicado en la ruta nacional 14, en las cercanías de la localidad correntina de Tapebicuá.", {
	'entities':  [(15, 26, 'ORG'),(54, 63, 'DRUG'),(97, 113, 'MISC'),(162, 171, 'LOC')]
}),

("La droga estaba escondida en la caja trasera de un camión, y fue arrestado el conductor que había iniciado el viaje en Misiones.", {
	'entities':  [(3, 8, 'DRUG'),(119, 127, 'LOC')]
}),

("El cargamento de marihuana fue detectado con la asistencia de perros adiestrados para encontrar drogas.", {
	'entities':  [(17, 26, 'DRUG'),(96, 102, 'DRUG')]
}),

("Anoche aún continuaba el pesaje del ilegal cargamento incautado, que fue trasladada al Escuadrón 7 de Paso de los Libres.", {
	'entities':  [(87, 120, 'ORG')]
}),

("La organización tenía un hándicap importante sobre otrasbandas narco que operan en el país: un método especial les permitía estirar un 20% cada kilo de clorhidrato de cocaína con el mismo efecto alcaloide como si se tratara de una sustancia de máxima pureza.", {
	'entities':  [(63, 68, 'DRUG'),(152, 174, 'DRUG'),(195, 204, 'DRUG')]
}),

("Y para no tener fallas en la producción, los sospechosos hicieron venir desde Colombia al *Químico* que inventó la técnica e instalaron un laboratorio de estiramiento en un inmueble de Villa Luro.", {
	'entities':  [(78, 86, 'LOC'),(139, 150, 'MISC'),(173, 181, 'MISC'),(185, 195, 'LOC')]
}),

("Por orden del juez federal de Lomas de Zamora, Federico Villena, personal de la Gendarmería Nacional hizo una serie de allanamientos en el exclusivo country Olivos Golf Club, en Malvinas Argentinas; en Palermo, Villa Luro, Belgrano y Ramos Mejía.", {
	'entities':  [(30, 45, 'LOC'),(47, 63, 'PER'),(80, 100, 'ORG'),(149, 156, 'MISC'),(157, 173, 'ORG'),(178, 197, 'LOC'),(202, 209, 'LOC'),(211, 221, 'LOC'),(223, 231, 'LOC'),(234, 245, 'LOC')]
}),

("Si bien en uno de los dos inmuebles allanados en el Olivos Golf Club, los gendarmes secuestraron nueve bidones de productos químicos, dos prensas y una balanza de precisión, el laboratorio de estiramiento donde el *Químico* llevaba adelante su técnica de estiramiento estaba en la ciudad de Buenos Aires.", {
	'entities':  [(26, 35, 'MISC'),(52, 68, 'ORG'),(281, 303, 'LOC')]
}),

("Dos calificadas fuentes judiciales explicaron a la nacion que el centro de estiramiento estaba en un inmueble de Villa Luro, donde se decomisaron 25 paquetes de cocaína (que en principio tendrían un peso total de 20 kilos), una prensa, elementos de corte, sorbato de potasio, 30 litros de acetona, caloventores y microondas.", {
	'entities':  [(48, 57, 'ORG'),(113, 123, 'LOC'),(161, 168, 'DRUG'),(256, 274, 'DRUG'),(289, 296, 'DRUG')]
}),

("*El desbaratamiento de esta red de laboratorios que producen droga es un nuevo éxito en la lucha contra el narcotráfico.", {
	'entities':  [(61, 66, 'DRUG'),(107, 119, 'DRUG')]
}),

("Junto a las fuerzas federales continuaremos luchando y haremos lo que se deba hacer para derrotar a los narcos.", {
	'entities':  [(104, 110, 'DRUG')]
}),

("Nuestra meta es terminar con los que trafican, venden y fabrican droga, sea quien sea.", {
	'entities':  [(37, 45, 'DRUG'),(65, 70, 'DRUG')]
}),

("No le damos tregua al narcotráfico*, afirmó la ministra de Seguridad de la Nación, Patricia Bullirch.", {
	'entities':  [(22, 34, 'DRUG'),(59, 81, 'ORG'),(83, 100, 'PER')]
}),

("La investigación, delegada en la Procuraduría de Narcocriminalidad (Procunar), a cargo del fiscal Diego Iglesias, comenzó hace un par de meses con el aporte de información obtenida en trabajos de inteligencia criminal.", {
	'entities':  [(33, 77, 'ORG'),(98, 112, 'PER')]
}),

("Fuentes oficiales explicaron que los detectives de la Gendarmería Nacional tuvieron una colaboración valiosa de la Agencia Federal de Inteligencia (AFI) y de la DEA (la agencia antidrogas de los Estados Unidos, por su nombre en inglés).", {
	'entities':  [(54, 74, 'ORG'),(114, 152, 'ORG'),(161, 164, 'ORG'),(195, 209, 'LOC')]
}),

("Tenían un técnica para estirar un 20% el clorhidrato de cocaína con el mismo efecto alcaloide como si se tratara de una sustancia de máxima pureza.", {
	'entities':  [(41, 63, 'DRUG'),(84, 93, 'DRUG'),(120, 129, 'DRUG')]
}),

("Para poder llevar adelante esta metodología trajeron desde Colombia al ?Químico'*, sostuvo una fuente con acceso al expediente.", {
	'entities':  [(59, 67, 'LOC')]
}),

("El Olivos Golf Club es uno de los countries más tradicionales de la Argentina, inaugurado en 1950, con rigurosos requisitos de admisión para ser socio y con una de las canchas más importante del país, donde se jugaba el Torneo de Maestros y el ganador se llevaba un saco azul a la manera del Masters de Augusta.", {
	'entities':  [(3, 19, 'ORG'),(34, 43, 'MISC'),(68, 77, 'LOC')]
}),

("Por orden de Villena se allanaron dos inmuebles en el country.", {
	'entities':  [(13, 20, 'PER'),(38, 47, 'MISC'),(54, 61, 'MISC')]
}),

("En uno de los procedimientos fue detenido uno de los sospechosos, de nacionalidad argentina.", {
	'entities':  [(82, 91, 'LOC')]
}),

("En la propiedad, los gendarmes secuestraron los nueve bidones de productos químicos, dos prensas, una balanza de precisión, $67.000, US$7722, 160 pesos bolivianos, un automóvil y una moto, ambos vehículos marca BMW.", {
	'entities':  [(211, 214, 'ORG')]
}),

("En la segunda propiedad del country se incautaron una pistola Pietro Beretta calibre 22 con munición en recámara, diez municiones del mismo calibre sin documentación, dos teléfonos celulares y tres chips.", {
	'entities':  [(28, 35, 'MISC'),(62, 76, 'ORG')]
}),

("El técnico en comercio internacional no era propietario, le alquiló el inmueble del Olivos Golf Club a los dueños de una reconocida agencia de modelos.", {
	'entities':  [(84, 100, 'ORG')]
}),

("*El sospechoso detenido en el country es inquilino de la propiedad allanada.", {
	'entities':  [(30, 37, 'MISC')]
}),

("Se trata de un excelente jugador de golf que integra la selección del Olivos Golf Club*, sostuvo una calificada fuente de la causa.", {
	'entities':  [(70, 86, 'ORG')]
}),

("Las fuentes judiciales consultadas explicaron que otro de los acusados es ciudadano argentino con domicilio en Salvador Mazza, Salta, que ya había estado detenido en una causa por narcotráfico y que tendría vínculo con el sindicado capo narco Delfín Castedo, cuyo hermano fue detenido esta semana.", {
	'entities':  [(111, 125, 'LOC'),(127, 132, 'LOC'),(180, 192, 'DRUG'),(237, 242, 'DRUG'),(243, 257, 'PER')]
}),

("Los investigadores a cargo del expediente sospechan que la cocaína ingresaba a la Argentina por Salta desde Bolivia y suponen que tenía como destino países de Europa.", {
	'entities':  [(59, 66, 'DRUG'),(82, 91, 'LOC'),(96, 101, 'LOC'),(108, 115, 'LOC'),(159, 165, 'LOC')]
}),

("*La cocaína la estiraban con sorbato de potasio, algo que solo se había descubierto hace un par de años atrás en España*, sostuvo un investigador judicial.", {
	'entities':  [(4, 11, 'DRUG'),(29, 47, 'DRUG'),(113, 119, 'LOC')]
}),

("Los seis detenidos serán indagados hoy, desde la mañana, por el juez Villena.", {
	'entities':  [(69, 76, 'PER')]
}),

("Alan Funes, de 18 años, quien era buscado desde el 1° de enero pasado en Rosario , fue detenido este martes a las 6 de la mañana en un operativo conjunto entre fuerzas de seguridad federales y provinciales, que desde hace días están tras los pasos de este joven que está acusado de ser uno de los responsables del rebrote de la violencia en Rosario, que dejó 16 muertos en lo que va del año.", {
	'entities':  [(0, 10, 'PER'),(73, 80, 'LOC'),(341, 348, 'LOC')]
}),

("La ministra de Seguridad Patricia Bullrich confirmó esta mañana que Funes fue detenido tras una serie de operativos que se produjeron en forma conjunta entre Gendarmería y la Policía de Santa Fe .", {
	'entities':  [(25, 42, 'PER'),(68, 73, 'PER'),(158, 169, 'ORG'),(175, 194, 'ORG')]
}),

("Fuentes de esa cartera señalaron a LA NACIÓN que anoche se hizo una serie de allanamientos y no lograron hallar al muchacho, oriundo de barrio Municipal, donde se enfrentó con la familia Caminos, históricos líderes de la barra brava de Newell's.", {
	'entities':  [(35, 44, 'ORG'),(136, 152, 'LOC'),(187, 194, 'PER'),(236, 244, 'ORG')]
}),

("A muy temprana edad, Alan, hijo de Jorge, un veterano pirata del asfalto que fue blanco de un ataque a balazos el 1° de enero, se transformó junto con su hermano Lautaro, de 20 años, en asesinos en potencia, con una sed de venganza incontenible, luego de que los Caminos mataran a su madre.", {
	'entities':  [(21, 25, 'PER'),(35, 40, 'PER'),(162, 169, 'PER'),(263, 270, 'PER')]
}),

("Los enfrentamientos entre estos dos clanes familiares vinculados al narcomenudeo dejaron 36 personas muertas, que fueron asesinadas por sicarios.", {
	'entities':  [(68, 80, 'DRUG')]
}),

("Disparó una ráfaga de 15 tiros al aire con una ametralladora FMK3 mientras estaba con prisión domiciliaria en la casa de su abuela en el sur de Rosario.", {
	'entities':  [(144, 151, 'LOC')]
}),

("El 1° de mayo de 2016, Alan, en ese momento de 17 años, entró al pasillo de casas precarias de Ayacucho al 4300, apuntó su mirada y la pistola 9 milímetros contra Julio Solano, conocido como Pupi, y lo acribilló.", {
	'entities':  [(23, 27, 'PER'),(95, 111, 'LOC'),(163, 175, 'PER'),(191, 195, 'PER')]
}),

("Solano murió en el acto, en ese pasillo ancho en cuya entrada hay una enorme palmera que se trenza con la maraña de cables de las conexiones ilegales.", {
	'entities':  [(0, 6, 'PER')]
}),

("Unos meses después, el muchacho fue detenido y enviado al Instituto de Rehabilitación del Adolescente (IRAR), y la causa judicial tuvo varias idas y venidas en el Juzgado de Menores N° 3 con recurrentes pedidos de nulidades de sus abogados hasta que acordaron con la fiscalía en octubre pasado que fuera enviado a la casa de su abuela en el barrio La Tablada.", {
	'entities':  [(58, 108, 'ORG'),(163, 186, 'ORG'),(341, 358, 'LOC')]
}),

("Alexis Caminos, contemporáneo y principal enemigo de Alan y Lautaro, fue acusado por el asesinato de la madre de los Funes y de Claudio Fernández, a quien mataron de 11 disparos en el barrio Municipal.", {
	'entities':  [(0, 14, 'PER'),(53, 57, 'PER'),(60, 67, 'PER'),(117, 122, 'PER'),(128, 145, 'PER'),(184, 200, 'LOC')]
}),

("Alexis era menor cuando cometió el crimen.", {
	'entities':  [(0, 6, 'PER')]
}),

("El Juzgado de Menores enfrentó varias nulidades del abogado Marcos Cella -quien estuvo preso, como partícipe secundario de un asesinato- hasta que la Cámara Penal confirmó el procesamiento de Alexis recién en marzo de 2016.", {
	'entities':  [(3, 21, 'ORG'),(60, 72, 'PER'),(150, 162, 'ORG'),(192, 198, 'PER')]
}),

("Actualmente está preso en la cárcel de Coronda.", {
	'entities':  [(29, 35, 'MISC'),(39, 46, 'LOC')]
}),

("Delfín Castedo está sindicado como el mayor proveedor de droga del país.", {
	'entities':  [(0, 14, 'PER'),(57, 62, 'DRUG')]
}),

("Fue capturado por la Gendarmería Nacional en Parque Leloir en julio de 2016, después de haber estado ocho años prófugo.", {
	'entities':  [(21, 41, 'ORG'),(45, 58, 'LOC')]
}),

("Ahora, en las últimas horas, en Salta, fue detenido su hermano, Roberto César Castedo.", {
	'entities':  [(32, 37, 'LOC'),(64, 85, 'PER')]
}),

("En el operativo se secuestraron casi 100 kilos de cocaína.", {
	'entities':  [(50, 57, 'DRUG')]
}),

("Así lo informaron a LA NACION fuentes del Ministerio de Seguridad.", {
	'entities':  [(20, 29, 'ORG'),(42, 65, 'ORG')]
}),

("El hecho ocurrió en las últimas horas cuando personal de la Gendarmería Nacional realizaba un control vehicular sobre la ruta 50, a la altura tura del puente Río Colorado.", {
	'entities':  [(60, 80, 'ORG'),(151, 157, 'MISC'),(158, 170, 'LOC')]
}),

("Cuando el conductor de un Renault Clio azul oscuro que circulaba por la ruta 50 sentido norte-sur advirtió que a pocos metros había un control vehicular de la Gendarmería Nacional, giró en U y intentó escaparse a toda velocidad.", {
	'entities':  [(26, 33, 'ORG'),(72, 79, 'LOC'),(159, 179, 'ORG')]
}),

("Los gendarmes comenzaron una persecución que culminó en la localidad de Hipólito Yrigoyen donde fue hallado el vehículo sospechoso.", {
	'entities':  [(72, 89, 'LOC')]
}),

("Cuando revisaron el auto, los gendarmes encontraron cuatro bolsas con paquetes rectangulares con 99,202 kilos de cocaína.", {
	'entities':  [(113, 120, 'DRUG')]
}),

("El hermano del presunto máximo proveedor de cocaína de la Argentina tenía domicilio en Salvador Mazza, Salta, una de las zonas calientes del tráfico de drogas.", {
	'entities':  [(44, 51, 'DRUG'),(58, 67, 'LOC'),(87, 101, 'LOC'),(103, 108, 'LOC'),(152, 158, 'DRUG')]
}),

("*Nunca nos conformamos hasta detener a todas la piezas de estas redes narco.", {
	'entities':  [(70, 75, 'DRUG')]
}),

("Estábamos atentos porque sabíamos que algún miembro de este clan podría seguir traficando cocaína*, sostuvo la ministra Patricia Bullrich en un comunicado de prensa.", {
	'entities':  [(90, 97, 'DRUG'),(120, 137, 'PER')]
}),

("Informe de Gabriel Di Nicola", {
	'entities':  [(11, 28, 'PER')]
}),

("La nueva guerra entre clanes narco golpeó otra vez la zona sur de Rosario, donde acribillaron a Ulises Funes, de 18 años, el hermano de Alan, quien el 1º de enero pasado fue filmado disparando al aire 15 tiros con una ametralladora, mientras estaba bajo detención domiciliaria por un crimen que cometió cuando era menor de edad.", {
	'entities':  [(29, 34, 'DRUG'),(54, 73, 'LOC'),(96, 108, 'PER'),(136, 140, 'PER')]
}),

("Dos hermanos de la víctima, Alan y Lautaro Funes, lanzaron fuertes amenazas contra sus históricos enemigos en el sur rosarino, la familia Caminos, que desde hace casi dos décadas está vinculada al narcotráfico y a la barra brava de Newell's, y que siempre fueron aliados de la banda Los Monos.", {
	'entities':  [(28, 32, 'PER'),(35, 48, 'PER'),(138, 145, 'PER'),(197, 209, 'DRUG'),(217, 240, 'ORG'),(283, 292, 'ORG')]
}),

("Uno por uno los voy a matar*, escribió Alan en su perfil de Facebook, quien está prófugo tras disparar al aire con una ametralladora.", {
	'entities':  [(39, 43, 'PER'),(60, 68, 'ORG')]
}),

("Estaba detenido acusado del crimen de Julio Solaro, alias *Pupi*, el 1º de mayo de 2016, en venganza por el asesinato de su madre, Mariela Miranda.", {
	'entities':  [(38, 50, 'PER'),(59, 63, 'PER'),(131, 146, 'PER')]
}),

("La fiscalía acusó a Alexis Caminos, de la banda contraria, por ese homicidio.", {
	'entities':  [(20, 34, 'PER')]
}),

("El otro hermano de Ulises que juró vengar su muerte fue Lautaro, quien desde la cárcel de Piñero, donde está detenido desde mayo pasado tras un megaoperativo que hizo la Policía Federal, prometió matar a todas las generaciones de los Caminos.", {
	'entities':  [(19, 25, 'PER'),(56, 63, 'PER'),(80, 86, 'MISC'),(90, 96, 'LOC'),(170, 185, 'ORG'),(230, 241, 'ORG')]
}),

("*La guerra va a terminar cuando los mate a todos, hasta la generación más chica*, posteó en Facebook desde su calabozo.", {
	'entities':  [(92, 100, 'ORG'),(110, 118, 'MISC')]
}),

("La tensión se instaló en Rosario, porque las amenazas de estos jóvenes miembros de dos clanes narco tienden a cumplirse.", {
	'entities':  [(25, 32, 'LOC'),(94, 99, 'DRUG')]
}),

("A pesar de que se incrementaron los controles de la policía y las fuerzas federales en los barrios donde tienen su radio de acción, como La Tablada, Mercado y República de la Sexta, durante los últimos 20 meses hubo 30 homicidios en esa zona.", {
	'entities':  [(137, 147, 'LOC'),(149, 156, 'LOC'),(159, 180, 'LOC')]
}),

("En lo que va del año se produjeron diez crímenes en Rosario.", {
	'entities':  [(52, 59, 'LOC')]
}),

("Anteayer se reunieron el secretario de Seguridad de la Nación, Eugenio Burzaco, con el ministro santafesino, Maximiliano Pullaro, para analizar la coordinación entre fuerzas federales y provinciales frente al aumento de la violencia narco.", {
	'entities':  [(39, 61, 'ORG'),(63, 78, 'PER'),(109, 128, 'PER'),(233, 238, 'DRUG')]
}),

("En diálogo con LA NACION, Pullaro aseguró que la disputa entre estas dos familias *no es una pelea por territorio para el narcotráfico, sino una enemistad histórica*.", {
	'entities':  [(15, 24, 'ORG'),(26, 33, 'PER'),(122, 134, 'DRUG')]
}),

("*Varios de los crímenes se podrían evitar si esas personas siguieran en prisión*, señaló Pullaro.", {
	'entities':  [(72, 79, 'MISC'),(89, 96, 'PER')]
}),

("*La Chancha y el Mono Ale gozaban de total impunidad en Tucumán para llevar adelante sus ilícitos.", {
	'entities':  [(1, 11, 'PER'),(17, 25, 'PER'),(56, 63, 'LOC')]
}),

("Así graficó la operatoria de lavado de los hermanos Ale, Rubén *la Chancha* y Ángel *el Mono*, uno de los investigadores de la Unidad de Información Financiera (UIF) asignados al caso.", {
	'entities':  [(52, 55, 'PER'),(57, 76, 'PER'),(78, 93, 'PER'),(127, 165, 'ORG')]
}),

("Ambos fueron condenados a mediados de diciembre pasado a 10 años de prisión por liderar una asociación ilícita dedicada al lavado de activos provenientes de la trata de personas con fines de explotación sexual y del narcotráfico.", {
	'entities':  [(216, 228, 'DRUG')]
}),

("La simple mención del grupo causaba temor en Tucumán.", {
	'entities':  [(45, 52, 'LOC')]
}),

("El mecanismo de lavado de ese clan, según pudo reconstruir LA NACION, era simple, pero efectivo.", {
	'entities':  [(59, 68, 'ORG')]
}),

("Apenas tres sociedades tenían los hermanos Ale bajo su mando.", {
	'entities':  [(43, 46, 'PER')]
}),

("*Todo era a lo bruto y delante de todo el mundo*, señaló la fuente de la UIF.", {
	'entities':  [(73, 76, 'ORG')]
}),

("Solo durante dos años, entre 2011 y 2013, la UIF -cuyo titular es Mariano Federecci-, en conjunto con la Agencia Federal de Ingresos Públicos, detectó un lavado de activos por $40.000.000, la compra de 130 vehículos, 70 armas, una veintena de propiedades y un campo de 900 hectáreas.", {
	'entities':  [(45, 48, 'ORG'),(66, 83, 'PER'),(105, 141, 'ORG')]
}),

("Con Transportes Lionel SRL compraban camiones para su flota, siempre nuevos, con pagos al contado.", {
	'entities':  [(4, 26, 'ORG')]
}),

("Similar era el funcionamiento de Cinco Estrellas, la agencia de remises del clan.", {
	'entities':  [(33, 48, 'ORG')]
}),

("Los hermanos Ale colocaban el dinero espurio cosechado por sus ilícitos en la empresa al adquirir vehículos.", {
	'entities':  [(13, 16, 'PER'),(78, 85, 'MISC')]
}),

("Entre los investigadores no podían evitar hacer la comparación con la empresa de taxis del narcotraficante colombiano Pablo Escobar Gaviria, mediante la cual empezó a lavar fondos que obtenía por el tráfico de cocaína.", {
	'entities':  [(91, 106, 'DRUG'),(118, 139, 'PER'),(210, 217, 'DRUG')]
}),

("Otra de las joyas del clan tucumano se vincula a la industria del juego y es uno de los puntos en los que los investigadores observan las conexiones políticas de los Ale.", {
	'entities':  [(166, 169, 'PER')]
}),

("Se trata de Point Limits SRL, la sociedad mediante la cual explotaban un casino con máquinas tragamonedas.", {
	'entities':  [(12, 28, 'ORG')]
}),

("El encargado de llevar esa tarea bajo la gestión del entonces gobernador José Alperovich era Armando Cortalezzi, actual presidente del Concejo Deliberante de San Miguel de Tucumán, quien estaba a cargo de la Caja Popular de Ahorros, el organismo de control del juego.", {
	'entities':  [(73, 88, 'PER'),(93, 111, 'PER'),(135, 154, 'ORG'),(158, 179, 'LOC'),(208, 231, 'ORG')]
}),

("Él aparece como el titular de una de las 20 propiedades encontradas en la investigación de la UIF.", {
	'entities':  [(94, 97, 'ORG')]
}),

("Ante esta situación, y por el cargo partidario que tiene Cortalezzi, es que el titular de la UIF le envió una carta al gobernador Juan Manzur.", {
	'entities':  [(57, 67, 'PER'),(93, 96, 'ORG'),(130, 141, 'PER')]
}),

("Federecci aún no recibió respuesta.", {
	'entities':  [(0, 9, 'PER')]
}),

("Esa propiedad, según uno de los testigos del juicio, fue conseguida mediante la coacción efectuada por el clan Ale, que extorsionó a su antiguo dueño para que se la cediese a Cortalezzi.", {
	'entities':  [(106, 114, 'ORG'),(175, 185, 'PER')]
}),

("Se trata de un departamento situado en la calle Salta al 100, en la capital tucumana.", {
	'entities':  [(15, 27, 'MISC'),(42, 60, 'LOC'),(68, 84, 'LOC')]
}),

("El inmueble habría sido un pago realizado por la Chancha Ale, aunque todavía no quedó claro en la Justicia en concepto de qué fue concretada esa entrega.", {
	'entities':  [(49, 60, 'PER')]
}),

("La víctima, que dio testimonio en el juicio, era el abogado Armando Cáceres.", {
	'entities':  [(60, 75, 'PER')]
}),

("Pero esa no fue la única propiedad en la que estuvieron vinculados Cortalezzi y los hermanos Ale.", {
	'entities':  [(67, 77, 'PER'),(93, 96, 'PER')]
}),

("El funcionario le vendió una casa a la Chancha, situada en Adolfo de la Vega 721, de grandes proporciones.", {
	'entities':  [(39, 46, 'PER'),(59, 80, 'LOC')]
}),

("Un dato no menor es que la Chancha Ale se encontraba anotado como monotributista, en la categoría G, que no es la más alta, cuando por el volumen de dinero que manejaban sus negocios tendría que haberse registrado como responsable inscripto.", {
	'entities':  [(27, 38, 'PER')]
}),

("*Por sus ingresos declarados no había forma posible de que tuvieran tanto patrimonio*, afirmó una fuente de la AFIP.", {
	'entities':  [(111, 115, 'ORG')]
}),

("Una de las principales impulsoras de la investigación penal contra los Ale, la madre de la desaparecida Marita Verón, Susana Trimarco, afirmó en pleno juicio que había visto al juez Carlos Jiménez Montilla en un asado con los condenados.", {
	'entities':  [(67, 74, 'ORG'),(104, 116, 'PER'),(118, 133, 'PER'),(182, 205, 'PER')]
}),

("Es que los hermanos Ale comandan el club San Martín, que tuvo un breve paso por la primera división en 2009.", {
	'entities':  [(20, 23, 'PER'),(36, 51, 'ORG')]
}),

("Asimismo, y según consta en una serie de declaraciones, los Ale también habrían entrado en la operatoria de los adelantos del dinero por los derechos de la televisación de los partidos, con el posterior cambio de cheques en financieras ligadas a la AFA.", {
	'entities':  [(56, 63, 'ORG'),(249, 252, 'ORG')]
}),

("La Unidad de Información Financiera (UIF) detectó una irregular transferencia de propiedades entre Armando Cortalezzi, presidente del Concejo Deliberante de San Miguel de Tucumán, y Rubén *la Chancha* Ale, uno de los jefes del clan que fue condenado el mes pasado por lavar dinero del narcotráfico y la trata de personas.", {
	'entities':  [(3, 41, 'ORG'),(99, 117, 'PER'),(134, 153, 'ORG'),(157, 178, 'LOC'),(182, 204, 'PER'),(285, 297, 'DRUG')]
}),

("Ese dato causó preocupación en las autoridades, ya que Cortalezzi estuvo a cargo de la Caja Popular de Ahorros, la entidad que controla el juego en Tucumán.", {
	'entities':  [(55, 65, 'PER'),(87, 110, 'ORG'),(148, 155, 'LOC')]
}),

("Para la Justicia, el clan Ale utilizó un casino para lavar dinero ilegal.", {
	'entities':  [(21, 29, 'ORG'),(41, 47, 'MISC')]
}),

("Durante la gestión del gobernador tucumano José Alperovich, la Chancha Ale se reunió en varias oportunidades con el mandatario provincial en su condición de presidente del club de fútbol San Martín.", {
	'entities':  [(43, 58, 'PER'),(63, 74, 'PER'),(172, 186, 'MISC'),(187, 197, 'ORG')]
}),

("Durante las campañas electorales, el aparato peronista utilizaba la red de remises de los hermanos Ale.", {
	'entities':  [(99, 102, 'PER')]
}),

("Un ex chofer oficial del actual presidente de la Cámara de Diputados de Entre Ríos y ex gobernador de la provincia, Sergio Urribarri , será juzgado a partir del 3 de abril próximo, acusado de haber transportado en 2014 unos 20 kilos de cocaína, informaron fuentes judiciales.", {
	'entities':  [(49, 68, 'ORG'),(72, 82, 'LOC'),(116, 132, 'PER'),(236, 243, 'DRUG')]
}),

("Se trata de Marcelo Alejandro Acosta, de 52 años, a quien el Tribunal Oral Federal (TOF) de Rosario extendió la prisión preventiva y dispuso el inicio del juicio oral y público.", {
	'entities':  [(12, 36, 'PER'),(61, 88, 'ORG'),(92, 99, 'LOC')]
}),

("Ambas medidas fueron dispuestas por los jueces Beatriz Caballero de Barabani, Omar Digerónimo y Otmar Paulucci, quienes tendrán a su cargo el juicio al ex chofer y a otros cinco acusados de integrar una organización dedicada al tráfico de drogas con ramificaciones en distintos puntos del país.", {
	'entities':  [(47, 76, 'PER'),(78, 93, 'PER'),(96, 110, 'PER'),(239, 245, 'DRUG')]
}),

("Acosta fue detenido el 13 de mayo de 2014, cuando circulaba a bordo de un auto Peugeot 307, chapa patente EEG-741, en el que eran trasladados 20 kilos de cocaína por una ruta cerca de Rosario.", {
	'entities':  [(0, 6, 'PER'),(79, 86, 'ORG'),(154, 161, 'DRUG'),(184, 191, 'LOC')]
}),

("El auto interceptado fue el mismo que había sido utilizado días antes por Gonzalo Caudana, acusado de ser uno de los jefes del narcotráfico en Paraná, detenido en la Unidad Penal N°1 de la capital provincial.", {
	'entities':  [(74, 89, 'PER'),(127, 139, 'DRUG'),(143, 149, 'LOC'),(166, 182, 'ORG')]
}),

("Acosta está acusado de colaborar en actividades de comercio de estupefacientes, en su caso como transportista, agravado por la intervención de más de tres personas, y podría recibir una pena de entre seis y veinte años de cárcel.", {
	'entities':  [(0, 6, 'PER'),(63, 78, 'DRUG'),(222, 228, 'MISC')]
}),

("Mientras tanto, está suspendido en sus funciones en el Estado y tiene abierto un sumario administrativo.", {
	'entities':  [(55, 61, 'ORG')]
}),

("En su decisión, el tribunal resaltó que *las restricciones de la libertad de una persona durante el proceso sólo puede tener fines cautelares y no sancionatorios pues si esto último sucediera, se atentaría contra el principio de inocencia*.", {
	'entities':  [(19, 27, 'MISC')]
}),

("La investigación se había iniciado cinco años antes, centrada en un narcotraficante internacional que se había instalado en Misiones, en una chacra que tenía muy cerca del río Paraná.", {
	'entities':  [(68, 83, 'DRUG'),(124, 132, 'LOC'),(141, 147, 'MISC'),(172, 182, 'LOC')]
}),

("La sospecha de los investigadores es que desde allí se gestionaba el ingreso de importantes cargamentos de marihuana provenientes de Paraguay, para luego insertarlos en distintos mercados, sobre todo, en Chile y la Patagonia argentina.", {
	'entities':  [(107, 116, 'DRUG'),(133, 141, 'LOC'),(204, 209, 'LOC'),(215, 234, 'LOC')]
}),

("Con información de la agencia Télam", {
	'entities':  [(30, 35, 'ORG')]
}),

("ROSARIO.- El dinero de Los Monos se derramó con fluidez en distintas zonas grises de la economía.", {
	'entities':  [(0, 7, 'LOC'),(23, 32, 'ORG')]
}),

("Francisco Lapiana, el cazatalentos que trabajaba para la banda, tenía olfato para encontrar esos diamantes en los barrios pobres y pueblos cercanos que caminaba los fines de semana cuando se juegan los picados de fútbol.", {
	'entities':  [(0, 17, 'PER')]
}),

("Ángel Correa y Ever Banega.", {
	'entities':  [(0, 12, 'PER'),(15, 26, 'PER')]
}),

("Ambos conservan los lazos con sus orígenes, y devuelven esa gratitud cada tanto cuando vuelven a jugar a la cancha del barrio La Granada, que tiene como escenografía el mural en honor al líder de Los Monos Claudio Cantero, alias *Pájaro*, asesinado el 26 de mayo de 2013.", {
	'entities':  [(126, 136, 'LOC'),(196, 205, 'ORG'),(206, 221, 'PER'),(230, 236, 'PER')]
}),

("Correa deberá regresar de Madrid e interrumpir la temporada en el Atlético para declarar el 11 de diciembre próximo en el juicio que se inició hace una semana contra la banda de Los Monos.", {
	'entities':  [(0, 6, 'PER'),(26, 32, 'LOC'),(66, 74, 'ORG'),(178, 187, 'ORG')]
}),

("En el banquillo está sentado entre los 25 imputados Lapiana, el alfil de los Cantero en el negocio del fútbol y quien conserva el 20 por ciento del pase del jugador del seleccionado argentino.", {
	'entities':  [(52, 59, 'PER'),(77, 84, 'PER')]
}),

("La familia de Correa intentó radicarse en la capital española, pero nunca se pudo adaptar y volvió a La Granada, ese barrio repleto de contrastes.", {
	'entities':  [(14, 20, 'PER'),(101, 111, 'LOC')]
}),

("Lapiana había intervenido además en los pases de dos rosarinos de pie magnífico y con partidos en el seleccionado.", {
	'entities':  [(0, 7, 'PER')]
}),

("Ever Banega, ex volante central de Boca, Newell's, Valencia y Sevilla, y César Delgado, delantero de Rosario Central, Cruz Azul y Paris Saint Germain.", {
	'entities':  [(0, 11, 'PER'),(35, 39, 'ORG'),(41, 49, 'ORG'),(51, 59, 'ORG'),(62, 69, 'ORG'),(73, 86, 'PER'),(101, 116, 'ORG'),(118, 127, 'ORG'),(130, 149, 'ORG')]
}),

("Los dos futbolistas son de la zona de Los Monos, los dos surgieron de Alianza Sport, el club que Lapiana manejaba con la influencia económica de Ramón Machuca, uno de los líderes de Los Monos.", {
	'entities':  [(38, 47, 'ORG'),(70, 83, 'ORG'),(88, 92, 'MISC'),(97, 104, 'PER'),(145, 158, 'PER'),(182, 191, 'ORG')]
}),

("En la Justicia se investiga que Los Monos y Lapiana compartían intereses en unos 120 futbolistas con el objetivo de blanquear el dinero del narcotráfico.", {
	'entities':  [(32, 41, 'ORG'),(44, 51, 'PER'),(140, 152, 'DRUG')]
}),

("Correa nació el 9 de marzo de 1995 en La Granada.", {
	'entities':  [(0, 6, 'PER'),(38, 48, 'LOC')]
}),

("A los 10 años emigró de ese barrio para recalar en River.", {
	'entities':  [(51, 56, 'ORG')]
}),

("A los 15 llegó a San Lorenzo.", {
	'entities':  [(17, 28, 'ORG')]
}),

("Cuando no había debutado en el club del Bajo Flores Diego Simeone envió un representante del Atlético de Madrid a seguirlo.", {
	'entities':  [(31, 35, 'MISC'),(40, 51, 'LOC'),(52, 65, 'PER'),(93, 111, 'ORG')]
}),

("En 2007 por pedido de Marcela Martínez, la madre de Correa, Lapiana se convirtió en su manager.", {
	'entities':  [(22, 38, 'PER'),(52, 58, 'PER'),(60, 67, 'PER')]
}),

("En 2012 lo cedió a San Lorenzo reteniendo el 30 por ciento del pase.", {
	'entities':  [(19, 30, 'ORG')]
}),

("Para entonces Lapiana, contó en el juzgado, le pagaba el contrato de alquiler al futbolista en un departamento de la calle Thompson, en Caballito.", {
	'entities':  [(14, 21, 'PER'),(117, 131, 'LOC'),(136, 145, 'LOC')]
}),

("Lapiana es un hombre astuto, de conversación fluida, muy conocido en el ámbito del fútbol de inferiores de Santa Fe.", {
	'entities':  [(0, 7, 'PER'),(107, 115, 'ORG')]
}),

("Actualmente es dueño de una flota de camiones en Paraguay y propietario de un edificio de departamentos a veinte cuadras del Monumento a la Bandera.", {
	'entities':  [(49, 57, 'LOC'),(78, 86, 'MISC'),(125, 147, 'LOC')]
}),

("El radar judicial recayó sobre Lapiana y Correa en la investigación contra Los Monos cuando Marcelo Tinelli dijo que no vendería al jugador en 2013.", {
	'entities':  [(31, 38, 'PER'),(41, 47, 'PER'),(75, 84, 'ORG'),(92, 107, 'PER')]
}),

("El juez Juan Carlos Vienna, a cargo de la instrucción de Los Monos, paró las antenas.", {
	'entities':  [(8, 26, 'PER'),(57, 66, 'ORG')]
}),

("El ruido de la declaración hizo pensar al juez que esa frase estaba, en realidad, destinada a elevar la cotización del chico de Las Flores.", {
	'entities':  [(128, 138, 'LOC')]
}),

("Decidió entonces embargar los derechos federativos del volante por entender que las escuchas eran claras respecto a que Lapiana compartía un porcentaje del pase con Machuca, líder de Los Monos, a quien la Fiscalía pidió en el inicio del juicio condenarlo a 41 años de prisión.", {
	'entities':  [(120, 127, 'PER'),(165, 172, 'PER'),(183, 192, 'ORG'),(205, 213, 'MISC')]
}),

("Lapiana fue detenido e imputado formalmente como miembro de la banda en carácter de lavador del dinero producido ilegalmente.", {
	'entities':  [(0, 7, 'PER')]
}),

("Tras su declaración se reforzaron las sospechas judiciales de que Los Monos y Lapiana compartían intereses en unos 120 futbolistas.", {
	'entities':  [(66, 75, 'ORG'),(78, 85, 'PER')]
}),

("El sumariante le empezó a nombrar a jugadores de los que, en los diálogos con Monchi Cantero, aparecían como dueños de los pases.", {
	'entities':  [(78, 92, 'PER')]
}),

("Lapiana hablaba de su actividad de cazatalentos.", {
	'entities':  [(0, 7, 'PER')]
}),

("Si me gusta un jugador lo hablo al padre para que saque el pase del club, lo llevo a los clubes de Buenos Aires, los dejo una semana para que los prueben.", {
	'entities':  [(99, 111, 'LOC')]
}),

("Lo hago para Lanús, para River.", {
	'entities':  [(13, 18, 'ORG'),(25, 30, 'ORG')]
}),

("Eso es lo que pasó con Angelito en San Lorenzo*, dijo.", {
	'entities':  [(23, 31, 'PER'),(35, 46, 'ORG')]
}),

("Y en diálogo con LA NACION, agregó: *Cada vez está más complicado, porque los pibes ya no comen vidrio.", {
	'entities':  [(17, 26, 'ORG')]
}),

("Y antes de debutar en primera te exigen vivir en Puerto Madero*.", {
	'entities':  [(49, 62, 'LOC')]
}),

("Las sospechas de que el pase de Correa pertenecía a la familia Cantero surgieron a partir de escuchas telefónicas entre integrantes del grupo y Lapiana, representante del jugador, que firmó el 21 de septiembre de 2012 un contrato por cuatro años con San Lorenzo.", {
	'entities':  [(32, 38, 'PER'),(63, 70, 'PER'),(144, 151, 'PER'),(250, 261, 'ORG')]
}),

("Se acrecentaron cuando varios miembros de Los Monos acordaron viajar al estadio del Bajo Flores.", {
	'entities':  [(42, 51, 'ORG'),(72, 79, 'MISC'),(84, 95, 'LOC')]
}),

("Fue el 11 de mayo de 2013 y San Lorenzo recibió a Boca en el Nuevo Gasómetro.", {
	'entities':  [(28, 39, 'ORG'),(50, 54, 'ORG'),(61, 76, 'LOC')]
}),

("Era el segundo partido de Correa con la camiseta azulgrana.", {
	'entities':  [(26, 32, 'PER')]
}),

("Con ese gol, San Lorenzo ganó 3 a 0.", {
	'entities':  [(13, 24, 'ORG')]
}),

("Esa noche de sábado Monchi Cantero y sus lugartenientes Emanuel Chamorro y Mariano Salomón estuvieron en la platea.", {
	'entities':  [(20, 34, 'PER'),(56, 72, 'PER'),(75, 90, 'PER')]
}),

("Las escuchas telefónicas revelan la euforia de los miembros de la banda y la enorme satisfacción por el desempeño de Correa.", {
	'entities':  [(117, 123, 'PER')]
}),

("Tres horas después del final del partido, Lapiana, desde su departamento en Puerto Madero, habló por teléfono con Monchi.", {
	'entities':  [(42, 49, 'PER'),(76, 89, 'LOC'),(114, 120, 'PER')]
}),

("*Jugó rebien*, respondió Monchi, que estaba junto al jugador, en su departamento.", {
	'entities':  [(25, 31, 'PER')]
}),

("El narcotráfico ya había comenzado a hurgar por las grietas del negocio del fútbol unos años antes.", {
	'entities':  [(3, 15, 'DRUG')]
}),

("Patricio Gorosito, quien fue condenado a 21 años de prisión por ser considerado uno de los líderes de una de las bandas más importantes que traficaba cocaína a Europa, llegó a tener 80 jugadores, ubicados en diferentes países de América del Sur.", {
	'entities':  [(0, 17, 'PER'),(150, 157, 'DRUG'),(160, 166, 'LOC'),(229, 244, 'LOC')]
}),

("Este hombre de 67 años, que está detenido en su casa de Arroyo Seco, confesó haber sido *testaferro* de Julio Grondona.", {
	'entities':  [(56, 67, 'LOC'),(104, 118, 'PER')]
}),

("La penetración narco en el negocio del fútbol", {
	'entities':  [(15, 20, 'DRUG')]
}),

("El delantero del Atlético de Madrid fue citado a prestar declaración testimonial el 11 de diciembre próximo en el juicio que se sigue contra Los Monos;el jugador creció en el barrio rosarino de La Granada,una de las zonas controladas por el clan narco", {
	'entities':  [(141, 150, 'ORG'),(194, 204, 'LOC'),(246, 251, 'DRUG')]
}),

("Además del caso de Ángel Correa, los investigadores estiman que Los Monos tendrían participación en los contratos de unos 120 futbolistas, incluso de varios destacados, como Ever Banegas y César Delgado", {
	'entities':  [(19, 31, 'PER'),(64, 73, 'ORG'),(174, 186, 'PER'),(189, 202, 'PER')]
}),

("El vínculo entre la organización criminal rosarina y el mundo del fútbol sería el representante de jugadores Francisco Lapiana.", {
	'entities':  [(109, 126, 'PER')]
}),

("Así lo considera la fiscalía en el juicio contra Los Monos, ya que ese *cazatalentos* es uno de los 25 acusados.", {
	'entities':  [(49, 58, 'ORG')]
}),

("Escuchas telefónicas demostrarían su relación con Ramón Machuca, con quien compartiría los derechos de Ángel Correa", {
	'entities':  [(50, 63, 'PER'),(103, 115, 'PER')]
}),

("El club rosarino Alianza Sport es una cuna de talentos futbolísticos, como Ever Banega y César Delgado, aunque se sospecha que allí influyen decisivamente Los Monos", {
	'entities':  [(3, 7, 'MISC'),(17, 30, 'ORG'),(75, 86, 'PER'),(89, 102, 'PER'),(155, 164, 'ORG')]
}),

("El narcomenudeo es hoy el problema más importante vinculado con las drogas.", {
	'entities':  [(3, 15, 'DRUG'),(68, 74, 'DRUG')]
}),

("En las zonas donde se instala la venta minorista de estupefacientes crece la violencia.", {
	'entities':  [(52, 67, 'DRUG')]
}),

("Eso quedó demostrado, incluso, con las estadísticas de homicidios en la ciudad de Buenos Aires.", {
	'entities':  [(72, 94, 'LOC')]
}),

("Dos áreas bajo disputa de grupos narcos, las villas 31 y 1-11-14, concentraron la mayor cantidad de asesinatos.", {
	'entities':  [(33, 39, 'DRUG'),(45, 64, 'LOC')]
}),

("Durante muchos años se dejó de lado la lucha directa contra los quioscos narcos y se tomó judicialmente esos puntos de comercialización como simples eslabones débiles de la cadena del narcotráfico.", {
	'entities':  [(73, 79, 'DRUG'),(184, 196, 'DRUG')]
}),

("En el barrio Mitre quedó expuesto que los grupos locales se enfrentan con el sangriento intento de penetración de bandas con soportes logísticos establecidos en el Bajo Flores.", {
	'entities':  [(6, 18, 'LOC'),(164, 175, 'LOC')]
}),

("En esa zona la lucha también se mantiene, casi de manzana a manzana en el asentamiento ubicado frente al estadio de San Lorenzo.", {
	'entities':  [(105, 112, 'MISC'),(116, 127, 'ORG')]
}),

("Y en la villa 31 las ejecuciones son ahora dentro de las propias bandas, ya que por la mayor presencia policial los clanes no avanzan directamente sobre sus rivales, sino que compran con dinero los puestos de venta adversarios.", {
	'entities':  [(8, 16, 'LOC')]
}),

("También en Rosario los narcos están activos en sus disputas a balazos.", {
	'entities':  [(11, 18, 'LOC'),(23, 29, 'DRUG')]
}),

("Allí Los Monos, con la mayoría de sus jefes en prisión, tienen la emergente competencia de otros dos clanes familiares, los Funes y los Caminos.", {
	'entities':  [(5, 14, 'ORG'),(120, 129, 'ORG'),(132, 143, 'ORG')]
}),

("Y las ametralladoras son la herramienta más contundente en la negociación narco.", {
	'entities':  [(74, 79, 'DRUG')]
}),

("En el conurbano la situación no es mejor.", {
	'entities':  [(6, 15, 'LOC')]
}),

("Moreno fue escenario de varias masacres por ventas de drogas.", {
	'entities':  [(0, 6, 'LOC'),(54, 60, 'DRUG')]
}),

("El narcomenudeo merece la mayor atención.", {
	'entities':  [(3, 15, 'DRUG')]
}),

("Así hablaban por teléfono dos de los seis sospechosos detenidos en las últimas horas acusados de integrar una banda narco que operaba desde el tradicional Olivos Golf Club.", {
	'entities':  [(116, 121, 'DRUG')]
}),

("Se referían a una técnica que les permitía estirar 20% cada kilo de clorhidrato de cocaína con el mismo efecto alcaloide como si se tratara de una sustancia de máxima pureza.", {
	'entities':  [(147, 156, 'DRUG')]
}),

("La conversación, según informaron a LA NACION calificadas fuentes judiciales, ocurrió el 16 de este mes.", {
	'entities':  [(36, 45, 'ORG')]
}),

("Faltaban diez días para los operativos hechos por la Gendarmería Nacional que culminaron con los seis sospechosos detenidos, el secuestro de 25 paquetes de cocaína, armas, $67.000, US$7722, 160 pesos bolivianos y precursores químicos.", {
	'entities':  [(53, 73, 'ORG'),(156, 163, 'DRUG')]
}),

("El coso parecía un laboratorio.", {
	'entities':  [(19, 30, 'MISC')]
}),

("El que hablaba es un técnico en Comercio Internacional y agente de transporte aduanero que había alquilado dos casas en el exclusivo Olivos Golf Club, las dos propiedades fueron allanadas anteayer por orden del juez federal de Lomas de Zamora Federico Villena.", {
	'entities':  [(133, 149, 'ORG'),(227, 242, 'LOC'),(243, 259, 'PER')]
}),

("Los interlocutores se referían al trabajado que hacían dos ciudadanos colombianos en el *laboratorio* para estirar la cocaína que habían instalado en una propiedad de Emilio Castro al 4800, en Villa Luro.", {
	'entities':  [(89, 100, 'MISC'),(118, 125, 'DRUG'),(167, 188, 'LOC'),(193, 203, 'LOC')]
}),

("Los dos ciudadanos colombianos, según información aportada por la Dirección Nacional de Migraciones a la Justicia, llegaron el 12 de este mes en un vuelo de Aerolíneas Argentinas que aterrizó en el aeroparque metropolitano Jorge Newbery a las 17.50.", {
	'entities':  [(66, 113, 'ORG'),(157, 178, 'ORG'),(198, 208, 'MISC'),(198, 236, 'LOC')]
}),

("Habían volado desde Bolivia.", {
	'entities':  [(20, 27, 'LOC')]
}),

("Los sospechosos no sabían que detectives de la Gendarmería Nacional estaban tras sus pasos.", {
	'entities':  [(47, 67, 'ORG')]
}),

("Pero desde hace unos meses eran investigados por el fiscal federal de Lomas de Zamora Sergio Mola y la Procuraduría de Narcocriminalidad (Procunar), a cargo del fiscal Diego Iglesias.", {
	'entities':  [(70, 85, 'LOC'),(86, 97, 'PER'),(103, 147, 'ORG'),(168, 182, 'PER')]
}),

("Los investigadores tuvieron un aporte sustancial de la agencia antidrogas de los Estados Unidos (DEA, por su nombre en inglés).", {
	'entities':  [(55, 73, 'MISC'),(81, 95, 'LOC'),(97, 100, 'ORG')]
}),

("Después se sumó la colaboración de la Agencia Federal de Inteligencia (AFI).", {
	'entities':  [(38, 75, 'ORG')]
}),

("Los investigadores no tuvieron dudas de que los sospechosos habían instalado un laboratorio en la propiedad de Villa Luro cuando revisaron la basura que arrojaron en un contenedor.", {
	'entities':  [(111, 121, 'LOC')]
}),

("Los gendarmes agarraron dos bolsas de residuos cuyo contenido fue analizado por la Dirección de Criminalística y Estudios Forenses de la Gendarmería.", {
	'entities':  [(83, 148, 'ORG')]
}),

("*En la primera bolsa se hallaron doce guantes de látex blancos, trece bolsas de nylon transparentes, dos trozos de papel blanco y un envoltorio de goma, todo ello con restos de sustancia polvorienta de color blanco al igual que la bolsa.", {
	'entities':  [(177, 214, 'DRUG')]
}),

("En consecuencia, se realizó el test orientativo con los restos de las sustancias encontradas en dicha bolsa dando resultado positivo para clorhidrato de cocaína*, según consta en el expediente judicial.", {
	'entities':  [(138, 160, 'DRUG')]
}),

("Ayer los seis sospechosos se negaron a prestar declaración indagatoria en la audiencia donde estuvieron el juez Villena y representantes del Ministerio Público Fiscal.", {
	'entities':  [(112, 119, 'PER'),(141, 166, 'ORG')]
}),

("Según sostuvo el fiscal Mola en el dictamen donde pidió las detenciones de los sospechosos, los dos ciudadanos colombianos *tendrían un acabado conocimiento sobre el proceso de estiramiento y/o producción del material estupefaciente que le estarían enseñando al técnico en Comercio Internacional*.", {
	'entities':  [(24, 28, 'PER')]
}),

("Un hombre de 37 años fue asesinado ayer frente a dos de sus ocho hijos en la ciudad de Rosario.", {
	'entities':  [(87, 94, 'LOC')]
}),

("La esposa de la víctima aseguró que fue una venganza, ya que su pareja había dejado de vender drogas, informaron fuentes policiales y judiciales.", {
	'entities':  [(94, 100, 'DRUG')]
}),

("La víctima, identificada como Roberto Godoy, fue baleada desde un automóvil mientras estacionaba en el garaje de su casa.", {
	'entities':  [(30, 43, 'PER')]
}),

("Según su esposa, el motivo del asesinato fue la decisión de Godoy de dejar el negocio del narcomenudeo, por lo que cree que los autores del crimen estarían vinculados a una *puntera* de otro barrio para quien comercializaban droga.", {
	'entities':  [(60, 65, 'PER'),(90, 102, 'DRUG'),(225, 230, 'DRUG')]
}),

("El crimen se produjo anteanoche, en la vivienda situada en Olivé al 2400, cuando Godoy estaba junto a dos de sus hijos, que presenciaron la balacera, precisaron voceros policiales.", {
	'entities':  [(59, 72, 'LOC'),(81, 86, 'PER')]
}),

("*Voy a decir la verdad, vendíamos droga hace mucho tiempo, vendíamos para ellos y les dijimos que no*, contó sorpresivamente la esposa de la víctima, identificada como Virginia.", {
	'entities':  [(168, 176, 'PER')]
}),

("El hombre recibió varios disparos y fue trasladado por familiares al Hospital Alberdi, donde falleció, según informó el Ministerio Público de la Acusación.", {
	'entities':  [(69, 85, 'ORG'),(120, 154, 'ORG')]
}),

("Según contó uno de los hijos, menor de edad, cuando se bajó del auto de su padre escuchó varias detonaciones desde un Chevrolet Corsa color gris.", {
	'entities':  [(118, 127, 'ORG')]
}),

("Tres de los sospechosos estarían identificados, señalaron desde la fiscalía que investiga el caso, a cargo de Eugenio Malaponte.", {
	'entities':  [(110, 127, 'PER')]
}),

("*Teníamos miedo, estábamos bajando con los chicos, aparece un auto y sin mediar palabra dispara*, relató la mujer de la víctima, en declaraciones a Canal 3 de Rosario.", {
	'entities':  [(148, 155, 'ORG'),(159, 166, 'LOC')]
}),

("Para ella el crimen está vinculado a la decisión de dejar de vender drogas para una mujer del barrio La Cerámica.", {
	'entities':  [(68, 74, 'DRUG'),(94, 112, 'LOC')]
}),

("Con dos de las tres incautaciones más importantes de cocaína registradas en la Argentina, se alcanzó el año pasado un récord de decomisos de drogas.", {
	'entities':  [(53, 60, 'DRUG'),(141, 147, 'DRUG')]
}),

("El Ministerio de Seguridad informó ayer que fueron secuestradas 15 toneladas de cocaína al sumarse los operativos realizados por la Policía Federal, Gendarmería, Prefectura y Policía de Seguridad Aeroportuaria con los golpes al narcotráfico conseguidos por las policías provinciales.", {
	'entities':  [(3, 26, 'ORG'),(80, 87, 'DRUG'),(132, 147, 'ORG'),(149, 160, 'ORG'),(162, 172, 'ORG'),(175, 209, 'ORG'),(228, 240, 'DRUG')]
}),

("Esa cifra prácticamente duplica la cantidad de cocaína capturada por todas las fuerzas de seguridad durante 2016.", {
	'entities':  [(47, 54, 'DRUG')]
}),

("También se notificó un mejor registro de incautaciones de marihuana con relación a 2016.", {
	'entities':  [(58, 67, 'DRUG')]
}),

("El año pasado fueron decomisadas 128 toneladas de cannabis, cifra que representa un aumento de 4,5 por ciento con relación al período anterior.", {
	'entities':  [(50, 58, 'DRUG')]
}),

    ("Más allá de las cifras, los operativos antidrogas se mantienen y este fin de semana fue detectado un cargamento de 350 kilos de marihuana en la ciudad correntina de Ituzaingó.", {
	'entities':  [(128, 137, 'DRUG'),(165, 174, 'LOC')]
}),

("Casi un tercio de la marihuana incautada en la Argentina fue decomisada en Corrientes, según las cifras del Ministerio de Seguridad.", {
	'entities':  [(21, 30, 'DRUG'),(47, 56, 'LOC'),(75, 85, 'LOC'),(108, 131, 'ORG')]
}),

("*Es el año que más se incautó en toda la historia argentina y también es el salto interanual más alto de decomiso de cocaína con un incremento de casi el ciento por ciento*, afirmó a Télam el subsecretario de Lucha contra el Narcotráfico, Martín Verrier, y señaló que en 2016 se habían secuestrado 8,5 toneladas de cocaína.", {
	'entities':  [(117, 124, 'DRUG'),(183, 188, 'ORG'),(239, 253, 'PER'),(315, 322, 'DRUG')]
}),

("En la edición del pasado 20 de diciembre, LA NACION consignó que se estaba frente a un año récord de capturas de cargamentos de cocaína, si se toma en cuenta el resultado de 12 toneladas de esa droga incautada por las fuerzas federales.", {
	'entities':  [(42, 51, 'ORG'),(128, 135, 'DRUG'),(194, 199, 'DRUG')]
}),

("El Ministerio de Seguridad confirmó ayer que se trató del ciclo anual con mejor registro de decomisos al sumarse los resultados obtenidos por las policías provinciales.", {
	'entities':  [(3, 26, 'ORG')]
}),

("El 20 de diciembre pasado se había informado la captura de una red narco que trasladaba cargamentos de cocaína entre Salta y el conurbano bonaerense.", {
	'entities':  [(67, 72, 'DRUG'),(103, 110, 'DRUG'),(117, 122, 'LOC'),(128, 148, 'LOC')]
}),

("En ese operativo se decomisaron 1116 kilos de cocaína, el tercer golpe en importancia en 2017 y uno de los diez mayores anotados en los últimos 20 años.", {
	'entities':  [(46, 53, 'DRUG')]
}),

("Ese registro histórico arranca con el llamado Operativo Strawberry, momento en que se incautaron 2200 kilos de cocaína en 1997.", {
	'entities':  [(111, 118, 'DRUG')]
}),

("El segundo procedimiento con mayor volumen de captura de cocaína se produjo en junio pasado, con 2000 kilos decomisados a una organización transnacional que planeaba enviar ese cargamento a España, oculto en una exportación de bobinas que estaban listas para ser embarcadas en el puerto de Bahía Blanca.", {
	'entities':  [(57, 64, 'DRUG'),(190, 196, 'LOC'),(290, 302, 'LOC')]
}),

("Veinte días después se consiguió el tercer registro de captura de cocaína más importante en dos décadas.", {
	'entities':  [(66, 73, 'DRUG')]
}),

("Se investigó la actividad de vuelos ilegales que *bombardeaban* cocaína en un campo en la provincia de Santiago del Estero y se decomisó un cargamento de 1838 kilos de cocaína.", {
	'entities':  [(103, 122, 'LOC'),(168, 175, 'DRUG')]
}),

("Las autoridades del ministerio conducido por Patricia Bullrich estimaron que las 15 toneladas de cocaína incautadas en 2017 provocaron una pérdida de 155 millones de dólares a los grupos narcos.", {
	'entities':  [(45, 62, 'PER'),(97, 104, 'DRUG'),(187, 193, 'DRUG')]
}),

("*El récord histórico es la respuesta al incremento de operatividad que estamos teniendo, con muchos más operativos, más detenidos, y aparte lo que registramos también es un aumento del precio de la cocaína en la calle*, explicó Verrier al ser consultado por Télam sobre el incremento de las cifras.", {
	'entities':  [(198, 205, 'DRUG'),(228, 235, 'PER'),(258, 263, 'PER')]
}),

("En el caso de la cocaína, el costo se duplicó entre septiembre de 2016 y octubre de 2017: llegó a 250 pesos la dosis (alrededor de un gramo) en las calles de la ciudad de Buenos Aires y alrededores, donde esta droga tiene una pureza del 60 por ciento.", {
	'entities':  [(17, 24, 'DRUG'),(111, 116, 'DRUG'),(161, 183, 'LOC'),(210, 215, 'DRUG')]
}),

("*Esto demuestra que, a medida que se empieza a dificultar el acceso a la cocaína más pura, empiezan a cortarla más*, explicó Verrier.", {
	'entities':  [(73, 80, 'DRUG'),(125, 132, 'PER')]
}),

("Toneladas de cocaína", {
	'entities':  [(13, 20, 'DRUG')]
}),

("El mayor golpe al narcotráfico registrado este año fue el decomiso de 2000 kilos de cocaína que estaban ocultos en bobinas de exportación", {
	'entities':  [(84, 91, 'DRUG')]
}),

("Toneladas de marihuana", {
	'entities':  [(13, 22, 'DRUG')]
}),

("Casi un tercio de los embarques de cannabis secuestrados en 2017 fueron detectados en Corrientes; solo en la ciudad de Itatí se incautaron 4,6 toneladas", {
	'entities':  [(35, 43, 'DRUG'),(86, 96, 'LOC'),(109, 124, 'LOC')]
}),

("Un adolescente de 19 años se convirtió este mes en el enemigo público N° 1 en Rosario.", {
	'entities':  [(78, 85, 'LOC')]
}),

("Desafiante con su ametralladora FMK3, el arma policial preferida por los narcos argentinos, Alan Funes lanzó a su clan a un enfrentamiento abierto contra la familia Caminos.", {
	'entities':  [(92, 102, 'PER'),(165, 172, 'PER')]
}),

("Cuando Los Monos parecían contenidos con los arrestos de sus jefes y principales sicarios, la sangre llegó nuevamente a las calles.", {
	'entities':  [(7, 16, 'ORG')]
}),

("Otra vez Rosario quedó como escenario de una guerra narco, que suma al menos 15 muertos este año y unos 30 en los últimos 20 meses.", {
	'entities':  [(9, 16, 'LOC')]
}),

("Pese a algunos momentos de aparente calma, la tensión narco se mantiene en las villas 1-11-14 y 31.", {
	'entities':  [(79, 98, 'LOC')]
}),

("En Barrio Mitre, en el barrio porteño de Saavedra, los vendedores locales de drogas pelean con la expansión propuesta por organizaciones radicadas en el Bajo Flores.", {
	'entities':  [(3, 15, 'LOC'),(23, 49, 'LOC'),(77, 83, 'DRUG'),(153, 164, 'LOC')]
}),

("Y en La Plata al menos tres grupos buscan *colonizar* la calle 524.", {
	'entities':  [(5, 13, 'LOC'),(57, 66, 'LOC')]
}),

("*Estos son grupos que pueden tener alguna complejidad en su organización y pueden tener que ver con la comercialización de estupefacientes, pero en los homicidios vemos que tienen que ver más con peleas de barras, tribales, familiares*, explicó en los últimos días el ministro de Seguridad de Santa Fe, Maximiliano Pullaro.", {
	'entities':  [(123, 138, 'DRUG'),(280, 301, 'ORG'),(303, 322, 'PER')]
}),

("De todas maneras, el encadenamiento de asesinatos y la exposición pública buscada por los narcos -Alan Funes difundió un video mientras disparaba su ametralladora- aumentaron la preocupación.", {
	'entities':  [(98, 108, 'PER')]
}),

("En los próximos días, la ministra de Seguridad, Patricia Bullrich, se reunirá con el gobernador santafesino, Miguel Lifschitz, para coordinar operativos especiales.", {
	'entities':  [(48, 65, 'PER'),(109, 125, 'PER')]
}),

("La situación de Rosario sirve como ejemplo concreto de la actualidad narco argentina.", {
	'entities':  [(16, 23, 'LOC')]
}),

("En Rosario eso ocurre en los barrios La Tablada, Mercado y República de la Sexta, por ejemplo, ubicados en la zona sur.", {
	'entities':  [(3, 10, 'LOC'),(29, 47, 'LOC'),(49, 56, 'LOC'),(59, 80, 'LOC'),(110, 118, 'LOC')]
}),

("Tanto en la villa 1-11-14 como en la villa 31 los enfrentamientos dividen a las bandas de acuerdo con la nacionalidad.", {
	'entities':  [(12, 25, 'LOC'),(37, 45, 'LOC')]
}),

("Informaciones de inteligencia criminal determinaron que en el Bajo Flores el clan de origen peruano tiene influencia en las avenidas Perito Moreno, Varela y Riestra, desde la manzana 21 a la 30, mientras que la banda de nacionalidad paraguaya controla las manzanas 5, 6, 7, 8, 9A, 9B y 26.", {
	'entities':  [(62, 73, 'LOC'),(133, 146, 'LOC'),(148, 154, 'LOC'),(157, 164, 'LOC'),(256, 288, 'LOC')]
}),

("Parte de la organización de origen peruano, al menos una derivación de ese grupo, busca expandir sus actividades al barrio de Saavedra, a la zona conocida como Barrio Mitre.", {
	'entities':  [(116, 134, 'LOC'),(160, 172, 'LOC')]
}),

("Los investigadores estiman que allí se procura establecer una cabecera de acopio de drogas para abastecer luego los búnkeres de la villa 1-11-14.", {
	'entities':  [(84, 90, 'DRUG'),(116, 124, 'MISC'),(131, 144, 'LOC')]
}),

("Una investigación del juez federal Sergio Torres señaló la semana pasada que Marcos Estrada González, el detenido jefe del clan peruano, obtenía ganancias de al menos $500.000 cada día.", {
	'entities':  [(35, 48, 'PER'),(77, 100, 'PER')]
}),

("La expansión narco desde la 1-11-14, tal como estaría en marcha con Barrio Mitre como objetivo, no es nueva.", {
	'entities':  [(28, 35, 'LOC'),(68, 80, 'LOC')]
}),

("Causó una guerra que continúa, atenuada hoy por la presencia de fuerzas federales, en la villa 31.", {
	'entities':  [(89, 97, 'LOC')]
}),

("Allí las zonas más conflictivas se ubican en las manzanas 99, 102 y 104, y en los sectores conocidos como Playón Este y San Martín.", {
	'entities':  [(49, 71, 'LOC'),(106, 117, 'LOC'),(120, 130, 'LOC')]
}),

("Entre las autoridades bonaerenses hay preocupación por varios latentes focos de disputa narco, en zonas de Moreno y Lomas de Zamora, pero la policía intervino la semana pasada para frenar un brote de violencia en La Plata.", {
	'entities':  [(107, 113, 'LOC'),(116, 131, 'LOC'),(213, 221, 'LOC')]
}),

("Al menos tres grupos se enfrentan por los puestos de venta de drogas en la calle 524, entre 27 y 29.", {
	'entities':  [(62, 68, 'DRUG'),(75, 84, 'LOC'),(86, 99, 'LOC')]
}),

("*Hubo varios hechos de violencia en la disputa de la venta al menudeo de estupefacientes*, explicaron investigadores policiales tras decomisar varias armas.", {
	'entities':  [(73, 88, 'DRUG')]
}),

("Una fiscal de Moreno solicitó que cuatro hombres, entre ellos *Yeyé*, el presunto líder de una banda narco, sean enjuiciados por un triple crimen cometido en diciembre de 2016 en una casa que era usada como búnker para la venta de drogas.", {
	'entities':  [(14, 20, 'LOC'),(63, 67, 'PER'),(207, 213, 'MISC'),(231, 237, 'DRUG')]
}),

("El requerimiento de la fiscal Carina Saucedo alcanza a Carlos Alberto *Yeyé* Rodríguez Ávalos; Jorge Omar *Murdock* Pereyra; su hermano, Ariel Hernán, alias *Colorado*, y Esteban Mazzone, todos procesados con prisión preventiva por homicidio criminis causae.", {
	'entities':  [(30, 44, 'PER'),(55, 93, 'PER'),(95, 123, 'PER'),(137, 149, 'PER'),(158, 166, 'PER'),(171, 186, 'PER')]
}),

("El cuarteto está acusado de los homicidios de Jorge Luis Trovato (de 34 años), Jonathan Damián Catriel Flores (de 22) y Yésica de los Ángeles Garcilazo (de 24), cometidos el 30 de diciembre de 2016.", {
	'entities':  [(46, 64, 'PER'),(79, 109, 'PER'),(120, 151, 'PER')]
}),

("Las víctimas estaban en una casa situada en la esquina de la avenida La Plata y Storni, en el barrio La Perla, de Moreno.", {
	'entities':  [(61, 86, 'LOC'),(94, 109, 'LOC'),(114, 120, 'LOC')]
}),

("Alguien llamó al 911 y alertó a la comisaría 1» del distrito, cuyo personal entró en la vivienda y encontró a los dos hombres y a la mujer acribillados.", {
	'entities':  [(35, 46, 'MISC'),(52, 60, 'MISC')]
}),

("Las fuentes judiciales consultadas por la agencia de noticias Télam señalaron que en la escena del triple crimen se levantaron unas 15 vainas servidas, todas de calibre 9 milímetros.", {
	'entities':  [(62, 67, 'ORG')]
}),

("En el dormitorio donde fue encontrado el cadáver de Garcilazo había una bolsa con 55 dosis de cocaína fraccionadas en sobres de papel glasé metalizado.", {
	'entities':  [(52, 61, 'PER'),(94, 101, 'DRUG')]
}),

("Varios testigos declararon que la casa estaba *tomada* desde hacía tiempo y que era usada para la venta de estupefacientes.", {
	'entities':  [(107, 122, 'DRUG')]
}),

("*La casa no tenía mobiliario, solo una silla en el living y una camita en la pieza, como pasa en los búnkeres*, dijo a Télam uno de los investigadores.", {
	'entities':  [(119, 124, 'ORG')]
}),

("La policía bonaerense desbarató una organización narco y decomisó 43 kilos de cocaína durante allanamientos realizados en Quilmes, Florencio Varela y Presidente Perón.", {
	'entities':  [(78, 85, 'DRUG'),(122, 129, 'LOC'),(131, 147, 'LOC'),(150, 166, 'LOC')]
}),

("Más allá de la cantidad de droga incautada, con un valor estimado en US$ 500.000, a los investigadores les llamó la atención la forma en que estaba marcado cada paquete de cocaína.", {
	'entities':  [(27, 32, 'DRUG'),(172, 179, 'DRUG')]
}),

("Ese grupo narco compuesto por argentinos y peruanos había grabado los panes de cocaína con una cruz esvástica.", {
	'entities':  [(79, 86, 'DRUG')]
}),

("Ese símbolo no sólo remite al nazismo, sino que en temas de tráfico de drogas se lo vincula especialmente con el peligroso cartel colombiano Los Urabeños, que identifica de esa manera su mercancía.", {
	'entities':  [(141, 153, 'ORG')]
}),

("La presencia de esa organización colombiana en la Argentina había quedado expuesta tras el arresto en 2012 de Henry De Jesús López Londoño, alias *Mi Sangre*.", {
	'entities':  [(50, 59, 'LOC'),(110, 138, 'PER'),(147, 156, 'PER')]
}),

("Fue considerado uno de los jefes de sicarios de Los Urabeños, banda también conocida como clan Usuga.", {
	'entities':  [(48, 60, 'ORG'),(90, 100, 'ORG')]
}),

("López Londoño, ex integrante del grupo paramilitar denominado Autodefensas Unidas de Colombia, fue extraditado en noviembre de 2016 a los Estados Unidos.", {
	'entities':  [(0, 13, 'PER'),(62, 93, 'ORG'),(138, 152, 'LOC')]
}),

("El Ministerio de Seguridad bonaerense informó que la investigación había comenzado en marzo pasado.", {
	'entities':  [(3, 37, 'ORG')]
}),

("También se colocaba en cada pan de cocaína una cubierta de papel metalizado, en un intento de complicar las verificaciones en pasos fronterizos y aeropuertos.", {
	'entities':  [(35, 42, 'DRUG')]
}),

("Los cargamentos de cocaína resultaban aquí rápidamente cambiados por automóviles de alta gama, como forma de pago que permitía a los vendedores un rápido lavado de la ganancia narco.", {
	'entities':  [(19, 26, 'DRUG')]
}),

("Dos integrantes de ese grupo fueron arrestados en los procedimientos encabezados por la Dirección de Operaciones contra el Crimen Organizado de la Superintendencia de Investigaciones del Tráfico de Drogas Ilícitas y Crimen Organizado, agentes que contaron con el apoyo de los grupos especiales GAD y Halcón.", {
	'entities':  [(88, 233, 'ORG'),(294, 297, 'ORG'),(300, 306, 'ORG')]
}),

("*Nosotros tenemos un combate directo contra los delincuentes, las bandas organizadas y el narcotráfico porque queremos que los bonaerenses vivan un poco mejor todos los días*, señaló el ministro de Seguridad bonaerense, Cristian Ritondo, al supervisar el resultado del operativo.", {
	'entities':  [(220, 236, 'PER')]
}),

("En un operativo conjunto de la Policía Federal y la Gendarmería se decomisaron algo más de 67 kilogramos de cocaína y 27 kilogramos de marihuana en la localidad salteña de Cafayate.", {
	'entities':  [(31, 46, 'ORG'),(52, 63, 'ORG'),(108, 115, 'DRUG'),(135, 144, 'DRUG'),(172, 180, 'LOC')]
}),

("La droga era transportada en camionetas, que fueron seguidas por agentes policiales desde la ciudad de Salta.", {
	'entities':  [(3, 8, 'DRUG'),(93, 108, 'LOC')]
}),

("La investigación determinó que ese grupo narco tenía previsto trasladar el cargamento de cocaína hasta Buenos Aires, donde la droga era acopiada en espera de su transporte hacia Europa.", {
	'entities':  [(89, 96, 'DRUG'),(103, 115, 'LOC'),(178, 184, 'LOC')]
}),

("La pesquisa se inició en noviembre de 2016, a partir de informaciones compartidas con unidades policiales de España.", {
	'entities':  [(109, 115, 'LOC')]
}),

("Un suboficial de la Policía de Salta fue detenido ayer en un operativo vial de la Gendarmería realizado en la ruta nacional 34, en Salvador Mazza.", {
	'entities':  [(20, 36, 'ORG'),(82, 93, 'ORG'),(110, 126, 'LOC'),(131, 145, 'LOC')]
}),

("Ese agente fue atrapado con un importante cargamento de droga oculto en cajas de productos de limpieza.", {
	'entities':  [(56, 61, 'DRUG')]
}),

("Fueron decomisados 135 kilos de cocaína.", {
	'entities':  [(32, 39, 'DRUG')]
}),

("El detenido fue identificado como Marcelo Flores.", {
	'entities':  [(34, 48, 'PER')]
}),

("sargento de la Policía de Salta.", {
	'entities':  [(15, 31, 'ORG')]
}),

("El punto de inicio de la travesía era Misiones para cruzar a Brasil y seguir camino hacia Paraguay, donde se retiraba la *mercadería* que debía ser entregada en una casona del residencial barrio de Belgrano.", {
	'entities':  [(38, 46, 'LOC'),(61, 67, 'LOC'),(90, 98, 'LOC'),(165, 171, 'MISC'),(188, 206, 'LOC')]
}),

("La *mercadería* que los viajantes iban a buscar a Paraguay eran billetes: pesos argentinos que ingresaban de forma ilegal en la Argentina.", {
	'entities':  [(50, 58, 'LOC'),(128, 137, 'LOC')]
}),

("En la casona de Belgrano R donde se entregaba el dinero traído desde el exterior vive el presunto dueño o destinatario de las divisas: Li Feng Hsieh, nacido hace 41 años en Taiwán y con ciudadanía argentina.", {
	'entities':  [(6, 12, 'MISC'),(16, 26, 'LOC'),(135, 148, 'PER'),(173, 179, 'LOC')]
}),

("En las últimas horas, el juez federal de Campana, Adrián González Charvay, procesó, sin prisión preventiva, a Feng Hsieh, conocido según la investigación judicial como *Arian*, por el delito de contrabando agravado y le embargó los bienes hasta cubrir la suma de $ 4.000.000.", {
	'entities':  [(41, 48, 'LOC'),(50, 73, 'PER'),(110, 120, 'PER'),(169, 174, 'PER')]
}),

("Otros 12 sospechosos fueron procesados por González Charvay por el delito de contrabando agravado.", {
	'entities':  [(43, 59, 'PER')]
}),

("*El modus operandi de la organización consistía en efectuar cruces a la frontera con Brasil, para de allí dirigirse a Paraguay, donde se haría el cambio de dólares por pesos argentinos, retornando luego con la moneda nacional a la Argentina.", {
	'entities':  [(85, 91, 'LOC'),(118, 126, 'LOC'),(231, 240, 'LOC')]
}),

("Una vez en el país, y generalmente el mismo día, emprendían el viaje a la Ciudad Autónoma de Buenos Aires, más precisamente al domicilio de Feng Hsieh, alias *Arian*, propietario o destinatario del dinero mencionado*, sostuvo el juez González Charvay en la resolución a la que tuvo acceso LA NACION.", {
	'entities':  [(74, 105, 'LOC'),(140, 150, 'PER'),(159, 164, 'PER'),(234, 250, 'PER'),(289, 298, 'ORG')]
}),

("La causa comenzó el 7 de agosto pasado después de una denuncia telefónica anónima que se recibió en la Delegación Departamental de Investigaciones del Tráfico de Drogas Ilícitas y Crimen Organizado Zárate-Campana de la policía bonaerense.", {
	'entities':  [(103, 237, 'ORG')]
}),

("El denunciante sostuvo que desde la provincia de Misiones hacia Zárate iba a salir un vehículo cargado de droga.", {
	'entities':  [(36, 57, 'LOC'),(64, 70, 'LOC'),(106, 111, 'DRUG')]
}),

("Un día después se organizó un operativo de prevención en tres puntos claves: en el puesto de peaje Zárate-Brazo Largo, en el cruce de las rutas 12 y 6 y sobre la ruta 193.", {
	'entities':  [(99, 117, 'LOC'),(138, 150, 'LOC'),(162, 170, 'LOC')]
}),

("Faltaban 15 minutos para las 4 del 9 de agosto pasado cuando el personal policial advirtió al Chevrolet Prisma blanco con tres ocupantes.", {
	'entities':  [(94, 103, 'ORG')]
}),

("Entonces, el juez González Charvay autorizó la requisa del automóvil.", {
	'entities':  [(18, 34, 'PER')]
}),

("Para sorpresa de los policías, no se encontró droga.", {
	'entities':  [(46, 51, 'DRUG')]
}),

("El magistrado ordenó una serie de intervenciones telefónicas para intentar descubrir cuál era el destino del dinero que había entrado en la Argentina de contrabando.", {
	'entities':  [(140, 149, 'LOC')]
}),

("En la investigación, el juez González Charvay tuvo la colaboración de la policía bonaerense y del Departamento de Delitos Federales de la Policía Federal Argentina (PFA).", {
	'entities':  [(29, 45, 'PER'),(73, 91, 'ORG'),(98, 169, 'ORG')]
}),

("En varias comunicaciones, los sospechosos comentaron que *Arian* le reclamaba a uno de los organizadores US$ 400.000 que se habían *perdido*.", {
	'entities':  [(58, 63, 'PER')]
}),

("La causa avanzó y el 22 del mes pasado, por orden del juez González Charvay, los detectives policiales allanaron la casona de Belgrano R donde reside *Arian*.", {
	'entities':  [(59, 75, 'PER'),(116, 122, 'MISC'),(126, 136, 'LOC'),(151, 156, 'PER')]
}),

("Los uniformados habían advertido el ingreso de otro Chevrolet Prisma usado por la organización en la vivienda, situada en General Enrique Martínez al 1900.", {
	'entities':  [(52, 61, 'ORG'),(122, 154, 'LOC')]
}),

("En su primera indagatoria, Feng Hsieh se negó a declarar.", {
	'entities':  [(27, 37, 'PER')]
}),

("Pero en una segunda oportunidad sostuvo que desconocía la existencia de la organización criminal y que nunca participó *en traslado alguno de dinero en efectivo desde o hacia Paraguay*.", {
	'entities':  [(175, 183, 'LOC')]
}),

("*Sin pretender hacer la defensa de otros encartados, surge palmariamente que las sumas involucradas incluso carecen de sustento para enrostrar algún tipo de infracción aduanera ya que si se hiciera un análisis contrafáctico del caso, siendo tres personas mayores de edad, tendrían en su poder sumas menores a las que estarían obligadas a declarar en un supuesto control aduanero*, dijo el acusado según recordó González Charvay en su resolución.", {
	'entities':  [(411, 427, 'PER')]
}),

("Para el magistrado, las palabras de Feng Hsieh fueron *un intento de ubicarse en una mejor situación procesal.", {
	'entities':  [(36, 46, 'PER')]
}),

("ROSARIO.- Un megaoperativo de la Policía Federal se lleva adelante desde la madrugada en barrio Las Flores, la zona que dominan Los Monos en Rosario.", {
	'entities':  [(0, 7, 'LOC'),(89, 106, 'LOC'),(128, 137, 'ORG'),(141, 148, 'LOC')]
}),

("Un centenar de efectivos de esta fuerza llevan adelante 28 allanamientos por una seguidilla de homicidios que se produjeron en junio pasado cuando fue asesinada Petrona Cantero, la hermana de Ariel, histórico líder de la organización narcocriminal.", {
	'entities':  [(161, 176, 'PER'),(192, 197, 'PER')]
}),

("Este operativo se produce cuando se realiza en Rosario el juicio contra 25 integrantes de la banda de Los Monos, acusados por asociación ilícita y cinco homicidios.", {
	'entities':  [(47, 54, 'LOC'),(102, 111, 'ORG')]
}),

("Ayer declaró Ramón Machuca, uno de los líderes de la organización, quien acusó al gobierno socialista, a la justicia y a la policía de Santa Fe de armar una causa contra la familia Cantero.", {
	'entities':  [(13, 26, 'PER'),(135, 143, 'LOC'),(181, 188, 'PER')]
}),

("La policía detuvo a cinco personas durante el operativo que dejó desiertas las calles del barrio de la zona sur de Rosario.", {
	'entities':  [(79, 122, 'LOC')]
}),

("Las órdenes de detención fueron libradas por la Fiscalía de Rosario, donde se investigan siete crímenes ligados a las venganzas de la familia Cantero.", {
	'entities':  [(48, 67, 'ORG'),(142, 149, 'PER')]
}),

("Desde la medianoche un helicóptero sobrevuela la zona, donde se vivieron momentos de tensión tras la llegada de los efectivos de la Policía Federal.", {
	'entities':  [(132, 147, 'ORG')]
}),

("El operativo tiene relación con la investigación por el crimen de Isabel Petrona Cantero, el 16 de junio pasado.", {
	'entities':  [(66, 88, 'PER')]
}),

("Como publicó LA NACION el 24 de julio pasado, se produjeron siete asesinatos como respuesta a la muerte de la hermana del líder de los Monos.", {
	'entities':  [(13, 22, 'ORG'),(131, 140, 'ORG')]
}),

("Los crímenes se vinculan a una serie de venganzas gestadas en el barrio Las Flores, en la zona sur de la ciudad, donde hace poco más de un mes arrancó una disputa por el territorio dominado históricamente por la banda de Los Monos.", {
	'entities':  [(65, 82, 'LOC'),(90, 111, 'MISC'),(221, 230, 'ORG')]
}),

("El crimen que encendió esta nueva batalla en las calles cercanas al casino de Rosario fue el de Isabel Petrona Cantero, alias Chabela, hermana de Máximo Ariel, el histórico líder del grupo narcocriminal Los Monos, preso en la cárcel de Piñero, a unos 20 kilómetros de Rosario.", {
	'entities':  [(68, 74, 'MISC'),(78, 85, 'LOC'),(96, 118, 'PER'),(126, 133, 'PER'),(146, 158, 'PER'),(203, 212, 'ORG'),(226, 232, 'MISC'),(236, 242, 'LOC'),(268, 275, 'LOC')]
}),

("Chabela Cantero fue asesinada el 16 de junio por otro clan que pretende dominar ese barrio -los Schneider- a balazos.", {
	'entities':  [(0, 15, 'PER'),(92, 105, 'ORG')]
}),

("La mujer, de 56 años, fue blanco de la ira de los Schneider y murió de un disparo en el abdomen, mientras que resultaron heridas su nieta y otra joven.", {
	'entities':  [(46, 59, 'ORG')]
}),

("Al ataque lo tramaron, según los investigadores, Patricia Schneider, alias Pato, y su marido, David Díaz, alias Nango.", {
	'entities':  [(49, 67, 'PER'),(75, 79, 'PER'),(94, 104, 'PER'),(112, 117, 'PER')]
}),

("Fue un ataque premeditado después del mediodía en España al 7000.", {
	'entities':  [(50, 64, 'LOC')]
}),

("Las mujeres volvían a su casa cuando Patricia salió de un almacén situado a pocos metros y las increpó.", {
	'entities':  [(37, 45, 'PER')]
}),

("Dos hombres salieron en defensa de Schneider y otros atacantes descendieron de una camioneta.", {
	'entities':  [(35, 44, 'PER')]
}),

("A Chabela Cantero le dispararon con un arma calibre 38 y murió casi en el acto.", {
	'entities':  [(2, 17, 'PER')]
}),

("La venganza no se hizo esperar en Las Flores.", {
	'entities':  [(34, 44, 'LOC')]
}),

("Los Cantero quemaron la casa de María de los Ángeles Schneider, hija de Patricia, la supuesta instigadora del crimen.", {
	'entities':  [(0, 11, 'ORG'),(32, 62, 'PER'),(72, 80, 'PER')]
}),

("Mientras este espiral de violencia en esa parte de Rosario recrudecía, fue detenida en ese barrio Celestina Contreras, la madre de Claudio Cantero, líder de Los Monos asesinado el 26 de mayo de 2013.", {
	'entities':  [(51, 58, 'LOC'),(98, 117, 'PER'),(131, 146, 'PER'),(157, 166, 'ORG')]
}),

("Esta mujer, conocida como *la Cele*, tenía pedido de captura por la causa narco conocida como Los Patrones, que desmanteló parte de este grupo a fines de 2015.", {
	'entities':  [(27, 34, 'PER'),(94, 106, 'ORG')]
}),

("El 11 de julio pasado, Gustavo Díaz, de 40 años, fue asesinado dentro de su casa, y su hijo de 10 años resultó herido.", {
	'entities':  [(23, 35, 'PER')]
}),

("Este hombre es el hermano de David, la pareja de Schneider, quien se había refugiado allí, en Uriburu y Acceso Sur, porque sabía que los Cantero lo buscaban para matarlo.", {
	'entities':  [(29, 34, 'PER'),(49, 58, 'PER'),(94, 114, 'LOC'),(137, 144, 'PER')]
}),

("Uno de los sicarios que fueron a asesinar a Díaz metió la mano por la ventana de la casa y comenzó a disparar con desenfreno.", {
	'entities':  [(44, 48, 'PER')]
}),

("Ejecutó al hermano del hombre que buscaban, que unos días antes había abandonado el escondite.", {
	'entities':  [(84, 93, 'MISC')]
}),

("José Schneider, de 40 años, miembro del clan homónimo, fue ejecutado de un tiro en la nuca el 24 de julio.", {
	'entities':  [(0, 14, 'PER')]
}),

("Según testimonios de la familia de la víctima, Jesús Fernández, de 23 años, fue asesinado al resistirse al robo de su celular en la zona de Hortensia y Flor de Nácar.", {
	'entities':  [(47, 62, 'PER'),(140, 165, 'LOC')]
}),

("*Pidan lo que quieran, pero esto tiene que aprobarse hoy*, urgió a los siete ediles Diego Garavano, el presidente del Concejo Deliberante de Villa Gobernador Gálvez, una ciudad de 80.000 habitantes separada de Rosario por una avenida.", {
	'entities':  [(84, 98, 'PER'),(118, 164, 'ORG'),(210, 217, 'LOC'),(226, 233, 'MISC')]
}),

("La había enviado unos minutos antes el intendente Pedro González (Partido Justicialista), yerno de Garavano.", {
	'entities':  [(50, 64, 'PER'),(99, 107, 'PER')]
}),

("Carlos Dolce, del Partido Socialista, fue el único que se abstuvo y no aprobó el expediente Nº 4933/13.", {
	'entities':  [(0, 12, 'PER')]
}),

("Esa *inversión* del cartel colombiano de los Urabeños formaba parte de los $ 15.712.068 que esta organización había lavado en la Argentina a través de 30 empresas que crearon en el país desde 2010.", {
	'entities':  [(41, 53, 'ORG')]
}),

("Esta organización se asentó aquí con el liderazgo de los hermanos Erman y Williams Triana Peña a través de una red de empresas en la Capital, Santa Fe, Tucumán y Mendoza, y en otros países, fundamentalmente Colombia y Panamá.", {
	'entities':  [(66, 94, 'PER'),(133, 140, 'LOC'),(142, 150, 'LOC'),(152, 159, 'LOC'),(162, 169, 'LOC'),(207, 215, 'LOC'),(218, 224, 'LOC')]
}),

("El cartel buscaba nuevas rutas para el tráfico de cocaína y África aparecía como un punto intermedio para llegar a Europa y a Asia.", {
	'entities':  [(50, 57, 'DRUG'),(60, 66, 'LOC'),(115, 121, 'LOC'),(126, 130, 'LOC')]
}),

("Aquel trámite en el Concejo de Villa Gobernador Gálvez es una muestra de cómo el dinero del narcotráfico podía colarse por los puntos más débiles del Estado.", {
	'entities':  [(20, 54, 'ORG'),(150, 156, 'ORG')]
}),

("En este caso, de un municipio donde las grietas y los escasos controles institucionales dejaban el resquicio para que los fondos sucios se blanquearan en obras que no eran necesarias y por las que nadie pediría demasiadas explicaciones.", {
	'entities':  [(20, 29, 'MISC')]
}),

("Y nadie, según Dolce, iba a controlar qué cuerpos se cremarían.", {
	'entities':  [(15, 20, 'PER')]
}),

("El 17 de septiembre de 2015, la Gendarmería allanó el depósito fiscal de la empresa Binder SRL, en Rosario, y halló una carga de 46 toneladas de arroz que escondía 12 kilos de cocaína.", {
	'entities':  [(32, 43, 'ORG'),(54, 69, 'MISC'),(84, 94, 'ORG'),(99, 106, 'LOC'),(176, 183, 'DRUG')]
}),

("Esa carga, despachada por la empresa Euroexport SRL -con domicilio en Buenos Aires 440, San Miguel de Tucumán-, tenía como destino Guinea-Bissau, África, donde el cereal llegaría a través del programa Hambre Cero, de la Organización de las Naciones Unidas (ONU).", {
	'entities':  [(37, 51, 'ORG'),(70, 86, 'LOC'),(88, 109, 'LOC'),(131, 144, 'LOC'),(146, 152, 'LOC'),(220, 261, 'ORG')]
}),

("En el predio de tres hectáreas lindero al cementerio San Lorenzo, de Gálvez (298 kilómetros al noroeste de Buenos Aires), la mutual Provincias Unidas -pantalla que usaba el cartel- iba a desembolsar, según el convenio de concesión Nº 3369/2013, 19.500.000 pesos y 700.000 dólares para el crematorio.", {
	'entities':  [(53, 64, 'ORG'),(69, 75, 'LOC'),(107, 119, 'LOC'),(125, 149, 'ORG')]
}),

("El 11 de noviembre de 2014, la mutual Provincias Unidas pagó al municipio, en concepto de canon, un adelanto de $ 2.000.000.", {
	'entities':  [(31, 55, 'ORG'),(64, 73, 'MISC')]
}),

("Un mes después de que el dinero se acreditó en la cuenta Nº 0074002 del Nuevo Banco de Santa Fe, Guillermo Heisinger, el arquitecto financiero del cartel y funcionario del Ministerio del Interior durante la gestión de Carlos Menem, caminaba por San Martín al 800, en la city porteña, cuando sonó su teléfono.", {
	'entities':  [(72, 95, 'ORG'),(97, 116, 'PER'),(172, 195, 'ORG'),(218, 230, 'PER'),(245, 262, 'LOC')]
}),

("Estaba a sólo 20 metros del edificio del Consejo Federal de Inversiones, pero prefirió no entrar; decidió soportar el calor parado en la vereda del viejo edificio de Harrods para atender esa comunicación, que era importante por quien llamaba.", {
	'entities':  [(41, 71, 'ORG'),(166, 173, 'ORG')]
}),

("Lo primero que le preguntó a su socio Aldo Corizzo fue: *¿Vio la luz lo del crematorio?*.", {
	'entities':  [(38, 50, 'PER')]
}),

("Corizzo, un jubilado que vivía en el barrio Martín, de Rosario, y tenía como domicilio legal el departamento de Heisinger en Alvear 1502, en el barrio porteño de Recoleta, fue quien tejió el *negocio* en Villa Gobernador Gálvez.", {
	'entities':  [(0, 7, 'PER'),(37, 50, 'LOC'),(55, 62, 'LOC'),(112, 121, 'ORG'),(125, 136, 'LOC'),(144, 170, 'LOC'),(204, 227, 'LOC')]
}),

("*Ya firmé con el «Gordo» González*, le contó Corizzo.", {
	'entities':  [(18, 23, 'PER'),(25, 33, 'PER'),(45, 52, 'PER')]
}),

("Preguntó si Carlos Yorelmy Duarte Díaz, uno de los capos colombianos de la banda, había vuelto de Uruguay.", {
	'entities':  [(12, 38, 'PER'),(98, 105, 'LOC')]
}),

("Tenía que reunirse con él en Rosario para pasarle las novedades.", {
	'entities':  [(29, 36, 'LOC')]
}),

("*Primero firmo lo del crematorio y después lo del puerto*, resumió Corizzo en esa breve comunicación, de dos minutos.", {
	'entities':  [(67, 74, 'PER')]
}),

("Faltaba cerrar otros eslabones de la cadena de *inversiones* que delineaba el cartel liderado por los hermanos Triana Peña para lavar dinero del narcotráfico y, además, exportar cocaína vía África.", {
	'entities':  [(111, 122, 'PER'),(178, 185, 'DRUG'),(190, 196, 'LOC')]
}),

("Querían manejar un puerto en Fray Luis Beltrán, al norte de Rosario, para exportar los cargamentos de arroz con cocaína de máxima pureza que *el Especialista* Wilmar Yuriano Valencia Estrada (detenido por la policía en el aeropuerto de Cali, Colombia) preparaba en la casa en Arroyito (Víctor Mercante al 1100), junto con el oncólogo argentino Gabriel Zilli, reconocido especialista en tratamientos contra el dolor en enfermos terminales.", {
	'entities':  [(29, 46, 'LOC'),(60, 67, 'LOC'),(112, 119, 'DRUG'),(159, 190, 'PER'),(236, 240, 'LOC'),(242, 250, 'LOC'),(276, 284, 'LOC'),(286, 309, 'LOC'),(344, 357, 'PER')]
}),

("La otra pata estaba relacionada con el fútbol: pretendían desembolsar dinero en Rosario Central para la compra de jugadores.", {
	'entities':  [(80, 95, 'ORG')]
}),

("Era un recorrido similar al que habían trazado en el club El Porvenir, de Gerli, en el sur del conurbano.", {
	'entities':  [(58, 69, 'ORG'),(74, 79, 'LOC'),(87, 104, 'LOC')]
}),

("*El Porve* atravesaba uno de los momentos más duros desde su fundación, en 1915: jugaba en la D y no tenía muchas chances de ascender.", {
	'entities':  [(1, 9, 'ORG')]
}),

("El 25 de febrero de 2015, la comisión directiva firmó un acuerdo con la empresa International Trade and Commerce (ITC), cuyos titulares eran el colombiano Carlos Yorelmy Duarte Díaz y Heisinger.", {
	'entities':  [(80, 118, 'ORG'),(155, 181, 'PER'),(184, 193, 'PER')]
}),

("El veterano dirigente de El Porvenir Enrique Merelas, entonces presidente de la institución de Gerli, había firmado el acuerdo ante la desesperación por obtener fondos frescos.", {
	'entities':  [(25, 36, 'ORG'),(37, 52, 'PER'),(95, 100, 'ORG')]
}),

("*El Porve* estaba en bancarrota y el cartel de los Urabeños se aprovechaba de las debilidades.", {
	'entities':  [(1, 9, 'ORG'),(47, 59, 'ORG')]
}),

("El 15 de mayo pasado, Merelas fue llamado a declarar por la Fiscalía Nº 8 de Lomas de Zamora por los delitos de *administración fraudulenta, estafa y confección de balances apócrifos*.", {
	'entities':  [(22, 29, 'PER'),(60, 73, 'MISC'),(77, 92, 'LOC')]
}),

("Duarte Díaz y Heisinger querían volver a aplicar el *manual* para lavar dinero en Central, un club mucho más grande que El Porvenir, pero al que se asemejaba en la crisis que atravesaba tras el descenso de 2010, en la presidencia del histórico dirigente radical Horacio Usandizaga.", {
	'entities':  [(0, 11, 'PER'),(14, 23, 'PER'),(82, 89, 'ORG'),(120, 131, 'ORG'),(262, 280, 'PER')]
}),

("El acuerdo con Rosario Central no se pudo sellar.", {
	'entities':  [(15, 30, 'ORG')]
}),

("El juez federal porteño Sergio Torres decidió, el 17 de septiembre de 2014, cinco días después de otra conversación entre Heisinger y Corizzo, que la Gendarmería debía allanar el depósito fiscal Binder, donde estaba el cargamento de arroz embebido en cocaína que iría a Guinea-Bissau.", {
	'entities':  [(24, 37, 'PER'),(122, 131, 'PER'),(134, 141, 'PER'),(251, 258, 'DRUG'),(270, 283, 'LOC')]
}),

("Durante los días en que ambos conversaban sobre la posibilidad de meterse por las grietas de Rosario Central para manejar la compraventa de jugadores, a cuatro cuadras del Gigante de Arroyito, el oncólogo Gabriel Zilli *cocinaba* arroz en una gigantesca olla con *el Especialista* Valencia Estrada.", {
	'entities':  [(93, 108, 'ORG'),(172, 191, 'ORG'),(205, 218, 'PER'),(230, 235, 'DRUG'),(281, 297, 'PER')]
}),

("En esa casa también participaba del *experimento* Jorge Eliécer Ramírez Cuartas.", {
	'entities':  [(50, 79, 'PER')]
}),

("*El Especialista* era uno de los expertos más hábiles del mundo en camuflar cocaína para no ser descubierta por los escáneres.", {
	'entities':  [(76, 83, 'DRUG'),(76, 83, 'DRUG')]
}),

("A los peritos les llevó medio año determinar cómo hacía para cubrir con una fina película de cocaína cada grano de arroz.", {
	'entities':  [(93, 100, 'DRUG')]
}),

("Hace tres días, Alan Funes, prófugo con pedido de captura nacional e internacional, anunció que mataría *a todas las generaciones* de los Caminos, sus rivales ligados al narcotráfico en Rosario y a la barra de Newell's.", {
	'entities':  [(134, 145, 'ORG'),(186, 193, 'LOC'),(210, 218, 'ORG')]
}),

("Sus amenazas, escritas desde la clandestinidad en Facebook fueron fruto de la sed de venganza tras el crimen de su hermano Ulises, a quien acribillaron el 6 del actual.", {
	'entities':  [(50, 58, 'ORG'),(123, 129, 'PER')]
}),

("Alan empezó a cumplir su promesa anteanoche al ejecutar -según testigos- a Marcela Díaz, hermana de uno de los miembros del clan Caminos.", {
	'entities':  [(75, 87, 'PER'),(124, 136, 'ORG')]
}),

("Y ayer a la tarde Leandro Rafatti, de 29 años, cuñado de Díaz, fue ultimado desde un VW Gol con una pistola 44 Magnun.", {
	'entities':  [(18, 33, 'PER'),(57, 61, 'PER'),(85, 87, 'ORG')]
}),

("Detrás de esta seguidilla de asesinatos, más de 30 en 20 meses, está la larga pelea sostenida por dos familias que viven en las torres del Fonavi de barrio Municipal, donde se mezcla el narcotráfico y las mafias vinculadas a las barras de fútbol.", {
	'entities':  [(128, 145, 'MISC'),(149, 165, 'LOC')]
}),

("Desde un VW Suran mataron a Marcela Díaz, hermana de Ariel Segovia, alias *Tubi*, miembro de la banda de los Caminos.", {
	'entities':  [(9, 11, 'ORG'),(28, 40, 'PER'),(53, 66, 'PER'),(75, 79, 'PER'),(105, 116, 'ORG')]
}),

("Tubi Segovia era uno de los candidatos impulsado por Los Monos para liderar la tribuna de Newell's, pero un atentado a balazos el 6 de octubre de 2016 lo sacó de circulación.", {
	'entities':  [(0, 12, 'PER'),(53, 62, 'ORG'),(90, 98, 'ORG')]
}),

("Y al ser hospitalizado quedó preso por el crimen de la joven Lorena Ojeda, a quien mató por error.", {
	'entities':  [(61, 73, 'PER')]
}),

("Las balas tenían como destino a Brisa, hermana de la mujer asesinada y testigo del homicidio de Jonathan Rosales, otro eslabón de la lucha de barras.", {
	'entities':  [(32, 37, 'PER'),(96, 112, 'PER')]
}),

("Segovia aparece involucrado en cinco crímenes, que tienen como punto en común la hinchada de Newell's y el barrio Municipal, centro de las disputas con los Funes.", {
	'entities':  [(0, 7, 'PER'),(93, 101, 'ORG'),(107, 123, 'LOC'),(152, 161, 'ORG')]
}),

("Marcela Díaz fue acribillada cuando viajaba en una moto acompañada por Nahuel G. Ella murió en el acto y su acompañante resultó herido en una pierna.", {
	'entities':  [(0, 12, 'PER'),(71, 79, 'PER')]
}),

("Este hombre declaró a la policía que Alan Funes estaba entre los ocupantes del auto.", {
	'entities':  [(37, 47, 'PER')]
}),

("La Fiscalía de Rosario ordenó un operativo especial en la sala de velatorios donde se realizará el sepelio de Díaz, luego de que al fiscal Ademar Bianchini le llegaran rumores de que los Funes podrían atacar a los parientes y amigos que concurren a la ceremonia.", {
	'entities':  [(3, 22, 'ORG'),(110, 114, 'PER'),(139, 155, 'PER'),(183, 192, 'ORG')]
}),

("Alan Funes festejó fin de año disparando 15 tiros al aire con una ametralladora, mientras se encontraba con prisión domiciliaria por un crimen que cometió, cuando era menor, en venganza de la muerte de su madre, Mariela Miranda, en marzo de 2016.", {
	'entities':  [(0, 10, 'PER'),(212, 227, 'PER')]
}),

("Casi de inmediato fue asesinado su hermano Ulises, de 18 años.", {
	'entities':  [(43, 49, 'PER')]
}),

("Alan Funes y su hermano Lautaro, quien está preso en la cárcel de Piñero, lanzaron entonces amenazas desde Facebook contra los Caminos.", {
	'entities':  [(0, 10, 'PER'),(24, 31, 'PER'),(56, 62, 'MISC'),(66, 72, 'LOC'),(107, 115, 'ORG'),(123, 134, 'ORG')]
}),

("Durante la tarde de ayer se produjo otro golpe contra el clan Caminos: Leandro Rafatti, de 29, condenado a 4 años de prisión por portación ilegal de arma de guerra, fue asesinado desde un auto en la zona sur de Rosario.", {
	'entities':  [(57, 69, 'ORG'),(71, 86, 'PER'),(199, 218, 'LOC')]
}),

("Y el sábado pasado fue ejecutado de 16 balazos, diez en la cabeza, Facundo Hernández, hermanastro de Milton César, a cuya familia trataron de exterminar Los Monos, al acusarlo por el crimen de Claudio *Pájaro* Cantero, en 2013.", {
	'entities':  [(67, 84, 'PER'),(101, 113, 'PER'),(153, 162, 'ORG'),(193, 217, 'PER')]
}),

("Como los Funes, Milton César también lanzó amenazas por Facebook desde la cárcel de Piñero.", {
	'entities':  [(5, 14, 'ORG'),(16, 28, 'PER'),(56, 64, 'ORG'),(74, 80, 'MISC'),(84, 90, 'LOC')]
}),

("*Se van a tener que meter en una caja fuerte porque los voy a matar a todos*, escribió desde la prisión con un teléfono celular.", {
	'entities':  [(96, 103, 'MISC')]
}),

("El gobierno de la ciudad avanzó con la transferencia de competencias penales a la órbita porteña ayer, cuando la Legislatura aprobó el tercer convenio, sancionado en 2011 en el Congreso y que nunca se había ratificado, por el cual ahora la Justicia porteña tendrá a su cargo las investigaciones de 33 nuevos tipos de delitos, entre los que se destaca el narcomenudeo.", {
	'entities':  [(177, 185, 'MISC')]
}),

("El motivo por el cual se decidió avanzar con la ratificación, según fuentes gubernamentales, es que ahora se realizará el traspaso de competencias con los fondos necesarios, cosa que no había sucedido con los dos primeros convenios y que se solucionó, como publicó LA NACION en septiembre pasado, con el giro del dinero adeudado por parte de la Nación.", {
	'entities':  [(265, 274, 'ORG'),(345, 351, 'ORG')]
}),

("Se prevé que la implementación de las nuevas competencias demandará al menos un año y requerirá una descentralización mayor de la Justicia, según explicaron fuentes del Consejo de la Magistratura.", {
	'entities':  [(169, 195, 'ORG')]
}),

("También se decidió crear una comisión dentro de la Legislatura que tendrá como objetivo el seguimiento de la implementación.", {
	'entities':  [(51, 62, 'MISC')]
}),

("*Es un paso importante para la construcción de mejores herramientas para combatir el delito en la ciudad de Buenos Aires, y es un compromiso del Gobierno y de las instituciones para resolver este problema*, dijo a LA NACION el ministro de Justicia y Seguridad porteño, Martín Ocampo.", {
	'entities':  [(98, 120, 'LOC'),(145, 153, 'MISC'),(214, 223, 'ORG'),(269, 282, 'PER')]
}),

("En lo que va del año la Policía de la Ciudad realizó 2363 actuaciones y 115 allanamientos por la ley de estupefacientes, con 336 detenidos.", {
	'entities':  [(24, 44, 'ORG'),(104, 119, 'DRUG')]
}),

("En esas cifras, a las que tuvo acceso LA NACION, se detalla, entre otras cosas, que los principales procedimientos estuvieron enfocados en el decomiso de drogas sintéticas: 3493 pastillas de éxtasis secuestradas, 587 dosis de LCD y 135 de anfetaminas.", {
	'entities':  [(38, 47, 'ORG'),(154, 171, 'DRUG'),(178, 198, 'DRUG'),(226, 229, 'DRUG'),(239, 250, 'DRUG')]
}),

("También, más de 131 kilos de marihuana y 81 de cocaína.", {
	'entities':  [(29, 38, 'DRUG'),(47, 54, 'DRUG')]
}),

("Ocampo manifestó que el traspaso de los cuerpos de seguridad metropolitana de la Policía Federal fue, además de la remisión de los fondos correspondientes, uno de los motivos que terminó por impulsar la cuestión.", {
	'entities':  [(0, 6, 'PER'),(81, 96, 'ORG')]
}),

("Es el trabajo coordinado del Ministerio de Justicia y Seguridad y la Comisión de Justicia, que presido, pero seguiremos reclamando la autonomía plena del Poder Judicial con el traspaso de todos los fueros con sus estructuras.", {
	'entities':  [(29, 63, 'ORG'),(69, 89, 'ORG')]
}),

("Este es el camino correcto hacia ese destino*, dijo a LA NACION el presidente de la comisión de Justicia, Daniel Presti (Pro), autor del proyecto.", {
	'entities':  [(54, 63, 'ORG'),(106, 119, 'PER')]
}),

("Cuando el Congreso apruebe los cuatro convenios que sancionó la Legislatura se completará la autonomía de la Ciudad, contemplada en la Constitución Nacional y en la de la ciudad*, afirmó la presidenta del Consejo de la Magistratura, Marcela Basterra, que además remarcó que la Corte Suprema de Justicia, en varias oportunidades sostuvo que la justicia nacional era *meramente transitoria*.", {
	'entities':  [(10, 18, 'MISC'),(64, 75, 'MISC'),(205, 231, 'ORG'),(233, 249, 'PER'),(277, 302, 'ORG')]
}),

("El traspaso de la justicia ordinaria es uno de los puntos del programa Justicia 2020 que más rispideces encontró en la Asociación de Magistrados y en el gremio de los judiciales.", {
	'entities':  [(119, 144, 'ORG'),(153, 177, 'ORG')]
}),

("El año pasado, varios de los jueces que la integran le hicieron saber al ministro de Justicia y Derechos Humanos, Germán Garavano, que de prosperar la intención de avanzar con esa iniciativa acudirían a los tribunales para frenar su aplicación.", {
	'entities':  [(114, 129, 'PER')]
}),

("Asimismo, en noviembre de 2016 consiguieron, de parte de los senadores justicialistas Miguel Ángel Pichetto y Pedro Guastavino, el compromiso de no tratarlo en el corto plazo.", {
	'entities':  [(86, 107, 'PER'),(110, 126, 'PER')]
}),

("No hay, por lo tanto, motivos válidos para oponerse a una iniciativa que por un lado cumple un mandato constitucional y por otro redundará en un mejor servicio de justicia para los porteños y para quienes, sin serlo, intervienen en procesos que se llevan a cabo en la Capital*, respondió el subsecretario de Justicia porteño, Jorge Enríquez.", {
	'entities':  [(268, 275, 'LOC'),(326, 340, 'PER')]
}),

("LA PLATA.- La Justicia Federal de esta ciudad comenzó a reunir toda la documentación necesaria para realizar el pedido de extradición del sindicalista Marcelo Balcedo y de su mujer, Paola Fiege.", {
	'entities':  [(0, 8, 'LOC'),(14, 30, 'ORG'),(151, 166, 'PER'),(182, 193, 'PER')]
}),

("Así estaría en condiciones para elevar la semana próxima la solicitud oficial a través de la cancillería argentina a la Justicia de Uruguay.", {
	'entities':  [(93, 114, 'MISC'),(132, 139, 'LOC')]
}),

("El juez Ernesto Kreplak, que instruye la causa en la que están imputados el sindicalista y su señora por los delitos de lavado de activos y asociación ilícita, giró la documentación a la oficina de Cooperación Internacional de la Procuración de la Corte de la Nación y a la Procuraduría de Criminalidad Económica y Lavado de Activos (Procelac) para contar con el respaldo de estos organismos en el pedido de extradición.", {
	'entities':  [(8, 23, 'PER'),(187, 194, 'MISC'),(198, 266, 'ORG'),(274, 343, 'ORG')]
}),

("Por eso decidió tomarse todo el tiempo necesario para reunir pruebas y realizar allanamientos que complican, aún más, la situación procesal del titular del Soeme.", {
	'entities':  [(156, 161, 'ORG')]
}),

("En Uruguay están expectantes porque llegue la solicitud del juez que les permita resolver la situación de Balcedo.", {
	'entities':  [(3, 10, 'LOC'),(106, 113, 'PER')]
}),

("Lo cierto es que, si bien no lo dicen abiertamente, en el Juzgado Federal de La Plata temen que,tras los 7,5 millones de dólares secuestrados a Balcedo en Punta del Este y en Montevideo, las autoridades judiciales decidan retener al titular del Soeme para juzgarlo en ese país por los cargos de evasión y lavado de activos.", {
	'entities':  [(58, 73, 'ORG'),(77, 85, 'LOC'),(144, 151, 'PER'),(155, 169, 'LOC'),(175, 185, 'LOC'),(245, 250, 'ORG')]
}),

("Sin embargo, ayer, en Uruguay se hacían la pregunta contraria: ¿por qué tarda tanto la Justicia de la Argentina en pedir la extradición del sindicalista?", {
	'entities':  [(22, 29, 'LOC'),(102, 111, 'LOC')]
}),

("Los investigadores judiciales uruguayos dijeron a LA NACION que se sigue *con medidas cautelares*, que consisten en lo que se denomina *pruebas por anticipado*, mientras se aguarda el trámite desde la Argentina, con la convicción de que *debe ser juzgado en su país, donde estuvo el origen del problema*.", {
	'entities':  [(50, 59, 'ORG'),(201, 210, 'LOC')]
}),

("Anoche, el juez Kreplak procesó con prisión preventiva al socio y mano derecha de Balcedo, Mauricio Yebra al considerárselo responsable de los delitos de lavado de activos agravado y asociación ilícita en calidad de miembro.", {
	'entities':  [(16, 23, 'PER'),(82, 89, 'PER'),(91, 105, 'PER')]
}),

("Balcedo fue detenido el 4 de este mes junto a Fiege en su mansión El Gran Chaparral, situada en la loma del Cerro del Burro, a pocos kilómetros de Punta del Este.", {
	'entities':  [(0, 7, 'PER'),(46, 51, 'PER'),(66, 83, 'MISC'),(108, 123, 'LOC'),(147, 161, 'LOC')]
}),

("Allí se le secuestraron tres armas de guerra, casi 500.000 dólares en efectivo (guardados en una caja fuerte) y 14 vehículos de alta gama valuados en más de dos millones de dólares, entre ellos, un Mercedes-Benz edición McLaren, una Ferrari y un Porsche.", {
	'entities':  [(198, 211, 'ORG'),(233, 240, 'ORG'),(246, 253, 'ORG')]
}),

("Además del pedido de extradición de Balcedo y de Fiege, el magistrado que instruye la causa en nuestro país podría solicitar parte de los montos y vehículos secuestrados durante los allanamientos en Uruguay.", {
	'entities':  [(36, 43, 'PER'),(49, 54, 'PER'),(199, 206, 'LOC')]
}),

("El juez Kreplak está convencido de que Balcedo lideraba una red de lavado de dinero en la que participaban su esposa, su secretario privado y socio Mauricio Yebra, que entre 2012 y 2013 habría retirado más de 80 millones de pesos de las arcas del Soeme.", {
	'entities':  [(8, 15, 'PER'),(39, 46, 'PER'),(148, 162, 'PER'),(247, 252, 'ORG'),(247, 252, 'PER')]
}),

("También el magistrado agregó a su investigación la comisión del posible delito de asociación ilícita, debido a las ramificaciones que ha tenido la investigación, que incluye afiliaciones compulsivas, extorsiones y posibles vinculaciones con la banda de narcotraficantes de Rosario Los Monos.", {
	'entities':  [(273, 280, 'LOC'),(281, 290, 'ORG')]
}),

("Las voces políticas hacen siempre referencia a la existencia de *un problema muy complejo* para evitar mencionar el análisis de estadísticas que apuntan al único responsable del crecimiento de la oferta de drogas local: el consumidor.", {
	'entities':  [(206, 212, 'DRUG')]
}),

("Anunciar guerras frontales contra fantasmas puede tener -para todos los partidos políticos- menos costo electoral que enfrentarse con el 33,8 por ciento de los porteños entre los 25 y 34 años que compran drogas de manera habitual.", {
	'entities':  [(204, 210, 'DRUG')]
}),

("No hay franja etaria ni lugar en la Argentina con esa dimensión de consumidores de marihuana y otras sustancias ilegales.", {
	'entities':  [(36, 45, 'LOC'),(83, 92, 'DRUG'),(101, 120, 'DRUG')]
}),

("Así lo determina la última encuesta nacional realizada por la Sedronar.", {
	'entities':  [(62, 70, 'ORG')]
}),

("Duplican los adultos jóvenes porteños el consumo de drogas registrado en Buenos Aires o Santa Fe.", {
	'entities':  [(52, 58, 'DRUG'),(73, 85, 'LOC'),(88, 96, 'LOC')]
}),

("Las razones sobre el aumento de los puestos de venta de droga en la región metropolitana no habrá que buscarlas, entonces, en supuestas fronteras porosas.", {
	'entities':  [(56, 61, 'DRUG'),(68, 88, 'LOC')]
}),

("Ni siquiera con todas las Fuerzas Armadas instalando puntos de chequeos en cada ruta podrá evitarse la creciente penetración narco, porque no se trata de formar un simple bloqueo contra la circulación de mercancías.", {
	'entities':  [(26, 41, 'ORG'),(80, 84, 'MISC')]
}),

("El narcotráfico y su violencia asociada aumenta en la Argentina por la irresponsable generación de una cultura narco.", {
	'entities':  [(54, 63, 'LOC')]
}),

("Otra estadística reciente de la Sedronar permite entender la lógica de expansión del mercado de drogas.", {
	'entities':  [(32, 40, 'ORG'),(96, 102, 'DRUG')]
}),

("Cada año 130.000 estudiantes, la mayoría con menos de 15 años, se suman al consumo de marihuana.", {
	'entities':  [(86, 95, 'DRUG')]
}),

("Hoy el crecimiento del mercado local de drogas provoca aquí mayor impacto negativo que la circulación de grandes cargamentos de drogas con destino a otros países.", {
	'entities':  [(40, 46, 'DRUG'),(128, 134, 'DRUG')]
}),

("Un ejemplo natural de ese caso es la banda rosarina conocida como Los Monos.", {
	'entities':  [(66, 75, 'ORG')]
}),

("Demasiados rudimentarios como para formar algo más que un peligroso clan, Los Monos captaron adeptos, colonizaron barrios y se volvieron el ideal de niños en sus zonas de influencia por la ausencia de la justicia federal de Rosario.", {
	'entities':  [(74, 83, 'ORG'),(224, 231, 'LOC')]
}),

("Los Monos no fueron juzgados aún por venta de droga, sino colocados frente a un tribunal por la justicia provincial en una causa de asociación ilícita y homicidios.", {
	'entities':  [(0, 9, 'ORG'),(46, 51, 'DRUG'),(80, 88, 'MISC')]
}),

("Situaciones similares se vivieron en varias provincias y en la ciudad de Buenos Aires.", {
	'entities':  [(63, 85, 'LOC')]
}),

("Se permitió por desinterés judicial que el vendedor local de drogas se convirtiese en un modelo social y que el sueño de niños fuese la integración en una pandilla.", {
	'entities':  [(61, 67, 'DRUG')]
}),

("Fue creada por el comprador argentino de drogas y su discurso de uso recreativo de la sustancia.", {
	'entities':  [(41, 47, 'DRUG')]
}),

("ROSARIO.- El Chevrolet Corsa color gris clavó los frenos poco después de las 22.30 y, en medio de la penumbra, un instante después comenzaron los disparos que tenían como destinatario a un ex convicto al que los sicarios buscaban por una vieja deuda de drogas.", {
	'entities':  [(0, 7, 'LOC'),(13, 22, 'ORG'),(253, 259, 'DRUG')]
}),

("Pero las balas mataron a dos jóvenes que cenaban en Grandoli y Seguí, en el barrio de La Tablada.", {
	'entities':  [(52, 68, 'LOC'),(76, 96, 'LOC')]
}),

("Uno de ellos, Luis Hernán Tourn, de 26 años, era un jugador de fútbol que transitó por las ligas chilena y de Puerto Rico con escaso éxito y que ahora probaba suerte en Zavalla, una localidad ubicada a 38 kilómetros de Rosario.", {
	'entities':  [(14, 31, 'PER'),(110, 121, 'LOC'),(169, 176, 'LOC'),(219, 226, 'LOC')]
}),

("En las últimas 48 horas se produjeron siete homicidios en distintas zonas de Rosario y de Villa Gobernador Gálvez, una espiral de violencia que sacudió el fin de año, luego de un 2017 en el que, a pesar de la repetición de casos de venganzas ligadas a tramas de narcomenudeo, hubo una leve baja en el número general de homicidios, que pasaron de 171 en 2016 a 160 el año pasado.", {
	'entities':  [(77, 84, 'LOC'),(90, 113, 'LOC')]
}),

("Los balazos en el barrio La Tablada también alcanzaron a Sofía Barreto, de 24 años, una amiga de la novia del futbolista.", {
	'entities':  [(18, 35, 'LOC'),(57, 70, 'PER')]
}),

("Una mujer de 64 años recibió un disparo en la espalda que le comprometió un pulmón, mientras que un hombre de 62 y su hijo de 22 se encuentran en estado crítico en el hospital Roque Sáenz Peña, al recibir balazos en una pierna y en la cabeza, respectivamente.", {
	'entities':  [(167, 192, 'ORG'),(167, 175, 'MISC')]
}),

("La escena violenta se completó con otro crimen en Villa Gobernador Gálvez, ciudad vecina a Rosario, donde un joven de 24 años murió de un disparo en el tórax en un complejo de Fonavi, adonde -según la pareja de la víctima- llegó un hombre que tras una breve discusión lo ultimó de un escopetazo en una casa ubicada en Guereño y Mármol.", {
	'entities':  [(50, 73, 'LOC'),(91, 98, 'LOC'),(176, 182, 'ORG'),(318, 334, 'LOC')]
}),

("Los vecinos de barrio La Tablada estaban consternados ayer a la mañana luego de que fueron asesinados dos jóvenes en medio de una cena familiar.", {
	'entities':  [(22, 32, 'LOC')]
}),

("*Fue un ajuste de cuentas y todos en el barrio sabemos que es por drogas*, sentenció una mujer, que se negó a decir su nombre por temor a represalias.", {
	'entities':  [(66, 72, 'DRUG')]
}),

("Las víctimas no tenían nada que ver con esa trama atravesada por el narcomenudeo, en una zona que está en permanente disputa entre la banda Los Monos y otros clanes familiares, como los Funes y los Caminos.", {
	'entities':  [(140, 149, 'ORG'),(182, 191, 'ORG'),(194, 205, 'ORG')]
}),

("Los tres sicarios que irrumpieron poco después de las 22.30 en Grandoli y Seguí buscaban al cuñado de Tourn, un muchacho que gozaba de salidas transitorias de la cárcel de Piñero, donde estaba preso desde hacía tres años por robo calificado.", {
	'entities':  [(63, 79, 'LOC'),(102, 107, 'PER'),(162, 168, 'MISC'),(172, 178, 'LOC')]
}),

("Según el relato de los vecinos, el presidiario logró huir del tiroteo, al escabullirse unos segundos después de que apareció el Chevrolet Corsa.", {
	'entities':  [(128, 137, 'ORG'),(138, 143, 'MISC')]
}),

("Los disparos no dieron en el blanco buscado, pero mataron a Tourn y Barreto e hirieron a tres personas que compartían la cena.", {
	'entities':  [(60, 65, 'PER'),(68, 75, 'PER')]
}),

("El hijo del hombre que vive acá había salido con permiso de la cárcel de Piñero.", {
	'entities':  [(63, 69, 'MISC'),(73, 79, 'PER')]
}),

("Tourn era jugador de fútbol y había probado suerte en las categorías de ascenso en Chile y luego en Puerto Rico.", {
	'entities':  [(83, 88, 'LOC'),(100, 111, 'LOC')]
}),

("Además de jugar al fútbol, Tourn trabajaba en la distribuidora de galletitas Tyna.", {
	'entities':  [(27, 32, 'PER'),(77, 81, 'ORG')]
}),

("La última saga de asesinatos en Rosario comenzó durante la madrugada del 1º de enero en la zona oeste, con un enfrentamiento en las calles Ituzaingó y Servando Bayo, donde dos familias se enfrentaron a tiros.", {
	'entities':  [(32, 39, 'LOC'),(139, 164, 'LOC')]
}),

("Según voceros policiales, este hecho tendría que ver con viejas disputas territoriales por la venta de droga en ese sector de Rosario, donde la violencia recrudeció en diciembre último.", {
	'entities':  [(103, 108, 'DRUG'),(126, 133, 'LOC')]
}),

("Fabrizio Moreira, de 28 años, y Jorge Mendoza, de 27, fueron llevados por sus familiares al Hospital de Emergencias Clemente Álvarez (HECA) en vehículos particulares, pero fallecieron a causa de las heridas de bala cuando ingresaron en el centro asistencial.", {
	'entities':  [(0, 16, 'PER'),(32, 45, 'PER'),(92, 139, 'ORG')]
}),

("En el norte de Rosario, en La Cerámica, se produjo otro crimen durante esa madrugada.", {
	'entities':  [(15, 22, 'LOC'),(27, 38, 'LOC')]
}),

("Un joven de 22 años fue asesinado a balazos en Servellera y Grandoli.", {
	'entities':  [(47, 68, 'LOC')]
}),

("Según indicaron desde el Ministerio Público de la Acusación (MPA) de Rosario, Joel Tejera fue derivado en un auto particular al hospital Alberdi, donde murió por múltiples heridas de arma de fuego.", {
	'entities':  [(25, 65, 'ORG'),(69, 76, 'LOC'),(78, 89, 'PER'),(128, 144, 'ORG'),(128, 136, 'MISC')]
}),

("Fue atacado por un grupo de personas cuando estaba en un Peugeot 207, que también presentaba tres orificios de bala.", {
	'entities':  [(57, 68, 'MISC'),(57, 64, 'ORG')]
}),

("La policía detuvo en Luzuriaga al 3900 a un adolescente de 15 años, apuntado por una vecina como presunto autor de los disparos mortales.", {
	'entities':  [(21, 38, 'LOC')]
}),

("Un hombre de 46 años fue asesinado de un tiro en el abdomen tras mantener una supuesta discusión en la zona oeste de Rosario.", {
	'entities':  [(103, 124, 'LOC')]
}),

("Fue trasladado al HECA, pero murió a las pocas horas.", {
	'entities':  [(18, 22, 'ORG')]
}),

("Y otro ataque a balazos se produjo durante la madrugada en la localidad de Alvear, vecina a Rosario, donde un hombre de 44 años fue acribillado en la puerta de su casa en El Aguaribay y El Timbó.", {
	'entities':  [(75, 81, 'LOC'),(92, 99, 'LOC'),(171, 194, 'LOC')]
}),

("La zona en la que se concretó el ataque es un territorio de venta de drogas disputado por Los Monos y otros clanes familiares, como los Funes y los Caminos.", {
	'entities':  [(69, 75, 'DRUG'),(90, 99, 'ORG'),(132, 141, 'ORG'),(144, 155, 'ORG')]
}),

("Los vecinos aseguran que esta nueva agresión fue originada por una deuda de drogas.", {
	'entities':  [(76, 82, 'DRUG')]
}),

("Y, ahora, otras mafias siguen esos pasos, tal como quedó expuesto al ser desbaratada una banda que traficaba medicamentos y pagaba los cargamentos con autos de lujo.", {
	'entities':  [(109, 121, 'DRUG')]
}),

("La investigación empezó el 8 de julio pasado, en el Paso Internacional Cardenal Antonio Samoré, cuando inspectores de la Dirección General de Aduanas descubrieron el intento de dos supuestos turistas chilenos de ingresar en forma ilegal un cargamento de tiras reactivas para medir el nivel de glucosa por un valor de $ 900.000.", {
	'entities':  [(52, 94, 'LOC'),(121, 149, 'ORG'),(200, 208, 'MISC')]
}),

("Detrás de los dos sospechosos había una organización criminal dedicada a la falsificación de la fecha de vencimiento de medicamentos y la adulteración de recetas con la intención de estafar al PAMI y otras obras sociales.", {
	'entities':  [(193, 197, 'ORG')]
}),

("En el sector farmacéutico se estima que el 11% de los remedios comercializados en la Argentina son ilegales.", {
	'entities':  [(85, 94, 'LOC')]
}),

("Por escuchas telefónicas incorporadas en el expediente, se comprobó que el hecho en el que fueron detenidos los dos falsos turistas chilenos *tenía relación directa con las personas involucradas en la presente causa*, informaron fuentes del caso.", {
	'entities':  [(132, 140, 'MISC')]
}),

("Hace diez días, después de cuatro meses de investigación, fueron detenidos siete sospechosos en allanamientos realizados en Tucumán, Santiago del Estero y Córdoba.", {
	'entities':  [(124, 131, 'LOC'),(133, 152, 'LOC'),(155, 162, 'LOC')]
}),

("Así lo informaron a LA NACION calificadas fuentes de la Policía de Seguridad Aeroportuaria (PSA), fuerza que estuvo a cargo de la investigación desde el 4 de agosto pasado por solicitud del fiscal federal de Córdoba Enrique Senestrari.", {
	'entities':  [(20, 29, 'ORG'),(56, 96, 'ORG'),(208, 215, 'LOC'),(216, 234, 'PER')]
}),

("El representante del Ministerio Público tiene delegado el expediente.", {
	'entities':  [(21, 39, 'ORG')]
}),

("Según informaron las fuentes consultadas, la organización se dedicaba al contrabando de medicamentos (tanto en la importación desde Chile como en la exportación a Bolivia); defraudaciones mediante el uso de recetas falsas (de PAMI y otras obras sociales); venta, suministro, distribución y almacenamiento de remedios peligrosos para la salud.", {
	'entities':  [(88, 100, 'DRUG'),(132, 137, 'LOC'),(163, 170, 'LOC'),(226, 230, 'ORG'),(308, 316, 'DRUG')]
}),

("El comercio ilegal de medicamentos representa en la Argentina un mercado anual de $ 200.000.000, según explicaron referentes del sector farmacéutico.", {
	'entities':  [(22, 34, 'DRUG'),(52, 61, 'LOC')]
}),

("*Esta organización introducía de manera ilegal medicamentos, principalmente desde Chile, modificando las fechas de vencimiento de los medicamentos y los troqueles, con la intención de obtener grandes ganancias a través de la afectación de la salud pública y la evasión fiscal*, explicaron fuentes de la PSA.", {
	'entities':  [(47, 59, 'DRUG'),(82, 87, 'LOC'),(303, 306, 'ORG')]
}),

("Como hacen muchas organizaciones narcocriminales, esta banda pagaba los medicamentos que eran comprados a proveedores de Chile con vehículos del alta gama.", {
	'entities':  [(72, 84, 'DRUG'),(121, 126, 'LOC')]
}),

("No les importaban de dónde venían la insulina y las tiras reactivas.", {
	'entities':  [(37, 45, 'DRUG'),(52, 67, 'DRUG')]
}),

("«Los muertos no reclaman», decían los sospechosos*, remarcó a LA NACION una fuente con acceso a la causa.", {
	'entities':  [(62, 71, 'ORG')]
}),

("*Pero no sólo se dedicaban al contrabando de medicamentos y a cambiar las fechas de vencimiento, sino que también encontramos recetas, troqueles y sellos, lo que indicaría una estafa millonaria contra el PAMI y otras obras sociales*, sostuvo un investigador del caso.", {
	'entities':  [(45, 57, 'DRUG'),(204, 208, 'ORG')]
}),

("En la causa también colabora la Unidad Fiscal para la Investigación de delitos cometidos en el ámbito de actuación del Instituto Nacional de Servicios Sociales para Jubilados y Pensionados, más conocida como UFI PAMI, que está a cargo del fiscal Javier Arzubi Calvo.", {
	'entities':  [(32, 188, 'ORG'),(208, 216, 'ORG'),(246, 265, 'PER')]
}),

("En los próximos días, el juez federal de Córdoba Ricardo Bustos Fierro deberá definir la situación procesal de los siete imputados detenidos.", {
	'entities':  [(41, 48, 'LOC'),(49, 70, 'PER')]
}),

("*Luego de meses de investigación desarticulamos una banda que ingresaba ilegalmente medicamentos en el país, adulteraba la fecha de vencimiento y falsificaba los troqueles, evadía al fisco y lo peor: jugaba con la salud de la gente*, sostuvo la ministra de Seguridad, Patricia Bullrich, al referirse a este caso en su perfil de la red social Facebook.", {
	'entities':  [(268, 285, 'PER'),(342, 350, 'ORG')]
}),

("Los allanamientos, ordenados por el juez Bustos Fierros, se hicieron en Córdoba, Tucumán y Santiago del Estero.", {
	'entities':  [(41, 55, 'PER'),(72, 79, 'LOC'),(81, 88, 'LOC'),(91, 110, 'LOC')]
}),

("En los procedimientos se incautaron cajas para armar medicamentos, planchas de troqueles presuntamente apócrifos, troqueles sueltos, ampollas sin rótulo con etiquetas sueltas con la leyenda *heroína 0,001*, lapiceras de insulina con etiquetas presuntamente falsas, insulina sin troquel, una heladera con medicación, sellos de médicos, tickets de envío de encomiendas y recetas de PAMI.", {
	'entities':  [(53, 65, 'DRUG'),(191, 198, 'DRUG'),(265, 285, 'DRUG'),(380, 384, 'ORG')]
}),

("Los detectives de la Unidad Operacional de Control del Narcotráfico y el Delito Complejo 2 del Centro de la PSA también decomisaron $ 2.521.472 y US$ 4077; 22 armas, y 27 vehículos, cuatriciclos, motos, teléfonos celulares y dispositivos electrónicos.", {
	'entities':  [(21, 111, 'ORG')]
}),

("ROSARIO.- Entraron sonrientes y desafiantes a la sala de audiencias, después de desvestirse y provocar un retraso de casi tres horas en el inicio del juicio.", {
	'entities':  [(0, 7, 'LOC')]
}),

("Los Monos demostraron, una vez más, que podían dominar la situación hasta en el propio juicio que enfrentan con expectativas de penas elevadas.", {
	'entities':  [(0, 9, 'ORG')]
}),

("Pero esto pareció no importarle al grupo criminal rosarino que recién fue procesado por narcotráfico en la justicia federal en noviembre de 2015, cuando la mayoría de los líderes estaban presos.", {
	'entities':  [(50, 58, 'MISC')]
}),

("Desde la cárcel, seguían controlando la violencia y la venta de drogas.", {
	'entities':  [(9, 15, 'MISC'),(64, 70, 'DRUG')]
}),

("Los búnkeres, donde se vendía una cocaína barata y adaptada al mercado popular, que los hizo ricos, estaban en lugares fijos, a contramano de lo que es una actividad ilícita.", {
	'entities':  [(34, 41, 'DRUG')]
}),

("Los Monos no podrían haber existido sin este brazo del Estado, que es mayoría en el banquillo de los acusados, ni tampoco sin la complicidad y la indiferencia del poder político, que sólo los divisó en el radar cuando Los Monos quisieron.", {
	'entities':  [(0, 9, 'ORG'),(218, 227, 'ORG')]
}),

("Ocurrió horas después del crimen del líder del grupo Claudio Ariel Cantero, alias *Pájaro*, cuando este clan narco se esforzó por hacer teatral la venganza, con una persecución febril por los pasillos de tribunales a Diego Demarre, a quien consideraron un entregador y que fue acribillado en la esquina de su casa.", {
	'entities':  [(53, 74, 'PER'),(83, 89, 'PER'),(217, 230, 'PER')]
}),

("Y el ataque horas después a la familia de Milton César, a quien apuntaban como sicario, que dejó tres muertos dentro de una camioneta Toyota Hilux en pleno mediodía y frente a un jardín de infantes.", {
	'entities':  [(42, 54, 'PER'),(134, 140, 'ORG'),(134, 146, 'MISC')]
}),

("Esa demostración de rabia de Los Monos en una ciudad conmovida por 264 crímenes en un año estaba dirigida a preservar el territorio que dominaban y, también, a evitar ser apartados del negocio millonario del narcotráfico que regulaba la propia policía.", {
	'entities':  [(29, 38, 'ORG')]
}),

("También tenía como destinatario al gobierno de Santa Fe.", {
	'entities':  [(47, 55, 'LOC')]
}),

("Los fiscales argumentaron esta semana que este grupo *rentabilizó la violencia* para crecer en el negocio de la droga.", {
	'entities':  [(112, 117, 'DRUG')]
}),

("En las 408 páginas del fallo de procesamiento se advierte que los Cantero *ejercieron cierto gobierno de facto por sobre toda otra autoridad*.", {
	'entities':  [(66, 73, 'PER')]
}),

("Desde hace cinco años, Los Monos se convirtieron en un actor político.", {
	'entities':  [(23, 32, 'ORG')]
}),

("Antes negociaban por debajo de la superficie, como lo hicieron cuando se empezó a construir el casino City Center hace más de una década en la zona sur de Rosario.", {
	'entities':  [(95, 101, 'MISC'),(102, 113, 'ORG'),(143, 162, 'LOC')]
}),

("La sala de juegos más grande de América del Sur, que hasta el año pasado fue controlada por el consorcio de Cristóbal López, se edificó en un terreno de siete hectáreas que dominaban Los Monos.", {
	'entities':  [(32, 47, 'LOC'),(108, 123, 'PER'),(183, 192, 'ORG')]
}),

("Los Cantero negociaron con la empresa el traslado de las 300 familias que ocupaban una villa de emergencia en el predio donde tres años después se inauguró la sala de juegos de 135.000 metros cuadrados, donde llamativamente la inseguridad nunca afectó a los apostadores en una de las zonas más peligrosas de Rosario.", {
	'entities':  [(0, 11, 'ORG'),(308, 315, 'LOC')]
}),

("Las obras de la colectora de la autopista necesarias para la zona no se lograban terminar por los piquetes permanentes que interrumpían el flujo de tráfico en el acceso desde Buenos Aires.", {
	'entities':  [(175, 187, 'LOC')]
}),

("Los Cantero acordaron y el municipio tuvo que contratar sus máquinas retroexcavadoras para llevar adelante las obras.", {
	'entities':  [(0, 11, 'ORG')]
}),

("Cada protesta de vecinos en el barrio Las Flores, que se disparaba por distintos motivos, como la falta de una escuela, terminaba en una negociación mediada por los Cantero.", {
	'entities':  [(38, 48, 'LOC'),(111, 118, 'MISC'),(161, 172, 'ORG')]
}),

("En muchos casos, los acuerdos incluían cederles a Los Monos el ingreso de personal al Estado, como lo hicieron otros jugadores aliados a esta banda en el mapa narco, como el ex jefe de la barra de Newell's Roberto Caminos, alias *Pimpi*.", {
	'entities':  [(50, 59, 'ORG'),(197, 205, 'ORG'),(206, 221, 'PER'),(230, 235, 'PER')]
}),

("Con ese apoyo, ahora los Monos planean disputar la conducción de uno de los sindicatos estatales.", {
	'entities':  [(21, 30, 'ORG')]
}),

("Después de un largo recorrido, los Cantero discuten actualmente sobre la superficie de la escena pública, como ocurrió hace unos días en el juicio, cuando Ramón Machuca, uno de los líderes, dijo frente al tribunal que Los Monos *son un chivo expiatorio del socialismo*.", {
	'entities':  [(155, 168, 'PER'),(218, 227, 'ORG')]
}),

("El resto del arco político, incluido Cambiemos, prefiere estar lejos del *debate* entre un grupo narco y un sector político.", {
	'entities':  [(37, 46, 'ORG')]
}),

("*Cuando el diputado (Andrés) Larroque trató de narcosocialismo al gobierno de esta provincia, la respuesta política fue armar una causa para demostrarle a la sociedad que nosotros somos el mal de Santa Fe y que yo vendría a ser el monstruo más grande que existe*, dijo el imputado en el juicio, a quien la Fiscalía pidió 41 años de condena, acusado de liderar una asociación ilícita y por cuatro asesinatos, entre ellos el de Lourdes, de sólo 14 años.", {
	'entities':  [(21, 27, 'PER'),(29, 37, 'PER'),(196, 204, 'LOC'),(426, 433, 'PER')]
}),

("Machuca contextualizó su declaración en la audiencia con la acusación que lanzó el legislador de La Cámpora en una sesión en 2012 de la Cámara de Diputados de la Nación, algo que le valió el repudio de gran parte del arco político y la ira del socialismo, porque entendían que ese rótulo iba a ser difícil de olvidar.", {
	'entities':  [(0, 7, 'PER'),(97, 107, 'ORG'),(136, 168, 'ORG')]
}),

("Hermes Binner, quien encabezaba la coalición del Frente Amplio Progresista, se perfilaba en ese momento como uno de los principales opositores a Cristina Fernández, tras quedar segundo en las elecciones presidenciales de 2011.", {
	'entities':  [(0, 13, 'PER'),(49, 74, 'ORG'),(145, 163, 'PER')]
}),

("En el socialismo están convencidos de que el kirchnerismo dejó que el problema de la violencia y el narcotráfico estallara en Santa Fe para así poder neutralizar y dejar fuera de carrera un potencial contrincante político, en momentos en que estaban en experimentación alianzas electorales para enfrentar a Cristina.", {
	'entities':  [(126, 134, 'LOC'),(307, 315, 'PER')]
}),

("Los que más se aprovecharon de ese contexto político fueronLos Monos.", {
	'entities':  [(59, 68, 'ORG')]
}),

("La justicia federal los empezó a investigar por narcotráfico 15 días antes de que la entonces presidenta dejara el poder, una causa que aún no fue elevada a juicio, pero que se activó 18 años después de que Ariel Cantero, el líder más antiguo de la banda, fuera detenido con 70 kilos de marihuana en Itatí, Corrientes.", {
	'entities':  [(207, 220, 'PER'),(287, 296, 'DRUG'),(300, 305, 'LOC'),(307, 317, 'LOC')]
}),

("El líder de Los Monos trajo otra vez esa frase de *Cuervo* Larroque y lanzó una acusación contra el ex gobernador Antonio Bonfatti al asegurar que este tejió un trato comercial con el narco Luis Medina (asesinado a fines de 2013), por dos autos que estaban a nombre del ex gobernador.", {
	'entities':  [(12, 21, 'ORG'),(51, 57, 'PER'),(59, 67, 'PER'),(114, 130, 'PER'),(190, 201, 'PER')]
}),

("También expresó que si hubiera pagado el millón de pesos que le pedía un grupo de policías que lo perseguía no estaría sentado en el banquillo de los acusados en el juicio ni hubiese permanecido prófugo durante tres años, hasta que fue detenido el 6 de junio del año pasado por la Policía Federal en el barrio de Flores, en Buenos Aires.", {
	'entities':  [(281, 296, 'ORG'),(313, 319, 'LOC'),(324, 336, 'LOC')]
}),

("El lugar del arresto no fue extraño, ya que ese jefe del clan de Los Monos estuvo varias veces en la cancha de San Lorenzo.", {
	'entities':  [(65, 74, 'ORG'),(101, 107, 'MISC'),(111, 122, 'ORG')]
}),

("La Justicia estima que este grupo narco mantuvo fuertes vínculos con representantes de jugadores como forma de lavar el dinero originado en la venta de drogas.", {
	'entities':  [(152, 158, 'DRUG')]
}),

("La respuesta que ensayó el socialismo, presidido por Bonfatti, fue un comunicado de prensa, en el que advierten que *con mentiras (los Monos) buscan entorpecer el trabajo del Poder Judicial*.", {
	'entities':  [(53, 61, 'PER'),(131, 140, 'ORG')]
}),

("Bonfatti no dio una respuesta al desafío lanzado por el jefe narco y sus allegados señalaron que su posición personal está en línea con el comunicado del socialismo.", {
	'entities':  [(0, 8, 'PER')]
}),

("En esa fuerza nunca terminaron de explicar por qué Bonfatti retiró la imputación contra el único identificado por el atentado con 21 balazos contra el frente de su casa en octubre de 2013.", {
	'entities':  [(51, 59, 'PER')]
}),

("El gobierno de Bonfatti intentó sellar un acuerdo con Los Monos en abril de 2015 a cambio de la reducción de penas.", {
	'entities':  [(15, 23, 'PER'),(54, 63, 'ORG')]
}),

("Temían que la investigación del juez Juan Carlos Vienna se cayera por el comportamiento del magistrado: había hecho dos viajes a Estados Unidos con un narco cuyo hijo había pertenecido a la banda y fue asesinado por tratar de independizarse.", {
	'entities':  [(37, 55, 'PER'),(129, 143, 'LOC')]
}),

("El legislador de Cambiemos Federico Angelini consideró que *lo que quedó de manifiesto fue la convivencia política entre el gobierno y este grupo narcocriminal, algo que se cristalizó en muchos otros planos*.", {
	'entities':  [(17, 26, 'ORG'),(27, 44, 'PER')]
}),

("Lo que rompió el acuerdo fue la derrota electoral de Miguel Lifschitz en las PASO de 2015 frente a Miguel Del Sel.", {
	'entities':  [(53, 69, 'PER'),(99, 113, 'PER')]
}),

("*Los barrios de Rosario se convirtieron en un territorio dominado por la violencia de este grupo y el monopolio de esa violencia terminó siendo respetado políticamente*, dijo el diputado Carlos Del Frade, a quien el líder de los Monos Máximo Ariel Cantero, alias *Guille*, le apuntó con el dedo índice y una sonrisa desafiante desde el banquillo.", {
	'entities':  [(16, 23, 'LOC'),(187, 203, 'PER'),(225, 234, 'ORG'),(235, 255, 'PER'),(264, 270, 'PER')]
}),

("Se lo considera el juicio penal más importante de la provincia de Santa Fe.", {
	'entities':  [(66, 74, 'LOC')]
}),

("Los acusados son 25 integrantes de la banda de narcotraficantes rosarina Los Monos, entre los cuales hay policías que integran el grupo.", {
	'entities':  [(73, 82, 'ORG')]
}),

("La actitud desafiante que adoptaron mientras se les leían las graves acusaciones que pesan sobre ellos es un reflejo del poder que acumuló este grupo capitaneado por la familia Cantero, que ejerce en el mundo del crimen desde hace décadas, hasta que la violencia que lo caracteriza le otorgó dimensión nacional, poniéndole nombre y ubicación en el mapa a un fenómeno que no es exclusivo de Rosario, pues se reproduce con menos ruido pero idéntico poder destructivo en el Gran Buenos Aires y otras ciudades de la Argentina.", {
	'entities':  [(177, 184, 'PER'),(390, 397, 'LOC'),(471, 488, 'LOC'),(512, 521, 'LOC')]
}),

("Se trata, en principio, de un doble poder destructivo, pues al de la droga se le suma el de las armas de fuego que emplean los narcos para defender sus zonas de venta ajusticiando a las familias rivales -que a su vez toman sus represalias- y amedrentando a los que podrían hacerles frente.", {
	'entities':  [(69, 74, 'DRUG')]
}),

("Los Monos son un ejemplo de cómo se expande un imperio edificado a partir de drogas de baja calidad y, por consiguiente, más dañinas, al alcance de más adictos.", {
	'entities':  [(0, 9, 'ORG'),(77, 83, 'DRUG')]
}),

("Es que parte de la cúpula de la policía santafecina había sido captada por los narcos y, luego de que el gobierno de la provincia comenzó una depuración en la fuerza en 2013, la casa del gobernador Antonio Bonfatti fue atacada a balazos mientras él y su familia estaban adentro.", {
	'entities':  [(198, 214, 'PER')]
}),

("Ese año hubo 264 asesinatos en Rosario.", {
	'entities':  [(31, 38, 'LOC')]
}),

("Los fiscales del juicio afirmaron que Los Monos *rentabilizaron la violencia* para incrementar sus negocios con la droga y que los Cantero *ejercieron cierto gobierno de facto por sobre toda otra autoridad*.", {
	'entities':  [(38, 47, 'ORG'),(115, 120, 'DRUG'),(131, 138, 'PER')]
}),

("De ahí que, como informó LA NACION, cuyo corresponsal en Rosario fue amenazado de muerte años atrás, hace ya cinco años que Los Monos se convirtieron en un actor político tejiendo alianzas diversas.", {
	'entities':  [(25, 34, 'ORG'),(57, 64, 'LOC'),(124, 133, 'ORG')]
}),

("En un principio negociaban en secreto, como ocurrió cuando comenzó a erigirse el casino City Center en la zona sur de Rosario, la sala de juegos más grande de América del Sur, que hasta el año pasado controló el consorcio que lideraba Cristóbal López.", {
	'entities':  [(81, 87, 'MISC'),(88, 99, 'ORG'),(106, 125, 'LOC'),(159, 174, 'LOC'),(235, 250, 'PER')]
}),

("Ese casino se edificó en un terreno de siete hectáreas que dominaban Los Monos.", {
	'entities':  [(69, 78, 'ORG')]
}),

("Por eso, los Cantero negociaron con la empresa el traslado de las 300 familias que habitaban la villa de emergencia que creció en ese terreno.", {
	'entities':  [(9, 20, 'ORG')]
}),

("Siempre llamó la atención que, tras la inauguración, nunca hubo problemas de inseguridad para los apostadores en una de las zonas más peligrosas de Rosario.", {
	'entities':  [(148, 155, 'LOC')]
}),

("Ramón Machuca, uno de los líderes del grupo, dijo ante el tribunal que Los Monos *son un chivo expiatorio del socialismo*.", {
	'entities':  [(0, 13, 'PER'),(71, 80, 'ORG')]
}),

("Esa actitud puede ayudar a explicar las derrotas sufridas por esa fuerza política, que nunca explicó por qué Bonfatti retiró la acusación contra el único identificado por el atentado contra su casa.", {
	'entities':  [(109, 117, 'PER')]
}),

("Su gobierno buscó un acuerdo con Los Monos en 2015 a cambio de la reducción de penas, ante el temor de que se cayera una investigación por la conducta de un cuestionado juez.", {
	'entities':  [(33, 42, 'ORG')]
}),

("Hubo que esperar hasta noviembre de 2015, poco antes de que Cristina Kirchner abandonara el poder, para que la justicia federal procesara a un grupo de Los Monos cuando sus principales líderes ya se encontraban presos y desde sus celdas seguían manejando y administrando los negocios paralelos de la droga y la violencia, actividad que continuarían realizando ahora.", {
	'entities':  [(60, 77, 'PER'),(152, 161, 'ORG'),(300, 305, 'DRUG')]
}),

("Durante la tarde del pasado 19 de junio, mientras decenas de niños regresaban de la escuela por un pasillo de la manzana 105, el sicario paraguayo Fredy Ramón Gaona Rivas disparó ocho municiones de su pistola 9 milímetros para sellar un ajuste de cuentas.", {
	'entities':  [(137, 146, 'MISC'),(147, 170, 'PER')]
}),

("Juan Carlos Torrico Herbas recibió el primer impacto en el estómago.", {
	'entities':  [(0, 26, 'PER')]
}),

("En un bolsillo de su pantalón, la víctima tenía un billete de dos pesos y también algunos gramos de marihuana.", {
	'entities':  [(100, 109, 'DRUG')]
}),

("La Fiscalía Federal N° 1 presentó este mes el requerimiento de elevación a juicio por ese homicidio y dio por concluida la investigación iniciada por el fiscal Ignacio Mahiques.", {
	'entities':  [(3, 24, 'ORG'),(160, 176, 'PER')]
}),

("Los documentos judiciales revelan cómo se mueven actualmente los grupos criminales que con ramificaciones en Perú y Paraguay dominan un importante escenario del narcotráfico porteño.", {
	'entities':  [(109, 113, 'LOC'),(116, 124, 'LOC')]
}),

("El asesinado Juan Carlos Torrico Herbas trabajaba como custodio para la organización de narcotraficantes que es dirigida por el peruano César Morán de la Cruz, actualmente detenido en una cárcel de la Patagonia.", {
	'entities':  [(13, 32, 'PER'),(128, 135, 'MISC'),(136, 158, 'PER'),(188, 194, 'MISC'),(201, 210, 'LOC')]
}),

("Y fue asesinado por orden de un criminal -identificado tras averiguaciones policiales con el alias *Oki* que dirige en la villa 31 algunos movimientos territoriales del segundo grupo más poderoso de la zona, cuyos miembros son todos inmigrantes paraguayos.", {
	'entities':  [(122, 130, 'LOC'),(245, 255, 'MISC')]
}),

("Según el expediente, agentes encubiertos e investigadores judiciales pudieron comprobar que a Torrico Herbas lo mataron con ocho disparos porque luego de traicionar a sus propios líderes fracasó un negocio que él había planeado junto con narcotraficantes rivales.", {
	'entities':  [(94, 108, 'PER')]
}),

("Desprotegido, estafado y sin dinero, Torrico Herbas exigió violentamente el pago de una deuda, y los narcos paraguayos no tuvieron piedad.", {
	'entities':  [(37, 51, 'PER'),(108, 118, 'MISC')]
}),

("Datos a los que accedió LA NACION indican que más de 30 traficantes vinculados a las disputas en la villa 31 se encuentran detenidos en prisiones federales.", {
	'entities':  [(24, 33, 'ORG'),(100, 108, 'LOC')]
}),

("El homicidio de Torrico Herbas reveló, en primer lugar, un cambio de métodos.", {
	'entities':  [(16, 30, 'PER')]
}),

("Frente al inmenso operativo policial y judicial desplegado en la villa 31 durante 2016, los traficantes de la zona ahora apelan también a los sobornos de rivales para ganar nuevos puntos de venta, como una alternativa a las ruidosas armas de fuego y las usurpaciones.", {
	'entities':  [(65, 73, 'LOC')]
}),

("Un testigo que declaró bajo identidad reservada ante la Justicia luego del crimen de Torrico Herbas aseguró que los narcotraficantes paraguayos no suelen descartar las armas utilizadas en los homicidios, y dijo que *los fierros* circulan permanentemente, de mano en mano.", {
	'entities':  [(85, 99, 'PER'),(133, 143, 'MISC')]
}),

("Días antes de ser ejecutado, en un suceso que anticipó su final, Torrico Herbas fue apuñalado dos veces en un pasillo de la villa por un peligroso narcotraficante paraguayo apodado *Bombilla*, que ahora también es investigado por la Justicia como lugarteniente de la zona.", {
	'entities':  [(65, 79, 'PER'),(124, 129, 'MISC'),(124, 129, 'MISC'),(163, 172, 'MISC'),(182, 190, 'PER')]
}),

("Paulo Seco se tiró debajo de la camioneta VW Amarok como un rayo.", {
	'entities':  [(0, 10, 'PER'),(42, 44, 'ORG'),(42, 51, 'MISC')]
}),

("Temía que la policía brasileña lo matara.", {
	'entities':  [(21, 30, 'MISC')]
}),

("Cuando los efectivos le ordenaron que saliera, mientras lo apuntaban con sus armas, José Paulo Vieira de Mello, conocido como Paulo Seco, recurrió a un viejo truco: les ofreció un millón de reales, que les entregaría su socio Pinto Brum.", {
	'entities':  [(84, 110, 'PER'),(126, 136, 'PER'),(226, 236, 'PER')]
}),

("Pero su coartada no prosperó, porque su colega del Comando Vermelho estaba esposado aquel 12 de agosto pasado en la mansión del barrio Cruzeiro do Sul en Tramandaí, en Río Grande Do Sul.", {
	'entities':  [(51, 67, 'ORG'),(135, 150, 'LOC'),(154, 163, 'LOC'),(168, 185, 'LOC')]
}),

("Allí, junto con dos narcos colombianos, Pinto Brum y Paulo Seco, camuflados como empresarios del rubro de lencería, planeaban un golpe millonario a un banco de Porto Alegre.", {
	'entities':  [(27, 38, 'MISC'),(40, 50, 'PER'),(53, 63, 'PER'),(160, 172, 'LOC')]
}),

("Brum había regresado hacía poco tiempo de la Argentina, de donde se fugó -como ya lo había hecho en otros países- por la frontera extensa y porosa con Paraguay y Brasil.", {
	'entities':  [(0, 4, 'PER'),(45, 54, 'LOC'),(151, 159, 'LOC'),(162, 168, 'LOC')]
}),

("Su nuevo proyecto delictivo se financió con una especie de aeródromo narco que montó en las estancias Santa Úrsula y Santa María de Aguapey, en un monte cerrado cerca de Santo Tomé, Corrientes.", {
	'entities':  [(102, 114, 'LOC'),(117, 139, 'LOC'),(170, 180, 'LOC'),(182, 192, 'LOC')]
}),

("Allí dos veces a la semana aterrizaban avionetas con cargamentos de cocaína.", {
	'entities':  [(68, 75, 'DRUG')]
}),

("La droga se enviaba a los mercados de Brasil y Buenos Aires.", {
	'entities':  [(3, 8, 'DRUG'),(38, 44, 'LOC'),(47, 59, 'LOC')]
}),

("Marino Divaldo Pinto Brum, nombre completo del narco brasileño, vivía en una casa de grandes dimensiones en avenida Trinchera de San José, en Posadas, Misiones, donde se movía en una camioneta Jeep Cherokee blindada, con patente brasileña (PK0777).", {
	'entities':  [(0, 25, 'PER'),(53, 62, 'MISC'),(108, 137, 'LOC'),(142, 149, 'LOC'),(151, 159, 'LOC'),(193, 197, 'ORG'),(193, 206, 'MISC'),(229, 238, 'MISC')]
}),

("En el campo que arrendaba a Hilda Calabrese, una hacendada correntina, pastoreaban unas 150 vacas, pero el negocio no estaba centrado en la raza Braford, sino en el narcotráfico, con una ruta que se viene consolidando desde hace cinco años.", {
	'entities':  [(28, 43, 'PER'),(59, 69, 'MISC')]
}),

("Este corredor de la cocaína tiene a Perú y Bolivia como proveedores del estupefaciente y a Brasil como principal punto de destino, donde se encuentra el segundo mercado de cocaína del mundo después de Estados Unidos, con 2,8 millones de consumidores, según un estudio de la Universidad Federal de San Pablo.", {
	'entities':  [(20, 27, 'DRUG'),(36, 40, 'LOC'),(43, 50, 'LOC'),(72, 86, 'DRUG'),(91, 97, 'LOC'),(172, 179, 'DRUG'),(201, 215, 'LOC'),(274, 306, 'ORG')]
}),

("Los registros en los GPS Garmin Aera 500 que fueron secuestrados a la banda mostraban en detalle la ruta que hacían las avionetas Cessna desde Perú y Bolivia hasta Paraguay y la Argentina.", {
	'entities':  [(21, 40, 'MISC'),(25, 31, 'ORG'),(130, 136, 'MISC'),(143, 147, 'LOC'),(150, 157, 'LOC'),(164, 172, 'LOC'),(178, 187, 'LOC')]
}),

("Descendían en esa pista y en unos minutos los miembros reclutados por Pinto Brum -peruanos, bolivianos, brasileños y argentinos- descargaban la droga, que era llevada una parte a Buenos Aires y otra a Brasil, por la frontera seca de Uruguayana.", {
	'entities':  [(70, 80, 'PER'),(82, 90, 'MISC'),(92, 102, 'MISC'),(104, 114, 'MISC'),(117, 127, 'MISC'),(144, 149, 'DRUG'),(179, 191, 'LOC'),(201, 207, 'LOC'),(233, 243, 'LOC')]
}),

("En abril pasado 11 miembros de esta banda fueron condenados a penas de entre 5 y 20 años de prisión por pedido del fiscal Carlos Schaefer y el titular de la Procuraduría contra el Narcotráfico (Procunar), Diego Iglesias.", {
	'entities':  [(122, 137, 'PER'),(157, 203, 'ORG'),(205, 219, 'PER')]
}),

("Donde había un campo y un aeródromo controlado por un grupo narco internacional ahora se harán trabajos agronómicos de la Universidad de Buenos Aires (UBA).", {
	'entities':  [(122, 155, 'ORG')]
}),

("Brum se fugó tras el allanamiento que hizo la Gendarmería en su casa en Posadas.", {
	'entities':  [(0, 4, 'PER'),(46, 57, 'ORG'),(72, 79, 'LOC')]
}),

("No se supo más de su rastro hasta que fue detenido en una mansión a una cuadra de la playa en Tramandaí por la policía brasileña, que lo identificó como uno de los jefes del Comando Vermelho, una de las organizaciones que junto con el Primer Comando Capital (PCC) son actualmente las más poderosas de América Latina.", {
	'entities':  [(85, 90, 'MISC'),(94, 103, 'LOC'),(119, 128, 'MISC'),(174, 190, 'ORG'),(235, 263, 'ORG'),(301, 315, 'LOC')]
}),

("Estos grupos que surgieron de las cárceles se expandieron hacia Paraguay desde hace más de cinco años.", {
	'entities':  [(64, 72, 'LOC')]
}),

("En la Argentina Pinto Brum usaba el nombre falso de Silvio André de Lima Borges, alias Max, y nadie sabía que en Brasil se enfrentaba con tres condenas por narcotráfico que suman 23 años de prisión.", {
	'entities':  [(6, 15, 'LOC'),(16, 26, 'PER'),(52, 64, 'PER'),(68, 79, 'PER'),(87, 90, 'PER'),(113, 119, 'LOC')]
}),

("En la Argentina no hay una presencia estable ni orgánica de estos dos grupos mafiosos, que tienen una raíz particular, son bastante inorgánicos y actúan muchas veces en células, señalan en el Ministerio de Seguridad.", {
	'entities':  [(6, 15, 'LOC'),(192, 215, 'ORG')]
}),

("Fuentes de la Gendarmería y voceros judiciales coinciden en que empezaron a verse *lobos solitarios* de PCC y Comando Vermelho en Corrientes y Misiones, dos provincias limítrofes con Paraguay, donde estas organizaciones mueven cada vez más los hilos del narcotráfico, con epicentro en Pedro Juan Caballero, que además de ser la zona núcleo de producción de marihuana -ese país es el principal productor mundial de cannabis- se transformó en un área logística de cocaína con dominio de esas dos bandas brasileñas, algo que se aprecia en la violencia que derraman en el departamento de Amambay.", {
	'entities':  [(14, 25, 'ORG'),(104, 107, 'ORG'),(110, 126, 'ORG'),(130, 140, 'LOC'),(143, 151, 'LOC'),(183, 191, 'LOC'),(285, 305, 'LOC'),(357, 366, 'DRUG'),(414, 422, 'DRUG'),(462, 469, 'DRUG'),(501, 511, 'MISC'),(584, 591, 'ORG')]
}),

("El crimen del narco Jorge Rafaat Toumani (con vínculos con el PCC) el 15 de junio de 2016, acribillado de 12 balazos con un arma antiaérea .70, montada en una camioneta, mostró el poder de fuego de esos grupos.", {
	'entities':  [(20, 40, 'PER'),(62, 65, 'ORG')]
}),

("Se sospecha que detrás de su muerte estuvo el brasileño Jarvis Chimenes Pavão.", {
	'entities':  [(46, 55, 'MISC'),(56, 77, 'PER')]
}),

("El argentino nacionalizado paraguayo Néstor Ariel Palma es considerado por la Secretaría Nacional Antidrogas de Paraguay como la mano derecha de Jarvis Pavão.", {
	'entities':  [(3, 12, 'MISC'),(27, 36, 'MISC'),(37, 55, 'PER'),(78, 120, 'ORG'),(145, 157, 'PER')]
}),

("Palma fue detenido por la Gendarmería en Ituzaingó, Corrientes, dos meses después de uno de los asaltos más grandes de la historia de América del Sur.", {
	'entities':  [(0, 5, 'PER'),(26, 37, 'ORG'),(41, 50, 'LOC'),(52, 62, 'LOC'),(134, 149, 'LOC')]
}),

("El 27 de abril pasado un grupo comando de PCC robó la bóveda de Prosegur en Ciudad del Este.", {
	'entities':  [(42, 45, 'ORG'),(64, 72, 'ORG'),(76, 91, 'LOC')]
}),

("Palma, un hombre alto y fornido, con su cabello teñido de canas, fue quien -según el fiscal Marcelo Saldívar- financió parte del asalto.", {
	'entities':  [(0, 5, 'PER'),(92, 108, 'PER')]
}),

("El funcionario del Ministerio Público paraguayo lo acusa de haber alquilado una casa de grandes dimensiones en el country San José, donde se alojaron más de 30 miembros de la organización para planear el golpe.", {
	'entities':  [(19, 37, 'ORG'),(38, 47, 'MISC'),(114, 130, 'LOC')]
}),

("Con un nivel logístico poco común y armas pesadas, como cuatro ametralladoras calibre .50, este brazo del PCC se llevó US$11.720.255 de la bóveda de Prosegur.", {
	'entities':  [(106, 109, 'ORG'),(149, 157, 'ORG')]
}),

("Palma se fugó hacia Buenos Aires y desde allí viajó a Posadas.", {
	'entities':  [(0, 5, 'PER'),(20, 32, 'LOC'),(54, 61, 'LOC')]
}),

("Fue atrapado en una hostería en Ituzaingó, Corrientes.", {
	'entities':  [(32, 41, 'LOC'),(43, 53, 'LOC')]
}),

("Las autoridades guaraníes enviaron un pedido de extradición al juez federal Carlos Soto Dávila.", {
	'entities':  [(76, 94, 'PER')]
}),

("Palma no quería seguir preso en la Unidad Penitenciaria Nº 7 de Resistencia, donde estaba aislado del resto de los presos.", {
	'entities':  [(0, 5, 'PER'),(35, 75, 'ORG')]
}),

("Cinco días después el supuesto financista de PCC estaba en Asunción, donde tenía aceitadas influencias en el gobierno paraguayo para tener un trato no tan estricto.", {
	'entities':  [(45, 48, 'ORG'),(59, 67, 'LOC'),(118, 127, 'MISC')]
}),

("A fines de diciembre pasado el Parlamento paraguayo fue centro de un escándalo luego de que se difundieron audios en los que el senador Oscar González Daher menciona en una conversación telefónica cómo puede hacer lobby para favorecer a Palma.", {
	'entities':  [(42, 51, 'MISC'),(136, 156, 'PER'),(237, 242, 'PER')]
}),

("Fue la primera vez que se destituyó a un senador en Paraguay.", {
	'entities':  [(52, 60, 'LOC')]
}),

("Otro *lobo solitario* de PCC convertido en un cadáver apareció flotando en el río Paraná el 7 de noviembre pasado, en Granadero Baigorria, la localidad vecina a Rosario.", {
	'entities':  [(25, 28, 'ORG'),(78, 88, 'LOC'),(118, 137, 'LOC'),(161, 168, 'LOC')]
}),

("Identificado como Maciel Amantino Wagner, de 45 años y conocido como Junino, era señalado en Brasil como integrante del PCC y uno de los organizadores de otro asalto malogrado a la bóveda de Prosegur de Ciudad del Este, la misma que fue atacada en abril pasado por un grupo comando de la misma organización.", {
	'entities':  [(18, 40, 'PER'),(69, 75, 'PER'),(93, 99, 'LOC'),(120, 123, 'ORG'),(191, 199, 'ORG'),(203, 218, 'LOC')]
}),

("Este hecho preocupó al Ministerio de Seguridad, que empezó a rastrear las posibles conexiones de Junino en el país.", {
	'entities':  [(23, 46, 'ORG'),(97, 103, 'PER')]
}),

("Informes de la Gendarmería y datos aportados por investigadores judiciales confirman que movimientos de células del PCC y del Comando Vermelho fueron observados en Misiones y Corrientes.", {
	'entities':  [(15, 26, 'ORG'),(116, 119, 'ORG'),(126, 142, 'ORG'),(164, 172, 'LOC'),(175, 185, 'LOC')]
}),

("Uno de sus líderes fue arrestado en Ituzaingó.", {
	'entities':  [(36, 45, 'LOC')]
}),

("El cuerpo baleado de un referente del PCC fue encontrado en noviembre pasado en el río Paraná, en los alrededores de la ciudad santafesina de Granadero Baigorria.", {
	'entities':  [(38, 41, 'ORG'),(83, 93, 'LOC'),(127, 138, 'MISC'),(142, 161, 'LOC')]
}),

("Sospechan que planeaba radicarse en Rosario, donde tenía previsto realizar inversiones inmobiliarias.", {
	'entities':  [(36, 43, 'LOC')]
}),

("Informes de la Gendarmería y datos aportados por investigadores judiciales confirman que movimientos de células del PCC y del Comando Vermelho fueron observados en Misiones y Corrientes.", {
	'entities':  [(15, 26, 'ORG'),(116, 119, 'ORG'),(125, 142, 'ORG'),(164, 172, 'LOC'),(175, 185, 'LOC')]
}),

("Uno de sus líderes fue arrestado en Ituzaingó.", {
	'entities':  [(36, 45, 'LOC')]
}),

("El cuerpo baleado de un referente del PCC fue encontrado en noviembre pasado en el río Paraná, en los alrededores de la ciudad santafesina de Granadero Baigorria.", {
	'entities':  [(38, 41, 'ORG'),(83, 93, 'LOC'),(127, 138, 'MISC'),(142, 161, 'LOC')]
}),

("Sospechan que planeaba radicarse en Rosario, donde tenía previsto realizar inversiones inmobiliarias.", {
	'entities':  [(36, 43, 'LOC')]
}),

("Una mujer de la nacionalidad argentina y un hombre español fueron detenidos luego de un allanamiento realizado, en un templo espiritual marplatense, en medio de un ritual *chamánico* en el que utilizaban una sustancia alucinógena de alto efecto llamada Kambó, compuesta por metanfetamina, informaron hoy fuentes policiales.", {
	'entities':  [(29, 38, 'MISC'),(51, 58, 'MISC'),(136, 147, 'MISC'),(208, 229, 'DRUG'),(253, 258, 'DRUG'),(274, 287, 'DRUG')]
}),

("El operativo, supervisado por el coordinador del Operativo Sol, comisario general Marcelo Seal, se llevó a cabo en un domicilio de la calle Río Negro al 4413 de la ciudad de Mar del Plata, donde los efectivos irrumpieron cuando siete personas practicaban la ceremonia.", {
	'entities':  [(82, 94, 'PER'),(134, 157, 'LOC'),(174, 187, 'LOC')]
}),

("En el lugar, los efectivos secuestraron varios sobres con sustancias que dieron positivo al reactivo de metanfetamina y escamas de rana, que forman parte de una droga alucinógena de alto efecto denominada Kambó.", {
	'entities':  [(104, 117, 'DRUG'),(120, 135, 'DRUG'),(161, 178, 'DRUG'),(205, 210, 'DRUG')]
}),

("Según se informó, la pareja detenida era la encargada del lugar y se dedicaban a difundir los talleres que realizaban y a proveer las sustancias que se consumían durante los encuentros.", {
	'entities':  [(134, 144, 'DRUG')]
}),

("Los rituales eran divulgados a través de internet y ya los habían realizado en Mar Azul y Pinamar, añadieron las fuentes a cargo de la investigación.", {
	'entities':  [(79, 87, 'LOC'),(90, 97, 'LOC')]
}),

("La organización ofrecía talleres, charlas y eventos -algunos gratuitos y otros arancelados- donde brindaban información sobre la utilización de Ayahuasca, Bufo y Kambó.", {
	'entities':  [(144, 153, 'DRUG'),(155, 159, 'DRUG'),(162, 167, 'DRUG')]
}),

("El Bufo, nombre científico (INCILIUS ALVARIUS) es una sustancia que se extrae de las secreciones del sapo y se consume fumándola.", {
	'entities':  [(3, 7, 'DRUG'),(28, 45, 'DRUG'),(54, 63, 'DRUG')]
}),

("Por su parte, el Kambó proviene de una rana amazónica de nombre Phyllomedusa bicolor, y provoca la aparición rápida de efectos periféricos gastrointestinales y cardiovasculares violentos, alteración de los sentidos, pérdida del apetito y aumento de la energía física, entre otros efectos.", {
	'entities':  [(17, 22, 'DRUG')]
}),

("*Tomamos conocimiento de esta organización y los veníamos investigando desde Pinamar.", {
	'entities':  [(77, 84, 'LOC')]
}),

("Nos anoticiamos sobre el ritual que iban a realizar en Mar del Plata y preparamos el operativo para detenerlos*, afirmó un alto jefe policial a cargo del procedimiento.", {
	'entities':  [(55, 68, 'LOC')]
}),

("La investigación estuvo a cargo de personal policial perteneciente a la Delegación Prevención Ecológica y Sustancias Peligrosas de Mar del Plata, dependiente de la Superintendencia de Seguridad Siniestral, que montaron el operativo y contaron con la colaboración de la Delegación de Drogas Ilícitas, de la DDI local y Policía Científica.", {
	'entities':  [(72, 144, 'ORG'),(164, 204, 'ORG'),(269, 298, 'ORG'),(306, 309, 'ORG'),(318, 336, 'ORG')]
}),

("Los miembros de la organización y encargados de los rituales quedaron a disposición de la justicia en un caso en el que interviene el titular de la UFI temática Leandro Favaro, del departamento Judicial de Mar del Plata.", {
	'entities':  [(148, 151, 'ORG'),(161, 175, 'PER'),(206, 219, 'LOC')]
}),

("Agencia Télam", {
	'entities':  [(0, 13, 'ORG')]
}),

("La religiosa y titular de la ONG Infancia Robada Martha Pelloni se refirió a la importancia de asistir a las víctimas de la trata de personas y dijo: *Es un problema social grande y grave; el tema de la trata en la Argentina y en Latinoamérica está unido al narcotráfico, es decir, que funcionan en forma paralela, uno necesita del otro*.", {
	'entities':  [(29, 49, 'ORG'),(49, 63, 'PER'),(215, 224, 'LOC'),(230, 243, 'LOC')]
}),

("*Toda la trata necesita de la droga.", {
	'entities':  [(30, 35, 'DRUG')]
}),

("A las chicas que se las secuestra para explotarlas sexualmente tienen que drogarlas para despersonalizarlas*, advirtió la mujer que también detalló: *Despersonalizarlas significa perder su identidad, perder la familia, perder sus deseos, perder su libertad, perder todo lo que significa su identidad como persona porque se la convierte en cosa, en objeto.", {
	'entities':  [(74, 83, 'DRUG')]
}),

("Para intentar explicar este tipo de terribles situaciones, Pelloni detalla: *[Los proxenetas] pagan bien y la vulnerabilidad va [hacia ellos].", {
	'entities':  [(59, 66, 'PER')]
}),

("He tenido en Corrientes mamás que buscaban a chicas de sexto grado de doce, trece años por la escuela, les sacaban el delantal, las peinaban un poco y las iban a entregar en la ruta*.", {
	'entities':  [(13, 23, 'LOC')]
}),

("La Justicia y la policía investigan los asesinatos de dos jóvenes, de entre 20 y 25 años, cuyos cuerpos fueron hallados en un descampado de la localidad de Virrey del Pino, en el partido de La Matanza.", {
	'entities':  [(156, 171, 'LOC'),(179, 200, 'LOC')]
}),

("Al revisar la escena del doble homicidio, los técnicos de la Superintendencia de Policía Científica encontraron evidencias que indican que los mataron de, al menos, treinta balazos.", {
	'entities':  [(61, 99, 'ORG')]
}),

("Fuentes de la investigación, dirigida por el fiscal Jorge Yametti, de la Unidad Funcional de Instrucción de Homicidios de La Matanza, revelaron que los cadáveres fueron encontrados debajo de un árbol en un descampado ubicado en la calle 13, sin número, del barrio denominado 16 de Septiembre, un asentamiento que se instaló hace pocos meses.", {
	'entities':  [(52, 65, 'PER'),(73, 132, 'ORG'),(231, 239, 'LOC'),(275, 291, 'LOC')]
}),

("*Es una zona donde se suele vender droga y no descartamos que una cuestión de territorio entre bandas narco sea el móvil de este doble asesinato*, indicó uno de los investigadores del caso, según consignó Télam.", {
	'entities':  [(35, 40, 'DRUG'),(205, 210, 'PER')]
}),

("Los peritos de la Policía Científica que procesaron la escena del doble homicidio recolectaron casi 30 vainas servidas, la mayoría 9 milímetros, pero también hallaron cápsulas calibre 357 Magnum.", {
	'entities':  [(18, 36, 'ORG')]
}),

("Si bien la mecánica y la causa de las muertes será determinada en la morgue policial donde fueron trasladados los cadáveres, en Puente 12, las fuentes indicaron que a simple vista los cuerpos también tenían heridas compatibles con machetazos.", {
	'entities':  [(128, 137, 'LOC')]
}),

("Los investigadores policiales tampoco descartaban que el móvil estuviera vinculado a alguna cuestión personal y seguían la pista de que al menos una de las víctimas podría provenir de la villa 31 de Retiro.", {
	'entities':  [(187, 205, 'LOC')]
}),

("Un hecho similar se produjo el 1° de septiembre último en la misma localidad, cuando tres jóvenes fueron hallados asesinados a balazos, uno de ellos de siete disparos, en una casa prefabricada y sin muebles en inmediaciones de las calles Góngora y Fidias.", {
	'entities':  [(238, 254, 'LOC')]
}),

("Una investigación sobre narcotráfico que comenzó con el aporte de información de inteligencia criminal, que sostenía que operaba en el país una organización integrada por ciudadanos argentinos, bolivianos y colombianos, derivó en dos allanamientos en el exclusivo Olivos Golf Club, en Malvinas Argentinas, donde se detuvo a un sospechoso.", {
	'entities':  [(182, 192, 'MISC'),(194, 204, 'MISC'),(207, 218, 'MISC'),(264, 280, 'ORG'),(285, 304, 'LOC')]
}),

("En otro procedimiento en el barrio de Villa Luro la Gendarmería Nacional secuestró, en principio, 20 kilos de cocaína.", {
	'entities':  [(38, 48, 'LOC'),(52, 72, 'ORG'),(110, 117, 'DRUG')]
}),

("Así lo informaron a LA NACION calificadas fuentes oficiales.", {
	'entities':  [(20, 29, 'ORG')]
}),

("Se trata de una investigación que estuvo delegada en la Procuraduría de Narcocriminalidad (Procunar), a cargo del fiscal Diego Iglesias, que trabajó con detectives de la Gendarmería Nacional.", {
	'entities':  [(56, 100, 'ORG'),(121, 135, 'PER'),(170, 190, 'ORG')]
}),

("Además del sospechoso detenido en el Olivos Golf Club, fueron apresadas otras cinco personas.", {
	'entities':  [(37, 53, 'ORG')]
}),

("Los allanamientos fueron ordenados por el juez federal de Lomas de Zamora Federico Villena, a cargo de la causa..", {
	'entities':  [(58, 73, 'LOC'),(74, 90, 'PER')]
}),

("El Olivos Golf Club es uno de los countries más tradicionales de la Argentina con rigurosos requisitos de admisión para ser socio y su cancha es considerada como una de las más importante del país, donde se jugaba hasta hace unos año el tradicional Torneo de Maestros -el ganador se lleva un saco azul a la manera del Masters de Augusta-, el segundo campeonato en relevancia después del Abierto.", {
	'entities':  [(3, 19, 'ORG'),(68, 77, 'LOC'),(249, 267, 'MISC'),(318, 336, 'MISC'),(387, 394, 'MISC')]
}),

("*El desbaratamiento de esta red de laboratorios que producen droga, es un nuevo éxito en la lucha contra el narcotrafico.", {
	'entities':  [(61, 66, 'DRUG')]
}),

("Nuestra meta es terminar con los que trafican, venden y fabrican droga, sea quien sea.", {
	'entities':  [(65, 70, 'DRUG')]
}),

("No le damos tregua al narcotrafico*, afirmó la ministra de Seguridad de la Nación, Patricia Bullirch.", {
	'entities':  [(59, 81, 'ORG'),(83, 100, 'PER')]
}),

("Dos calificadas fuentes de la investigación afirmaron que, si bien en uno de los dos domicilios allanados en el Olivos Golf Club se encontraron precursores químicos, una prensa y una balanza de precisión, el laboratorio utilizado por la organización narco para estirar la cocaína estaba instalado en un departamento de Villa Luro.", {
	'entities':  [(112, 128, 'ORG'),(272, 279, 'DRUG'),(319, 329, 'LOC')]
}),

("El sospechoso detenido en Malvinas Argentinas es un ciudadano argentino que alquiló una casa en el Olivos Golf Club.", {
	'entities':  [(26, 45, 'LOC'),(62, 71, 'MISC'),(99, 115, 'ORG')]
}),

("Además se detuvo a dos ciudadanos colombianos, una persona de nacionalidad boliviana y otros dos argentinos.", {
	'entities':  [(34, 45, 'MISC'),(75, 84, 'MISC'),(97, 107, 'MISC')]
}),

("Los 25 paquetes de cocaína (que en un principio tendrían un peso de 20 kilos) fueron secuestrados en un allanamiento hecho en la ciudad de Buenos Aires.", {
	'entities':  [(19, 26, 'DRUG'),(139, 151, 'LOC')]
}),

("Fuentes del Ministerio de Seguridad de la Nación explicaron que se trata de una exhaustiva investigación hecha por la Gendarmería Nacional con colaboración de la Agencia Federal de Inteligencia (AFI) y la DEA (la agencia antidrogas de los Estados Unidos).", {
	'entities':  [(12, 48, 'ORG'),(118, 138, 'ORG'),(162, 199, 'ORG'),(205, 208, 'ORG'),(239, 253, 'LOC')]
}),

("A partir de varios operativos especiales y controles de ruta, las fuerzas federales incautaron durante la última semana más de ocho toneladas de marihuana en Misiones.", {
	'entities':  [(145, 154, 'DRUG'),(158, 166, 'LOC')]
}),

("Se trata de una cifra importante de decomisos, más si se toma en cuenta que entre enero y noviembre pasado se había registrado el secuestro de 90 toneladas de marihuana en todo el país.", {
	'entities':  [(159, 168, 'DRUG')]
}),

("En ese período, las capturas de marihuana en Misiones combinadas con los decomisos en Corrientes sumaron 63 de esas 90 toneladas incautadas en la Argentina.", {
	'entities':  [(32, 41, 'DRUG'),(45, 53, 'LOC'),(86, 96, 'LOC'),(146, 155, 'LOC')]
}),

("Con esos datos cobran mayor relevancia los procedimientos realizados en los últimos días en Misiones.", {
	'entities':  [(92, 100, 'LOC')]
}),

("Uno de esos operativos fue concretado por el Escuadrón 50 Posadas, de la Gendarmería, cuyos efectivos interceptaron un vehículo de transporte Ford 700.", {
	'entities':  [(45, 65, 'ORG'),(73, 84, 'ORG'),(142, 150, 'MISC')]
}),

("Al verificarse la carga, los gendarmes descubrieron un embarque de 3091 kilogramos de marihuana.", {
	'entities':  [(86, 95, 'DRUG')]
}),

("Una similar cantidad de cannabis había sido decomisada pocos días antes en las cercanías de la localidad misionera de Candelaria, donde una investigación de la Gendarmería permitió la captura de un cargamento de droga y el arresto de 15 sospechosos.", {
	'entities':  [(24, 32, 'DRUG'),(118, 128, 'LOC'),(160, 171, 'ORG'),(212, 217, 'DRUG')]
}),

("Esa organización criminal escondía la droga en despachos de madera con destino a Buenos Aires.", {
	'entities':  [(38, 43, 'DRUG'),(81, 93, 'LOC')]
}),

("La pesquisa fue iniciada tras el decomiso en Buenos Aires durante 2016 de un camión con 2500 kilogramos de marihuana.", {
	'entities':  [(45, 57, 'LOC'),(107, 116, 'DRUG')]
}),

("Los investigadores estiman que todo el clan narco fue detenido en los allanamientos realizados en los últimos días en Misiones.", {
	'entities':  [(118, 126, 'LOC')]
}),

("En tanto, el Escuadrón Eldorado consiguió la captura de 972 kilogramos de marihuana en la localidad de Colonia Victoria.", {
	'entities':  [(13, 31, 'ORG'),(74, 83, 'DRUG'),(103, 119, 'LOC')]
}),

("Una patrulla de gendarmes detectó la sospechosa presencia de una camioneta Chevrolet S10 en un sendero poco transitado.", {
	'entities':  [(75, 88, 'MISC')]
}),

("El conductor abandonó el vehículo al visualizar al personal de Gendarmería y dejó en ese lugar la carga de marihuana que estaba dispuesta en la caja de la camioneta y amontonada, incluso, dentro de la cabina.", {
	'entities':  [(63, 74, 'ORG'),(107, 116, 'DRUG')]
}),

("En una camioneta también fue encontrado un embarque de 740 kilogramos de marihuana, decomisado por una patrulla de la Prefectura a la vera del río Paraná, cerca de la localidad de Puerto Libertad.", {
	'entities':  [(73, 82, 'DRUG'),(118, 128, 'ORG'),(143, 153, 'LOC'),(180, 195, 'LOC')]
}),

("*Este histórico decomiso de droga fue posible por la vocación y el profesionalismo de las fuerzas federales, que patrullan todos días la zona de frontera para prevenir los delitos complejos y luchar contra el narcotráfico*, dijo la ministra de Seguridad, Patricia Bullrich, al referirse a los casos de recientes incautaciones de marihuana en Misiones.", {
	'entities':  [(255, 272, 'PER'),(329, 338, 'DRUG'),(342, 350, 'LOC')]
}),

("Durante este año se concretaron al menor tres procedimientos en localidades misioneras que representaron capturas superiores a las cuatro toneladas de drogas.", {
	'entities':  [(76, 86, 'MISC'),(151, 157, 'DRUG')]
}),

("Ese fue el peso, por ejemplo, de uno de los cargamentos detectados en Posadas, mientras que en la zona de Campo Grande se concretó el decomiso de un embarque de 4512 kilogramos de cannabis.", {
	'entities':  [(70, 77, 'LOC'),(106, 118, 'LOC'),(180, 188, 'DRUG')]
}),

("El cargamento más importante de marihuana secuestrado en Misiones durante este año por las fuerzas federales fue registrado con un peso de 6060 kilogramos, en un operativo realizado en la ciudad de Oberá.", {
	'entities':  [(32, 41, 'DRUG'),(57, 65, 'LOC'),(198, 203, 'LOC')]
}),

("Sin embargo, el mayor decomiso de marihuana en Misiones fue conseguido el mes pasado por la policía de esa provincia.", {
	'entities':  [(34, 43, 'DRUG'),(47, 55, 'LOC')]
}),

("Más de ocho toneladas de marihuana fueron incautadas en un procedimiento llevado adelante por cien agentes antidrogas que lograron el arresto de un clan familiar que manejaba la circulación de la marihuana en la localidad de Montecarlo.", {
	'entities':  [(25, 34, 'DRUG'),(225, 235, 'LOC')]
}),

("Lo que yo vi el lunes es la más impresionante manifestación de la izquierda radicalizada en la historia argentina*, tuiteó ayer Pablo Gerchunoff.", {
	'entities':  [(104, 113, 'MISC'),(128, 144, 'PER')]
}),

("Ciertamente hubo otros episodios memorables en la historia contemporánea argentina con fuerte presencia de estos sectores, como la masacre de Ezeiza el 20 de junio de 1973 y el Cordobazo del 29 de mayo de 1969.", {
	'entities':  [(73, 82, 'MISC'),(142, 148, 'LOC'),(177, 186, 'MISC')]
}),

("Pero a diferencia de aquellos, donde imperaba la táctica del *entrismo* para estar cerca de la clase obrera, el notable protagonismo que tuvieron frente al Congreso los grupos de la izquierda radicalizada implica un desplazamiento de los de origen peronista a un inusual segundo plano.", {
	'entities':  [(156, 164, 'LOC')]
}),

("Esta irrupción con semejante escala de organizaciones diversas ideológicamente (trotskistas, anarquistas, guevaristas, algunas derivaciones del maoísmo versión Sendero Luminoso) pero que tienen en común la reivindicación de la violencia (directa o solapadamente) como una táctica válida en la lucha por el poder constituye a la vez una grave alarma para la sociedad argentina, un enorme desafío para su enclenque aparato estatal y una cabal manifestación del fracaso de un sistema político que no sólo es incapaz de resolver los problemas más elementales, sino que reabre heridas que parecían suturadas.", {
	'entities':  [(366, 375, 'MISC')]
}),

("Hasta hace poco, la violencia política parecía erradicada de nuestras prácticas políticas: el último episodio había sido el ataque al Regimiento de la Tablada de 1989.", {
	'entities':  [(134, 158, 'MISC')]
}),

("Lo que se vio en las calles aledañas al Congreso fue la expresión de una Argentina tumbera, lumpenizada, con algunas pinceladas de cultura barrabrava.", {
	'entities':  [(40, 48, 'LOC'),(73, 82, 'LOC')]
}),

("Tanto Sendero Luminoso como las FARC terminaron imbricadas en ellas.", {
	'entities':  [(6, 22, 'ORG'),(32, 36, 'ORG')]
}),

("Evo Morales llegó a la presidencia de Bolivia gracias a su rol como líder de los productores cocaleros.", {
	'entities':  [(0, 11, 'PER'),(38, 45, 'LOC')]
}),

("Y Venezuela hace mucho se ha convertido en un narco-estado.", {
	'entities':  [(2, 11, 'LOC')]
}),

("Sobre todo, dado el serio compromiso de Cambiemos en la lucha contra el narcotráfico, tanto a nivel nacional como en la Provincia de Buenos Aires.", {
	'entities':  [(40, 49, 'ORG'),(120, 145, 'LOC')]
}),

("El radicalismo quedó reducido a su mínima expresión en la política universitaria, donde el PRO aún no tiene una presencia relevante.", {
	'entities':  [(91, 94, 'ORG')]
}),

("Los grupos de izquierda radicalizada prácticamente hegemonizan los centros de estudiantes de los colegios secundarios más politizados, donde a comienzos de la transición a la democracia reinaba Franja Morada.", {
	'entities':  [(194, 207, 'ORG')]
}),

("Las organizaciones feministas y los grupos LGBTQ están también totalmente alejados de las organizaciones políticas formales.", {
	'entities':  [(43, 48, 'ORG')]
}),

("Es decir, del fracaso argentino, que tiene en el inmenso, inseguro e indomable Gran Buenos Aires su expresión más perversa y a la vez más genuina.", {
	'entities':  [(22, 31, 'MISC'),(79, 96, 'LOC')]
}),

("Más de dos décadas de gimnasia piquetera (todo comenzó en 1996 en localidades donde YPF había sido el eje de la vida económica y social, como Cutral-Có y Plaza Huincul) han consagrado una nueva cultura política y un tejido organizacional singular, donde el desarrollo económico y el empleo formal constituyen, lejos de una solución, una amenaza a la continuidad y vigencia de estas formaciones.", {
	'entities':  [(84, 87, 'ORG'),(142, 151, 'ORG'),(154, 167, 'ORG')]
}),

("Cuando luego de la Revolución Rusa la amenaza socialista se extendió por todo Occidente, hubo reacciones múltiples para evitar su avance.", {
	'entities':  [(19, 34, 'MISC'),(78, 87, 'LOC')]
}),

("En particular, la Iglesia Católica alentó la formación de organizaciones obreras que disputaran palmo a palmo con otras de origen marxista la lucha por la concientización de la clase trabajadora.", {
	'entities':  [(18, 34, 'MISC')]
}),

("Argentina no fue la excepción.", {
	'entities':  [(0, 9, 'LOC')]
}),

("Incluso mucho antes, en 1892, antes de que Juan B. Justo fundara el Partido Socialista, el padre Federico Grote había creado los Círculos de Obreros Católicos.", {
	'entities':  [(43, 56, 'PER'),(68, 86, 'ORG'),(97, 111, 'PER'),(129, 158, 'ORG')]
}),

("Más tarde, la Acción Católica expandió ese esfuerzo, que se consolidó más tarde con el surgimiento del peronismo.", {
	'entities':  [(14, 29, 'ORG')]
}),

("Se trata de algunos antecedentes históricos relevantes para entender la enorme preocupación con la que la jerarquía de la Iglesia, incluyendo el papa Francisco, tiene con el fenómeno de la pobreza extrema.", {
	'entities':  [(150, 159, 'PER')]
}),

("También, el apoyo que reciben líderes como Juan Grabois o la reciente ordenación como Obispo del cura villero Gustavo Carrara, el párroco de la iglesia María Madre del Pueblo, de la villa 1-11-14.", {
	'entities':  [(43, 55, 'PER'),(110, 125, 'PER'),(144, 174, 'LOC'),(182, 195, 'LOC')]
}),

("La investigación de Germán de los Santos que hoy publicamos en LA NACION fue elegida -junto con una de Irene Benito, de La Gaceta de Tucumán- por el jurado internacional de Chequeado Investigación entre más de 40 postulaciones.", {
	'entities':  [(20, 40, 'PER'),(63, 72, 'ORG'),(103, 115, 'PER'),(120, 140, 'ORG'),(173, 196, 'ORG')]
}),

("Ambos recibieron un premio de US$ 2000 y contaron con la codirección de los periodistas Hugo Alconada Mon y Laura Zommer y el apoyo de los equipos de redacción e innovación de Chequeado.", {
	'entities':  [(176, 185, 'ORG')]
}),

("El jurado de Chequeado Investigación estuvo integrado por los periodistas Mónica González (Ciper, Chile), Daniel Moreno (Animal Político, México) y Giannina Segnini (Universidad de Columbia, ex La Nación de Costa Rica) y los docentes argentinos Damián Loreti (UBA) y Fernando Ruiz (Universidad Austral).", {
	'entities':  [(13, 36, 'ORG'),(74, 89, 'PER'),(91, 96, 'ORG'),(98, 103, 'LOC'),(106, 119, 'PER'),(121, 136, 'ORG'),(138, 144, 'LOC'),(148, 164, 'PER'),(166, 189, 'ORG'),(194, 217, 'LOC'),(245, 258, 'PER'),(260, 263, 'ORG'),(267, 280, 'PER'),(282, 301, 'ORG')]
}),

("Chequeado es un medio no partidario y sin fines de lucro cuya misión es fortalecer la democracia a través de la defensa del derecho a la información y la verificación del discurso público.", {
	'entities':  [(0, 9, 'ORG')]
}),

("El ministro de Seguridad bonaerense, Cristian Ritondo, supervisó ayer la incineración de más de 700 kilos de marihuana que habían sido secuestrados el año pasado a una banda conocida como *Tereré*, que traía la droga desde Paraguay, informaron fuentes policiales.", {
	'entities':  [(37, 53, 'PER'),(109, 118, 'DRUG'),(189, 195, 'ORG'),(211, 216, 'DRUG'),(223, 231, 'LOC')]
}),

("El procedimiento fue realizado en el Crematorio Privado Boulogne, ubicado en el partido de San Isidro, donde el ministro bonaerense afirmó que *la droga que se encuentra se quema* y que ese es *el último paso en la lucha contra el narcotráfico y el crimen organizado*.", {
	'entities':  [(37, 64, 'ORG'),(91, 101, 'LOC'),(121, 131, 'MISC'),(147, 152, 'DRUG')]
}),

("*Hemos asumido la decisión de transformar la provincia de Buenos Aires, porque también el circuito de las drogas forma parte de esas mafias que asolaban a los bonaerenses y que hoy estamos combatiendo*, agregó Ritondo.", {
	'entities':  [(58, 70, 'LOC'),(106, 112, 'DRUG'),(159, 170, 'MISC'),(210, 217, 'PER')]
}),

("Según precisaron los voceros, la marihuana incinerada fue incautada en noviembre del año pasado durante una serie de allanamientos realizados en diversos puntos del norte y el oeste del conurbano que permitieron desbaratar la banda conocida como *Tereré*.", {
	'entities':  [(33, 42, 'DRUG'),(186, 195, 'LOC'),(247, 253, 'ORG')]
}),

("Los operativos se llevaron a cabo tras una investigación que incluyó escuchas telefónicas a través de las cuales se constató que la banda utilizaba como pantalla un almacén de venta de frutas, verduras y carnes ubicado en la localidad de Cuartel V, partido de Moreno, para realizar la actividad ilícita.", {
	'entities':  [(238, 247, 'LOC'),(260, 266, 'LOC')]
}),

("Por ese motivo, la policía bonaerense dispuso una serie de allanamientos en varios domicilios ubicados en las localidades de Tigre, José C. Paz, Moreno, Hurlingham y Ramos Mejía.", {
	'entities':  [(125, 130, 'LOC'),(132, 143, 'LOC'),(145, 151, 'LOC'),(153, 163, 'LOC'),(166, 177, 'LOC')]
}),

("Como resultado de esos procedimientos fueron apresados el presunto líder de la organización, de nacionalidad paraguaya, y siete de sus cómplices.", {
	'entities':  [(109, 118, 'MISC')]
}),

("Además, las fuentes agregaron que desde principios de 2016 la policía bonaerense decomisó 25 toneladas de marihuana, 1027 kilos de cocaína, 45 kilos de pasta base, 369.000 dosis de paco, 145.000 dosis de ácido y 8150 pastillas de éxtasis.", {
	'entities':  [(70, 80, 'MISC'),(106, 115, 'DRUG'),(131, 138, 'DRUG'),(152, 162, 'DRUG'),(181, 185, 'DRUG'),(204, 209, 'DRUG'),(230, 237, 'DRUG')]
}),

("El recrudecimiento de la violencia en Rosario , que tiene como protagonistas a bandas nuevas y provocaron 14 homicidios en la primera quincena del año, obligaron al Ministerio de Seguridad de la Nación a diseñar un abordaje de urgencia en un territorio que está en tensión y disputa con actores jóvenes que buscan con la hegemonía de la violencia mantener el negocio de la droga.", {
	'entities':  [(38, 45, 'LOC'),(165, 201, 'ORG'),(373, 378, 'DRUG')]
}),

("La ministra de Seguridad, Patricia Bullrich, se reunió ayer con los jefes de las fuerzas federales de Rosario para terminar de pulir el plan de lucha contra el narcotráfico y la violencia que se instrumentará en esa ciudad en los próximos días.", {
	'entities':  [(26, 43, 'PER'),(102, 109, 'LOC')]
}),

("No enviarán un refuerzo de efectivos a Rosario sino que apuntarán a desmantelar, a corto plazo estas nuevas bandas mediante estrategias de inteligencia criminal.", {
	'entities':  [(39, 46, 'LOC')]
}),

("Desde hace más de un año unos 3000 efectivos de la Gendarmería, la Prefectura, las policías Federal y de Seguridad Aeroportuaria están asentados en la provincia de Santa Fe y actúan en coordinación con los efectivos provinciales.", {
	'entities':  [(51, 62, 'ORG'),(67, 77, 'ORG'),(105, 128, 'ORG'),(164, 172, 'LOC')]
}),

("Esto se concretó luego de que la cartera de Seguridad firmara con el gobernador Miguel Lifschitz un convenio que se venció hace unos días y que está previsto que sea renovado.", {
	'entities':  [(80, 96, 'PER')]
}),

("*Estamos a tiempo de evitar que estas bandas con gente muy joven se consoliden en Rosario*, afirmó Bullrich en diálogo con LA NACION y agregó: *Es imprescindible que con investigaciones en conjunto entre las fuerzas federales, provinciales y la Justicia se avance en desmantelar estas redes.", {
	'entities':  [(82, 89, 'LOC'),(99, 107, 'PER'),(123, 132, 'ORG')]
}),

("A la par de la persecución criminal, el Gobierno pretende replicar en Rosario el programa Barrios Seguros, que se mantiene en la villa 31 en la Capital y en el barrio de Alto Verde en la ciudad de Santa Fe.", {
	'entities':  [(70, 77, 'LOC'),(90, 105, 'MISC'),(129, 137, 'LOC'),(170, 180, 'LOC'),(197, 205, 'LOC')]
}),

("Maximiliano Pullaro, ministro de Seguridad santafesino, coincidió en que el recrudecimiento de la violencia durante los últimos días *no es generalizado, sino que está acotado a personas y lugares muy puntuales.", {
	'entities':  [(0, 19, 'PER'),(43, 54, 'MISC')]
}),

("El primer desafío lo protagonizó Alan Funes, de 18 años, uno de los líderes de la banda familiar, quien está prófugo tras festejar el Año Nuevo disparando una ametralladora FMK3 mientras estaba con prisión domiciliaria por un asesinato.", {
	'entities':  [(33, 43, 'PER')]
}),

("Una semana después su hermano Ulises fue acribillado por dos sicarios.", {
	'entities':  [(30, 36, 'PER')]
}),

("Alan y su hermano Lautaro, quien está preso en la cárcel de Piñero, juraron por las redes sociales *exterminar* a toda la generación de los Caminos, el clan rival de barrio Municipal, una zona donde hubo 30 homicidios en 20 meses.", {
	'entities':  [(0, 4, 'PER'),(18, 25, 'PER'),(60, 66, 'LOC'),(136, 147, 'ORG'),(166, 182, 'LOC')]
}),

("En esa cadena de violencia fue asesinada Marcela Díaz, hermana de Rubén Segovia, alias Tubi, miembro de los Caminos y Los Monos, quien está preso por estar involucrado en cuatro asesinatos.", {
	'entities':  [(41, 53, 'PER'),(66, 79, 'PER'),(87, 91, 'PER'),(104, 115, 'ORG'),(118, 127, 'ORG')]
}),

("El único testigo de la muerte de Díaz dijo que en el auto donde les disparaban estaba Alan Funes, que tiene pedido de captura nacional e internacional.", {
	'entities':  [(33, 37, 'PER'),(86, 96, 'PER')]
}),

("Esta nueva ola de violencia recuerda la que se produjo cuando comenzó la guerra narco con la banda de Los Monos como protagonistas centrales, que empezaron a matar en las calles de Rosario a sus enemigos y a los que acusaban de haber acribillado el 26 de mayo de 2013 al líder de la banda, Claudio Cantero.", {
	'entities':  [(102, 111, 'ORG'),(181, 188, 'LOC'),(290, 305, 'PER')]
}),

("Luego de la difusión de un video en el que se lo veía a Alan Funes, prófugo de un homicidio y narcotráfico , disparando una ametralladora a modo de festejo de fin de año, la justicia ordenó la captura nacional e internacional de este joven que estaba hasta hace unos meses bajo el régimen de detención domiciliaria.", {
	'entities':  [(56, 66, 'PER')]
}),

("Luego de que el video del joven disparando al aire tomara estado público, efectivos de la Policía de Investigaciones (PDI)de Santa Fe realizó un allanamiento en un la casa de Funes, donde debía cumplir la prisión domiciliaria que había acordado la Fiscalía de Rosario y el abogado defensor de Funes.", {
	'entities':  [(90, 133, 'ORG'),(175, 180, 'PER'),(248, 267, 'ORG'),(293, 298, 'PER')]
}),

("Este muchacho estaba imputado del homicidio de Eugenio Solano.", {
	'entities':  [(47, 61, 'PER')]
}),

("Tenía 17 años cuando mató al supuesto asesino de su madre María Griselda Miranda.", {
	'entities':  [(58, 80, 'PER')]
}),

("En los festejos violentos de fin de año, que dejaron siete muertos en Rosario, se conoció ahora un video de uno de los integrantes del clan Funes, una banda narcocriminal que opera en la zona sur de la ciudad, en el que se lo ve disparando con una ametralladora ráfagas de tiros al aire.", {
	'entities':  [(70, 77, 'LOC')]
}),

("Jorge Funes, el padre de Alan, un veterano pirata del asfalto devenido en narco, fue herido de tres balazos el 1° de enero pasado en la localidad de Alvear, a 35 kilómetros de Rosario, donde se había ido a recluir tras la guerra que se desató en la zona sur de Rosario entre los clanes de los Funes y los Caminos, históricos referentes de la barra brava de Newell's.", {
	'entities':  [(0, 11, 'PER'),(25, 29, 'PER'),(149, 155, 'LOC'),(176, 183, 'LOC'),(261, 268, 'LOC'),(289, 298, 'ORG'),(301, 312, 'ORG'),(357, 365, 'ORG')]
}),

("Voceros policiales calculan que en la zona de disputa en barrio La Tablada y Municipal se produjeron más de 25 crímenes por la disputa territorial entre estos dos clanes, que tenían el terreno allanado tras la supuesta caída de la banda de los Monos que tenía la hegemonía de todo el sur de Rosario.", {
	'entities':  [(64, 74, 'LOC'),(77, 86, 'LOC'),(240, 249, 'ORG'),(291, 298, 'LOC')]
}),

("El 23 de mayo pasado hubo un gran operativo de la Policía Federal Argentina (PFA) en esa región de disputa narco, buscando sacar de desarticular a la banda de los Funes.", {
	'entities':  [(50, 81, 'ORG'),(159, 168, 'ORG')]
}),

("El operativo fue bautizado *Los miserables*.", {
	'entities':  [(28, 42, 'MISC')]
}),

("En una rueda de prensa realizada en la Delegación local de los efectivos de la Policía Federal y presidida por el secretario de Seguridad Interior de la Nación, Gerardo Millman, el fiscal local Adrián Spelta confirmó que hubo 13 detenidos.", {
	'entities':  [(79, 94, 'ORG'),(128, 159, 'ORG'),(161, 176, 'PER'),(194, 207, 'PER')]
}),

("Diez de ellos fueron imputados por una serie de delitos contra la propiedad, en su mayoría escruches y entraderas, por la fiscal Gisela Paolicelli.", {
	'entities':  [(129, 146, 'PER')]
}),

("Y los otros tres quedaron a disposición de la Fiscalía federal ya que en uno de los domicilios allanados se encontró droga.", {
	'entities':  [(117, 122, 'DRUG')]
}),

("En una trama en el que tercia la venta de drogas , un suboficial de la Policía de Santa Fe fue detenido por el crimen de una joven de 23 años, cuyo cuerpo calcinado fue encontrado en un contenedor de residuos hace tres días en el barrio Triángulo de Rosario.", {
	'entities':  [(42, 48, 'DRUG'),(71, 90, 'ORG'),(237, 246, 'LOC'),(250, 257, 'LOC')]
}),

("El efectivo policial Andrés Miguez, de 30 años, que se desempeña en el Comando Radioeléctrico de Rosario se entregó este sábado en la sede de la Policía Federal.", {
	'entities':  [(21, 34, 'PER'),(71, 104, 'ORG'),(145, 160, 'ORG')]
}),

("En las próximas 48 horas será sometido por el fiscal Florentino Malaponte a una audiencia imputativa.", {
	'entities':  [(53, 73, 'PER')]
}),

("El trasfondo de este crimen está atravesado por una trama en el que se mezclan la venta de drogas en ese sector complicado de Rosario y una relación que María del Rosario Vera mantenía con el policía.", {
	'entities':  [(91, 97, 'DRUG'),(126, 133, 'LOC'),(153, 175, 'PER')]
}),

("De acuerdo a los datos aportados por el Ministerio Público de la Acusación (MPA), en la madrugada de este sábado se realizaron tres allanamientos para dar con el sospechoso.", {
	'entities':  [(40, 80, 'ORG')]
}),

("Dos se realizaron en la zona donde fue encontrado el cadáver y otro en Bolonia al 4700.", {
	'entities':  [(71, 86, 'LOC')]
}),

("En ninguno de los domicilios fue encontrado el policía, que se entregó luego en dependencias de la Policía Federal Argentina.", {
	'entities':  [(99, 124, 'ORG')]
}),

("En uno de ellos culpaba a los soldaditos de *Martín* por lo que pudiera pasarle.", {
	'entities':  [(45, 51, 'PER')]
}),

("Ese nombre era el que utilizaba el policía Andrés Miguez, que desde hace cuatro años se desempeña en el Comando Radioeléctrico.", {
	'entities':  [(43, 56, 'PER'),(104, 126, 'ORG')]
}),

("El fiscal sospecha que planeó el crimen de Vera, quien fue hallada con signos de haber sido asfixiada con una soga.", {
	'entities':  [(43, 47, 'PER')]
}),

("La autopsia que realizó el Instituto Médico Legal al otro día determinó algunos indicios que rondaban en torno a la causa.", {
	'entities':  [(27, 49, 'ORG')]
}),

("*Los peritajes indican que la causa de la muerte fue por asfixia por ahorcamiento*, reveló el fiscal Florentino Malaponte, quien está al frente del caso.", {
	'entities':  [(101, 121, 'PER')]
}),

("Se cree, como alertó Vera a su familia, que son soldaditos que venden droga en un búnker que está en esa zona que maneja el efectivo del Comando Radioeléctrico.", {
	'entities':  [(137, 159, 'ORG')]
}),

("Durante las primeras horas después del hallazgo del cuerpo uno de los sospechosos era el ex marido de Vera, a quien ella había denunciado hace poco más de un año por violencia de género y estaba bajo detención domiciliaria, monitoreado con una tobillera electrónica.", {
	'entities':  [(102, 106, 'PER')]
}),

("El 20 de diciembre pasado este hombre de 28 años incumplió el régimen de prisión y el juez Luis María Caterina aceptó la calificación presentada por la fiscal de Violencia de Género Luciana Valarella y revocó la prisión domiciliaria para Néstor Jesús R., quien pasó a prisión preventiva efectiva sin plazos.", {
	'entities':  [(91, 110, 'PER'),(182, 199, 'PER'),(238, 252, 'PER')]
}),

("En los festejos violentos de fin de año, que dejaron siete muertos en Rosario, se conoció ahora un video de uno de los integrantes del clan Funes, una banda narcocriminal que opera en la zona sur de la ciudad, en el que se lo ve disparando con una ametralladora ráfagas de tiros al aire.", {
	'entities':  [(70, 77, 'LOC'),(135, 145, 'ORG')]
}),

("Lo más llamativo es que Alan Funes, el joven que aparece en el video, está con prisión domiciliaria desde octubre pasado cuando la Fiscalía de Rosario acordó con el abogado defensor ese beneficio.", {
	'entities':  [(24, 34, 'PER'),(131, 150, 'ORG')]
}),

("Está acusado del crimen de Julio Solaro, alias *Pupi*, quien fue acribillado el 1º de mayo pasado en un pasillo de Ayacucho al 4300.", {
	'entities':  [(27, 39, 'PER'),(48, 52, 'PER'),(115, 131, 'LOC')]
}),

("Ese crimen se habría producido como venganza de la muerte de la madre de Alan Funes, Mariela Griselda Miranda, quien fue atacada a tiros desde una moto.", {
	'entities':  [(73, 83, 'PER'),(85, 109, 'PER')]
}),

("Jorge Funes, el padre de Alan, un veterano pirata del asfalto devenido en narco, fue herido de tres balazos el 1° de enero pasado en la localidad de Alvear, a 35 kilómetros de Rosario, donde se había ido a recluir tras la guerra que se desató en la zona sur de Rosario entre los clanes de los Funes y los Caminos, históricos referentes de la barra brava de Newell's.", {
	'entities':  [(0, 11, 'PER'),(25, 29, 'PER'),(149, 155, 'LOC'),(176, 183, 'LOC'),(261, 268, 'LOC'),(289, 298, 'ORG'),(301, 312, 'ORG'),(357, 365, 'ORG')]
}),

("Voceros policiales calculan que en la zona de disputa en barrio La Tablada y Municipal se produjeron más de 25 crímenes por la disputa territorial entre estos dos clanes, que tenían el terreno allanado tras la supuesta caída de la banda de los Monos que tenía la hegemonía de todo el sur de Rosario.", {
	'entities':  [(64, 74, 'LOC'),(77, 86, 'LOC'),(240, 249, 'ORG'),(291, 298, 'LOC')]
}),

("El 23 de mayo pasado hubo un gran operativo de la Policía Federal Argentina (PFA) en esa región de disputa narco, buscando sacar de desarticular a la banda de los Funes.", {
	'entities':  [(50, 81, 'ORG'),(159, 168, 'ORG')]
}),

("El operativo fue bautizado *Los miserables*.", {
	'entities':  [(28, 42, 'MISC')]
}),

("En una rueda de prensa realizada en la Delegación local de los efectivos de la Policía Federal y presidida por el secretario de Seguridad Interior de la Nación, Gerardo Millman, el fiscal local Adrián Spelta confirmó que hubo 13 detenidos.", {
	'entities':  [(79, 94, 'ORG'),(128, 159, 'ORG'),(161, 176, 'PER'),(194, 207, 'PER')]
}),

("Diez de ellos fueron imputados por una serie de delitos contra la propiedad, en su mayoría escruches y entraderas, por la fiscal Gisela Paolicelli.", {
	'entities':  [(129, 146, 'PER')]
}),

("Y los otros tres quedaron a disposición de la Fiscalía federal ya que en uno de los domicilios allanados se encontró droga.", {
	'entities':  [(46, 62, 'MISC'),(117, 122, 'DRUG')]
}),

("Un nuevo golpe de las fuerzas de seguridad federales revela que sigue activo el tráfico de drogas a través del río Paraná y con ingreso al país por la ciudad correntina de Itatí, cuyo intendente, Natividad *Roger* Terán, fue detenido este año en el contexto de la investigación sobre una narcobanda con fluidos contactos políticos en la zona.", {
	'entities':  [(111, 121, 'LOC'),(158, 168, 'MISC'),(172, 177, 'LOC'),(196, 219, 'PER')]
}),

("Esta vez, efectivos de la Prefectura secuestraron allí más de 439 kilos de marihuana.", {
	'entities':  [(26, 36, 'ORG'),(75, 84, 'DRUG')]
}),

("La incautación fue resultado de un intercambio de información entre personal de inteligencia criminal de las dependencias de Paso de la Patria e Itatí, ya que en esa zona se intensificaron los controles tras el exitoso Operativo Sapucay, en el que fueron detenidos el intendente Terán; su vice, Fabio Aquino, y el jefe de la comisaría de la localidad.", {
	'entities':  [(125, 142, 'LOC'),(145, 150, 'LOC'),(219, 236, 'MISC'),(279, 284, 'PER'),(295, 307, 'PER')]
}),

("En primera instancia, una patrulla conducida por el prefecto general Eduardo Scarzello halló 35 *panes* con un peso de 23,580 kilos de marihuana, a la altura del kilómetro 1278 del río Paraná, en el Barrio Ibiray.", {
	'entities':  [(69, 86, 'PER'),(97, 102, 'DRUG'),(135, 144, 'DRUG'),(181, 191, 'LOC'),(199, 212, 'LOC')]
}),

("Los rastrillajes continuaron hasta la madrugada de ayer, cuando los efectivos de la Prefectura encontraron entre la maleza otros 14 bultos que contenían 415,485 kilos de Cannabis sativa.", {
	'entities':  [(84, 94, 'ORG'),(170, 185, 'DRUG')]
}),

("El fiscal federal de Corrientes Favio Ferrini, que quedó a cargo del caso, ordenó proseguir la investigación.", {
	'entities':  [(21, 31, 'LOC'),(32, 45, 'PER')]
}),

("*Todos los días avanzamos en la lucha contra el narcotráfico en Itatí.", {
	'entities':  [(64, 69, 'LOC')]
}),

("Vamos a seguir intensificando nuestra presencia en esa ciudad y en toda la provincia de Corrientes*, sostuvo la ministra de Seguridad, Patricia Bullrich, según un comunicado de prensa difundido ayer por la Prefectura.", {
	'entities':  [(88, 98, 'LOC'),(135, 152, 'PER'),(206, 216, 'ORG')]
}),

("Incautaron un embarque de 400 kilos de marihuana", {
	'entities':  [(39, 48, 'DRUG')]
}),

("Personal de la Prefectura Naval decomisó un cargamento de 400 kilos de marihuana en Misiones.", {
	'entities':  [(15, 31, 'ORG'),(71, 80, 'DRUG'),(84, 92, 'LOC')]
}),

("El procedimiento se realizó en la zona conocida como Puerto Natural Maciel cuando una patrulla de la fuerza de seguridad que conduce Eduardo Scarzello, encontró 20 bolsas de arpillera dispersas en la costa.", {
	'entities':  [(53, 74, 'LOC'),(133, 150, 'PER')]
}),

("Con la ayuda de *Marys*, uno de los perros antinarcóticos de Prefectura, se constató que las bolsas contenían 374 *panes* de marihuana, con un peso superior a 402 kilos.", {
	'entities':  [(17, 22, 'PER'),(61, 71, 'ORG'),(115, 120, 'DRUG'),(125, 134, 'DRUG')]
}),

("Llevaban cuatro kilos de cocaína en un ómnibus", {
	'entities':  [(25, 32, 'DRUG')]
}),

("Una patrulla de la Gendarmería Nacional detuvo a dos hombres que viajaban en un ómnibus de larga distancia con más de cuatro kilos de cocaína en su equipaje.", {
	'entities':  [(19, 39, 'ORG'),(134, 141, 'DRUG')]
}),

("Efectivos del Escuadrón 55 Tucuman realizaban un control sobre ruta nacional Nº 9, a la altura del peaje Molle Yaco, cuando decidieron inspeccionar el transporte de pasajeros que había iniciado el recorrido en Salta y se dirigía La Plata.", {
	'entities':  [(14, 34, 'ORG'),(63, 81, 'LOC'),(99, 115, 'LOC'),(210, 215, 'LOC'),(229, 237, 'LOC')]
}),

("Los efectivos requisaron las mochilas de los dos sospechosos, dos ciudadanos bolivianos, y detectaron 25 paquetes rectangulares que contenían la droga.", {
	'entities':  [(77, 87, 'MISC'),(145, 150, 'DRUG')]
}),

("SAN MIGUEL DE TUCUMAN.- La Policía local secuestró esta madrugada 61 kilos de cocaína en un operativo en la terminal de ómnibus de San Miguel de Tucumán.", {
	'entities':  [(0, 21, 'LOC'),(78, 85, 'DRUG'),(131, 152, 'LOC')]
}),

("La droga, valuada en más de $5.000.000, era transportada oculta en el piso de un colectivo de línea y tenía como destino a la Ciudad de Buenos Aires.", {
	'entities':  [(3, 8, 'DRUG'),(126, 148, 'LOC')]
}),

("Según informaron fuentes policiales, efectivos de la Dirección General de Drogas Peligrosas de la fuerza concretaron la medida tras una investigación que indicaba que la cocaína era transportada en un micro que había partido desde la provincia de Jujuy con destino a la Capital Federal.", {
	'entities':  [(53, 104, 'ORG'),(247, 252, 'LOC'),(270, 285, 'LOC')]
}),

("El secretario de Seguridad de Tucumán, Miguel Gómez, informó que por el momento no hay detenidos por este hecho.", {
	'entities':  [(17, 37, 'ORG'),(39, 51, 'PER')]
}),

("Según precisó Gómez, la droga secuestrada, que estaba fraccionada en 57 panes, tiene un valor de aproximadamente $5.000.000.", {
	'entities':  [(14, 19, 'PER'),(24, 29, 'DRUG'),(72, 77, 'DRUG')]
}),

("Por su parte, el jefe de Policía, José Díaz, contó que *la observación [sobre el transporte de la droga] fue realizada por un empleado de la empresa a razón de que habían tenido un desperfecto mecánico*.", {
	'entities':  [(34, 43, 'PER')]
}),

("Por último, Díaz dijo que se mantendrán los operativos de control.", {
	'entities':  [(12, 16, 'PER')]
}),

("*Venimos en una línea de trabajo intensificada con el esfuerzo del personal de Drogas Peligrosas.", {
	'entities':  [(79, 96, 'ORG')]
}),

("Es un compromiso de lucha constante contra las drogas*, concluyó.", {
	'entities':  [(47, 53, 'DRUG')]
}),

("Con la competencia exclusiva de los tribunales federales, siempre más abocados a las *grandes causas* o, mejor dicho, a las de más alta exposición pública, la venta al por menor de drogas siempre fue dejada de lado.", {
	'entities':  [(181, 187, 'DRUG')]
}),

("La problemática cobró dimensión dramática a fuerza de violencia y sangre: hace una década eso se vivió especialmente en el conurbano y en zonas periféricas o marginales de otras grandes ciudades, como Córdoba y, especialmente, Rosario, con el dominio de Los Monos.", {
	'entities':  [(123, 132, 'LOC'),(201, 209, 'LOC'),(227, 234, 'LOC'),(254, 263, 'ORG')]
}),

("Los jueces federales conservarían para sí la competencia de las *grandes causas*, el narcotráfico de envergadura o la investigación del crimen organizado dedicado a la producción, el contrabando y la venta de estupefacientes a gran escala.", {
	'entities':  [(209, 224, 'DRUG')]
}),

("Eso se notó especialmente en la provincia de Buenos Aires.", {
	'entities':  [(45, 57, 'LOC')]
}),

("Todo comenzó ocho meses atrás cuando en la ruta nacional 34, en las afueras de la ciudad de Salta, fueron hallados poco más de 30 kilos de droga.", {
	'entities':  [(43, 59, 'LOC'),(92, 97, 'LOC'),(139, 144, 'DRUG')]
}),

("Fue el génesis de una investigación que en las últimas horas permitió el secuestro de uno de los mayores cargamentos de cocaína que circularon por la Argentina: 1166 kilos.", {
	'entities':  [(120, 127, 'DRUG'),(150, 159, 'LOC')]
}),

("En una serie de allanamientos realizados durante el fin de semana pasado por personal de la Gendarmería Nacional y detectives de la Policía Federal Argentina (PFA), además del decomiso de droga fueron apresados cuatro sospechosos.", {
	'entities':  [(92, 163, 'ORG'),(188, 193, 'DRUG')]
}),

("Entre los detenidos se encuentra el presunto dueño del cargamento, un ciudadano argentino de 54 años conocido por su alias de *el Tío*.", {
	'entities':  [(127, 133, 'PER')]
}),

("Además de los 1166 kilos de cocaína secuestrados en un galpón y en una vivienda de Tapiales, en La Matanza, a la organización le habían secuestrado la semana pasada en Cafayate, Salta, 67 kilos de cocaína y 25 kilos de marihuana.", {
	'entities':  [(28, 35, 'DRUG'),(83, 91, 'LOC'),(96, 106, 'LOC'),(168, 176, 'LOC'),(178, 183, 'LOC'),(197, 204, 'DRUG'),(219, 228, 'DRUG')]
}),

("Los allanamientos y las detenciones fueron ordenados por el juez federal de Salta Julio Bavio, a cargo del expediente que se inició hace ocho meses con el hallazgo de la droga abandonada.", {
	'entities':  [(76, 81, 'LOC'),(82, 93, 'PER'),(170, 175, 'DRUG')]
}),

("En la investigación, el Ministerio Público estuvo representado por el fiscal federal de Salta Eduardo Villalba y la Procuraduría de Narcocriminalidad (Procunar), conducida por Diego Iglesias.", {
	'entities':  [(24, 42, 'ORG'),(88, 93, 'LOC'),(94, 110, 'PER'),(116, 160, 'ORG'),(176, 190, 'PER')]
}),

("Fuentes judiciales resaltaron y destacaron el buen trabajo en equipo hecho entre la PFA y la Gendarmería Nacional.", {
	'entities':  [(84, 87, 'ORG'),(93, 113, 'ORG')]
}),

("*Se trata de una de las incautaciones de cocaína más importantes de la historia argentina y fue posible por el trabajo en equipo*, sostuvo la ministra de Seguridad, Patricia Bullrich, en una conferencia de prensa.", {
	'entities':  [(80, 89, 'MISC'),(165, 182, 'PER')]
}),

("En realidad es el tercer mayor cargamento de cocaína secuestrado en lo que va del año.", {
	'entities':  [(45, 52, 'DRUG')]
}),

("En junio pasado, en Bahía Blanca, la PFA había decomisado 2000 kilos ocultos en bobinas que tenían como destino Barcelona, España.", {
	'entities':  [(20, 32, 'LOC'),(37, 40, 'ORG'),(112, 121, 'LOC'),(123, 129, 'LOC')]
}),

("Un mes después, en Santiago del Estero, la Gendarmería Nacional incautó 1838 kilos de la misma droga en el operativo denominado Halcón 9.", {
	'entities':  [(19, 38, 'LOC'),(43, 63, 'ORG'),(95, 100, 'DRUG'),(128, 136, 'MISC')]
}),

("El mayor cargamento de cocaína decomisado en la Argentina ocurrió hace 20 años, en el llamado operativo Strawberry, con una captura de 2200 kilos.", {
	'entities':  [(23, 30, 'DRUG'),(48, 57, 'LOC'),(104, 114, 'MISC')]
}),

("En la conferencia de prensa, Bullrich estuvo acompañada por el jefe de la Policía Federal Argentina, comisario general Néstor Roncaglia; el subdirector de la Gendarmería Nacional, comandante general Federico Sosa, y los funcionarios del ministerio Eugenio Burzaco, Gerardo Milman, Martín Verrier, Darío Oroquieta y Rodrigo Bonini.", {
	'entities':  [(29, 37, 'PER'),(74, 99, 'ORG'),(119, 135, 'PER'),(158, 178, 'ORG'),(199, 212, 'PER'),(248, 263, 'PER'),(265, 279, 'PER'),(281, 295, 'PER'),(297, 312, 'PER'),(315, 329, 'PER')]
}),

("A partir del accidental hallazgo de droga en Salta, hace ocho meses, se puso la lupa sobre *el Tío*.", {
	'entities':  [(36, 41, 'DRUG'),(45, 50, 'LOC'),(92, 98, 'PER')]
}),

("*Hace un tiempo que sospechábamos de esta persona como un importante distribuidor de droga*, afirmó a LA NACION un calificado detective.", {
	'entities':  [(85, 90, 'DRUG'),(102, 111, 'ORG')]
}),

("El juez Bavio le encargó las tareas de investigación a la División Precursores Químicos y Drogas Emergentes de la Superintendencia de Drogas Peligrosas de la PFA y a la Unidad Operaciones Antidrogas de la Gendarmería.", {
	'entities':  [(8, 13, 'PER'),(58, 161, 'ORG'),(169, 216, 'ORG')]
}),

("*Amigo, ya vamos, son 820 facturas y serían 328 gringas*, fue el mensaje de texto que se interceptó de uno de los 30 teléfonos intervenidos.", {
	'entities':  [(26, 34, 'DRUG'),(48, 55, 'DRUG')]
}),

("Los investigadores estaban convencidos de que se trataba de una entrega de droga.", {
	'entities':  [(75, 80, 'DRUG')]
}),

("Se intensificaron las investigaciones sobre *el Tío* y se determinó que un cargamento estaba en viaje hacia el conurbano.", {
	'entities':  [(45, 51, 'PER'),(111, 120, 'LOC')]
}),

("El domingo pasado a la noche, un camión Mercedes Benz que transportaba puertas de madera ingresó en un depósito de Talcahuano al 1200, en Tapiales, La Matanza.", {
	'entities':  [(40, 53, 'ORG'),(115, 133, 'LOC'),(138, 146, 'LOC'),(148, 158, 'LOC')]
}),

("Se trataba del vehículo que había transportado la droga.", {
	'entities':  [(50, 55, 'DRUG')]
}),

("Cuando la Gendarmería Nacional y la PFA irrumpieron en el depósito, la droga había sido bajada del camión y cargada en una camioneta Toyota Hilux.", {
	'entities':  [(10, 30, 'ORG'),(36, 39, 'ORG'),(71, 76, 'DRUG'),(133, 145, 'MISC')]
}),

("En el lugar encontraron 817 paquetes de cocaína, que tenían pegados el logo de un ave rapaz.", {
	'entities':  [(40, 47, 'DRUG')]
}),

("Los 817 ladrillos de droga era las *820 facturas* del mensaje, suponen los investigadores.", {
	'entities':  [(8, 26, 'DRUG'),(40, 48, 'DRUG')]
}),

("En el depósito fueron detenidos *el Tío* y otros tres sospechosos.", {
	'entities':  [(33, 39, 'PER')]
}),

("El juez Bavio ordenó un allanamiento en la casa del presunto dueño del cargamento donde fueron hallados otros 305 kilos de cocaína, 280 mil dólares, elementos de corte y fraccionamiento, armas de fuego, documentación y 11 teléfonos celulares.", {
	'entities':  [(8, 13, 'PER'),(123, 130, 'DRUG')]
}),

("Según explicó el Ministerio de Seguridad de la Nación, el valor de los 1166 kilos de cocaína alcanzaría en el mercado local una cifra superior a los US$ 6.000.000, pero en Europa el valor de ese cargamento puede llegar a los 34.800.000 euros.", {
	'entities':  [(17, 53, 'ORG'),(85, 92, 'DRUG'),(172, 178, 'LOC')]
}),

("Un agente del Servicio Penitenciario cordobés fue detenido acusado de integrar una banda narco junto con su esposa y otras seis personas, durante una serie de allanamientos realizados ayer en localidades limítrofes entre las provincias de Córdoba y Santa Fe, en los cuales se secuestraron 78 kilos de marihuana, informaron fuentes policiales consignadas por Télam.", {
	'entities':  [(14, 36, 'ORG'),(37, 45, 'MISC'),(239, 246, 'LOC'),(249, 257, 'LOC'),(301, 310, 'DRUG'),(358, 363, 'ORG')]
}),

("Uno de los lugares allanados fue la sede del Servicio Penitenciario de San Francisco, ya que se sospecha que un preso allí detenido comandaba uno de los puntos de venta de la droga.", {
	'entities':  [(45, 84, 'ORG'),(175, 180, 'DRUG')]
}),

("Los procedimientos fueron realizados en las localidades cordobesas de San Francisco, Arroyito y Tránsito, y en la población santafesina de Frontera, y estuvieron a cargo de la Fuerza Policial Antinarcotráfico (FPA) de Córdoba en el marco de una causa que instruye el Ministerio Público Fiscal de Córdoba.", {
	'entities':  [(70, 83, 'LOC'),(85, 93, 'LOC'),(96, 104, 'LOC'),(124, 135, 'MISC'),(139, 147, 'LOC'),(176, 214, 'ORG'),(218, 225, 'LOC'),(267, 303, 'ORG')]
}),

("En esos operativos fueron secuestrados 78 kilos de marihuana y fueron detenidos cuatro hombres y cuatro mujeres, quienes quedaron a disposición de la Fiscalía de Lucha contra el Narcotráfico de San Francisco.", {
	'entities':  [(51, 60, 'DRUG'),(150, 207, 'ORG')]
}),

("Según fuentes policiales, entre los detenidos se encuentra un agente del Servicio Penitenciario cordobés y su esposa, quienes están acusados de estar a cargo de un punto de venta de drogas.", {
	'entities':  [(73, 95, 'ORG'),(96, 104, 'MISC'),(182, 188, 'DRUG')]
}),

("En tanto, la policía de Corrientes decomisó más de media tonelada de marihuana durante procedimientos realizados en la ciudad de Paraná.", {
	'entities':  [(24, 34, 'LOC'),(69, 78, 'DRUG'),(129, 135, 'LOC')]
}),

("En uno de esos operativos se logró la incautación de 170 kilos de cannabis tras interceptar a un Fiat Siena.", {
	'entities':  [(66, 74, 'DRUG'),(97, 107, 'MISC')]
}),

("Así se encontraron otros 350 kilos de marihuana y el embarque de más de 500 kilos fue valuado por las autoridades provinciales en unos $14.000.000.", {
	'entities':  [(38, 47, 'DRUG')]
}),

("Por su parte, la Gendarmería incautó un cargamento de tres toneladas de marihuana en Entre Ríos.", {
	'entities':  [(17, 28, 'ORG'),(72, 81, 'DRUG'),(85, 95, 'LOC')]
}),

("No fue una casualidad que a Marcelo Balcedo y a su esposa, Paola Fiege, los detuvieran en la chacra uruguaya El Gran Chaparral, cerca de Punta del Este.", {
	'entities':  [(28, 43, 'PER'),(59, 70, 'PER'),(100, 108, 'MISC'),(109, 126, 'LOC'),(137, 151, 'LOC')]
}),

("La mujer hizo 26 viajes -varios solo por unas horas- en los últimos dos años al país vecino, donde la Justicia investiga que Balcedo tiene parte de las propiedades que fueron detectadas en la causa por supuesto lavado de dinero que se investiga desde 2015, con vinculaciones de blanqueo de dinero a la banda de Los Monos.", {
	'entities':  [(125, 132, 'PER'),(311, 320, 'ORG')]
}),

("Balcedo, titular del Sindicato de Obreros y Empleados de Minoridad y de Educación (Soeme), viene siendo investigado por la Procuraduría de Criminalidad Económica y Lavado de Activos (Procelac) y la Unidad de Información Financiera (UIF) desde hace más de dos años, cuando comenzaron a detectarse maniobras sospechosas con extracciones millonarias de dinero del Banco Columbia, con montos que superaron los $53.000.000.", {
	'entities':  [(0, 7, 'PER'),(21, 89, 'ORG'),(123, 192, 'ORG'),(198, 236, 'ORG'),(361, 375, 'ORG')]
}),

("Mauricio Yebra es una figura clave en la arquitectura de lavado de dinero que habría montado Balcedo, con el Soeme como principal pantalla.", {
	'entities':  [(0, 14, 'PER'),(93, 100, 'PER'),(109, 114, 'ORG')]
}),

("Según fuentes judiciales consultadas por LA NACION, durante los últimos dos años la pareja de Balcedo realizó 26 viajes a Uruguay, varios en vuelos privados.", {
	'entities':  [(41, 50, 'ORG'),(94, 101, 'PER'),(122, 129, 'LOC')]
}),

("Permanecía en ese país unas horas y después retornaba a Buenos Aires.", {
	'entities':  [(56, 68, 'LOC')]
}),

("*Balcedo y su pareja tenían un nivel de vida propio de magnates, que no se correspondía con los ingresos que tenían.", {
	'entities':  [(1, 8, 'PER')]
}),

("Muchos de los desembolsos millonarios en propiedades y vehículos figuraban a nombre del sindicato, incluidos los de Fiege*, señaló una fuente judicial.", {
	'entities':  [(116, 121, 'PER')]
}),

("En la chacra uruguaya que allanó la policía de ese país se incautaron fajos de dinero, armas automáticas y también, numerosos autos de lujo, entre ellos una Ferrari, un Porsche, un Chevrolet Corvette y un Mercedes Benz, todos patentados en Punta del Este.", {
	'entities':  [(13, 21, 'MISC'),(157, 164, 'ORG'),(169, 176, 'ORG'),(181, 190, 'ORG'),(191, 199, 'MISC'),(205, 218, 'ORG'),(240, 254, 'LOC')]
}),

("Uno de los principales apuntados en esta investigación es Mauricio Yebra, un empleado del sindicato, que sería uno de sus testaferros de esta organización criminal.", {
	'entities':  [(58, 72, 'PER')]
}),

("LA NACION publicó el 9 de octubre de 2015 las vinculaciones de este lugarteniente de Balcedo con la banda de Los Monos para la compra de autos de alta gama.", {
	'entities':  [(0, 9, 'ORG'),(85, 92, 'PER'),(109, 118, 'ORG')]
}),

("Una de las inconsistencias que se encontraron en las finanzas de Yebra fueron las extracciones bancarias que realizó entre diciembre de 2012 y 2013, que fueron -según los tres reportes sospechosos de la Unidad de Información Financiera (UIF)- por $53.523.221.", {
	'entities':  [(65, 70, 'PER'),(203, 241, 'ORG')]
}),

("La operación consistía en el depósito de cheques por ese monto, que después Yebra retiraba por la ventanilla del Banco Columbia.", {
	'entities':  [(76, 81, 'PER'),(113, 127, 'ORG')]
}),

("Ese dinero fue a parar a una empresa vinculada a la venta de publicidad en medios de comunicación, que se llama Emprendimientos Publicitarios Bonaerenses SA, que se sospecha es propiedad de la mujer de Balcedo.", {
	'entities':  [(112, 156, 'ORG'),(202, 209, 'PER')]
}),

("Allí funciona una radio FM del grupo empresarial de Balcedo, entre los que se encuentra también el diario Hoy de La Plata.", {
	'entities':  [(52, 59, 'PER'),(99, 121, 'ORG')]
}),

("El nombre de Yebra apareció en el radar de la Procelac cuando comenzaron a investigar a la banda rosarina de Los Monos.", {
	'entities':  [(46, 54, 'ORG'),(109, 118, 'ORG')]
}),

("Detectaron que 14 autos de alta gama en poder de la familia Cantero estaban registrados a nombre de Yebra.", {
	'entities':  [(60, 67, 'PER'),(100, 105, 'PER')]
}),

("Según esa pesquisa, Yebra habría adquirido de manera legal esos vehículos, que después utilizaba la organización narcocriminal, a la que le secuestraron en total 56 autos, motos y camionetas, y otros nueve inmuebles.", {
	'entities':  [(20, 25, 'PER')]
}),

("La adquisición de los autos se realizaba en una concesionaria de La Plata que se llama El Chaqueñito.", {
	'entities':  [(65, 73, 'LOC'),(87, 100, 'LOC')]
}),

("Según el expediente 10.315/2015, se le adjudican a Los Monos unos 46 autos.", {
	'entities':  [(51, 60, 'ORG')]
}),

("Yebra no tenía ingresos comprobados ni estaba registrado en la AFIP hasta 2012, cuando tras ser intimado de oficio por el organismo recaudador se anotó como monotributista categoría F, con ingresos anuales de hasta $96.000.", {
	'entities':  [(0, 5, 'PER'),(63, 67, 'ORG')]
}),

("El abogado de Yebra, Fernando Sirio, dijo que la única relación con la banda de Los Monos era que Yebra tenía asegurado sus autos en la misma compañía que la familia Cantero.", {
	'entities':  [(14, 19, 'PER'),(21, 35, 'PER'),(80, 89, 'ORG'),(98, 103, 'PER'),(166, 173, 'PER')]
}),

("La investigación sobre el nexo entre esta banda con Balcedo y Yebra continuó durante los últimos años y se detectaron más bienes.", {
	'entities':  [(52, 59, 'PER'),(62, 67, 'PER')]
}),

("El diario Hoy de La Plata, propiedad de Marcelo Balcedo, criticó duramente al juez Ernesto Kreplak por ordenar la detención del gremialista.", {
	'entities':  [(10, 25, 'ORG'),(40, 55, 'PER'),(83, 98, 'PER')]
}),

("Lo consideró una *represalia* por las investigaciones que el periódico publicó y que *comprometieron* a su hermano, Nicolás Kreplak.", {
	'entities':  [(116, 131, 'PER')]
}),

("Un joven de 22 años, que supuestamente vendía drogas, fue acribillado con una ametralladora en la zona sur de Rosario, luego de contactarse con dos compradores de estupefacientes por una red social.", {
	'entities':  [(46, 52, 'DRUG'),(110, 117, 'LOC'),(163, 178, 'DRUG')]
}),

("El hecho ocurrió el domingo a la madrugada, cuando Javier Moyano se dispuso a hacer la entrega de una dosis de cocaína a una pareja con quienes se había contactado en Facebook.", {
	'entities':  [(51, 64, 'PER'),(111, 118, 'DRUG'),(167, 175, 'ORG')]
}),

("La cita fue en Presidente Quintana y Ovidio Lagos, en la zona sur de Rosario, donde aparentemente -según las fuentes policiales Moyano entregó la droga y recibió el dinero de los compradores que se movían en una moto.", {
	'entities':  [(15, 49, 'LOC'),(69, 76, 'LOC'),(128, 134, 'PER'),(146, 151, 'DRUG')]
}),

("La Policía Científica recolectó en la escena del crimen 15 vainas servidas.", {
	'entities':  [(3, 22, 'ORG')]
}),

("El joven sufrió heridas en la espalda y en una pierna, y fue trasladado en un patrullero del Comando Radioeléctrico al Hospital de Emergencias Clemente Álvarez (HECA), donde murió después de que los médicos trataran de salvar su vida.", {
	'entities':  [(93, 166, 'ORG')]
}),

("La ráfaga de disparos alcanzó no solo a Moyano, sino también a un Renault Sandero que estaba estacionado allí y a un colectivo del transporte público.", {
	'entities':  [(40, 46, 'PER'),(66, 81, 'MISC')]
}),

("A pocas cuadras del lugar del crimen, la policía detuvo a los dos compradores de droga que circulaban en una moto.", {
	'entities':  [(81, 86, 'DRUG')]
}),

("Declararon que segundos después que se fueran en la moto, tras comprar una dosis de cocaína, apareció un utilitario en la esquina de Presidente Quintana y Ovidio Lagos.", {
	'entities':  [(133, 167, 'LOC')]
}),

("Apuntaron que del vehículo vieron bajar a un hombre con una ametralladora que comenzó a disparar contra Moyano, y escucharon una ráfaga de tiros.", {
	'entities':  [(104, 110, 'PER')]
}),

("En el rebrote de violencia que sacude la ciudad de Rosario, donde se cometieron 16 homicidios en lo que va del año, se empezó a ver que los últimos crímenes se cometieron con armas de gran poder de fuego.", {
	'entities':  [(51, 58, 'LOC')]
}),

("Uno de los prófugos más buscados de Rosario actualmente es Alan Funes, miembro de una banda narcocriminal de la zona sur de Rosario, quien el 1° de enero pasado festejó fin de año con una ráfaga de ametralladora mientras se encontraba con detención domiciliaria por un crimen que había cometido en 2016.", {
	'entities':  [(36, 43, 'LOC'),(59, 69, 'PER'),(124, 131, 'LOC')]
}),

("El vehículo había partido desde la localidad salteña de Salvador Mazza y se dirigía hacia Tucumán.", {
	'entities':  [(45, 52, 'MISC'),(56, 70, 'LOC'),(90, 97, 'LOC')]
}),

("Llevaba en su automóvil un cargamento de 47 kilos de cocaína.", {
	'entities':  [(53, 60, 'DRUG')]
}),

("El operativo se desarrolló a la altura del kilómetro 37 de la ruta nacional 68, cerca de la ciudad de Cafayate.", {
	'entities':  [(62, 78, 'LOC'),(102, 110, 'LOC')]
}),

("Los uniformados frenaron allí la marcha de un Volkswagen Suran que era conducido por una mujer.", {
	'entities':  [(46, 62, 'MISC')]
}),

("Durante la requisa, comprobaron que llevaba a sus dos hijas hacia Tucumán.", {
	'entities':  [(66, 73, 'LOC')]
}),

("Los integrantes de esa patrulla de la Gendarmería decidieron, entonces, registrar el rodado.", {
	'entities':  [(38, 49, 'ORG')]
}),

("No se trataba de un perfil habitual de traficante, más por la compañía de los menores, pero los gendarmes optaron por verificar la carrocería del rodado y se sorprendieron al descubrir que se habían acondicionado 44 paquetes rectangulares en los paneles de las puertas, con un contenido total de 47 kilos de cocaína.", {
	'entities':  [(308, 315, 'DRUG')]
}),

("La mujer fue arrestada al inspeccionarse su vehículo en un puesto que la Gendarmería había instalado en la ruta nacional 68, cerca de la ciudad salteña de Cafayate", {
	'entities':  [(73, 84, 'ORG'),(107, 123, 'LOC'),(144, 151, 'MISC'),(155, 163, 'LOC')]
}),

("Le cortaron elpelo", {
	'entities':  [(12, 18, 'ME')]
}),

("Que distinto qeda es otra persona", {
	'entities':  [(13, 17, 'ME')]
}),

("Viste parece mas joben", {
	'entities':  [(17, 22, 'ME')]
}),

("Ke ases ? Ase frio ahora", {
	'entities':  [(0, 2, 'ME'),(3, 7, 'ME'),(10, 13, 'ME')]
}),

("Yendo al hospital x la medicacion feliz cumple flaca", {
	'entities':  [(9, 17, 'MISC'),(18, 19, 'ME'),(23, 33, 'DRUG')]
}),

("X limpiar", {
	'entities':  [(0, 1, 'ME')]
}),

("Xq ayer me la rasque jijijiji", {
	'entities':  [(0, 2, 'ME'),(21, 29, 'ME')]
}),

("Como todos los dias jijiji", {
	'entities':  [(20, 26, 'ME')]
}),

("Capaz jijiji", {
	'entities':  [(6, 12, 'ME')]
}),

("Bueno voi a ver si veo al medico besos", {
	'entities':  [(6, 9, 'ME')]
}),

("A q hora llegaste", {
	'entities':  [(2, 3, 'ME')]
}),

("Hace un rato me fui en cole hoi", {
	'entities':  [(23, 27, 'ME'),(28, 31, 'ME')]
}),

("Vas a venir puts", {
	'entities':  [(12, 16, 'ME')]
}),

("Ya la necesitas x que te la iva a llevar a la tarde", {
	'entities':  [(16, 17, 'ME'),(28, 31, 'ME')]
}),

("Y te dava para el escavio", {
	'entities':  [(5, 9, 'ME'),(18, 25, 'DRUG')]
}),

("A q hora chavona", {
	'entities':  [(2, 3, 'ME'),(9, 16, 'ME')]
}),

("Tipo 4 x tengo que viajar otra ves y cuando vuelva voi derecho para alla pivita rocha", {
	'entities':  [(7, 8, 'ME'),(31, 34, 'ME'),(51, 54, 'ME'),(73, 85, 'ME')]
}),

("Te conbiene q me traigas un regalo...", {
	'entities':  [(3, 11, 'ME'),(12, 13, 'ME')]
}),

(".mas vale y algo mas che jijijiji*", {
	'entities':  [(25, 33, 'ME')]
}),

("De na cuña te quiero flaca puta", {
	'entities':  [(3, 5, 'ME')]
}),

("Mira rre linda", {
	'entities':  [(5, 8, 'ME')]
}),

("Orrenda la mato a la cachetona ella me la saco", {
	'entities':  [(0, 7, 'ME')]
}),

("No te olvides de las cervesas", {
	'entities':  [(21, 29, 'ME')]
}),

("Y el escabio lo compro alla", {
	'entities':  [(5, 12, 'DRUG')]
}),

("Yo tomo un remis y voi para alla x que estoi esperando a sofia", {
	'entities':  [(19, 22, 'ME'),(33, 34, 'ME'),(39, 44, 'ME'),(57, 62, 'PER')]
}),

("Tengo que llevar a nico a lo de la pico", {
	'entities':  [(19, 23, 'PER')]
}),

("Nada aca en la casa de un amigo que me imvito a comer. Y vos", {
	'entities':  [(39, 45, 'ME')]
}),

("En casa aburrida mirando tele como llegaste ayer dezpues de tanta caminata jiji", {
	'entities':  [(49, 56, 'ME')]
}),

("Vos todo tranki", {
	'entities':  [(9, 15, 'ME')]
}),

("Si todo tranqui x eso estoi aburrida jeje", {
	'entities':  [(16, 17, 'ME'),(22, 27, 'ME')]
}),

("Hlaa", {
	'entities':  [(0, 4, 'ME')]
}),

("Aca se esta poniendo re feo pero ya voi de vuelta no me hago drama je", {
	'entities':  [(36, 39, 'ME')]
}),

("Un faso y medio", {
	'entities':  [(3, 7, 'DRUG')]
}),

("U que poco bueno te guardo para vos y te aviso asi lo vas a vuscar queres", {
	'entities':  [(60, 66, 'ME')]
}),

("Contesta yaaaaa", {
	'entities':  [(9, 15, 'ME')]
}),

("Que hces amiga", {
	'entities':  [(4, 8, 'ME')]
}),

("Hola paola cuando cobras preguntastes ?", {
	'entities':  [(5, 10, 'PER'),(25, 37, 'ME')]
}),

("*Tía yo te quiero mucho vos sabes que sos mi tía preferida, yo no soy nadie para decirte algo porque soy pendeja y nose nada de la vida todavía . Quiero que estés bien pensa en nosotros que te queremos mucho! Te Deceo Lo mejor y espero que esto que te pasó sirva de algo. Igual a pesar de todo todos te queremos igual beso*", {
	'entities':  [(212, 217, 'ME')]
}),

("Ke ases ?", {
	'entities':  [(0, 7, 'ME')]
}),

("Hlaaa", {
	'entities':  [(0, 5, 'ME')]
}),

("Te cuento ke a juan yA le dieron el alta pobre esta en un hogar de abuelitos ..bueno te msndo besooooo. Cuando cobras la pecion el 3 o 4 yo no me acuardo ..jaja bueno mañana capas ke balla para el pueblo y llego a tomar unos mates y voy a ver a la abuela bibi ..y de paso lo veo a juan en el hogar ..besoooo.", {
	'entities':  [(10, 12, 'ME'),(15, 19, 'PER'),(20, 22, 'ME'),(88, 93, 'ME'),(94, 102, 'ME'),(121, 127, 'ME'),(180, 182, 'ME'),(183, 188, 'ME'),(255, 259, 'PER'),(281, 285, 'PER'),(300, 307, 'ME')]
}),

("Ah y no hacía falta que me bloquees del fb porque yo nunca dije nada en contra tuyo yo quería el bien para vos & vos en esos momentos que pasamos juntas te hiciste querer mucho más. Pero ya pasó una vez con Horacio que te alejaste de nosotros que no pasen dos y disfruta a pleno tu vida y a tus hijas. Te Quiero Muchísimo Tia", {
	'entities':  [(27, 35, 'ME'),(40, 42, 'ORG'),(207, 214, 'PER')]
}),

("Felis dia sobrina !!!", {
	'entities':  [(0, 5, 'ME')]
}),

("Hla ste es mi nuevo num. Soi dlfi.", {
	'entities':  [(0, 3, 'ME'),(4, 7, 'ME'),(20, 23, 'ME'),(25, 28, 'ME'),(29, 33, 'PER')]
}),

("avisa cuando llegas pa tu ksa ok?", {
	'entities':  [(20, 22, 'ME'),(26, 29, 'ME')]
}),

("Uuuula primix jaja", {
	'entities':  [(0, 6, 'ME'),(7, 13, 'ME')]
}),

("ya llegaste pa tu ksa?", {
	'entities':  [(12, 14, 'ME'),(18, 21, 'ME')]
}),

("Siiiii yege jajja si te envie un maj", {
	'entities':  [(7, 11, 'ME'),(33, 36, 'ME')]
}),

("*ah wueno pero llegaste bien no ,,,che prima la karo k ta haciendo?*", {
	'entities':  [(4, 9, 'ME'),(48, 52, 'PER'),(53, 54, 'ME')]
}),

("holaaaa prima?", {
	'entities':  [(0, 7, 'ME')]
}),

("k haces plaga todo bien?", {
	'entities':  [(0, 1, 'ME')]
}),

("bien aka viendo la tv y vs?", {
	'entities':  [(5, 8, 'ME'),(24, 26, 'ME')]
}),

("anda forro yo te hablo de wuena onda tampoco pa k me digas gay sos un gil?", {
	'entities':  [(26, 31, 'ME'),(45, 47, 'ME'),(48, 49, 'ME')]
}),

("Ooola k hces???", {
	'entities':  [(0, 12, 'ME')]
}),

("*naa en kamita descansando xk trab hoy hasta las 8 y recien llegue hace un rato pa mi ksa ,,,vs k hacías?*", {
	'entities':  [(8, 14, 'ME'),(27, 29, 'ME'),(30, 34, 'ME'),(80, 82, 'ME'),(86, 89, 'ME'),(93, 95, 'ME'),(96, 97, 'ME')]
}),

("Jajajaj etoy viend unas pelis jajaja", {
	'entities':  [(8, 12, 'ME'),(13, 18, 'ME')]
}),

("*holaaa k haces primita cm les fue ayer con la venta ,,,?*", {
	'entities':  [(8, 9, 'ME'),(24, 26, 'ME')]
}),

("Jajjja gracias estab re llenooo encina estabams los 4 na mas xk laro se fue a mar del plata ja", {
	'entities':  [(15, 20, 'ME'),(24, 31, 'ME'),(32, 38, 'ME'),(39, 47, 'ME'),(61, 63, 'ME'),(64, 68, 'PER'),(78, 91, 'LOC')]
}),

("*uhhh mira vs de seguro taban sin tiempo jeje,,,?*", {
	'entities':  [(11, 13, 'ME'),(24, 29, 'ME')]
}),

("Jjaja siii encima tenia k ir a jugar.....kasi no me deja", {
	'entities':  [(24, 25, 'ME'),(41, 45, 'ME')]
}),

("*holaaaa prima cm taz k haces,?*", {
	'entities':  [(15, 17, 'ME'),(18, 21, 'ME'),(22, 23, 'ME')]
}),

("Oola ben mirando las noticias...y voz???", {
	'entities':  [(0, 4, 'ME'),(5, 8, 'ME'),(34, 37, 'ME')]
}),

("*k haceS prima todo bien ,x*", {
	'entities':  [(1, 2, 'ME'),(3, 8, 'ME')]
}),

("Ben aka con la familia ja y voz???", {
	'entities':  [(0, 3, 'ME'),(4, 7, 'ME')]
}),

("ah wueno y yo recien llegó del trab un poco cansado?", {
	'entities':  [(3, 8, 'ME'),(31, 35, 'ME')]
}),

("y la karo ta ahi ?", {
	'entities':  [(5, 9, 'ME'),(10, 12, 'ME')]
}),

("Si akab de llegar me parec ja", {
	'entities':  [(3, 7, 'ME'),(21, 26, 'ME')]
}),

("Keres k le diga alg???", {
	'entities':  [(0, 5, 'ME'),(6, 7, 'ME'),(16, 19, 'ME')]
}),

("mmm k raro k llegue tan tarde mmm ya me imagina xk llegó tarde después dice k nooo?", {
	'entities':  [(4, 5, 'ME'),(11, 12, 'ME'),(48, 50, 'ME'),(76, 77, 'ME')]
}),

("creo k no le sirve de naaa sus vacaciones x mar del plata la verdad ?", {
	'entities':  [(5, 6, 'ME'),(22, 26, 'ME'),(42, 43, 'ME'),(44, 57, 'LOC')]
}),

("Ooooh mmm noce xk llego tarde seguro xk no abia colectiv", {
	'entities':  [(10, 14, 'ME'),(15, 17, 'ME'),(37, 39, 'ME'),(43, 47, 'ME'),(48, 56, 'ME')]
}),

("mmm hace rato me dijo k supuestamente taba con un amigo en mc Donalds noc si es verdad mmm no le digas k yo te dije?", {
	'entities':  [(22, 23, 'ME'),(38, 42, 'ME'),(70, 73, 'ME'),(103, 104, 'ME')]
}),

("No no le digo nad", {
	'entities':  [(14, 17, 'ME')]
}),

("holaaa primita cm taz ?", {
	'entities':  [(15, 17, 'ME'),(18, 21, 'ME')]
}),

("*k es de tu vida ,,?*", {
	'entities':  [(1, 2, 'ME')]
}),

("Oooola perdid y ben aka recien salg del cole", {
	'entities':  [(7, 13, 'ME'),(16, 19, 'ME'),(20, 23, 'ME'),(31, 35, 'ME')]
}),

("k haces primita?", {
	'entities':  [(0, 1, 'ME')]
}),

("Que haces  pa donde andas que haces", {
	'entities':  [(11, 13, 'ME')]
}),

("toy en mi ksa xk?", {
	'entities':  [(0, 3, 'ME'),(10, 13, 'ME'),(14, 16, 'ME')]
}),

("y vs k haces?", {
	'entities':  [(2, 4, 'ME'),(5, 6, 'ME')]
}),

("Che mañana vas a Balcarce", {
	'entities':  [(17, 25, 'LOC')]
}),

("dale ah k hora?", {
	'entities':  [(5, 7, 'ME'),(8, 9, 'ME')]
}),

("No se pregúntale s walde! Ya te mejorarste de la pierna ?", {
	'entities':  [(17, 18, 'ME'),(19, 24, 'PER')]
}),

("*si ya toy bien pa?,,,preg vs xk no tengo su num de walde?*", {
	'entities':  [(16, 18, 'ME'),(22, 26, 'ME'),(27, 29, 'ME'),(30, 32, 'ME'),(45, 48, 'ME'),(52, 57, 'PER')]
}),

("y k te dijo javi ?", {
	'entities':  [(2, 3, 'ME'),(12, 16, 'PER')]
}),

("Jugamos a las 14:00 aya en Balcarce.", {
	'entities':  [(20, 23, 'ME'),(27, 35, 'LOC')]
}),

("Rudy irá", {
	'entities':  [(0, 4, 'PER')]
}),

("wUeno y ah k hora salimos de aka?", {
	'entities':  [(0, 5, 'ME'),(11, 12, 'ME'),(29, 32, 'ME')]
}),

("y rudy no creo k vaya xk dijo k juega en el club ah las tres?", {
	'entities':  [(2, 6, 'PER'),(15, 16, 'ME'),(22, 24, 'ME'),(30, 31, 'ME'),(44, 48, 'MISC'),(49, 51, 'ME')]
}),

("A ! Pero decile para q vaya a compartir con nosotros", {
	'entities':  [(21, 22, 'ME')]
}),

("ok me pasas ah buscar noo.?", {
	'entities':  [(12, 14, 'ME'),(22, 26, 'ME')]
}),

("dale ah k hora pasas x mi ksa?", {
	'entities':  [(5, 7, 'ME'),(8, 9, 'ME'),(21, 22, 'ME'),(26, 29, 'ME')]
}),

("Dond taz", {
	'entities':  [(0, 4, 'ME'),(5, 8, 'ME')]
}),

("Oooola primo com estas???tant tiempo", {
	'entities':  [(0, 6, 'ME'),(13, 16, 'ME'),(25, 29, 'ME')]
}),

("*Yo toy bien primita ah pesAr de todo,,?*", {
	'entities':  [(21, 29, 'ME')]
}),

("*y si tanto tiempo k es de tu vida ,,cm vas con tus estudios??*", {
	'entities':  [(19, 20, 'ME'),(37, 39, 'ME')]
}),

("Bien primo gracias a dios...pero vo k hon k te paso xk decs eso k te paso", {
	'entities':  [(33, 43, 'ME'),(52, 54, 'ME'),(55, 59, 'ME'),(64, 65, 'ME')]
}),

("Che manana tipo 10:30 Toy pasando a buscarte ! Jugamos dos partidos contestame", {
	'entities':  [(22, 25, 'ME')]
}),

("hola prima cm taz?", {
	'entities':  [(11, 13, 'ME'),(14, 17, 'ME')]
}),

("holaaa prima cm taz k haces?", {
	'entities':  [(13, 15, 'ME'),(16, 19, 'ME'),(20, 21, 'ME')]
}),

("Ooooola ben y vo???=)", {
	'entities':  [(0, 7, 'ME'),(8, 11, 'ME'),(14, 16, 'ME')]
}),

("bien aka en mi kamita acostado xk toy re contra engripado y no tengo ganas pa naa?", {
	'entities':  [(5, 8, 'ME'),(15, 21, 'ME'),(31, 33, 'ME'),(34, 37, 'ME'),(75, 77, 'ME'),(78, 81, 'ME')]
}),

("Ooooooh ma ahi eso x tirar facha jajja", {
	'entities':  [(0, 7, 'ME'),(8, 10, 'ME'),(19, 20, 'ME')]
}),

("cm lo pasaron ah noche me enteré k estuvieron de joda?", {
	'entities':  [(0, 2, 'ME'),(14, 16, 'ME'),(33, 34, 'ME')]
}),

("x tirar mucha facha asi también me fue jeje?", {
	'entities':  [(0, 1, 'ME')]
}),

("contam k isiste hoy primita?", {
	'entities':  [(0, 6, 'ME'),(7, 8, 'ME'),(9, 15, 'ME')]
}),

("Emmm no yop yo fui la karo na mas y nocp jajja y nada primo tranki estub lloviend...", {
	'entities':  [(8, 11, 'ME'),(22, 26, 'ME'),(27, 29, 'ME'),(36, 40, 'ME'),(60, 66, 'ME'),(67, 72, 'ME'),(73, 81, 'ME')]
}),

("*mmm asi k fue la karo no más ,,,y aka también taba lloviendo después del medio dia ,,?*", {
	'entities':  [(9, 10, 'ME'),(18, 22, 'PER'),(35, 38, 'ME'),(47, 51, 'ME')]
}),

("decime k Libia tns primita asi te habilitó pa llamada gratis ?", {
	'entities':  [(7, 8, 'ME'),(9, 14, 'ME'),(15, 18, 'ME'),(43, 45, 'ME')]
}),

("Emmm  si kers ja no te kiero molestr", {
	'entities':  [(9, 13, 'ME'),(23, 28, 'ME'),(29, 36, 'ME')]
}),

("mmm no me kiers molestar en k sentido prima?", {
	'entities':  [(10, 15, 'ME'),(28, 29, 'ME')]
}),

("No primo ta ben jajaj digo talves te aburris jaja", {
	'entities':  [(27, 33, 'ME')]
}),

("*claro xk ahi días k toy mal y aburrido y noc en kien desaugarme,,?*", {
	'entities':  [(7, 9, 'ME'),(19, 20, 'ME'),(21, 24, 'ME'),(42, 45, 'ME'),(49, 53, 'ME'),(54, 64, 'ME')]
}),

("asi k cual kier kosa te llamó primita?", {
	'entities':  [(4, 5, 'ME'),(11, 15, 'ME'),(16, 20, 'ME')]
}),

("no ay problema primo llama cuand kieras jaj para eso estan las hermans jajaja arreee k decia ja", {
	'entities':  [(3, 5, 'ME'),(27, 32, 'ME'),(33, 39, 'ME'),(63, 70, 'ME'),(78, 84, 'ME'),(85, 86, 'ME')]
}),

("holaaaa primita k hacias?", {
	'entities':  [(16, 17, 'ME')]
}),

("holaaaa ?", {
	'entities':  [(0, 7, 'ME')]
}),

("Ooola k hces???", {
	'entities':  [(0, 5, 'ME'),(6, 7, 'ME'),(8, 12, 'ME')]
}),

("naaa aka en mi kama toy re mal no sabes hoy me caí en el trab de un andamio k se rompió?", {
	'entities':  [(5, 8, 'ME'),(15, 19, 'ME'),(20, 23, 'ME'),(57, 61, 'ME'),(76, 77, 'ME')]
}),

("Se rompio k???primo", {
	'entities':  [(10, 11, 'ME')]
}),

("Ah pence k vos...oooh k onda fuiste al hospital???", {
	'entities':  [(3, 8, 'ME'),(9, 10, 'ME'),(17, 21, 'ME'),(22, 23, 'ME')]
}),

("nooo xk ya era justo ah la hora de salida de mi trab ...asi k me vine asi naaa más síento la espalda y tengo unas rajaduras en mi cuerpo y un poco hinchado la rodilla?", {
	'entities':  [(5, 7, 'ME'),(48, 52, 'ME'),(60, 61, 'ME'),(74, 78, 'ME')]
}),

("Ooooooh y xk no fuiste al hospital???and ahora eh", {
	'entities':  [(10, 12, 'ME'),(26, 34, 'MISC'),(37, 40, 'ME')]
}),

("voy maqana primita ah ver k onda?", {
	'entities':  [(4, 10, 'ME'),(26, 27, 'ME')]
}),

("Ooooh wueno primo widate eh dele =)", {
	'entities':  [(6, 11, 'ME'),(18, 24, 'ME'),(28, 32, 'ME')]
}),

("*holaaa primita k hacías ,,,?*", {
	'entities':  [(16, 17, 'ME')]
}),

("Oooola ja nada las milaness para amañan y vos???", {
	'entities':  [(19, 27, 'ME'),(33, 39, 'ME')]
}),

("mmm k ahi maqana?", {
	'entities':  [(4, 5, 'ME'),(10, 16, 'ME')]
}),

("Esta la feria y tego k ayudar con algo xk no voy a tar tengo kir al cole jajja", {
	'entities':  [(21, 22, 'ME'),(39, 41, 'ME'),(51, 54, 'ME'),(61, 64, 'ME'),(68, 72, 'MISC')]
}),

("*ah cierto k tu mami máqana tiene la feria nooo,,?*", {
	'entities':  [(11, 12, 'ME'),(21, 27, 'ME')]
}),

("Ooola prmix k hces??", {
	'entities':  [(0, 18, 'ME')]
}),

("*naaa aka en mi piesa re cansado mal,,y vs k hacías primita?*", {
	'entities':  [(6, 9, 'ME'),(16, 21, 'ME'),(40, 42, 'ME'),(43, 44, 'ME')]
}),

("Oooh disculpa esty hciend las milaness para mañana primix jaj", {
	'entities':  [(14, 18, 'ME'),(19, 25, 'ME'),(51, 57, 'ME')]
}),

("hola primita k hacías ?", {
	'entities':  [(13, 14, 'ME')]
}),

("Ooola y recien llego a funier jaja me vy a mi kasita jaja", {
	'entities':  [(23, 29, 'MISC'),(38, 40, 'ME'),(46, 52, 'ME')]
}),

("mmm taz en camino tonces prima noo!", {
	'entities':  [(4, 7, 'ME'),(18, 24, 'ME')]
}),

("holaaa primita cm taz espero k bien?", {
	'entities':  [(15, 17, 'ME'),(18, 21, 'ME'),(29, 30, 'ME')]
}),

("Ooola prim jaja ben ben en el cole y vos???", {
	'entities':  [(0, 5, 'ME'),(6, 10, 'ME'),(16, 19, 'ME'),(20, 23, 'ME'),(30, 34, 'MISC')]
}),

("ulaaaa primucha k onda?", {
	'entities':  [(0, 6, 'ME'),(7, 15, 'ME'),(16, 17, 'ME')]
}),

("che toy en bs as y noc si llegue pa el domingo no te aseguró nada?", {
	'entities':  [(4, 7, 'ME'),(11, 16, 'LOC'),(19, 22, 'ME'),(33, 35, 'ME')]
}),

("Quien sos jose ?", {
	'entities':  [(10, 14, 'PER')]
}),

("sip gato ?", {
	'entities':  [(0, 3, 'ME')]
}),

("noooo xk no llegó ????", {
	'entities':  [(6, 8, 'ME')]
}),

("gatonoooo", {
	'entities':  [(0, 9, 'ME')]
}),

("feliz dia de la dulzura primita espero k recibas muchos regalitos ?", {
	'entities':  [(39, 40, 'ME')]
}),

("Che el domingo se juega si o si contra la gloria . A las tres no faltes. Jugamos cancha de dieZ acá en mi barrio a un par de cuadras de mi casa", {
	'entities':  [(39, 48, 'ORG'),(106, 112, 'LOC'),(113, 143, 'LOC')]
}),

("oka che no te prendes pa venir ah jugar hoy ah las 6 y media?", {
	'entities':  [(22, 24, 'ME')]
}),

("*aka en mar del la cancha keda x tres arroyos y falucho,,,?*", {
	'entities':  [(1, 4, 'ME'),(8, 15, 'LOC'),(19, 25, 'ME'),(26, 30, 'ME'),(31, 32, 'ME'),(33, 55, 'LOC')]
}),

("la cancha se llama club nación?", {
	'entities':  [(3, 9, 'MISC'),(19, 30, 'ORG')]
}),

("oh pasa x mi ksa esta ahi ah las 6 y 15x", {
	'entities':  [(8, 9, 'ME'),(13, 16, 'ME')]
}),

("Resp?", {
	'entities':  [(0, 4, 'ME')]
}),

("Che hay que poner plata? No tengo un mang. Pa la cerveza no más", {
	'entities':  [(37, 41, 'ME'),(43, 45, 'ME')]
}),

("la cancha es 15 no más rata?", {
	'entities':  [(3, 9, 'MISC')]
}),

("dale venite derecho pa la ksa de rudy estate 6 y 20 aka ?", {
	'entities':  [(20, 22, 'ME'),(26, 29, 'ME'),(33, 37, 'PER'),(52, 55, 'ME')]
}),

("y x dond taz ?", {
	'entities':  [(2, 3, 'ME'),(9, 12, 'ME')]
}),

("dale k ya vamos salir pa aya", {
	'entities':  [(5, 6, 'ME'),(22, 24, 'ME'),(25, 28, 'ME')]
}),

("yyyy", {
	'entities':  [(0, 4, 'ME')]
}),

("Toy en tu casa ahí en la esquina", {
	'entities':  [(0, 3, 'ME'),(10, 14, 'MISC'),(19, 32, 'LOC')]
}),

("te dije venite pa la ksa de rudy", {
	'entities':  [(15, 17, 'ME'),(21, 24, 'ME'),(28, 32, 'PER')]
}),

("yyy x dond taz", {
	'entities':  [(0, 3, 'ME'),(4, 5, 'ME'),(6, 10, 'ME'),(11, 14, 'ME')]
}),

("ya me fui pa la cancha?", {
	'entities':  [(10, 12, 'ME'),(16, 22, 'MISC')]
}),

("Espera Toy rn colón", {
	'entities':  [(7, 10, 'ME'),(11, 13, 'ME'),(14, 19, 'LOC')]
}),

("Responde Toy yendo a la cancha", {
	'entities':  [(9, 12, 'ME')]
}),

("si agarrast colón dobla x tres arroyos ah la mano izkierda", {
	'entities':  [(3, 11, 'ME'),(12, 17, 'LOC'),(24, 25, 'ME'),(26, 38, 'LOC'),(50, 58, 'ME')]
}),

("Lokiyo todo bien??", {
	'entities':  [(0, 6, 'ME')]
}),

("*todo bien lokito,,?*", {
	'entities':  [(11, 17, 'ME')]
}),

("y aka toy en la ksa de tu primo papu?", {
	'entities':  [(2, 5, 'ME'),(6, 9, 'ME'),(16, 19, 'ME'),(32, 36, 'ME')]
}),

("Jajaja para van a invitar... No???? Jajaj che ranchito.. Mañana jugamos con los primos... A las 11 nos juntamos donde tomamos te acordas?? Hay... Y a las 12 jugamos.... Che... Avísale a rudy....", {
	'entities':  [(186, 190, 'PER')]
}),

("*dale okey ,,pero no me dijo naa ever xk me dijo k me iva llamar y también ah rudy?*", {
	'entities':  [(29, 32, 'ME'),(33, 37, 'PER'),(38, 40, 'ME'),(49, 50, 'ME'),(54, 57, 'ME'),(78, 82, 'PER')]
}),

("Sí me dijo r100 que te llamo.... Y.no contestabas...  Asi k te aviso yo... Llevado a rudi... Dale no fallen lokiyo...", {
	'entities':  [(11, 15, 'ME'),(58, 59, 'ME'),(75, 82, 'ME'),(85, 89, 'PER'),(108, 114, 'ME')]
}),

("*naaa y si yo toy en la mano con el celu todo el dia pero nadie me llamo,,,?*", {
	'entities':  [(14, 17, 'ME')]
}),

("pasame su num de ever asi yo le escribo ah ver k onda?", {
	'entities':  [(10, 13, 'ME'),(17, 21, 'PER'),(47, 48, 'ME')]
}),

("+542235510405 ever", {
	'entities':  [(14, 18, 'PER')]
}),

("*dale igual ever lo tenía su num de rudy ,,igual ya lo escribi pero no me resp?*", {
	'entities':  [(12, 16, 'PER'),(29, 32, 'ME'),(36, 40, 'PER'),(74, 78, 'ME')]
}),

("Que raro amx me llegan los msj", {
	'entities':  [(9, 12, 'ME')]
}),

("ehi jagamos hoy o no?", {
	'entities':  [(0, 3, 'ME'),(4, 11, 'ME')]
}),

("sip ya toy yendo pa aya?", {
	'entities':  [(0, 3, 'ME'),(7, 10, 'ME'),(17, 19, 'ME'),(20, 23, 'ME')]
}),

("Acá a santa Paula?", {
	'entities':  [(6, 17, 'LOC')]
}),

("*si paja vamos ah ir ,,aka recien me dijo ever k no se juega aka ,,?*", {
	'entities':  [(23, 26, 'ME'),(42, 46, 'PER'),(47, 48, 'ME'),(61, 64, 'ME')]
}),

("Bueno ! Vienen en moto o te paso a busca", {
	'entities':  [(35, 40, 'ME')]
}),

("ahora viene rudy y hablamos si venimos en moto o nos venís ah buscar?", {
	'entities':  [(12, 16, 'PER')]
}),

("Che trate la camiseta que te quedaste el otra vos", {
	'entities':  [(4, 9, 'ME')]
}),

("*che toy x tu barrio en la cancha ,,?*", {
	'entities':  [(5, 8, 'ME'),(9, 10, 'ME'),(11, 33, 'LOC')]
}),

("sip Bola vení k tamos en la cancha *", {
	'entities':  [(0, 3, 'ME'),(4, 8, 'ME'),(14, 15, 'ME'),(16, 21, 'ME'),(28, 34, 'MISC')]
}),

("Con quien tas ahí? Ya están los de la gloria", {
	'entities':  [(10, 13, 'ME'),(35, 44, 'ORG')]
}),

("no ahi nadie toy con un amigo dale veni?", {
	'entities':  [(13, 16, 'ME')]
}),

("Toy yendo a buscar a Pablo", {
	'entities':  [(0, 3, 'ME'),(21, 26, 'PER')]
}),

("dale x lo menos vení un toke xk nos tamos cagando de frío?", {
	'entities':  [(5, 6, 'ME'),(24, 28, 'ME'),(29, 31, 'ME'),(36, 41, 'ME')]
}),

("*k KERS gato ,,dond taz,,!*", {
	'entities':  [(1, 25, 'ME')]
}),

("*! Lee esto!  :(....                     Satanás se monta  y se rié de Jesús diciendo:", {
	'entities':  [(41, 48, 'PER'),(71, 76, 'PER')]
}),

("¿Que vas a hacer con ellos? Preguntó Jesus. ", {
	'entities':  [(37, 42, 'PER')]
}),

("Ah, me voy a divertir con ellos. Respondió Satanás. Les enseñaré como casarse y como engañar a su pareja para divorciarse, cómo odiar , a beber , a fumar, a drogarse  por supuesto , les enseñaré a inventar armas y bombas para que se maten y se destruyan entre sí. Realmente me voy a divertir! ", {
	'entities':  [(43, 50, 'PER'),(157, 165, 'DRUG')]
}),

("¿Y qué harás cuando te canses de ellos?  Le preguntó Jesus. ", {
	'entities':  [(53, 58, 'PER')]
}),

("Ah, los mataré. Dijo Satanás con la mirada llena de odio y orgullo.  ", {
	'entities':  [(21, 28, 'PER')]
}),

(" ¿Cuánto quieres por ellos? Preguntó Jesus. ", {
	'entities':  [(37, 42, 'PER')]
}),

("¿Cuánto? Preguntó nuevamente Jesus.  Satanás miró a Jesus y sarcásticamente respondió: ", {
	'entities':  [(29, 34, 'PER'),(37, 44, 'PER'),(52, 57, 'PER')]
}),

]

def build_tags(tags_data):
	tags = list([])
	for entity_match in tags_data:
		(i_pos, e_pos, tag) = entity_match
		tags.append({
			'entity': tag,
			'i_pos': i_pos,
			'e_pos': e_pos
		})
	return tags

def get_training_data_examples_list():
	examples_list = list([])
	for sentence, ents in TRAIN_DATA:
		examples_list.append({
			'sentence': sentence,
			'type': 'SIMPLE',
			'tags': build_tags(ents['entities'])
		})
	return examples_list
