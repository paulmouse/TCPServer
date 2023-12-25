import socket
import datetime
import configparser
import threading

config = configparser.ConfigParser()
config.read('config.ini')
#hostIp = config.get('settings', 'hostip')
#port = int(config.get('settings', 'port'))

def datasplit(pos, data):
    relays = {'16': 1, '17': 2, '18': 3, '19': 4, '20': 5, '21': 6, '22': 7, '23': 8, '255': 'ON', '0': 'OFF',
              '5': 'DI', '4': 'AI'}
    bytes = list(data)
    #print(bytes[pos])
    ds = relays.get(str(bytes[pos]))
    #print(r1)
    try:
        return ds
    except:
        return ''

def analogdata(pos, datastrHex):
    pHex = datastrHex[pos:pos + 4]
    pDec = int(pHex, 16)
    pValue = round(((pDec / 1024) * 5.0),3)
    pt100Value = int(193 * pValue - 225)
    #print(pHex)
    #print(pValue)
    #print(pt100Value)
    #193 * CAST( @ value as decimal(19, 8)) - 220
    try:
        return pt100Value
    except:
        return ''

def handle_client(conn, addr):
    ip_address = addr[0]
    print(f"Подключен клиент {ip_address}")
    with open('tcp_requests.log', 'a') as log_file:
        log_file.write(f"{datetime.datetime.now()}\tConnected\t{ip_address}\n")
    with conn:
        while True:
            data = conn.recv(1024)
            bytes = list(data)
            inputType = datasplit(1, data)
            relayNo = datasplit(3, data)
            datastrHex = bytearray(bytes).hex()
            stateVal = datasplit(4, data)
            analogState = analogdata(6, datastrHex)
            if not data:
                print(f"Подключение клиента с {ip_address} закрыто")
                break
            if inputType == 'DI':
                print(f"Цифровой вход: {relayNo} Статус: {stateVal}")
            else:
                print(f"Аналоговый вход: 1 Значение: {analogState}");
            # print(f"Тип входа: {inputType}")
            with open('tcp_requests.log', 'a') as log_file:
                if inputType == 'DI':
                    log_file.write(f"{datetime.datetime.now()}\tInput\t{ip_address}\tDigital\t{relayNo}\t{stateVal}\n")
                else:
                    log_file.write(f"{datetime.datetime.now()}\tInput\t{ip_address}\tAnalog\t1\t{analogState}\n")

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


def main():
    HOST = get_local_ip() # Принимаем подключения со всех интерфейсов
    PORT = int(config.get('settings', 'port'))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        localIp = get_local_ip()
        print(f"Сервер запущен по адресу {localIp} и ожидает подключений на порту {PORT}...")
        with open('tcp_requests.log', 'a') as log_file:
            log_file.write(f"{datetime.datetime.now()}\tStart\n")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    main()
