from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import urllib.parse
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


#created API Handler class
class APIServerHandler(BaseHTTPRequestHandler):
    
    def _set_response(self,status_code=200,content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content_type',content_type)
        self.end_headers()

    def create_table(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                address TEXT
            )
        ''')
        connection.commit()
        connection.close()

    @staticmethod
    def is_table_exist(database_name, table_name):
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = cursor.fetchone() is not None

        connection.close()
        return table_exists

    # Read data from sql
    def do_GET(self):

        if(self.path == '/api/data'):
            api_key = self.headers.get('X-API-Key')
            if api_key != os.getenv('API_KEY'):
                self._set_response(401) 
                self.wfile.write(json.dumps({'error': 'Invalid API key'}).encode('utf-8'))
                return
            # Retrieve data from the database
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            cursor.execute("SELECT id,name, age, address FROM users")
            data = cursor.fetchall()
            connection.close()
            
            # Convert data to JSON format
            response_data = [{'id':row[0],'name': row[1], 'age': row[2], 'address': row[3]} for row in data]
            
            self._set_response()
            self.wfile.write(json.dumps(response_data,indent=4).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

    # Insert Data into sqlite database
    def do_POST(self):

        if self.path == '/api/submit':
            api_key = self.headers.get('X-API-Key')
            if api_key != os.getenv('API_KEY'):
                self._set_response(401) 
                self.wfile.write(json.dumps({'error': 'Invalid API key'}).encode('utf-8'))
                return
            database_name = 'data.db'
            table_name = 'users'
        
            if not self.is_table_exist(database_name,table_name):
                self.create_table()

            content_length = int(self.headers['Content-length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

            # Extract data from post_data
            name = post_data.get('name')[0]
            age = post_data.get('age')[0]
            address = post_data.get('address')[0]
            
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            cursor.execute("Insert into users(name,age,address)VALUES(?,?,?)",(name,age,address))
            connection.commit()
            connection.close()

            self._set_response()
            response_data = {'message': 'Data successfully submitted and stored in the database.'}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

    # Update Records from sqlite database
    def do_PUT(self):

        if self.path == '/api/update':
            api_key = self.headers.get('X-API-Key')
            if api_key != os.getenv('API_KEY'):
                self._set_response(401) 
                self.wfile.write(json.dumps({'error': 'Invalid API key'}).encode('utf-8'))
                return
            database_name = 'data.db'
            table_name = 'users'

            # check if table exist before update operation
            if not APIServerHandler.is_table_exist(database_name, table_name):
                self.wfile.write(json.dumps({'error':'Table not found'}).encode('utf-8'))

            content_length = int(self.headers['Content-length'])
            put_data = self.rfile.read(content_length)
            put_data = urllib.parse.parse_qs(put_data.decode('utf-8'))

            # Extract data from post_data
            name = put_data.get('name')[0]
            age = put_data.get('age')[0]
            address = put_data.get('address')[0]

            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            update_query = "UPDATE users SET age=?, address=? WHERE name=?"
            cursor.execute(update_query, (age, address, name))
            connection.commit()
            connection.close()

            self._set_response()
            response_data = {'message': 'Data successfully updated and stored in the database.'}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

    # API to delete records from sqlite database
    def do_DELETE(self):
        if self.path == '/api/delete':
            api_key = self.headers.get('X-API-Key')
            if api_key != os.getenv('API_KEY'):
                self._set_response(401) 
                self.wfile.write(json.dumps({'error': 'Invalid API key'}).encode('utf-8'))
                return
            database_name = 'data.db'
            table_name = 'users'

            if not APIServerHandler.is_table_exist(database_name, table_name):
                self.wfile.write(json.dumps({'error':'Table not found'}).encode('utf-8'))

            content_length = int(self.headers['Content-length'])
            get_data = self.rfile.read(content_length)
            get_data = urllib.parse.parse_qs(get_data.decode('utf-8'))

            # Extract data from get_data
            name = get_data.get('name')[0]

            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            delete_query = "DELETE from users WHERE name=?"
            cursor.execute(delete_query,(name,))
            connection.commit()
            connection.close()
            
            self._set_response()
            response_data = {'message': 'Data successfully deleted from the table.'}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode('utf-8'))

# Driver Code
def run_server():
    # server parameters
    host_name = 'localhost'
    host_port = 8000

    # Creating the server instance
    server = HTTPServer((host_name, host_port), APIServerHandler)

    print(f"Server started at http://{host_name}:{host_port}")

    # Starting the server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped")



if __name__=='__main__':
    run_server()