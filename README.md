# PvChat
### Private chatting server/client

## information
### admin commands
server admin can use special commands on the server prompt.  
```
help: shows this message (aliases: h, ?)  
announce <content>: sends announcement message to all members (aliases: say, a)  
stop <optional: reason>: stops this pvchat server (aliases: quit, q, s)  
kick <member> <optional: reason>: kicks the member (aliases: k)  
ban <member> <optional: reason>: bans the member (aliases: b)  
unban <member> <optional: reason>: ubbans the ip (aliases: u)  
```
### config.yml
![screenshot](https://cdn.discordapp.com/attachments/781193022347804672/820928254482841620/Screen_Shot_2021-03-15_at_4.55.44_PM.png)
```
port: change the port to open the server (default: 32198)
enable-log: not ready yet
password: not ready yet
```
### screenshots
![prompt](https://cdn.discordapp.com/attachments/781193022347804672/820926950603489280/Screen_Shot_2021-03-15_at_4.47.27_PM.png)
![client1](https://cdn.discordapp.com/attachments/781193022347804672/820926952046854174/Screen_Shot_2021-03-15_at_4.48.43_PM.png)
![client2](https://cdn.discordapp.com/attachments/781193022347804672/820927202978955294/Screen_Shot_2021-03-15_at_4.51.32_PM.png)
![prompt-help](https://cdn.discordapp.com/attachments/781193022347804672/820927349491105792/Screen_Shot_2021-03-15_at_4.52.07_PM.png)
## installation
### client
#### quick install
- [Windows]()
- [Macos]()

#### using source code
**python3 is required**  
download [client.py](), and use following command
```shell
python3 client.py
```

### server 
**python3 and git is required**  

```sh
git clone https://github.com/janu8ry/PvChat.git
cd PvChat
pip3 install -r requirements.txt
nano config.yml # change settings if you want
python3 server.py
```