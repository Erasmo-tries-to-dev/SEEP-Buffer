import os
import random
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Habilitar CORS para permitir peticiones seguras
CORS(app)

# Configurar Rate Limiting para proteger el servidor de peticiones masivas
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Diccionario en memoria: { "1234": [ {entrega1}, {entrega2} ] }
buzones = {}


@app.route("/crear_buzon", methods=["POST"])
@limiter.limit("5 per minute")
def crear_buzon():
    """El docente pide abrir una sesión."""
    pin = str(random.randint(1000, 9999))
    while pin in buzones:
        pin = str(random.randint(1000, 9999))

    buzones[pin] = []
    return jsonify({"pin": pin})


@app.route("/entregar", methods=["POST"])
@limiter.limit("15 per minute")  # Límite por IP para evitar spam de un mismo alumno
def entregar():
    """El alumno envía su parcial."""
    pin = request.form.get("pin")
    if pin not in buzones:
        return "PIN inválido o buzón cerrado", 404

    archivo = request.files.get("archivo")

    # Validación de seguridad: evitar cuelgues por envíos vacíos
    if not archivo or archivo.filename == "":
        return "No se adjuntó ningún archivo", 400

    # Empaquetamos la entrega (Convertimos el binario del archivo a texto Base64)
    entrega = {
        "id_entrega": str(
            random.randint(100000, 999999)
        ),  # ID único para confirmar recepción
        "apellidos": request.form.get("apellidos"),
        "nombres": request.form.get("nombres"),
        "legajo": request.form.get("legajo"),
        "nombre_archivo": archivo.filename,
        "contenido_b64": base64.b64encode(archivo.read()).decode("utf-8"),
    }

    buzones[pin].append(entrega)
    return "Examen recibido en la nube", 200


@app.route("/descargar/<pin>", methods=["GET"])
def descargar(pin):
    """El docente consulta si hay parciales nuevos."""
    if pin not in buzones:
        return jsonify({"error": "Buzón no existe"}), 404

    return jsonify(buzones[pin])


@app.route("/confirmar_recepcion/<pin>/<id_entrega>", methods=["POST"])
def confirmar_recepcion(pin, id_entrega):
    """El docente avisa que ya guardó el parcial en su disco, podemos borrarlo de la nube."""
    if pin in buzones:
        # Filtramos la lista para eliminar la entrega que ya fue descargada
        buzones[pin] = [e for e in buzones[pin] if e["id_entrega"] != id_entrega]
    return "OK", 200


@app.route("/cerrar_buzon/<pin>", methods=["DELETE"])
def cerrar_buzon(pin):
    """El docente avisa que terminó el examen, liberando la RAM del servidor."""
    if pin in buzones:
        del buzones[pin]
        return "Buzón cerrado y memoria liberada", 200
    return "Buzón no encontrado", 404


if __name__ == "__main__":
    # Render inyecta el puerto dinámicamente a través de variables de entorno
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
