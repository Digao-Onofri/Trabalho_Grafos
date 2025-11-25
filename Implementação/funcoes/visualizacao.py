import os
from . import node

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../instancias")

def leitura(instancia: str) -> list[node.Node]:

    instancia = os.path.join(DATA_DIR, instancia)

    with open(instancia, 'r') as arquivo:
        linhas = [l.strip().replace(",", "") for l in arquivo.readlines()]
    
    n = int(linhas[0])
    
    # ERB é sempre id = 0
    x_erb, y_erb = map(float, linhas[1].split())
    s = node.Station(0, x_erb, y_erb)

    nodes = [s]

    # Motes terão id = 1 até n
    for i in range(n):
        x, y = map(float, linhas[2 + i].split())
        nodes.append(node.Mote(i + 1, x, y, node.MAX_BATERIA))

    return nodes
