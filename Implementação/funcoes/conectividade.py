import sys
from .kruskal import geraArestas, unionfind_init, union, find
from .node import Mote, dist, MAX_RAIO

# Aumenta o limite de recursão para garantir que a DFS funcione em redes grandes
sys.setrecursionlimit(20000)

# =============================================================================
# MÉTODO 1: SIMULAÇÃO DE FALHAS (BRUTE FORCE / UNION-FIND)
# =============================================================================

def encontrar_nos_criticos_simulacao(nodes):
    """
    Identifica nós críticos verificando se sua remoção desconecta 
    outros sensores da Estação Base (Station).
    
    """
    nos_criticos = []
    motes_indices = [i for i, n in enumerate(nodes) if isinstance(n, Mote)]
    n = len(nodes)

    # 1. Retrato da Rede Original (Baseline)
    # Usa beta=1.0 para considerar apenas alcance geográfico
    todas_arestas = geraArestas(nodes, beta=1.0) 
    
    link_orig, size_orig = unionfind_init(n)
    for u, v, w in todas_arestas:
        union(link_orig, size_orig, u, v)
    
    # Identifica quem consegue falar com a Station (ID 0)
    root_station_orig = find(link_orig, 0)
    conectados_station_orig = set()
    for i in range(n):
        if find(link_orig, i) == root_station_orig:
            conectados_station_orig.add(i)

    # 2. Simulação de Falhas
    motes_relevantes = [m for m in motes_indices if m in conectados_station_orig]

    for indice_alvo in motes_relevantes:
        link, size = unionfind_init(n)
        
        # Conecta todo mundo MENOS o nó alvo
        for u, v, w in todas_arestas:
            if u == indice_alvo or v == indice_alvo:
                continue
            union(link, size, u, v)

        # Verifica conectividade com a Station agora
        root_station_now = find(link, 0)
        conectados_station_now = set()
        for i in range(n):
            if i != indice_alvo and find(link, i) == root_station_now:
                conectados_station_now.add(i)
        
        # Se perdeu nós além do que foi removido, é crítico
        if len(conectados_station_now) < (len(conectados_station_orig) - 1):
            nos_criticos.append(nodes[indice_alvo].id)

    return sorted(nos_criticos)


# =============================================================================
# MÉTODO 2: DFS (ALGORITMO DE TARJAN - PONTOS DE ARTICULAÇÃO)
# =============================================================================

def construir_grafo_adj(nodes):
    """Auxiliar: Cria lista de adjacência baseada apenas na distância."""
    n = len(nodes)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if dist(nodes[i], nodes[j]) <= MAX_RAIO:
                adj[i].append(j)
                adj[j].append(i)
    return adj

def encontrar_nos_criticos_dfs(nodes):
    """
    Identifica pontos de articulação usando DFS (Algoritmo de Tarjan).
    """
    adj = construir_grafo_adj(nodes)
    n = len(nodes)
    
    visited = [False] * n
    discovery = [float('inf')] * n
    low = [float('inf')] * n
    parent = [-1] * n
    ap = [False] * n  # Marca se é Articulation Point
    
    time = 0

    def dfs_ap(u):
        nonlocal time
        children = 0
        visited[u] = True
        discovery[u] = time
        low[u] = time
        time += 1

        for v in adj[u]:
            if v == parent[u]:
                continue
            
            if visited[v]:
                # Aresta de retorno (Back-edge)
                low[u] = min(low[u], discovery[v])
            else:
                children += 1
                parent[v] = u
                dfs_ap(v)
                
                # Na volta da recursão, atualiza low[u]
                low[u] = min(low[u], low[v])

                # Condição 1: U não é raiz e low[filho] >= discovery[u]
                if parent[u] != -1 and low[v] >= discovery[u]:
                    ap[u] = True
        
        # Condição 2: U é raiz da árvore DFS e tem mais de 1 filho
        if parent[u] == -1 and children > 1:
            ap[u] = True

    # Executa DFS (cobre componentes desconexos também)
    for i in range(n):
        if not visited[i]:
            dfs_ap(i)
    
    # Filtra apenas Motes (ignora Station se ela for AP)
    lista_criticos = []
    for i in range(n):
        if ap[i] and isinstance(nodes[i], Mote):
            lista_criticos.append(nodes[i].id)
            
    return sorted(lista_criticos)


# =============================================================================
# INTERFACE / RELATÓRIO
# =============================================================================

def exibir_relatorio_robustez(nodes):
    print("\n" + "=" * 80)
    print("ANÁLISE DE FRAGILIDADE DA REDE (COMPARATIVO)")
    print("=" * 80)
    print(f"Total de nós na rede: {len(nodes)}")

    # --- Executa Método 1 (Simulação) ---
    print("\n[1] Método Simulação de Falha (Union-Find)...")
    criticos_sim = encontrar_nos_criticos_simulacao(nodes)
    print(f"    -> Encontrou {len(criticos_sim)} nós críticos: {criticos_sim}")

    # --- Executa Método 2 (DFS / Tarjan) ---
    print("\n[2] Método Teoria dos Grafos (DFS / Tarjan)...")
    criticos_dfs = encontrar_nos_criticos_dfs(nodes)
    print(f"    -> Encontrou {len(criticos_dfs)} nós críticos: {criticos_dfs}")

    # --- Comparação ---
    print("-" * 80)
    if criticos_sim == criticos_dfs:
        print("✅ SUCESSO: Os dois algoritmos chegaram ao mesmo resultado!")
        
        if not criticos_dfs:
            print("   A rede é ROBUSTA. Nenhuma desconexão detectada.")
        else:
            print(f"   ⚠️  A rede possui {len(criticos_dfs)} PONTOS DE ARTICULAÇÃO.")
            print("      A falha destes nós causará a fragmentação da rede.")
    else:
        print("⚠️  DIVERGÊNCIA: Os algoritmos retornaram resultados diferentes.")
        print(f"   Simulação: {criticos_sim}")
        print(f"   DFS:       {criticos_dfs}")
        print("   Nota: O método de Simulação foca na desconexão da STATION.")
        print("         O método DFS foca na desconexão do GRAFO como um todo.")
    
    print("=" * 80 + "\n")