import paramiko
import json
import os
from datetime import datetime


def connect(server_address, port, user, password):
    print("Uzytkownik: {0}".format(user))
    print("Adres serwera: {0}".format(server_address))
    print("Port: {0}".format(port))

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server_address, port, user, password)
        print("Polaczono pomyslnie!")
        return ssh
    except paramiko.ssh_exception.AuthenticationException:
        exit("Zle haslo!")


def loadConfig():
    with open("config.json") as json_data:
        data = json.load(json_data)
    return data["server_address"], data["port"], input("username: "), \
           input("password: "), data["local_folder"], \
           data["remote_folder"], data["mode"], data["ignore"]


def overwrite():
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            if ignoreExtension(filename):
                sftp.put(local_folder + filename, filename)
                print(filename)
    ssh.close()


def update():
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            if ignoreExtension(filename):
                try:
                    sftp.stat(filename)
                    date1 = datetime.fromtimestamp(os.path.getmtime(local_folder + filename)) #local
                    date2 = datetime.fromtimestamp(sftp.stat(filename).st_mtime) #remote

                    if date1 > date2:
                        sftp.put(local_folder + filename, filename)
                        print(filename)
                        print(date2)
                except IOError:
                    pass
    ssh.close()


def add_non_existing():
    for root, dirs, files in os.walk(local_folder):
        for filename in files:
            if ignoreExtension(filename):
                try:
                    sftp.stat(filename)
                except IOError:
                    sftp.put(local_folder + filename, filename)
                    print(filename)
    ssh.close()


def ignoreExtension(filename):
    x = filename.split(".")
    flag = True
    for y in ignore:
        if x[1] == y:
            flag = False
            break
    if flag:
        return True
    return False


host, port, user, password, local_folder, remote_folder, mode, ignore = loadConfig()
ssh = connect(host, port, user, password)

sftp = ssh.open_sftp()
sftp.chdir(remote_folder)

# 1 of them: overwrite|update|add_non_existing
print("Wybrana opcja: {0}".format(mode))
if mode == "overwrite":
    overwrite()
elif mode == "update":
    update()
elif mode == "add_non_existing":
    add_non_existing()
else:
    ssh.close()
    exit("Nieprawidlowy wybor!")


#add_non_existing, update, overwrite

#a) overwrite: nadpisuje pliki w folderze zdalnym oraz dodaje pliki, których nie ma
#b) update: w folderze zdalnym nadpisuje tylko starsze pliki (pod względem daty modyfikacji),
#nie wysyła plików, których nie ma w zdalnym folderze
#c) add_non_existing: wysyła do zdalnego folderu tylko te pliki, których tam nie ma
