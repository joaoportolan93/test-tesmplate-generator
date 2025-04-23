from flask import Flask, render_template, request, jsonify, send_file
import json
import sqlite3
from datetime import datetime
import os
import pdfkit
import xlsxwriter
from io import BytesIO
import base64

app = Flask(__name__)

# Configurar diretório para upload de imagens
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value or '{}')
    except:
        return {}

def get_db():
    conn = sqlite3.connect('tests.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db()
        c = conn.cursor()
        # Verificar se a coluna image_data já existe
        c.execute("PRAGMA table_info(tests)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'image_data' not in columns:
            # Criar nova tabela com a coluna de imagem
            c.execute('''CREATE TABLE IF NOT EXISTS tests_new
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          description TEXT,
                          status TEXT,
                          timestamp TEXT,
                          categories TEXT,
                          steps TEXT,
                          environment TEXT,
                          custom_fields TEXT,
                          image_data TEXT)''')
            
            # Copiar dados da tabela antiga para a nova
            c.execute('''INSERT INTO tests_new 
                        (id, name, description, status, timestamp, categories, steps, environment, custom_fields)
                        SELECT id, name, description, status, timestamp, categories, steps, environment, custom_fields
                        FROM tests''')
            
            # Remover tabela antiga e renomear a nova
            c.execute('DROP TABLE IF EXISTS tests')
            c.execute('ALTER TABLE tests_new RENAME TO tests')
        else:
            # Se a coluna já existe, apenas criar a tabela normalmente
            c.execute('''CREATE TABLE IF NOT EXISTS tests
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          description TEXT,
                          status TEXT,
                          timestamp TEXT,
                          categories TEXT,
                          steps TEXT,
                          environment TEXT,
                          custom_fields TEXT,
                          image_data TEXT)''')
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        raise
    finally:
        conn.close()

def get_tests(test_ids=None):
    conn = get_db()
    c = conn.cursor()
    try:
        if test_ids:
            placeholders = ','.join('?' * len(test_ids))
            c.execute(f'SELECT * FROM tests WHERE id IN ({placeholders})', test_ids)
        else:
            c.execute('SELECT * FROM tests')
        
        tests = []
        for row in c.fetchall():
            test = dict(row)
            # Decodificar campos JSON
            for field in ['categories', 'steps', 'environment', 'custom_fields']:
                try:
                    test[field] = json.loads(test[field] or '{}')
                except:
                    test[field] = {}
            tests.append(test)
        return tests
    finally:
        conn.close()

# Inicializa o banco de dados ao carregar o aplicativo
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tests', methods=['GET'])
def get_all_tests():
    try:
        tests = get_tests()
        return jsonify(tests)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tests', methods=['POST'])
def add_test():
    try:
        data = request.json
        image_data = data.get('image_data', None)
        
        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO tests 
                     (name, description, status, timestamp, categories, steps, 
                      environment, custom_fields, image_data)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['name'], data['description'], data['status'],
                   datetime.now().isoformat(), json.dumps(data['categories']),
                   json.dumps(data['steps']), json.dumps(data['environment']),
                   json.dumps(data.get('custom_fields', {})), image_data))
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        return jsonify({"status": "success", "id": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tests/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM tests WHERE id = ?', (test_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Teste deletado com sucesso"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/export/pdf')
def export_pdf():
    try:
        test_ids = request.args.getlist('ids[]', type=int)
        tests = get_tests(test_ids)
        
        if not tests:
            return "Nenhum teste selecionado", 400
        
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
        html = render_template('pdf_template.html', tests=tests, datetime=datetime)
        
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
    except Exception as e:
        return str(e), 500

@app.route('/export/excel')
def export_excel():
    try:
        test_ids = request.args.getlist('ids[]', type=int)
        tests = get_tests(test_ids)
        
        if not tests:
            return "Nenhum teste selecionado", 400
        
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
            worksheet.set_column(col, col, 20)
        
        # Dados
        for row, test in enumerate(tests, start=1):
            col = 0
            worksheet.write(row, col, test['id']); col += 1
            worksheet.write(row, col, test['name']); col += 1
            worksheet.write(row, col, test['description']); col += 1
            worksheet.write(row, col, test['status']); col += 1
            worksheet.write(row, col, test['timestamp']); col += 1
            worksheet.write(row, col, json.dumps(json.loads(test['categories']), ensure_ascii=False)); col += 1
            worksheet.write(row, col, json.dumps(json.loads(test['steps']), indent=2, ensure_ascii=False)); col += 1
            worksheet.write(row, col, json.dumps(json.loads(test['environment']), indent=2, ensure_ascii=False)); col += 1
            worksheet.write(row, col, json.dumps(json.loads(test['custom_fields']), indent=2, ensure_ascii=False))
        
        workbook.close()
        
        # Retornar o arquivo
        output.seek(0)
        return send_file(
            output,
            download_name=f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 