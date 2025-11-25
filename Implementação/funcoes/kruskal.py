from .node import Node, Mote, dist, MAX_RAIO
from .cluster import calcular_custo_com_rotacao, consumir_energia_com_rotacao

def geraArestas(nodes: list[Node], beta=0.5, cluster_heads=None):
    """
    Gera uma lista de arestas usando custo energético como peso.
    
    Considera cluster heads para priorizar roteamento através deles.

    :param list[Node] nodes: Lista de nós.
    :param beta: Peso para balancear distância e energia
    :param cluster_heads: Conjunto de IDs dos cluster heads (opcional)
    :returns arcs: Lista de arestas (u, v, custo)
    """

    arcs = []
    n = len(nodes)
    
    if cluster_heads is None:
        cluster_heads = set()

    for i in range(n):
        for j in range(i + 1, n):

            u = nodes[i]
            v = nodes[j]
            
            # Pula nós sem bateria
            if isinstance(u, Mote) and u.bateria <= 0:
                continue
            if isinstance(v, Mote) and v.bateria <= 0:
                continue

            distancia = dist(u, v)

            # mantém limite de conexão baseado em distância
            if distancia <= MAX_RAIO:

                # custo energético como peso, considerando cluster heads
                custo = calcular_custo_com_rotacao(u, v, cluster_heads, beta)

                arcs.append((u.id, v.id, custo))

    # Ordena por custo energético
    arcs.sort(key=lambda arc: arc[2])
    return arcs


def unionfind_init(n: int):
    link = [i for i in range(n)]
    size = [1 for _ in range(n)]
    return link, size


def find(link: list[int], x: int):
    if link[x] != x:
        link[x] = find(link, link[x])
    return link[x]


def union(link, size, a, b):
    a = find(link, a)
    b = find(link, b)

    if a == b:
        return False

    if size[a] < size[b]:
        a, b = b, a

    size[a] += size[b]
    link[b] = a

    return True


def kruskal(nodes: list[Node], arcs: list[tuple], beta=0.5, cluster_heads=None):
    """
    Cria uma árvore geradora mínima usando Kruskal,
    agora considerando custo energético, descarga e rotação de cluster heads.

    :param nodes: Lista de nós
    :param arcs: Lista de arestas
    :param beta: Peso para balancear distância e energia
    :param cluster_heads: Conjunto de IDs dos cluster heads (opcional)
    :returns list: MST (Árvore Geradora Mínima)
    """

    tree = []
    n = len(nodes)
    link, size = unionfind_init(n)
    

    for u, v, w in arcs:
        if union(link, size, u, v):

            # adiciona aresta
            tree.append((u, v, w))

            # descarrega energia com rotação de cluster heads
            consumir_energia_com_rotacao(nodes[u], nodes[v], cluster_heads, beta)

    return tree
