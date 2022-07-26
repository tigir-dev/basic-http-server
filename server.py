# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import socket
import string
import re
import os


def upload_file(conn, parameter: dict, http_ver):
    if parameter.get("fileName") is None:
        response = http_ver + ' 400 Bad Request\r\nContent-Length: 56\r\nContent-Type: application/json\n\n' \
                              '{"success":False,message":"fileName parametresi eksik."}'
        conn.send(response.encode())
        return
    elif not os.path.exists(parameter.get("fileName")):
        response = http_ver + ' 400 Bad Request\r\nContent-Length: 56\r\nContent-Type: application/json\n\n' \
                              '{"success":False,"message":"Dosya sunucuda bulunamadi."}'
        conn.send(response.encode())
        return
    filename = parameter.get("fileName")
    total_packets = 0
    file_size = os.stat(filename).st_size
    # print("file-size: ", file_size)
    response = http_ver + ' 200 OK\r\nConnection:keep-alive\r\nContent-Length:' + str(file_size) + '\r\n' \
                            'Content-Type:application/octet-stream\r\nContent-Disposition:attachment;filename="' + filename + '"\n\n'
    conn.send(response.encode())
    with open(filename, 'rb') as f:
        # print('\nFile transfer started.')
        while True:
            data = f.read(1024)
            if not data:
                break
            conn.send(data)
            # print(total_packets, " giden paket")
            total_packets += 1
    # print("Transfer is completed. Total packets sent: ", total_packets)
    """response = http_ver + ' 200 OK\r\nContent-Length: '+str(56+file_size)+'\r\nContent-Type: application/json\n\n' \
               '{"success":True,"message":"Dosya gonderimi tamamlandi."}\n\n'
    conn.send(response.encode())"""


def is_int(number):
    try:
        int(number)
        return True
    except:
        return False


def is_prime(number):
    if is_int(number):
        for i in range(2, int(number)):
            if int(number) % i == 0:
                return 0
        return 1
    else:
        return -1

# def download_file(conn, filename: string, boundary, extra_data, http_version):
def download_file(conn, req, extra_data, http_version):
    total_packets = 0
    try:
        filename= get_filename(req)
        boundary = get_boundary(req)
    except:
        response = http_version + ' 400 Bad Request\r\nContent-Length: 55\r\nContent-Type: application/json\n\n' \
                                  '{"success":False,"message":"Dosya aktarimi basarisiz."}\n\n'
        conn.send(response.encode())
        return
    with open(filename, 'wb') as f:
        # print('\nFile transfer started.')
        f.write(extra_data)
        while True:
            data = conn.recv(1024)
            total_packets += 1
            if data.find(boundary) != -1:
                f.write(data[0:data.find(boundary) - 4])
                break
            f.write(data)
    # print("Transfer is completed. Total packets received: ", total_packets)
    response = http_version + ' 200 OK\r\nContent-Length: 52\r\nContent-Type: application/json\n\n' \
                              '{"success":True,"message":"Dosya basariyla alindi."}\n\n'
    conn.send(response.encode())


def get_filename(url):
    file_name = re.findall('filename=".*"', url)[0].replace("\"", "").replace("filename=", "")
    return file_name


def get_boundary(url):
    return re.findall('boundary=.*[^\r\n]', url)[0].replace("boundary=", "").encode()


def parse_req(url):
    # print(url)
    extra_data = None
    temp = data.split(b"\r\n\r\n", 2)
    parsed_url = temp[0].decode() + temp[1].decode()
    if len(temp) == 3:
        extra_data = temp[2]
    return parsed_url, extra_data


def parse_url(url):
    temp = url[0:url.find("\r\n")].split(" ")
    parameters = {}
    raw_url = temp[1][1:]
    http_version = temp[2]
    parameter_string = raw_url[raw_url.find("?") + 1:]
    if raw_url.find("?") != -1:
        request_key = raw_url[0:raw_url.find("?")]
    else:
        request_key = raw_url
    parameter_string = parameter_string.split("&")
    for line in parameter_string:
        before_eq = line[0:line.find("=")]
        after_eq = line[line.find("=") + 1:]
        parameters.update({before_eq: after_eq})
    return temp[0], parameters, request_key, http_version


