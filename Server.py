import sqlite3
from socket import socket
from threading import Thread

class DB:

    def __init__(self):
        self.conn = sqlite3.connect('credentials.db')
        self.c = self.conn.cursor()

        try:
            self.c.execute('SELECT username, password FROM credentials')
        except:
            self.c.execute("""CREATE TABLE credentials
                        (
                        username tinytext,
                        password tinytext
                        )""")

    def check(self, username):
        self.c.execute(f"SELECT username FROM credentials WHERE username = '{username}'")

        if len(self.c.fetchall()) == 0:
            return False
        return True

    def add(self, username, password):
        try:
            self.c.execute(f"""INSERT INTO credentials (username, password)
                    VALUES ('{username}', '{password}')""")
            self.conn.commit()
            return True
        except:
            return False

    def verify(self, username, password):
        self.c.execute(f"SELECT username, password FROM credentials WHERE username = '{username}'")
        res = self.c.fetchall()

        if len(res) == 0:
            return False

        if res [0] [1] != password:
            return False

        return True

HOST = '172.20.10.3'
PORT = 8080

soc = socket()
soc.bind((HOST, PORT))

active_users = {}

def send(connection_object, text):
    connection_object.send(str.encode(text))

def recieve(connection_object):
    return connection_object.recv(1024).decode('utf-8')

def pass_extract(list):
    lst = [list [i] for i in range(2, len(list))]
    return '.'.join(lst)

def initialise(connection_object, address, db):

    global active_users 

    username = ''

    while(True):
        try:
            cmd = recieve(connection_object)
        except:
            return False

        if cmd != '' and cmd [0] == 'c':
            respose = str(db.check(cmd[2:]))
            try:
                send(connection_object, str(respose))
            except:
                return False

        elif cmd != '' and cmd [0] == 'l':
            username = cmd.split('.') [1]
            password = pass_extract(cmd.split('.'))

            response = db.verify(username, password)

            if response and username not in active_users:
                try:
                    send(connection_object, 'True')
                except:
                    return False

                active_users[username] = connection_object
                break

            else:
                try:
                    send(connection_object, 'False')
                except:
                    return False

        elif cmd != '' and cmd [0] == 'r':
            username = cmd.split('.') [1]
            password = pass_extract(cmd.split('.'))

            if db.check(username):
                try:
                    send(connection_object, 'False')
                except:
                    return False
                continue

            else:
                pass

            db.add(username, password)
            try:
                send(connection_object, 'True')
            except:
                return False

            active_users[username] = connection_object
            break

        else:
            pass
    
    return username

def ditch(username):
    global active_users
    active_users.pop(username)

def main(connection_object, address):

    global active_users

    db = DB()
    username = initialise(connection_object, address, db)

    if not username:
        connection_object.close()
        return None

    print(f"{username} connected.")

    while(True):

        try:
            cmd = recieve(connection_object)
        except:
            ditch(username)
            connection_object.close()
            print(f"{username} disconnected")
            return None

        if cmd == '':
            ditch(username)
            connection_object.close()
            print(f"{username} disconnected")
            return None
        
        else:
            pass

        if cmd != '' and cmd [0] == 'm':

            cmd = cmd.split('.')
            destination = cmd[1]
            message = '.'.join([cmd[i] for i in range(2, len(cmd))])

            try:
                conn_obj = active_users[destination]
            except:
                try:
                    send(connection_object, 'False')
                except:
                    pass
                
            try:
                send(conn_obj, f"m.{username}.{message}")
                try:
                    send(connection_object, 'True')
                except:
                    pass
            except:
                try:
                    send(connection_object, 'False')
                except:
                    pass

        elif cmd != '' and cmd [0] == 'c':

            if cmd.split('.') [1] in active_users.keys():
                try:
                    send(connection_object, 'Online')
                except:
                    pass
            else:
                try:
                    send(connection_object, 'Offline')
                except:
                    pass

        elif cmd != '' and cmd [0] == 'u':

            user = cmd.split('.') [1]
            try:
                send(connection_object, str(db.check(user)))
            except:
                pass

def start():

    global PORT

    print(f'Listening on port {PORT}.')

    while(True):
        soc.listen()
        connection_object, address = soc.accept()
        # print(f'{address} connected.')
        thread = Thread(target = main, args = [connection_object, address])
        thread.start()

start()
