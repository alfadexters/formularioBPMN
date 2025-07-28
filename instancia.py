# instancia.py

# Importa una función adicional de Flask
from flask import Flask, request, jsonify, send_from_directory
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CAMUNDA_WEBHOOK_URL = "https://jfk-1.connectors.camunda.io/373d66fc-5019-4486-bcee-2a1172b702eb/inbound/formulario_externo"

# --- NUEVA RUTA PARA SERVIR EL FORMULARIO ---
# Esta ruta cargará el archivo HTML cuando alguien visite la URL principal.
@app.route('/')
def serve_form():
    # Devuelve el archivo 'formulario.html' desde el directorio actual ('.')
    return send_from_directory('.', 'formulario.html')

# --- RUTA EXISTENTE DEL API (SIN CAMBIOS) ---
@app.route("/enviar-a-camunda", methods=["POST"])
def enviar():
    datos_entrada = request.json or {}
    
    factura_data_uri = datos_entrada.get("factura", "")
    factura_base64_pura = factura_data_uri.split(',')[-1] if ',' in factura_data_uri else factura_data_uri

    datos_con_action = {
        "action": "start",
        "inicio_externo": "si",
        "cedula": datos_entrada.get("cedula"),
        "nombre": datos_entrada.get("nombre"),
        "email": datos_entrada.get("email"),
        "monto": datos_entrada.get("monto"),
        "factura": factura_base64_pura 
    }

    try:
        response = requests.post(CAMUNDA_WEBHOOK_URL, json=datos_con_action)
        return jsonify({"status": response.status_code, "response": response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)