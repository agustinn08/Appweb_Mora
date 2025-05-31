from flask import Flask, request, render_template_string
import pandas as pd
import os

app = Flask(__name__)

form_html = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Subir Archivos Excel</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f0f2f5;
      margin: 0;
      padding: 20px;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      min-height: 100vh;
    }
    .container {
      background: white;
      padding: 30px 40px;
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      max-width: 500px;
      width: 100%;
    }
    h1 {
      color: #333;
      text-align: center;
      margin-bottom: 30px;
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 15px;
      margin-bottom: 5px;
      color: #555;
    }
    input[type="file"] {
      width: 100%;
      padding: 6px;
      border-radius: 5px;
      border: 1px solid #ccc;
    }
    input[type="submit"] {
      margin-top: 25px;
      width: 100%;
      background-color: #4CAF50;
      border: none;
      color: white;
      padding: 12px 0;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
    input[type="submit"]:hover {
      background-color: #45a049;
    }
    .footer {
      margin-top: 15px;
      font-size: 0.9em;
      text-align: center;
      color: #888;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Subí dos archivos Excel</h1>
    <form method="post" enctype="multipart/form-data">
      <label for="archivo1">Archivo 1</label>
      <input type="file" name="archivo1" id="archivo1" required />
      <label for="archivo2">Archivo 2</label>
      <input type="file" name="archivo2" id="archivo2" required />
      <input type="submit" value="Comparar" />
    </form>
    <div class="footer">
      <p>Solo archivos Excel (.xls o .xlsx) con columna "Nro Orden" o "N° Orden".</p>
    </div>
  </div>
</body>
</html>
'''

result_html = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Resultados</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f0f2f5;
      margin: 0;
      padding: 20px;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      min-height: 100vh;
    }
    .container {
      background: white;
      padding: 30px 40px;
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      max-width: 600px;
      width: 100%;
      color: #333;
    }
    h1 {
      text-align: center;
      margin-bottom: 30px;
    }
    h2 {
      border-bottom: 2px solid #4CAF50;
      padding-bottom: 5px;
      color: #4CAF50;
    }
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      background: #e8f5e9;
      margin: 5px 0;
      padding: 8px 12px;
      border-radius: 6px;
      font-weight: 600;
      color: #2e7d32;
    }
    p {
      font-style: italic;
      color: #888;
    }
    a {
      display: inline-block;
      margin-top: 30px;
      padding: 12px 24px;
      background-color: #4CAF50;
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: bold;
      transition: background-color 0.3s ease;
    }
    a:hover {
      background-color: #45a049;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>IDs únicos que no se repiten en ambos archivos</h1>

    <h2>IDs solo en Archivo 1:</h2>
    {% if ids_solo_1 %}
      <ul>
      {% for id in ids_solo_1 %}
        <li>{{ id }}</li>
      {% endfor %}
      </ul>
    {% else %}
      <p>No hay IDs únicos en Archivo 1.</p>
    {% endif %}

    <h2>IDs solo en Archivo 2:</h2>
    {% if ids_solo_2 %}
      <ul>
      {% for id in ids_solo_2 %}
        <li>{{ id }}</li>
      {% endfor %}
      </ul>
    {% else %}
      <p>No hay IDs únicos en Archivo 2.</p>
    {% endif %}

    <a href="/">Volver</a>
  </div>
</body>
</html>
'''

# Tu HTML se mantiene igual (no lo repito aquí para ahorrar espacio)

# Función para leer archivo Excel con el engine correcto
def leer_excel_seguro(file):
    extension = os.path.splitext(file.filename)[-1].lower()
    file.seek(0)

    if extension == '.xls':
        try:
            file.seek(0)
            return pd.read_excel(file, sheet_name=None, engine='xlrd')
        except Exception as e:
            raise ValueError(f"No se pudo leer el archivo .xls. Detalle: {e}")
    elif extension == '.xlsx':
        try:
            file.seek(0)
            return pd.read_excel(file, sheet_name=None, engine='openpyxl')
        except Exception as e:
            raise ValueError(f"No se pudo leer el archivo .xlsx. Detalle: {e}")
    else:
        raise ValueError("Extensión no soportada. Use archivos .xls o .xlsx")
    
# Función para comparar los archivos por el nombre de las hojas
def comparar_archivos(df1, df2):
    resultados = []

    hojas1 = set(df1.keys())
    hojas2 = set(df2.keys())

    hojas_comunes = hojas1 & hojas2

    for hoja in hojas_comunes:
        tabla1 = df1[hoja].fillna("").astype(str)
        tabla2 = df2[hoja].fillna("").astype(str)

        iguales = tabla1.equals(tabla2)

        resultados.append((hoja, "✅ Iguales" if iguales else "❌ Diferentes"))

    hojas_solo1 = hojas1 - hojas2
    hojas_solo2 = hojas2 - hojas1

    for hoja in hojas_solo1:
        resultados.append((hoja, "⚠️ Solo en el archivo 1"))
    for hoja in hojas_solo2:
        resultados.append((hoja, "⚠️ Solo en el archivo 2"))

    return resultados

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje_error = None
    resultados = []

    if request.method == 'POST':
        archivo1 = request.files['archivo1']
        archivo2 = request.files['archivo2']

        try:
            excel1 = pd.read_excel(archivo1, sheet_name=None, engine='openpyxl')
        except Exception:
            archivo1.seek(0)
            excel1 = pd.read_excel(archivo1, sheet_name=None, engine='xlrd')

        try:
            archivo2.seek(0)
            excel2 = pd.read_excel(archivo2, sheet_name=None, engine='openpyxl')
        except Exception:
            archivo2.seek(0)
            excel2 = pd.read_excel(archivo2, sheet_name=None, engine='xlrd')

        try:
            resultados = comparar_archivos(excel1, excel2)
        except Exception as e:
            mensaje_error = f"Error al comparar archivos: {str(e)}"

    return render_template('index.html', resultados=resultados, error=mensaje_error)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)