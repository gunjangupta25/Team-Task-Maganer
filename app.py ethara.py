from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import jwt
import datetime
import bcrypt

app = Flask(__name__)
CORS(app)

# MySQL Config (CHANGE PASSWORD IF NEEDED)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Gunjan@25'
app.config['MYSQL_DB'] = 'taskdb'

mysql = MySQL(app)
SECRET_KEY = "secret123"

# Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data['name']
    email = data['email']
    password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    role = data['role']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
                (name, email, password, role))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "User created"})


# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user and password == user[3]:
        token = jwt.encode({
            'user_id': user[0],
            'role': user[4],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


# Create Task
@app.route('/tasks', methods=['POST'])
def create_task():
    token = request.headers.get('Authorization')
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    if data['role'] != 'admin':
        return jsonify({"message": "Only admin can create tasks"}), 403

    task = request.json
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tasks(title,assigned_to,created_by) VALUES(%s,%s,%s)",
                (task['title'], task['assigned_to'], data['user_id']))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Task created"})


# Get Tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    token = request.headers.get('Authorization')
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE assigned_to=%s", (data['user_id'],))
    tasks = cur.fetchall()

    return jsonify(tasks)


# Update Task
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    token = request.headers.get('Authorization')
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET status='done' WHERE id=%s AND assigned_to=%s",
                (id, data['user_id']))
    mysql.connection.commit()

    return jsonify({"message": "Task updated"})


if __name__ == '__main__':
    app.run(debug=True)