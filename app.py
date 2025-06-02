from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

# Inicializar Firebase
cred = credentials.Certificate("appzoo-e0319-firebase-adminsdk-fbsvc-23c0864789.json")
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



# 🔻 Esto debe estar AL FINAL DEL ARCHIVO
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
