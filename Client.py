from socket import socket
from tkinter import Tk, LabelFrame, Label, Frame, Entry, Checkbutton, Button, IntVar, END, RAISED
import sqlite3
from datetime import datetime
import time as tme
import threading

HOST = '172.20.10.3'
PORT = 8080
handle = ''

soc = socket()
soc.connect((HOST, PORT))

class DB:

    def __init__(self):
        
        self.conn = sqlite3.connect('archives.db')
        self.c = self.conn.cursor()

    def count(self):
        try:
            self.c.execute(f"select count(*) from {self.user}")
            response = self.c.fetchone() [0]
        except:
            return 1
            
        return response // 5 if response % 5 == 0 else response // 5 + 1

    def get(self, index):

        start = (index - 1) * 5 + 1
        stop = index * 5

        try:
            self.c.execute(f"select * from {self.user} where _rowid_ between {start} and {stop}")
        except:
            return []

        return self.c.fetchall()

    def store(self, message, TYPE):
        try:
            self.c.execute(f"insert into {self.user} values ('{message}', {TYPE}, '{time()}')")
            self.conn.commit()
        except:
            self.c.execute(f"create table {self.user} (message text, TYPE smallint(1), time char(19))")
            self.c.execute(f"insert into {self.user} values ('{message}', {TYPE}, '{time()}')")
            self.conn.commit()

    def store_else(self, user, message):
        try:
            self.c.execute(f"insert into {user} values ('{message}', {1}, '{time()}')")
            self.conn.commit()
        except:
            self.c.execute(f"create table {user} (message text, TYPE smallint(1), time char(19))")
            self.c.execute(f"insert into {user} values ('{message}', {1}, '{time()}')")
            self.conn.commit()

    def clear(self):
        try:
            self.c.execute(f'drop table {self.user}')
            self.conn.commit()
        except:
            pass

    def get_clients(self):
        self.c.execute("select name from sqlite_master where type='table'")
        resp = [i [0] for i in self.c.fetchall()]
        return {i:0 for i in resp}

class ortho:

    def __init__(self,root):

        self.state = IntVar()

        root.title('REGISTER')

        main = Frame(root, padx = 10, pady =10, bg = '#404040')
        main.pack()

        self.register = LabelFrame(main, text = 'REGISTER', bg = '#404040', fg = '#ffffff', padx = 10, pady = 10)
        self.register.pack()

        Label(self.register, text = 'Username', bg = '#404040', fg = '#ffffff').grid(row = 0, column = 0)
        self.username = Entry(self.register)
        self.username.grid(row = 0, column = 1)

        Label(self.register, text = 'Password', bg = '#404040', fg = '#ffffff').grid(row = 1, column = 0)
        self.password = Entry(self.register)
        self.password.grid(row = 1, column = 1)

        Label(self.register, text = 'Reenter password', bg = '#404040', fg = '#ffffff').grid(row = 2, column = 0)
        self.repass = Entry(self.register)
        self.repass.grid(row = 2, column = 1)

        self.check = Button(self.register, text = 'Check', command = check)
        self.check.grid(row = 0, column = 2)

        self.rem = Checkbutton(self.register, text = 'Remember me.', variable = self.state)
        self.rem.grid(row = 3, column = 0, columnspan = 3)

        self.register_button = Button(self.register, text = 'Register', command = register)
        self.register_button.grid(row = 4, column = 0, columnspan = 3)

        self.notify = Label(main, text = '\n\n\n', bg = '#404040', fg = '#ffffff')
        self.notify.pack()

        log = LabelFrame(main, text = 'OR LOGIN', bg = '#404040', fg = '#ffffff', padx = 10, pady = 10)
        log.pack()

        self.log_button = Button(log, text = 'LOGIN', command = swap)
        self.log_button.pack()

    def get_username(self):
        return self.username.get()

    def get_password(self):
        return self.password.get()

    def get_state(self):
        return self.state.get()

    def get_repass(self):
        return self.repass.get()

    def roll_already_taken(self):
        self.notify.configure(text = '\nUsername already taken.\n')

    def roll_weak_pass(self):
        self.notify.configure(text = '\nPassword too weak.\n')

    def roll_no_match(self):
        self.notify.configure(text = "\nPasswords don't match.\n")

