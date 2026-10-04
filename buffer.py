from flask import Flask, request, jsonify
import random
import base64

app = Flask(__name__)

# Diccionario en memoria: { "1234": [ {entrega1}, {entrega2} ] }
buzones = {}


@app.route("/crear_buzon", methods=["POST"])
def crear_buzon():
    """El docente pide abrir una sesión."""
    pin = str(random.randint(1000, 9999))
    while pin in buzones:
        pin = str(random.randint(1000, 9999))

    buzones[pin] = []
    return jsonify({"pin": pin})


@app.route("/entregar", methods=["POST"])
def entregar():
    """El alumno envía su parcial."""
    pin = request.form.get("pin")
    if pin not in buzones:
        return "PIN inválido o buzón cerrado", 404

    archivo = request.files.get("archivo")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
