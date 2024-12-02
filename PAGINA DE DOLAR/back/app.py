from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS  # Importa CORS
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests,json,os

class Moneda(ABC):
    @abstractmethod
    def __init__ (self, nombre):
        self.nombre = nombre
    @abstractmethod
    def cargar_nombre(self, nombre):
        self.nombre = nombre
    @abstractmethod      
    def mostrar_nombre(self):
        return self.nombre

class Tipo(Moneda):
    def __init__ (self, moneda, tipo):
        super().__init__(moneda)
        self.cargar_tipo(tipo)
        self.cotizaciones = []
    
    def cargar_nombre(self, nombre):
        return super().cargar_nombre(nombre)

    def cargar_tipo(self,tipo):
        
        self.tipo = tipo
    def mostrar_tipo(self):
        return self.tipo
    def mostrar_nombre(self):
        return super().mostrar_nombre()
    
    def __str__(self):
        if self.cotizaciones:
            return f"La moneda es: {self.mostrar_nombre()} {self.mostrar_tipo()} {self.cotizaciones[len(self.cotizaciones)-1]}"
        else:
            return f"La moneda es: {self.nombre} {self.tipo} sin cotizaciones"
    def cargarcotizacion(self,cotizacion):
        self.cotizaciones.append(cotizacion)
    def mostrarcotizaciones(self):
        return self.cotizaciones
    def ultimacotizacion(self):
        return self.cotizaciones[-1]

    def json_actual(self):
        return {'moneda': self.mostrar_nombre(), 
            'tipo': self.mostrar_tipo(),
            'venta': self.ultimacotizacion().mostrarventa(), 
            'compra': self.ultimacotizacion().mostrarcompra(),
            'fecha': self.ultimacotizacion().mostrarfecha()
            }
    
class Cotizacion:
    def __init__(self,venta,compra,fecha):
        self.cargarventa(venta)
        self.cargarcompra(compra)
        self.cargarfecha(fecha)
    def cargarcompra(self,compra):
        self.compra = compra
    def cargarventa(self,venta):
        self.venta = venta
    def cargarfecha(self,fecha):
        self.fecha = fecha
    def mostrarcompra(self):
        return self.compra
    def mostrarventa(self):
        return self.venta
    def mostrarfecha(self):
        return self.fecha
    def __str__(self):
        return f"El precio de compra es: {self.mostrarcompra()}, el precio de venta es: {self.mostrarventa()} y la fecha de actualizacion es {self.mostrarfecha()}"

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}}) # Activa CORS en toda la aplicación

# Ruta del archivo JSON
ruta_cotizaciones_json = os.path.join(os.path.dirname(__file__), "cotizaciones.json")
ruta_historico_json = os.path.join(os.path.dirname(__file__), "historico.json")


# Ruta para servir el archivo JSON directamente
@app.route('/static/cotizaciones.json')
def servir_json():
    return send_from_directory('.', 'cotizaciones.json')

# Función para obtener y guardar las cotizaciones
def obtener_y_guardar_cotizaciones():
    try:
        # Verifica si el archivo JSON existe
        if not os.path.exists(ruta_cotizaciones_json):
            return obtener_datos_api_y_guardar()

        # Si el archivo JSON existe, trae la fecha de la última actualización
        with open(ruta_cotizaciones_json, "r", encoding="utf-8") as archivo_cotizacion:
            data = json.load(archivo_cotizacion)
            ultima_actualizacion = datetime.fromisoformat(data.get("ultima_actualizacion", "1970-01-01T00:00:00"))
        
        # Compara la fecha de actualizacion con la fecha actual
        # Si han pasado más de 5 minutos desde la última actualización, actualizamos los datos
        if datetime.now() - ultima_actualizacion > timedelta(minutes=5):
            return obtener_datos_api_y_guardar()

        # Si no han pasado más de 5 minutos, devuelve los datos almacenados
        return data

    except Exception as e:
        print(f"Error al manejar el archivo JSON: {e}")
        return {"error": "Error al obtener datos"}, 500

# Función para obtener datos de las cotizaciones actuales de la API y guardar en el archivo JSON
def obtener_datos_api_y_guardar():
    try:
        # Realiza la primer solicitud a la API para obtener los datos de todos los dolares
        response = requests.get("https://dolarapi.com/v1/dolares")
        response.raise_for_status()
        listamonedas = []
        for cambio in response.json():
            moneda=Tipo(cambio['moneda'],cambio['nombre'])
            cotizacion=Cotizacion(cambio['venta'],cambio['compra'],cambio['fechaActualizacion'])
            moneda.cargarcotizacion(cotizacion)
            listamonedas.append(moneda)

        # Realiza una segunda solicitud a la API para obtener los datos de cotizaciones empezando en 1 para no repetir dolar oficial
        response2 = requests.get("https://dolarapi.com/v1/cotizaciones")
        response2.raise_for_status()
        for cambio in response2.json()[1:]:
            moneda=Tipo(cambio['moneda'],cambio['nombre'])
            cotizacion=Cotizacion(cambio['venta'],cambio['compra'],cambio['fechaActualizacion'])
            moneda.cargarcotizacion(cotizacion)
            listamonedas.append(moneda)
        
        cotizaciones=[moneda.json_actual() for moneda in listamonedas]
        
        
        # Guarda los datos en el archivo JSON con codificación UTF-8
        with open(ruta_cotizaciones_json, "w", encoding="utf-8") as archivo_cotizacion:
            json.dump({"cotizaciones": cotizaciones, "ultima_actualizacion": datetime.now().isoformat()},
                    archivo_cotizacion, ensure_ascii=False, indent=4)

        return {"cotizaciones": cotizaciones, "ultima_actualizacion": datetime.now().isoformat()}

    except requests.RequestException as e:
        print(f"Error al obtener los datos de la API: {e}")
        return {"error": "Error al obtener datos de la API"}, 500