class meta(DB):

    def __init__(self, root, master):

        self.database_con = DB()
        self.database_con.user = ''

        self.root = root
        self.master = master
        self.root.title(self.master)

        self.window_size = 1100
        root.geometry(f"{str(self.window_size)}x{str(int(self.window_size * 2 / 3))}")

        self.left_bar = Frame(self.root, bg = '#999999')
        self.left_bar.pack(fill = 'y', side = 'left')

        right_bar = Frame(self.root, bg = '#999999')
        right_bar.pack(fill = 'y', side = 'right')

        info_bar = Frame(right_bar)
        info_bar.pack()

        a = Frame(self.root)
        a.pack(fill = 'y', side = 'left')
        Label(a, text = '').pack()

        b = Frame(self.root)
        b.pack(fill = 'y', side = 'right')
        Label(b, text = '').pack()

        top_bar = Frame(self.root, bg = '#999999')
        top_bar.pack(fill = 'x', side = 'top')

        bottom_bar = Frame(self.root, bg = '#999999')
        bottom_bar.pack(fill = 'x', side = 'bottom')

        self.info_bar = Frame(right_bar)
        self.info_bar.pack()

        self.prev_button = Button(top_bar, text = 'PREV', state = 'disabled', command = lambda: self.message_scroll(-1))
        self.prev_button.pack(side = 'left')

        self.next_button = Button(top_bar, text = 'NEXT', state = 'disabled', command = lambda: self.message_scroll(1))
        self.next_button.pack(side = 'right')

        self.send_button = Button(bottom_bar, text = 'SEND', width = '15', state = 'disabled', command = self.send)
        self.send_button.pack(side = 'right')

        self.message_box = Entry(bottom_bar, width = '85')
        self.message_box.pack(side = 'top')
        self.message_box.insert(END, 'Enter your message')

        self.strip = Label(root, text = 'Select anyone and start chatting !!', pady = 10, bg = 'grey', fg = 'white')        
        self.strip.pack(fill = 'x')

        top = Frame(self.left_bar)
        top.pack(fill = 'x')

        bottom = Frame(self.left_bar)
        bottom.pack(side = 'bottom')

        self.prev_button2 = Button(top, text = 'PREV', state = 'disabled', command = lambda: self.chatbox_scroll(-1))
        self.prev_button2.pack(side = 'left')

        self.next_button2 = Button(top, text = 'NEXT', state = 'disabled', command = lambda: self.chatbox_scroll(1))
        self.next_button2.pack(side = 'right')

        self.user_search = Entry(bottom, width = '25')
        self.user_search.pack(fill = 'x')
        self.user_search.insert(END, 'username')

        self.search_button = Button(bottom, text = 'Chat !!', command = self.search)
        self.search_button.pack(fill = 'x')

        self.search_result = Label(bottom, text = '\n\n\n\n\n')
        self.search_result.pack(fill = 'both', expand = 1)

        Label(self.left_bar, text = 'Chats', pady = 5, bg = 'grey', fg = 'white').pack(fill = 'x')

        self.recipients = self.database_con.get_clients()
        self.recipients_btn = {}

        if len(self.recipients) > 2:
            for i in range(2):
                a = Button(self.left_bar, text = list(self.recipients.keys()) [i] + (10 - len(list(self.recipients.keys()) [i])) * ' ' + str(list(self.recipients.values()) [i]), command = lambda i = i: self.select(list(self.recipients.keys()) [i]))
                self.recipients_btn [list(self.recipients.keys()) [i]] = a
                a.pack(fill = 'x')
            self.next_button2.configure(state = 'normal')

        else:
            for i in self.recipients:
                a = Button(self.left_bar, text = i + (10 - len(i)) * ' ' + str(self.recipients [i]), command = lambda i = i: self.select(i))
                self.recipients_btn [i] = a
                a.pack(fill = 'x')

        self.recipients_state = 0

        self.chat_with = Label(info_bar, text = '-\n-', pady = 30)
        self.chat_with.pack()

        self.clearchat_button = Button(info_bar, text = 'Clear\nmessages', width = '25', state = 'disabled', command = self.clear_chat_a)
        self.clearchat_button.pack()

        self.messages = {}

    def select(self, user):

        global soc
        global handle

        send(soc, f"c.{user}")
        while True:
            if handle != '':
                status = handle
                handle = ''
                break
            else:
                continue

        try:
            if self.database_con.user in self.recipients_btn.keys():
                self.recipients_btn[self.database_con.user].configure(bg = 'white', fg = 'black', state = 'normal')
            else:
                pass
        except:
            pass

        self.database_con.user = user
        self.message_state = self.database_con.count()

        self.pack(self.database_con.get(self.message_state))

        if self.message_state != 1:
            self.prev_button.configure(state = 'normal')
        else:
            pass

        if user not in self.recipients:
            self.recipients [user] = 0
            self.chatbox_scroll(0)
        else:
            pass

        if user in self.recipients_btn.keys():
            self.recipients[user] = 0
            self.recipients_btn[user].configure(bg = 'grey', fg = 'white', state = 'disabled', text = user + (10 - len(user)) * ' ' + '0')
        else:
            pass

        self.chat_with.configure(text = f"{self.database_con.user}\n{status}")
        self.clearchat_button.configure(state = 'active')

        if status == 'Online':
            self.send_button.configure(state = 'normal')
        else:
            self.send_button.configure(state = 'disabled')

        self.strip.configure(text = f'Messages with {user}')

        return None

    def pack(self, lst):

        for i in self.messages.values():
            i.destroy()

        for i in lst:
            message = Frame(self.root)
            self.messages [i] = message
            time = invtime(i [2])

            if i [1]:
                Label(message, text = time, justify = 'left', fg = 'grey', anchor = 'w', padx = '10').pack(fill = 'x')
                Label(message, text = i [0], justify = 'left', anchor = 'w', padx = '10').pack(fill = 'x')
            else:
                Label(message, text = time, justify = 'right', fg = 'grey', anchor = 'e', padx = '10').pack(fill = 'x')
                Label(message, text = i [0], justify = 'right', anchor = 'e', padx = '10').pack(fill = 'x')

            message.pack(fill = 'x')

        return None

    def packone(self, message, TYPE, DB_con):

        DB_con.user = self.database_con.user

        if len(self.messages) >= 5:

            for i in self.messages.values():
                i.destroy()

            self.messages.clear()
            a = Frame(self.root)
            Time = invtime(time())
            self.messages[(message, TYPE, time)] = a
            self.message_state += 1
            DB_con.store(message, TYPE)
            self.prev_button.configure(state = 'active')

            if TYPE:
                Label(a, text = Time, justify = 'left', fg = 'grey', anchor = 'w', padx = '10').pack(fill = 'x')
                Label(a, text = message, justify = 'left', anchor = 'w', padx = '10').pack(fill = 'x')
            else:
                Label(a, text = Time, justify = 'right', fg = 'grey', anchor = 'e', padx = '10').pack(fill = 'x')
                Label(a, text = message, justify = 'right', anchor = 'e', padx = '10').pack(fill = 'x')

            a.pack(fill = 'x')

        else:

            Time = invtime(time())
            a = Frame(self.root)
            self.messages[(message, TYPE, time)] = a
            DB_con.store(message, TYPE)

            if TYPE:
                Label(a, text = Time, justify = 'left', fg = 'grey', anchor = 'w', padx = '10').pack(fill = 'x')
                Label(a, text = message, justify = 'left', anchor = 'w', padx = '10').pack(fill = 'x')
            else:
                Label(a, text = Time, justify = 'right', fg = 'grey', anchor = 'e', padx = '10').pack(fill = 'x')
                Label(a, text = message, justify = 'right', anchor = 'e', padx = '10').pack(fill = 'x')

            a.pack(fill = 'x')

        return None

    def send(self):

        global soc
        global handle

        message = self.message_box.get()
        if message == '':
            return None
        else:
            pass

        self.message_box.delete(0, END)
        to = self.database_con.user

        send(soc, f"m.{to}.{message}")
        while True:
            if handle != '':
                resp = handle
                handle = ''
                break
            else:
                continue

        if resp == 'False':
            self.message_box.delete(0, END)
            self.message_box.insert(END, 'Sorry the user went offline.')
            self.send_button.configure(state = 'disabled')
            self.chat_with.configure(text = f"{self.database_con.user}\nOfflne")

        else:
            self.packone(message, 0, self.database_con)

        return None

    def recieved(self, text, DB_con):

        sender = text.split('.') [1]
        message = '.'.join([text.split('.')[i] for i in range(2, len(text.split('.')))])
        if message  == '':
            return None
        else:
            pass

        DB_con.user = self.database_con.user

        if self.database_con.user == sender:
            self.packone(message, 1, DB_con)
            return None
        else:
            pass

        if sender in self.recipients:
            self.recipients[sender] += 1

            if sender in self.recipients_btn:
                self.recipients_btn [sender].configure(text = sender + (10 - len(sender)) * ' ' + str(self.recipients[sender]))
            else:
                pass

            DB_con.store_else(sender, message)

        else:
            self.recipients[sender] = 1
            self.chatbox_scroll(0)
            DB_con.store_else(sender, message)

        return None

    def message_scroll(self, direction):
        
        if direction == 1:
            self.message_state += 1
            self.prev_button.configure(state = 'active')
            lst = self.database_con.get(self.message_state)
            self.pack(lst)
            if self.database_con.count() == self.message_state:
                self.next_button.configure(state = 'disabled')
            else:
                pass

        elif direction == 0:
            lst = self.database_con.get(self.message_state)
            self.pack(lst)

        else:
            self.message_state -= 1
            self.next_button.configure(state = 'active')
            lst = self.database_con.get(self.message_state)
            self.pack(lst)
            if self.message_state == 1:
                self.prev_button.configure(state = 'disabled')
            else:
                pass

        return None

    def chatbox_scroll(self, direction):
        
        if direction == 1:
            self.recipients_state += 1
            self.prev_button2.configure(state = 'active')
            for i in self.recipients_btn.values():
                i.destroy()
            self.recipients_btn.clear()
            
            for i in range(self.recipients_state * 2, (self.recipients_state + 1) * 2):
                try:
                    a = Button(self.left_bar, text = list(self.recipients.keys()) [i] + (10 - len(list(self.recipients.keys()) [i])) * ' ' + str(list(self.recipients.values()) [i]), command = lambda i = i: self.select(list(self.recipients.keys()) [i]))
                    self.recipients_btn [list(self.recipients.keys()) [i]] = a
                    if list(self.recipients.keys()) [i] == self.database_con.user:
                        a.configure(bg = 'grey', fg = 'white', state = 'disabled')
                    else:
                        pass
                    a.pack(fill = 'x')
                except:
                    pass
            
            if len(self.recipients) <= (self.recipients_state + 1) * 2:
                self.next_button2.configure(state = 'disabled')
            else:
                pass

        elif direction == 0:
            for i in self.recipients_btn.values():
                i.destroy()
            self.recipients_btn.clear()
            
            for i in range(self.recipients_state * 2, (self.recipients_state + 1) * 2):
                try:
                    a = Button(self.left_bar, text = list(self.recipients.keys()) [i] + (10 - len(list(self.recipients.keys()) [i])) * ' ' + str(list(self.recipients.values()) [i]), command = lambda i = i: self.select(list(self.recipients.keys()) [i]))
                    self.recipients_btn [list(self.recipients.keys()) [i]] = a
                    if list(self.recipients.keys()) [i] == self.database_con.user:
                        a.configure(bg = 'grey', fg = 'white', state = 'disabled')
                    else:
                        pass
                    a.pack(fill = 'x')
                except:
                    return None
            
            if (self.recipients_state + 1) * 2 < len(self.recipients):
                self.next_button2.configure(state = 'active')
            else:
                pass

        else:
            self.recipients_state -= 1
            self.next_button2.configure(state = 'active')
            for i in self.recipients_btn.values():
                i.destroy()
            self.recipients_btn.clear()
            
            for i in range(self.recipients_state * 2, (self.recipients_state + 1) * 2):
                try:
                    a = Button(self.left_bar, text = list(self.recipients.keys()) [i] + (10 - len(list(self.recipients.keys()) [i])) * ' ' + str(list(self.recipients.values()) [i]), command = lambda i = i: self.select(list(self.recipients.keys()) [i]))
                    self.recipients_btn [list(self.recipients.keys()) [i]] = a
                    if list(self.recipients.keys()) [i] == self.database_con.user:
                        a.configure(bg = 'grey', fg = 'white', state = 'disabled')
                    else:
                        pass
                    a.pack(fill = 'x')
                except:
                    pass

            if self.recipients_state == 0:
                self.prev_button2.configure(state = 'disabled')
            else:
                pass

        return None

    def clear_chat_a(self):

        self.clearchat_button.configure(bg = 'red', text = 'Are you\nsure?', command = self.clear_chat_c)
        t = threading.Thread(target = self.clear_chat_b)
        t.start()

        return None

    def clear_chat_b(self):

        tme.sleep(2)
        self.clearchat_button.configure(bg = 'white', text = 'Clear\nmessages', command = self.clear_chat_a)

        return None

    def clear_chat_c(self):
        
        self.database_con.clear()
        for i in self.messages.values():
            i.destroy()
        self.clearchat_button.configure(bg = 'white', text = 'Clear\nmessages', command = self.clear_chat_a)
        self.messages.clear()
        self.prev_button.configure(state = 'disabled')
        self.next_button.configure(state = 'disabled')

        return None

    def search(self):

        global soc
        global handle
        
        user = self.user_search.get()

        if user == self.master:
            self.search_result.configure(text = '\n\nCannot select\nyourself\n\n', bg = 'red')
            t = threading.Thread(target = self.search_reset)
            t.start()
            return None
        else:
            pass

        if user != '':
            send(soc, f"u.{user}")
            while True:
                if handle != '':
                    resp = handle
                    handle = ''
                    break
                else:
                    continue
        else:
            return None

        if resp == 'True':
            self.search_result.configure(text = '\n\n\nDone\n\n', bg = 'green')
            self.select(user)
            t = threading.Thread(target = self.search_reset)
            t.start()

        else:
            self.search_result.configure(text = '\n\n\nNo such user\n\n', bg = 'red')
            t = threading.Thread(target = self.search_reset)
            t.start()
            
        return None

    def search_reset(self):

        tme.sleep(2)
        self.search_result.configure(text = '\n\n\n\n\n', bg = 'white')

        return None

