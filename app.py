from flask import Flask, render_template, request, jsonify, send_file
import json
import sqlite3
from datetime import datetime
import os
import pdfkit
import xlsxwriter
from io import BytesIO

app = Flask(__name__)

@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value or '{}')
    except:
        return {}

def init_db():
    conn = sqlite3.connect('tests.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  status TEXT,
                  timestamp TEXT,
                  categories TEXT,
                  steps TEXT,
                  environment TEXT,
                  custom_fields TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tests', methods=['GET'])
def get_tests():
    conn = sqlite3.connect('tests.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tests')
    tests = c.fetchall()
    conn.close()
    return jsonify(tests)

@app.route('/api/tests', methods=['POST'])
def add_test():
    data = request.json
    conn = sqlite3.connect('tests.db')
    c = conn.cursor()
    c.execute('''INSERT INTO tests 
                 (name, description, status, timestamp, categories, steps, environment, custom_fields)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['name'], data['description'], data['status'],
               datetime.now().isoformat(), json.dumps(data['categories']),
               json.dumps(data['steps']), json.dumps(data['environment']),
               json.dumps(data.get('custom_fields', {}))))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/export/pdf')
def export_pdf():
    # Configurar opções do PDF
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    
    # Gerar HTML com os dados
    conn = sqlite3.connect('tests.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tests')
    tests = c.fetchall()
    conn.close()
    
    html = render_template('pdf_template.html', tests=tests)
    
    # Criar PDF
    pdf = pdfkit.from_string(html, False, options=options)
    
    # Retornar o arquivo
    stream = BytesIO(pdf)
    stream.seek(0)
    return send_file(
        stream,
        download_name=f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

@app.route('/export/excel')
def export_excel():
    # Criar arquivo Excel em memória
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Estilos
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'bg_color': '#4B5563',
        'font_color': 'white'
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#E5E7EB',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Cabeçalhos
    headers = ['ID', 'Nome', 'Descrição', 'Status', 'Data/Hora', 'Categorias', 'Steps', 'Ambiente', 'Campos Personalizados']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
        worksheet.set_column(col, col, 20)  # Largura da coluna
    
    # Dados
    conn = sqlite3.connect('tests.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tests')
    tests = c.fetchall()
    conn.close()
    
    for row, test in enumerate(tests, start=1):
        for col, value in enumerate(test):
            if col in [5, 6, 7, 8]:  # Campos JSON
                try:
                    parsed = json.loads(value if value else '{}')
                    value = json.dumps(parsed, indent=2, ensure_ascii=False)
                except:
                    pass
            worksheet.write(row, col, value, cell_format)
    
    workbook.close()
    
    # Retornar o arquivo
    output.seek(0)
    return send_file(
        output,
        download_name=f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 