def handle_get(conn, url, req_key, parameters, http_version):
    if req_key == "isPrime":
        # 0 asal degil fakat tamsayi, -1 tam sayi degil

        if parameters.get("number") is None:
            response = http_version + ' 400 Bad Request\r\nContent-Length: 71\r\nContent-Type: application/json\n\n' \
                                      '{"success":False,"message":"number parametresi eksik.","isPrime":False}\n\n'
            # print(response)
            conn.send(response.encode())
        elif is_prime(parameters.get("number")) == 1:
            response = http_version + ' 200 OK\r\nContent-Length: 31\r\nContent-Type: application/json\n\n' \
                                      '{"success":True,"isPrime":True}\n\n'
            conn.send(response.encode())
        elif is_prime(parameters.get("number")) == 0:
            response = http_version + ' 200 OK\r\nContent-Length: 32\r\nContent-Type: ' \
                                      'application/json\n\n{"success":True,"isPrime":False}\n\n'
            conn.send(response.encode())
        elif is_prime(parameters.get("number")) == -1:
            response = http_version + ' 400 Bad Request\r\nContent-Length: 75\r\nContent-Type: application/json\n\n' \
                                      '{"success":False,"message":"Lutfen tamsayi deger ' \
                                      'giriniz.","isPrime":False}\n\n'
            conn.send(response.encode())
    elif req_key == "download":
        upload_file(conn, parameters, http_version)


def rename_file(conn, old_name, new_name, http_version):
    if old_name is None or new_name is None:
        response = http_version + ' 404 Not Found\r\nContent-Length: 47\r\nContent-Type: application/json\n\n' \
                                  '{"success":False,"message":"Hatali parametre."}'
        conn.send(response.encode())
        return
    try:
        os.rename(old_name, new_name)
        response = http_version + ' 200 OK\r\nContent-Length: 44\r\nContent-Type: application/json\n\n' \
                                  '{"success":True,"message":"Islem basarili."}'
        conn.send(response.encode())
    except FileNotFoundError:
        response = http_version + ' 400 Bad Request\r\nContent-Length: 47\r\nContent-Type: application/json\n\n' \
                                  '{"success":False,"message":"Dosya bulunamadi."}'
        conn.send(response.encode())


def delete_file(conn, filename, http_version):
    if filename is None:
        # print("hhhh")
        response = http_version + ' 404 Not Found\r\nContent-Length: 57\r\nContent-Type: application/json\n\n' \
                                  '{"success":False,"message":"fileName parametresi eksik."}'
        conn.send(response.encode())
        return
    try:
        os.remove(filename)
        response = http_version + ' 200 OK\r\nContent-Length: 57\r\nContent-Type: application/json\n\n' \
                                  '{"success":True,"message":"Dosya silme islemi basarili."}'
        conn.send(response.encode())
    except FileNotFoundError:
        response = http_version + ' 400 Bad Request\r\nContent-Length: 47\r\nContent-Type: application/json\n\n' \
                                  '{"success":False,"message":"Dosya bulunamadi."}'
        conn.send(response.encode())


def is_endpoint_valid(req_type, req_key):
    # 0 get endpointleri
    # 1 post endpointleri
    # 2 put endpointleri
    # 3 delete endpointleri
    # -1 hatalilar icin
    if req_type == "GET" and (req_key == "isPrime" or req_key == "download"):
        return 0
    elif req_type == "POST" and req_key == "upload":
        return 1
    elif req_type == "PUT" and req_key == "rename":
        return 2
    elif req_type == "DELETE" and req_key == "remove":
        return 3
    else:
        return -1


# main script buradan basliyor

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 8080))
    print("Socket creation successful.")
except:
    print("Socket creation failed.")
    exit(1)
server.listen(5)
while True:
    connection, connected_address = server.accept()
    # print("Connected from", connected_address)
    data = connection.recv(1024)
    req, extra_data = parse_req(data)
    req_type, parameters, req_key, http_ver = parse_url(req)
    # print(req)
    # download_file(connection, parameters.get("fileName"), get_boundary(req), extra_data)
    # print(create_response(req))
    if is_endpoint_valid(req_type, req_key) == 0:
        handle_get(connection, req, req_key, parameters, http_ver)
    elif is_endpoint_valid(req_type, req_key) == 1:
        download_file(connection, req, extra_data, http_ver)
    elif is_endpoint_valid(req_type, req_key) == 2:
        rename_file(connection, parameters.get("oldFileName"), parameters.get("newFileName"), http_ver)
    elif is_endpoint_valid(req_type, req_key) == 3:
        delete_file(connection, parameters.get("fileName"), http_ver)
    else:
        # print("else e girdim")
        response = http_ver + ' 400 Bad Request\r\nContent-Length: 52\r\nContent-Type: application/json\n\n' \
                              '{"success":False,"message":"Hata.Istek bulunamadi."}'
        connection.send(response.encode())
    connection.close()