class para:

    def __init__(self, root):

        self.state = IntVar()

        root.title('LOGIN')

        main = Frame(root, padx = 10, pady = 10, bg = '#404040')
        main.pack()

        self.login = LabelFrame(main, text = 'LOGIN', bg = '#404040', fg = '#ffffff', padx = 10, pady = 10)
        self.login.pack()

        Label(self.login, text = 'Username', bg = '#404040', fg = '#ffffff').grid(row = 0, column = 0)
        self.username = Entry(self.login)
        self.username.grid(row = 0, column = 1)

        Label(self.login, text = 'Password  ', bg = '#404040', fg = '#ffffff').grid(row = 1, column = 0)
        self.password = Entry(self.login)
        self.password.grid(row = 1, column = 1)

        self.rem = Checkbutton(self.login, text = 'Remember me', variable = self.state)
        self.rem.grid(row = 2, column = 0, columnspan = 2)

        self.login_button = Button(self.login, text = 'Login', command = login)
        self.login_button.grid(row = 3, column = 0, columnspan = 2)

        self.notify = Label(main, text = '\n\n\n', bg = '#404040', fg = '#ffffff')
        self.notify.pack()

        reg = LabelFrame(main, text = 'OR REGISTER', bg = '#404040', fg = '#ffffff', padx = 10, pady = 10)
        reg.pack()

        self.reg_button = Button(reg, text = 'REGISTER', command = swap)
        self.reg_button.pack()

    def get_username(self):
        return self.username.get()

    def get_password(self):
        return self.password.get()

    def get_state(self):
        return self.state.get()

    def roll_incorrect(self):
        self.notify.configure(text = '\nInvalid username or password\n')

