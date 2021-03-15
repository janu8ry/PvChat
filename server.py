import time
from weakref import WeakKeyDictionary
import sys
import threading
import json
from datetime import datetime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
import yaml


def get(data, path: list):
    if len(path) > 1:
        try:
            return get(data[path[0]], path[1:])
        except KeyError:
            return None
    else:
        try:
            return data[path[0]]
        except KeyError:
            return None


def config(query=None):
    with open('config.yml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        if not query:
            return data
        else:
            return get(data, query.split('.'))


def command_input(server):  # noqa
    while True:
        content = sys.stdin.readline().rstrip("\n")
        command = content.split(" ")[0]
        args = content.split(" ")[1:]
        if command in ('?', 'help', 'h'):
            print("""
--------------------------------------------------------------
<admin command reference>
help: shows this message (aliases: h, ?)
announce <content>: sends announcement message to all members (aliases: say, a)
stop <optional: reason>: stops this pvchat server (aliases: quit, q, s)
kick <member> <optional:reason>: kicks the member (aliases: k)
ban <member> <optional:reason>: bans the member (aliases: b)
unban <member> <optional:reason>: ubbans the ip (aliases: u)
--------------------------------------------------------------
""")
        elif command in ('announce', 'say', 'a'):
            server.send_to_all({'action': 'announce', 'message': args[1:]})
            print("announcement sent!")
        elif command in ('stop', 'quit', 'q', 's'):
            server.send_to_all({'action': 'server_closed', 'reason': args[1:]})
            print("server closed!")
            sys.exit(-1)
        elif command in ('kick', 'k'):
            target = server.get_member(args[0])
            if target is None:
                print(f"member \"{args[0]}\" not found")
            else:
                target.Send({'action': 'kick', 'reason': args[1:]})
                server.send_to_all({'action': 'member_kick', 'name': args[0], 'reason': args[1:]})
                server.remove_channel(target)
                print(f"kicked member \"{args[0]}\"")
        elif command in ('ban', 'b'):
            target = server.get_member(args[0])
            if target is None:
                print(f"member \"{args[0]}\" not found")
            else:
                target.Send({'action': 'ban', 'reason': args[1:]})
                server.send_to_all({'action': 'member_ban', 'name': args[0], 'reason': args[1:]})
                server.remove_channel(target)
                with open('blacklist.json', 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
                with open('blacklist.json', 'w', encoding='utf-8') as f:
                    blacklist[target.ip] = {'reason': args[1:], 'time': str(datetime.now())}
                    json.dump(blacklist, f)
                print(f"banned member \"{args[0]}\"")
        elif command in ('unban', 'u'):
            with open('blacklist.json', 'r', encoding='utf-8') as f:
                blacklist = json.load(f)
            if args[0] in blacklist:
                del blacklist[args[0]]
                with open('blacklist.json', 'w', encoding='utf-8') as f:
                    json.dump(blacklist, f)
                print(f"unbanned ip \"{args[0]}\"")
            else:
                print(f"ip \"{args[0]}\" not found")
        else:
            print(f"unknown command \"{command}\"...\n"
                  f"type \"help\" to show all commands")


# noinspection PyMethodMayBeStatic
class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.name = "ㅇㅇ"
        self.ip = None

    def Connected(self):
        pass

    def Close(self):
        self._server.member_leave(self)

    def Network_message(self, data):
        self._server.send_to_all({'action': 'message', 'message': data['message'], 'author': self.name})

    def Network_join(self, data):
        name = data['name'].replace(' ', '_').replace('\n', '')
        idx = 2
        while name in [i.name for i in self._server.members]:
            name += str(idx)
            idx += 1
        if data['name'].replace(' ', '_').replace('\n', '') != name:
            self.Send({'action': 'name_change', 'new_name': name})
        self.name = name
        self._server.member_join(self)


# noinspection PyMethodMayBeStatic
class ChatServer(Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        print("starting server...")
        host, port = kwargs.get('localaddr')
        try:
            Server.__init__(self, *args, **kwargs)
        except OSError:
            print(f"\033[31mError: server is already running on {host}:{port}\033[0m")
            sys.exit(-1)
        self.members = WeakKeyDictionary()
        print(f"\033[92mPvChat Server started on {host}:{port}\033[0m")
        self.command_loop = threading.Thread(target=command_input, args=(self,), daemon=True)
        self.command_loop.start()

    def Connected(self, channel, addr):
        with open('blacklist.json', 'r', encoding='utf-8') as f:
            blacklist = json.load(f)
        ip = addr[0]
        channel.ip = ip
        if ip in blacklist:
            print(f"\033[91mBanned member \"{ip}\" tried to join server\033[0m")
            self.remove_channel(channel)
        else:
            print(f"\033[96mNew connection from \"{ip}\"\033[0m")
            self.members[channel] = channel.name or 'ㅇㅇ'

    def member_join(self, channel):
        name = channel.name or 'ㅇㅇ'
        self.members[channel] = name
        self.send_to_all({'action': 'member_join', 'name': name})
        self.update_members()

    def member_leave(self, channel):
        print(f"\033[91mlost connection with {channel.name}\033[0m")
        self.send_to_all({'action': 'member_leave', 'name': channel.name})
        del self.members[channel]
        self.update_members()

    def update_members(self):
        self.send_to_all({'action': 'member_update', 'members': [i.name for i in self.members if i.name is not None]})

    def send_to_all(self, data):
        [ch.Send(data) for ch in self.members]

    def remove_channel(self, channel: Channel):
        del self.members[channel]
        self.update_members()
        channel.close()

    def get_member(self, name):
        try:
            return [i for i in self.members if i.name == name][0]
        except IndexError:
            return None

    def launch(self):
        while True:
            self.Pump()
            time.sleep(0.0001)


if __name__ == '__main__':
    server = ChatServer(localaddr=('0.0.0.0', config('port')))
    server.launch()
