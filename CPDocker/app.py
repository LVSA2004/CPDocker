import os
import json
from flask import Flask, jsonify, request
import mysql.connector
from datetime import date, datetime

app = Flask(__name__)

# Configura as variáveis de ambiente para conexão com o banco de dados
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]
AUTH_PLUGIN = os.environ["AUTH_PLUGIN"]

# Cria a conexão com o banco de dados
connection = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    auth_plugin=AUTH_PLUGIN,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# Cria a tabela 'employees' no banco de dados, caso ainda não exista
with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            birthdate DATE NOT NULL,
            cpf VARCHAR(11) NOT NULL,
            salary DECIMAL(10, 2) NOT NULL,
            PRIMARY KEY (id)
        )
    """)

# Testar se o App está no ar: http://127.0.0.1:5000/
# Deve retornar: API is running! no Browser
@app.route("/")
def index():
    return "A API esta Funcionando"

# Seleciona todos os registros da tabela 'employees'
# No Browser acesse: http://127.0.0.1:5000/employees
# para ver os produtos no navegador
@app.route("/employees", methods=["GET"])
def get_employees():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM employees')
            records = cursor.fetchall()
            data = [{'id': record[0], 'name': record[1], 'birthdate': record[2].strftime('%Y-%m-%d'), 'cpf': record[3], 'salary': float(record[4])} for record in records]
            return jsonify(data)
    except Error as e:
        print(e)
        return jsonify({'message': 'Erro ao buscar registros da tabela employees.'}), 500


# Insere registros no Banco (API)
@app.route("/employees", methods=["POST"])
def create_employee():
    # Obtém os dados enviados na requisição
    data = request.get_json()
    name = data["name"]
    birthdate = data["birthdate"]
    cpf = data["cpf"]
    salary = data["salary"]

    # Insere os dados na tabela 'employees'
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO employees (name, birthdate, cpf, salary)
            VALUES (%s, %s, %s, %s)
        """, (name, birthdate, cpf, salary))
        connection.commit()

    # Retorna uma mensagem de sucesso como resposta
    return {"message": "Registro inserido com sucesso!"}

# Atualiza registros no Banco (API)
@app.route("/employees/<int:id>", methods=["PUT"])
def update_employee(id):
    # Obtém os dados enviados na requisição
    data = request.get_json()
    name = data["name"]
    birthdate = data["birthdate"]
    cpf = data["cpf"]
    salary = data["salary"]

    # Atualiza os dados do registro com o ID especificado na tabela 'employees'
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE employees
            SET name=%s, birthdate=%s, cpf=%s, salary=%s
            WHERE id=%s
        """, (name, birthdate, cpf, salary, id))
        connection.commit()

    # Retorna uma mensagem de sucesso como resposta
    return {"message": "Funcionário atualizado com sucesso!"}

# Deleta registros no Banco (API)
@app.route("/employees/<int:id>/", methods=["DELETE"])
def delete_employee(id):
    # Deleta o registro com o ID especificado na tabela 'employees'
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM employees
            WHERE id=%s
        """, (id,))
        connection.commit()
    # Retorna uma mensagem de sucesso como resposta
    return {"message": "Funcionário deletado com sucesso!"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