class host:

    def __init__(self, soc):
        self.soc = soc

    def login(self, username, password):
        send(self.soc, f'l.{username}.{password}')
        response = recieve(self.soc)
        if response == 'False':
            return False
        return True

    def check(self, username):
        send(self.soc, f'c.{username}')
        response = recieve(self.soc)
        if response == 'False':
            return False
        return True

    def register(self, username, password):
        send(self.soc, f'r.{username}.{password}')
        response = recieve(self.soc)
        if response == 'False':
            return False
        return True

contact = host(soc)

def init():

    global LoginApp
    global transition
    global login_root
    global current

    creds = ret_creds()

    if not creds:
        transition = 0

    else:
        transition = 1
        username = creds [0]
        password = creds [1]

    if not transition:
        current = 0
        login_root = Tk()
        LoginApp = para(login_root)
        login_root.mainloop()

    else:
        if not login(username = username, password = password):
            current = 0
            login_root = Tk()
            LoginApp = para(login_root)
            login_root.mainloop()

        else:
            main(username)

def time():
    return f"{str(datetime.now().year)}.{str(datetime.now().month)}.{str(datetime.now().day)}.{str(datetime.now().hour)}.{str(datetime.now().minute)}.{str(datetime.now().second)}"

def invtime(stri):

    year = int(stri.split('.') [0])
    month = int(stri.split('.') [1])
    day = int(stri.split('.') [2])

    dday = datetime(year, month, day).strftime('%a')
    month = datetime(year, month, day).strftime('%b')

    return f"{stri.split('.') [3]}:{stri.split('.') [4]} {dday} {day} {month} {year}"

