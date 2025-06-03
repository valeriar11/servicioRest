from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

import os, json

json_cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
cred = credentials.Certificate(json.loads(json_cred))
firebase_admin.initialize_app(cred)
db = firestore.client()

# Ruta de prueba
@app.route('/')
def inicio():
    return 'Servidor Flask conectado a Firebase'

# Ruta para consultar especie
@app.route('/especies/<id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    try:
        doc = db.collection('especies').document(id_producto).get()
        if not doc.exists:
            return jsonify({'error': 'Producto no encontrado'}), 404

        data = doc.to_dict()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Ruta para contar animales con especie
@app.route('/contar_animales', methods=['POST'])
def contar_animales():
    data = request.get_json()
    nombre_especie = data.get('especie')

    try:
        animales_ref = db.collection('animales')
        query = animales_ref.where('especie', '==', nombre_especie)
        resultados = query.stream()
        contador = sum(1 for _ in resultados)

        return jsonify({
            'especie': nombre_especie,
            'cantidad': contador
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/especies', methods=['GET'])
def listar_especies():
    try:
        docs = db.collection('especies').stream()
        nombres = [doc.to_dict().get('nombre') for doc in docs if 'nombre' in doc.to_dict()]
        return jsonify({'especies': nombres})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/promedio_edad', methods=['POST'])
def promedio_edad():
    data = request.get_json()
    especie_nombre = data.get('especie')

    if not especie_nombre:
        return jsonify({'error': 'Falta el nombre de la especie'}), 400

    try:
        animales_ref = db.collection('animales')
        query = animales_ref.where('especie', '==', especie_nombre)
        docs = query.stream()

        edades = [doc.to_dict().get('edad', 0) for doc in docs]
        if not edades:
            return jsonify({'especie': especie_nombre, 'promedioEdad': 0})

        promedio = sum(edades) / len(edades)
        return jsonify({
            'especie': especie_nombre,
            'promedioEdad': round(promedio, 2)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 🔻 Esto debe estar AL FINAL DEL ARCHIVO
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
