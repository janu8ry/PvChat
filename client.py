import time

import PySimpleGUI as sg
from PodSixNet.Connection import connection, ConnectionListener


# noinspection PyMethodMayBeStatic
class Client(ConnectionListener):
    def __init__(self, host, port):  # noqa
        self.Connect((host, port))
        print("PvChat client on!")
        self.name = None
        self.members = list()
        self.host = host
        self.port = port

    def change_name(self, new_name):
        self.name = new_name.replace(' ', '_').replace('\n', '')
        connection.Send({'action': 'join', 'name': new_name})

    def loop(self):
        connection.Pump()
        self.Pump()

    def Network_message(self, data):
        print(f"[{data['author']}]: {data['message']}")

    def Network_name_change(self, data):
        self.name = data['new_name']

    def Network_member_join(self, data):
        print(f"--- \"{data['name']}\" has joined the chat! ---")

    def Network_member_leave(self, data):
        print(f"--- \"{data['name']}\" left the chat... ---")

    def Network_member_update(self, data):
        self.members = data['members']

    def Network_announce(self, data):
        print(f"---< [Server] {data['message']} >---")

    def Network_server_closed(self, data):
        print(f"[!] server is closed\nreason: {data['reason'] or 'None'}")

    def Network_kick(self, data):
        print(f"[!] kicked from the server\nreason: {data['reason'] or 'None'}")

    def Network_ban(self, data):
        print(f"[!] banned from the server... you can't join this server forever\nreason: {data['reason'] or 'None'}")

    def Network_member_kick(self, data):
        print(f"[!] member \"{data['name']}\" has been kicked from the server...\nreason: {data['reason'] or 'None'}")

    def Network_member_ban(self, data):
        print(f"[!] member \"{data['name']}\" has been banned from the server...\nreason: {data['reason'] or 'None'}")

# ------------------------------------------------------------
    def Network_connected(self, data):  # noqa
        print(f"Successfully connected to \"{self.host}:{self.port}\" as [{self.name}]!\n"
              f"-----------------------------------------------------------------------------------------------------")

    def Network_error(self, data):
        print('[error] ', data['error'])
        connection.Close()

    def Network_disconnected(self, data):  # noqa
        print(f"connection lost from \"{self.host}:{self.port}\"")


if __name__ == '__main__':
    sg.theme('LightBlue')
    chat_column = [[sg.Multiline(size=(70, 30), autoscroll=True, auto_refresh=True, disabled=True, reroute_stdout=True,
                                 reroute_cprint=True, write_only=True, key='CHAT')],
                   [sg.Multiline(size=(60, 1), enter_submits=True, focus=True, key='QUERY'),
                    sg.Button('send', bind_return_key=True, key='SEND')]]
    player_column = [[sg.Text("Online Members")],
                     [sg.Listbox([], size=(20, 10), key='MEMBERS')]]
    layout = [[sg.Column(chat_column), sg.VerticalSeparator(), sg.Column(player_column)]]
    window = sg.Window("PvChat Client", layout, finalize=True)
    addr = sg.popup_get_text("host (ip or ip:port)", "host configuration", '192.168.50.31', keep_on_top=True)
    addr = addr.split(":")
    if len(addr) == 2:
        host = addr[0]
        port = addr[1]
    else:
        host = addr[0]
        port = 32198
    client = Client(host, port=int(port))
    name = sg.popup_get_text("Enter your nickname", "name configuration", "anonymous", keep_on_top=True)
    client.change_name(name or "ㅇㅇ")
    while True:
        event, value = window.read(timeout=20)
        if event is None:
            break
        window['MEMBERS'].update(values=client.members)
        if event == 'SEND':
            content = value['QUERY'].strip(' \n')
            if content:
                window['QUERY'].update('')
            if len(content) > 200:
                print("[!] Message is too long")
            elif len(content) == 0:
                print("[!] Message is empty")
            else:
                connection.Send({'action': 'message', 'message': content})
        client.loop()
        time.sleep(0.001)