def send(soc, text):
    soc.send(str.encode(text))

def recieve(soc):
    return soc.recv(1024).decode('utf-8')

def stimulus():
    
    global soc
    global MainApp
    global handle
    global end

    DB_con = DB()

    while True:

        try:
            cmd = soc.recv(1024).decode('utf-8')
        except:
            cmd = ''

        if cmd != '' and cmd [0] == 'm':
            MainApp.recieved(cmd, DB_con)
        else:
            handle = cmd

        if end:
            break
        else:
            pass

    return None

def login(**kwargs):

    global LoginApp
    global contact
    global login_root

    if not len(kwargs):
        username = LoginApp.get_username()
        password = LoginApp.get_password()

    else:
        username = kwargs['username']
        password = kwargs['password']

    response = contact.login(username, password)

    if response and not len(kwargs):
        login_root.destroy()

        if LoginApp.get_state():
            cache_creds(username, password)
        else:
            pass

        main(username)
        return None

    elif not len(kwargs):
        LoginApp.roll_incorrect()

    else:
        return response

def register():

    global RegisterApp
    global contact
    global register_root

    username = RegisterApp.get_username()
    password = RegisterApp.get_password()
    repass = RegisterApp.get_repass()

    if password != repass:
        RegisterApp.roll_no_match()
        return None

    if contact.register(username, password):
        register_root.destroy()

        if RegisterApp.get_state():
            cache_creds(username, password)
        else:
            pass

        main(username)

    else:
        RegisterApp.roll_already_taken()

def check():

    global RegisterApp
    global contact

    username = RegisterApp.get_username()

    if contact.check(username):
        RegisterApp.username.configure(bg = 'red')

    else:
        RegisterApp.username.configure(bg = 'green')

def swap():

    global register_root
    global login_root
    global current
    global RegisterApp
    global LoginApp

    if current:
        current = 0
        register_root.destroy()
        login_root = Tk()
        LoginApp = para(login_root)
        login_root.mainloop()

    else:
        current = 1
        login_root.destroy()
        register_root = Tk()
        RegisterApp = ortho(register_root)
        register_root.mainloop()

def ret_creds():
    try:
        with open('cache.bin', 'rb') as f:
            stuff = f.read().decode('utf-8')
    except:
        return False

    if stuff != '':
        return [stuff.split('|') [0].split('.') [0], stuff.split('|') [0].split('.') [1]]

    return False

def cache_creds(username, password):
    with open('cache.bin', 'wb') as f:
        f.write(str.encode(f"{username}.{password}|"))

def main(username):

    global MainApp
    global end

    end = False

    main_root = Tk()
    MainApp = meta(main_root, username)
    t = threading.Thread(target = stimulus)
    t.start()
    main_root.mainloop()
    end = True

    return None
      
init()
soc.close()
