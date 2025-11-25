"""
Módulo de seleção e rotação de Cluster Heads.
Implementa rotação de cluster heads para distribuir consumo de energia uniformemente.
"""

from .node import Mote, Station, dist, MAX_RAIO

def selecionar_cluster_heads(nodes, porcentagem=0.1, rodada=0):
    """
    Seleciona cluster heads para a rodada atual usando rotação baseada em energia.
    
    Implementa uma estratégia similar ao LEACH:
    - Considera a energia residual dos nós
    - Rotaciona os cluster heads a cada rodada
    - Garante que nós com baixa bateria não sejam selecionados como CH
    
    :param nodes: Lista de nós da rede
    :param porcentagem: Porcentagem de nós que serão cluster heads (default 10%)
    :param rodada: Número da rodada atual (usado para rotação)
    :return: Conjunto de IDs dos cluster heads selecionados
    """
    motes = [n for n in nodes if isinstance(n, Mote) and n.bateria > 0]
    
    if not motes:
        return set()
    
    # Número desejado de cluster heads
    num_chs = max(1, int(len(motes) * porcentagem))
    
    # Calcula energia máxima e média dos motes ativos
    energia_max = max(m.bateria for m in motes)
    energia_media = sum(m.bateria for m in motes) / len(motes)
    
    # Filtra candidatos que têm energia acima da média (ou pelo menos algum nível razoável)
    # Isso garante que nós com baixa bateria não sejam forçados a ser CH
    limiar_energia = max(energia_media * 0.5, 1.0)  # Pelo menos 50% da média ou 1 unidade
    
    # Prioriza motes com mais energia para serem cluster heads
    # A rotação é feita de forma mais efetiva: dividimos em grupos baseados em rodada
    candidatos = []
    for m in motes:
        if m.bateria < limiar_energia:
            continue  # Pula nós com bateria muito baixa
            
        # Fator de prioridade baseado em energia (normalizado 0-1)
        # Quanto mais bateria, maior a probabilidade de ser CH
        prioridade_energia = m.bateria / energia_max if energia_max > 0 else 1.0
        
        # Fator de rotação: usa uma função mais efetiva para diversificar a seleção
        # A ideia é que em cada rodada, diferentes grupos de nós sejam priorizados
        grupo_rodada = (rodada // num_chs) % (len(motes) // num_chs + 1) if num_chs > 0 else 0
        indice_grupo = (m.id % (len(motes) // num_chs + 1)) if num_chs > 0 else 0
        
        # Bônus para nós cujo grupo corresponde à rodada atual
        bonus_rotacao = 1.0 if indice_grupo == grupo_rodada else 0.3
        
        # Score combinado: energia alta + bônus de rotação
        score = prioridade_energia * bonus_rotacao
        
        candidatos.append((m.id, score, m.bateria))
    
    # Se não há candidatos suficientes acima do limiar, use todos os disponíveis
    if len(candidatos) < num_chs:
        candidatos = []
        for m in motes:
            prioridade_energia = m.bateria / energia_max if energia_max > 0 else 1.0
            candidatos.append((m.id, prioridade_energia, m.bateria))
    
    # Ordena por score (maior primeiro) e seleciona os top cluster heads
    candidatos.sort(key=lambda x: (-x[1], -x[2]))
    
    cluster_heads = set()
    for i in range(min(num_chs, len(candidatos))):
        cluster_heads.add(candidatos[i][0])
    
    return cluster_heads


def calcular_custo_com_rotacao(sensor, ch, cluster_heads, beta=0.5, eps=0.0001):
    """
    Calcula o custo de associação considerando se o nó destino é cluster head.
    
    Se o destino é um cluster head selecionado, reduz o custo para priorizar
    a conexão através de cluster heads.
    
    :param sensor: Node sensor
    :param ch: Node destino (possível cluster head)
    :param cluster_heads: Conjunto de IDs dos cluster heads atuais
    :param beta: Peso para balancear distância e energia
    :param eps: Pequeno valor para evitar divisão por zero
    :return: Custo de associação ajustado
    """
    dij = dist(sensor, ch)
    
    # Custo base usando distância
    if isinstance(ch, Mote):
        Ej = ch.bateria
    else:
        Ej = float('inf')
    
    # Se energia é "infinita" (Station), custo depende só da distância
    if Ej == float('inf'):
        return beta * dij
    
    eps_val = float(eps) if eps is not None else 1e-9
    if eps_val <= 0:
        eps_val = 1e-9
    
    denom = Ej + eps_val
    if denom == 0.0:
        denom = eps_val
    
    # Custo base: combina distância e inverso da energia
    # O fator de energia é mais importante para evitar uso de nós com baixa bateria
    custo_energia = 1.0 / denom
    custo_base = beta * dij + (1.0 - beta) * custo_energia
    
    # Penalidade adicional para nós com bateria baixa
    # Isso evita que nós quase descarregados sejam usados como intermediários
    if Ej < 10.0:  # Se bateria está abaixo de 20% (10 de 50)
        custo_base *= (1.0 + (10.0 - Ej) / 10.0)  # Aumenta o custo gradualmente
    
    # Bônus para cluster heads: reduz o custo se o destino é cluster head
    # Isso incentiva o roteamento através dos cluster heads selecionados
    if ch.id in cluster_heads:
        custo_base *= 0.7  # 30% de desconto para cluster heads
    
    return custo_base


def consumir_energia_com_rotacao(sensor, ch, cluster_heads, beta=0.5, custo_base=0.01):
    """
    Consome energia do sensor e do cluster head de forma balanceada.
    
    Cluster heads consomem mais energia pois coordenam o cluster,
    mas isso é compensado pela rotação.
    
    :param sensor: Node sensor
    :param ch: Node cluster head/destino
    :param cluster_heads: Conjunto de IDs dos cluster heads atuais
    :param beta: Peso para balancear distância e energia
    :param custo_base: Fator base de consumo de energia
    """
    dij = dist(sensor, ch)
    
    # Consumo proporcional à distância (modelo simplificado de transmissão)
    consumo_transmissao = custo_base * dij
    
    # Sensor (origem) consome energia para transmitir
    if isinstance(sensor, Mote) and sensor.bateria > 0:
        sensor.bateria -= consumo_transmissao
    
    # Cluster head (destino) consome energia adicional para agregar/receber
    # Cluster heads consomem um pouco mais por serem responsáveis pelo cluster
    if isinstance(ch, Mote) and ch.bateria > 0:
        if ch.id in cluster_heads:
            # CH consome mais por ser coordenador
            ch.bateria -= consumo_transmissao * 1.2
        else:
            # Nó intermediário consome menos
            ch.bateria -= consumo_transmissao * 0.5
