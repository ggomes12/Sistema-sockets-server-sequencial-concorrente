import socket
import threading
import time
import random
import matplotlib.pyplot as plt

HOST = '127.0.0.1'  


#pra acabar com o problema de porta jah utilizada
def gerar_porta():
    return random.randint(15000, 63000)



def eh_bissexto(ano):
    return (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0)



# implementa um servidor sequencial que processa uma conexão de cliente por vez
def servidor_sequencial(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor_socket:
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor_socket.bind((HOST, porta))
        servidor_socket.listen()
        print(f"Servidor sequencial aguardando conexões em {HOST}:{porta}")
        while True:
            conn, addr = servidor_socket.accept()
            with conn:
                dados = conn.recv(1024)
                if dados:
                    ano = int(dados.decode())
                    resposta = "Bissexto" if eh_bissexto(ano) else "Não bissexto"
                    conn.sendall(resposta.encode())



# implementa um servidor concorrente que cria uma thread para cada conexão
def servidor_concorrente(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor_socket:
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor_socket.bind((HOST, porta))
        servidor_socket.listen()
        print(f"Servidor concorrente aguardando conexões em {HOST}:{porta}")
        while True:
            conn, addr = servidor_socket.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.start()

# trata cada cliente em uma thread separada
def tratar_cliente(conn, addr):
    with conn:
        dados = conn.recv(1024)
        if dados:
            ano = int(dados.decode())
            resposta = "Bissexto" if eh_bissexto(ano) else "Não bissexto"
            conn.sendall(resposta.encode())



# implementa o cliente que se conecta a um servidor e envia um ano para verificar
def cliente(ano, port):
    with socket.create_connection((HOST, port)) as cliente_socket:
        cliente_socket.sendall(str(ano).encode())
        resposta = cliente_socket.recv(1024)
        return resposta.decode()



# simula multiplos clientes se conectando ao servidor
def simular_clientes(num_clientes, port):
    tempos = []
    for _ in range(num_clientes):
        ano = random.randint(1800, 2400)
        inicio = time.time()
        cliente(ano, port)
        fim = time.time()
        tempos.append(fim - inicio)
    return tempos



# inicia o servidor sequencial ou concorrente em uma thread separada
def iniciar_servidor(tipo_servidor):
    porta = gerar_porta()  # gera uma porta aleatória
    while True:
        try:
            if tipo_servidor == "sequencial":
                servidor_thread = threading.Thread(target=servidor_sequencial, args=(porta,))
            else:
                servidor_thread = threading.Thread(target=servidor_concorrente, args=(porta,))
            servidor_thread.daemon = True
            servidor_thread.start()
            time.sleep(1)
            return servidor_thread, porta
        except OSError as e:
            print(f"Erro na tentativa de iniciar servidor na porta {porta}: {e}")
            porta = gerar_porta()


def executar_experimentos():
    clientes_testes = [10, 500, 1000, 10000] #coloquei 500, porque quando coloquei [10, 100, ...], o 10 e o 100 ficaram muito proximos, um numero encima do outro no grafico de linha
    tempos_sequencial = []
    tempos_concorrente = []

    for num_clientes in clientes_testes:
        # inicia o servidor sequencial
        servidor_thread, porta_sequencial = iniciar_servidor("sequencial")
        tempos_seq = simular_clientes(num_clientes, porta_sequencial)
        tempos_sequencial.append(sum(tempos_seq) / len(tempos_seq))
        print(f"Tempos servidor sequencial ({num_clientes} clientes): {tempos_sequencial[-1]} segundos")
        servidor_thread.join(1)

        # inicia o servidor concorrente
        servidor_thread, porta_concorrente = iniciar_servidor("concorrente")
        tempos_conc = simular_clientes(num_clientes, porta_concorrente)
        tempos_concorrente.append(sum(tempos_conc) / len(tempos_conc))
        print(f"Tempos servidor concorrente ({num_clientes} clientes): {tempos_concorrente[-1]} segundos")
        servidor_thread.join(1)

    return tempos_sequencial, tempos_concorrente


def gerar_graficos(tempos_sequencial, tempos_concorrente):
    clientes_testes = [ 10, 500, 1000, 10000]

    plt.figure(figsize=(10, 5))

    plt.plot(clientes_testes, tempos_sequencial, label='Servidor Sequencial', color='blue', marker='o')
    plt.plot(clientes_testes, tempos_concorrente, label='Servidor Concorrente', color='green', marker='o')

    plt.xticks(clientes_testes)

    plt.xlabel("Número de Clientes")
    plt.ylabel("Tempo Médio de Resposta (s)")
    plt.title("Tempo de Resposta do Servidor Sequencial vs Concorrente")
    plt.legend()
    plt.grid(True)
    plt.show()

tempos_sequencial, tempos_concorrente = executar_experimentos()
gerar_graficos(tempos_sequencial, tempos_concorrente)




"""
def executar_experimentos_parte2():
    clientes_testes = [10, 500, 1000, 10000]
    tempos_sequencial = []
    tempos_concorrente = []

    for num_clientes in clientes_testes:
        # Servidor Sequencial
        servidor_thread, porta_sequencial = iniciar_servidor("sequencial")
        servidor_thread.join(1)
        for execucao in range(10):
            tempos = simular_clientes(num_clientes, porta_sequencial)
            tempos_sequencial.append(sum(tempos) / len(tempos))
        print(f"Tempos servidor sequencial ({num_clientes} clientes) na porta {porta_sequencial}: {tempos_sequencial}")

        servidor_thread.join(1)

        # Servidor Concorrente
        servidor_thread, porta_concorrente = iniciar_servidor("concorrente")
        for execucao in range(10):
            tempos = simular_clientes(num_clientes, porta_concorrente)
            tempos_concorrente.append(sum(tempos) / len(tempos))
        print(f"Tempos servidor concorrente ({num_clientes} clientes) na porta {porta_concorrente}: {tempos_concorrente}")

        servidor_thread.join(1)

    return tempos_sequencial, tempos_concorrente
    
    
    
    
    
def gerar_boxplot(tempos_sequencial, tempos_concorrente):
    plt.figure(figsize=(10, 5))


    plt.boxplot([tempos_sequencial, tempos_concorrente],positions=[
                0, 1], widths=0.4, patch_artist=True, boxprops=dict(facecolor="lightblue"))


    plt.xticks([0, 1], ['Sequencial', 'Concorrente'])
    plt.ylabel("Tempo de Resposta (segundos)")
    plt.title("Box-Plot do Tempo de Resposta para Servidor Sequencial e Concorrente")

    plt.show()
    
    
    
tempos_sequencial, tempos_concorrente = executar_experimentos_parte2()
gerar_boxplot(tempos_sequencial, tempos_concorrente)
"""
