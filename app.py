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
def leer_excel(file):
    filename = file.filename
    extension = os.path.splitext(filename)[-1].lower()

    if extension == '.xls':
        return pd.read_excel(file, engine='xlrd')
    elif extension == '.xlsx':
        return pd.read_excel(file, engine='openpyxl')
    else:
        raise ValueError("El archivo debe ser .xls o .xlsx")

def encontrar_columna_id(columnas):
    posibles = ['nro', 'n°', 'n*', 'numero']
    for col in columnas:
        col_lower = col.lower()
        if 'orden' in col_lower and any(p in col_lower for p in posibles):
            return col
    return None

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        archivo1 = request.files.get('archivo1')
        archivo2 = request.files.get('archivo2')

        if not archivo1 or not archivo2:
            return "Por favor, subí los dos archivos"

        try:
            df1 = leer_excel(archivo1)
            df2 = leer_excel(archivo2)
        except Exception as e:
            return f"Error al leer los archivos: {e}"

        columna_id_1 = encontrar_columna_id(df1.columns)
        columna_id_2 = encontrar_columna_id(df2.columns)

        if not columna_id_1 or not columna_id_2:
            return "Error: No se encontró una columna de Orden válida en uno o ambos archivos."

        ids1 = set(df1[columna_id_1].dropna().astype(str))
        ids2 = set(df2[columna_id_2].dropna().astype(str))

        ids_solo_1 = sorted(ids1 - ids2)
        ids_solo_2 = sorted(ids2 - ids1)

        return render_template_string(result_html, ids_solo_1=ids_solo_1, ids_solo_2=ids_solo_2)

    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(debug=True)