# Funcion para traer los datos historicos de cada casa y guardarlos en el json
def obtener_datos_historico_api():
    tipos_cambios = ['oficial', 'blue', 'bolsa', 'contadoconliqui', 'cripto', 'mayorista', 'solidario', 'turista']
    historico = []
    #trae los datos de cada casa definidas arriba y los guarda en el historico
    for cambio in tipos_cambios:
        url = f"https://api.argentinadatos.com/v1/cotizaciones/dolares/{cambio}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()
            historico.append({
                "tipo": cambio,
                "datos": datos
            })
        except requests.RequestException as e:
            print(f"Error al obtener datos para {cambio}: {e}")
    
    # Agregar la última actualización al hsitorico
    historico.append({
        "ultima_actualizacion": datetime.now().isoformat()
    })
    
    # Guardar en el archivo JSON historico.json
    with open(ruta_historico_json, "w", encoding="utf-8") as archivo_historico:
        json.dump(historico, archivo_historico, ensure_ascii=False, indent=4)
    
    return historico

#funcion para revisar si el historico esta actualizado y traerlo
def revisar_historico():
    try:
        # Verificar si el archivo historico.json existe
        if not os.path.exists(ruta_historico_json):
            return obtener_datos_historico_api()

        # Leer el archivo json existente y trae la ultima fecha de actualizacion
        with open(ruta_historico_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            ultima_actualizacion = datetime.fromisoformat(data[-1].get("ultima_actualizacion", "1970-01-01T00:00:00"))

        # Compara la fecha de actualizacion con la fecha actual
        # Si han pasado más de 24 horas se actualiza
        if datetime.now() - ultima_actualizacion > timedelta(hours=24):
            return obtener_datos_historico_api()

        return data

    except Exception as e:
        print(f"Error al manejar el archivo JSON: {e}")
        return {"error": "Error al obtener datos"}, 500

def buscar_historico_fecha_cambio(tipo_dolar, fecha_buscada):
    historico = revisar_historico()
    
    # Buscar el tipo de cambio y fecha específica para retornarlo en forma de diccionario
    for registro in historico:
        if registro.get("tipo") == tipo_dolar:
            for entrada in registro["datos"]:
                if entrada.get("fecha") == fecha_buscada:
                    return {
                        "compra": entrada.get("compra"),
                        "venta": entrada.get("venta"),
                        "fecha": entrada.get("fecha")
                    }
    
    # Si no se encuentra, retornar None
    return None

#funcion que devuelve los datos para graficar el historico
def obtener_historico(tipo_dolar, fecha_inicio, fecha_fin, valores):
    fechainicial = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fechafinal = datetime.strptime(fecha_fin, "%Y-%m-%d")
    delta_dias = (fechafinal - fechainicial) / (valores - 1)
    datosgrafica = []
    
    for cont in range(valores):
        fecha_actual = fechainicial + delta_dias * cont
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        datos_cambio = buscar_historico_fecha_cambio(tipo_dolar, fecha_str)
        if datos_cambio:
            datosgrafica.append(datos_cambio)
    
    return jsonify(datosgrafica)

#funcion que arma los datos de forma tal que se vean mejor para mandarlos por mail
def formatear_datos_historico_a_mail(tipo_dolar, fecha_inicio, fecha_fin, valores):
    fechainicial = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fechafinal = datetime.strptime(fecha_fin, "%Y-%m-%d")
    delta_dias = (fechafinal - fechainicial) / (valores - 1)
    datos_historicos = []
    
    for cont in range(valores):
        fecha_actual = fechainicial + delta_dias * cont
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        datos_cambio = buscar_historico_fecha_cambio(tipo_dolar, fecha_str)
        if datos_cambio:
            datos_historicos.append(datos_cambio)
    # Armamos la filas de titulos
    mail = f'Cotizacion para el Dolar {tipo_dolar}\n'
    mail += f"{'Fecha':<20} | {'Compra':<10} | {'Venta':<10}\n"
    mail += ("-" * 40+'\n')
    # Llenamos cada fila con los datos del JSON
    for dato in datos_historicos:
        mail+=f"{dato['fecha']:<20} | {dato['compra']:<10} | {dato['venta']:<10}\n"
    return mail

#ruta para pedir el historico utilizando get con variables en la URL
@app.route('/api/historico/<tipo_dolar>/<fecha_inicio>/<fecha_fin>/<int:valores>')
def api_historico(tipo_dolar, fecha_inicio, fecha_fin, valores):
    return obtener_historico(tipo_dolar, fecha_inicio, fecha_fin, valores)


#ruta para traer las cotizaciones actuales
@app.route('/api/cotizaciones', methods=['GET'])
def obtener_cotizaciones():
    data = obtener_y_guardar_cotizaciones()
    return jsonify(data)

#ruta para enviar formulario de contacto
@app.route('/api/contacto/', methods=['POST', 'OPTIONS'])
def contacto():
    if request.method == 'OPTIONS':
        # Responde a la solicitud preflight con un estado 200 y headers de CORS
        response = app.response_class(status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Procesa la solicitud POST recibida
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400
    
    #Trabaja los datos del post. Agrega el mensaje y el mail de la persona que lo envia
    #Por si es necesario responder ademas del reply automatico en caso de falla
    mensaje_enviar=f'{data['mensaje']} \n'
    mensaje_enviar+=f'Responder al mail:{data['email']}'
    #print(f"Contacto recibido: {data}") #revisar informacion de contacto
    #Aca pusimos un mail nuestro como si fuera el mail de contacto para recibir la informacion de contacto de la pagina web
    mail_enviar(data['nombre'],data['apellido'],'tobianfuso@gmail.com',mensaje_enviar,data['email'])
    return jsonify({"status": "Contacto recibido", "data": data}), 200

#Ruta para enviar todas las cotizaciones actuales por mail
@app.route('/api/cotizaciones/email/', methods=['POST', 'OPTIONS'])
def cotizaciones_email():
    if request.method == 'OPTIONS':
        # Responde a la solicitud preflight con un estado 200 y headers de CORS
        response = app.response_class(status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Procesa la solicitud POST recibida
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    #Trabaja los datos del post
    #Trae las cotizaciones actuales y la formatea de una manera mas ordenada para enviarlas por mail
    cotizaciones=obtener_y_guardar_cotizaciones()
    cotizaciones_enviar=f'Cotizaciones actuales: \n'
    cotizaciones_enviar+=f'{'Moneda':<15} | {'Tipo':<15} | {'Compra':<5} | {'Venta':<5} | {'Fecha':<25}\n'
    for cotizacion in cotizaciones['cotizaciones']:
        cotizaciones_enviar+=f'{cotizacion['moneda']} | {cotizacion['tipo']} | {cotizacion['compra']} | {cotizacion['venta']} | {cotizacion['fecha']}\n'
    #print(cotizaciones_enviar) #revisar cotizaciones enviar
    mail_enviar(data['nombre'],data['apellido'],data['email'],cotizaciones_enviar)
    return jsonify({"status": "Cotizaciones recibias", "data": data}), 200

@app.route('/api/historico/email/', methods=['POST', 'OPTIONS'])
def historico_email():
    if request.method == 'OPTIONS':
        # Responde a la solicitud preflight con un estado 200 y headers de CORS
        response = app.response_class(status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Procesa la solicitud POST recibida
    informacion = request.get_json()
    if not informacion:
        return jsonify({"error": "No se proporcionaron datos"}), 400
    #Conseguimos y formateamos los datos del historico para enviarlos por mail de manera mas ordenada en el mail
    historico=formatear_datos_historico_a_mail(informacion['dolar'],informacion['fechainicio'],informacion['fechafin'],informacion['valores'])
    #print(historico) #revisar historico a enviar
    mail_enviar(informacion['nombre'],informacion['apellido'],informacion['email'],historico)
    return jsonify({"status": "Historico recibido", "data": informacion}), 200

'''
Funcion para enviar la informacion necesaria por mail
Tiene 5 parametros, nombre, apellido a rellenar,mail destinatario para enviarlo ,
informacion que se quiere enviar por mail, mail al que se le debe devolver la respuesta por defecto uno nuestro
ya que enviamos mail a una persona externa (cotizaciones,historico)
'''
def mail_enviar(nombre,apellido,email,informacion_enviar,reply='tobianfuso@gmail.com'):
    data = {
        'service_id': 'service_tq6wwwh',
        'template_id': 'template_mx23lgn',
        'user_id': 'kPneVDwcNx4UK_xyp',
        'accessToken': 'vs9nufahysZPpyZwuUS9L',
        'template_params': {
            'from_name': 'Pagina Cotizaciones',
            'to_name': f'{nombre} {apellido}',
            'to_mail':f'{email}',
            'message': f'{informacion_enviar}',
            'reply_to':f'{reply}'
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://your-website.com',  
        'Referer': 'https://your-website.com/'
    }

    try:
        response = requests.post(
            'https://api.emailjs.com/api/v1.0/email/send',
            data=json.dumps(data),
            headers=headers
        )
        response.raise_for_status()
        print('Your mail is sent!')
    except requests.exceptions.RequestException as error:
        print(f'Hubo un error ... {error}')
        if error.response is not None:
            print(error.response.text)



#Ejecuta la app flask

if __name__ == '__main__':
    app.run(debug=True)


