from . import visualizacao as v
from . import kruskal as k
from . import prim as p
from . import conectividade as c
from .node import Mote, MAX_BATERIA
from .cluster import selecionar_cluster_heads
import copy
import os


def listar_arquivos_rede():
    """
    Lista todos os arquivos de rede disponíveis na pasta instancias.
    
    :return: Lista de nomes de arquivos de rede disponíveis
    """
    instancias_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../instancias")
    arquivos = []
    if os.path.exists(instancias_dir):
        for arquivo in sorted(os.listdir(instancias_dir)):
            if arquivo.startswith("rede") and arquivo.endswith(".txt"):
                arquivos.append(arquivo)
    return arquivos


def selecionar_arquivo_rede():
    """
    Exibe um menu para o usuário selecionar qual arquivo de rede usar.
    
    :return: Nome do arquivo selecionado
    """
    arquivos = listar_arquivos_rede()
    
    if not arquivos:
        print("Nenhum arquivo de rede encontrado!")
        return None
    
    print("\n" + "=" * 50)
    print("SELEÇÃO DE ARQUIVO DE REDE")
    print("=" * 50)
    print("\nArquivos disponíveis:")
    for i, arquivo in enumerate(arquivos, 1):
        print(f"  {i}. {arquivo}")
    print()
    
    while True:
        try:
            escolha = input(f"Selecione uma opção (1-{len(arquivos)}): ").strip()
            indice = int(escolha) - 1
            if 0 <= indice < len(arquivos):
                arquivo_selecionado = arquivos[indice]
                print(f"\n>>> Arquivo selecionado: {arquivo_selecionado}")
                return arquivo_selecionado
            else:
                print(f"Por favor, digite um número entre 1 e {len(arquivos)}")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
        except EOFError:
            # Se não houver entrada interativa, retorna o primeiro arquivo
            print(f"\n>>> Usando arquivo padrão: {arquivos[0]}")
            return arquivos[0]


def simular_descarga_kruskal(nodes, rodadas=5, beta=0.5, porcentagem_ch=0.1, verbose=True, usar_cluster_heads=True):
    """
    Simula a descarga de bateria dos nós ao longo de várias rodadas usando Kruskal.
    
    Pode usar rotação de cluster heads para distribuir energia uniformemente ou não.
    
    :param nodes: Lista de nós da rede
    :param rodadas: Número de rodadas de simulação
    :param beta: Peso para balancear distância e energia
    :param porcentagem_ch: Porcentagem de nós que serão cluster heads por rodada
    :param verbose: Se True, imprime detalhes da simulação
    :param usar_cluster_heads: Se True, usa rotação de cluster heads; se False, não usa
    :return: Número de rodadas executadas
    """
    modo_ch = "COM" if usar_cluster_heads else "SEM"
    if verbose:
        print("=" * 60)
        print(f"SIMULAÇÃO KRUSKAL {modo_ch} CLUSTER HEADS")
        print("=" * 60)
    
    rodadas_executadas = 0
    
    for rodada in range(1, rodadas + 1):
        # Seleciona cluster heads para esta rodada com rotação (ou conjunto vazio se não usar)
        if usar_cluster_heads:
            cluster_heads = selecionar_cluster_heads(nodes, porcentagem_ch, rodada)
        else:
            cluster_heads = set()
        
        if verbose and (rodada <= 5 or rodada % 100 == 0):
            print(f"\n--- RODADA {rodada} ---")
            if usar_cluster_heads:
                print(f"Cluster Heads selecionados: {sorted(cluster_heads)}")
        
        # Gera arestas e constrói MST considerando cluster heads
        arcs = k.geraArestas(nodes, beta, cluster_heads)
        mst = k.kruskal(nodes, arcs, beta, cluster_heads)
        
        # Conta motes ativos
        motes_ativos = 0
        total_bateria = 0
        for node in nodes:
            if isinstance(node, Mote):
                if node.bateria > 0:
                    motes_ativos += 1
                    total_bateria += node.bateria
        
        total_motes = len([n for n in nodes if isinstance(n, Mote)])
        
        if verbose and (rodada <= 5 or rodada % 100 == 0):
            print(f"\nEstado das baterias após rodada {rodada}:")
            for node in nodes:
                if isinstance(node, Mote):
                    status = "ATIVO" if node.bateria > 0 else "SEM BATERIA"
                    ch_marker = " [CH]" if node.id in cluster_heads else ""
                    print(f"  Mote {node.id}: {node.bateriaPct:.2f}% ({node.bateria:.2f}) - {status}{ch_marker}")
            
            print(f"\nMotes ativos: {motes_ativos}/{total_motes}")
            print(f"Bateria total restante: {total_bateria:.2f}")
            print(f"Arestas na MST: {len(mst)}")
        
        rodadas_executadas = rodada
        
        # Verifica se ainda há motes com bateria ou se não há mais arestas
        if motes_ativos == 0:
            if verbose:
                print(f"\n*** SIMULAÇÃO ENCERRADA NA RODADA {rodada}: Todos os motes ficaram sem bateria ***")
            break
        
        if len(mst) == 0:
            if verbose:
                print(f"\n*** SIMULAÇÃO ENCERRADA NA RODADA {rodada}: Não há mais arestas disponíveis na MST ***")
            break
    
    if verbose:
        print("\n" + "=" * 60)
        print(f"ESTATÍSTICAS FINAIS - KRUSKAL {modo_ch} CLUSTER HEADS")
        print("=" * 60)
        motes_ativos_final = 0
        bateria_final = 0
        for node in nodes:
            if isinstance(node, Mote):
                if node.bateria > 0:
                    motes_ativos_final += 1
                    bateria_final += node.bateria
        
        total_motes = len([n for n in nodes if isinstance(n, Mote)])
        print(f"Rodadas executadas: {rodadas_executadas}")
        print(f"Motes ativos ao final: {motes_ativos_final}/{total_motes}")
        print(f"Bateria total restante: {bateria_final:.2f}")
        print("=" * 60)
    
    return rodadas_executadas


def simular_descarga_prim(nodes, rodadas=5, beta=0.5, porcentagem_ch=0.1, verbose=True, usar_cluster_heads=True):
    """
    Simula a descarga de bateria dos nós ao longo de várias rodadas usando Prim.
    
    Pode usar rotação de cluster heads para distribuir energia uniformemente ou não.
    
    :param nodes: Lista de nós da rede
    :param rodadas: Número de rodadas de simulação
    :param beta: Peso para balancear distância e energia
    :param porcentagem_ch: Porcentagem de nós que serão cluster heads por rodada
    :param verbose: Se True, imprime detalhes da simulação
    :param usar_cluster_heads: Se True, usa rotação de cluster heads; se False, não usa
    :return: Número de rodadas executadas
    """
    modo_ch = "COM" if usar_cluster_heads else "SEM"
    if verbose:
        print("=" * 60)
        print(f"SIMULAÇÃO PRIM {modo_ch} CLUSTER HEADS")
        print("=" * 60)
    
    rodadas_executadas = 0
    
    for rodada in range(1, rodadas + 1):
        # Seleciona cluster heads para esta rodada com rotação (ou conjunto vazio se não usar)
        if usar_cluster_heads:
            cluster_heads = selecionar_cluster_heads(nodes, porcentagem_ch, rodada)
        else:
            cluster_heads = set()
        
        if verbose and (rodada <= 5 or rodada % 100 == 0):
            print(f"\n--- RODADA {rodada} ---")
            if usar_cluster_heads:
                print(f"Cluster Heads selecionados: {sorted(cluster_heads)}")
        
        # Gera arestas e constrói MST usando Prim
        arcs = p.geraArestas(nodes, beta, cluster_heads)
        mst = p.prim(nodes, arcs, beta, cluster_heads)
        
        # Conta motes ativos
        motes_ativos = 0
        total_bateria = 0
        for node in nodes:
            if isinstance(node, Mote):
                if node.bateria > 0:
                    motes_ativos += 1
                    total_bateria += node.bateria
        
        total_motes = len([n for n in nodes if isinstance(n, Mote)])
        
        if verbose and (rodada <= 5 or rodada % 100 == 0):
            print(f"\nEstado das baterias após rodada {rodada}:")
            for node in nodes:
                if isinstance(node, Mote):
                    status = "ATIVO" if node.bateria > 0 else "SEM BATERIA"
                    ch_marker = " [CH]" if node.id in cluster_heads else ""
                    print(f"  Mote {node.id}: {node.bateriaPct:.2f}% ({node.bateria:.2f}) - {status}{ch_marker}")
            
            print(f"\nMotes ativos: {motes_ativos}/{total_motes}")
            print(f"Bateria total restante: {total_bateria:.2f}")
            print(f"Arestas na MST: {len(mst)}")
        
        rodadas_executadas = rodada
        
        # Verifica se ainda há motes com bateria ou se não há mais arestas
        if motes_ativos == 0:
            if verbose:
                print(f"\n*** SIMULAÇÃO ENCERRADA NA RODADA {rodada}: Todos os motes ficaram sem bateria ***")
            break
        
        if len(mst) == 0:
            if verbose:
                print(f"\n*** SIMULAÇÃO ENCERRADA NA RODADA {rodada}: Não há mais arestas disponíveis na MST ***")
            break
    
    if verbose:
        print("\n" + "=" * 60)
        print(f"ESTATÍSTICAS FINAIS - PRIM {modo_ch} CLUSTER HEADS")
        print("=" * 60)
        motes_ativos_final = 0
        bateria_final = 0
        for node in nodes:
            if isinstance(node, Mote):
                if node.bateria > 0:
                    motes_ativos_final += 1
                    bateria_final += node.bateria
        
        total_motes = len([n for n in nodes if isinstance(n, Mote)])
        print(f"Rodadas executadas: {rodadas_executadas}")
        print(f"Motes ativos ao final: {motes_ativos_final}/{total_motes}")
        print(f"Bateria total restante: {bateria_final:.2f}")
        print("=" * 60)
    
    return rodadas_executadas


def clonar_nodes(nodes):
    """
    Cria uma cópia profunda dos nós para simulação independente.
    
    :param nodes: Lista de nós original
    :return: Lista de nós clonada
    """
    return copy.deepcopy(nodes)


def comparar_algoritmos(instancia="rede50.txt", rodadas=2000, beta=0.5, porcentagem_ch=0.1, verbose=False):
    """
    Compara o desempenho de Kruskal e Prim em termos de número de rodadas.
    
    Executa simulações independentes com ambos os algoritmos, tanto com
    quanto sem cluster heads, e compara resultados.
    
    :param instancia: Nome do arquivo de instância
    :param rodadas: Número máximo de rodadas
    :param beta: Peso para balancear distância e energia
    :param porcentagem_ch: Porcentagem de nós que serão cluster heads
    :param verbose: Se True, imprime detalhes das simulações
    :return: Dicionário com resultados da comparação
    """
    print("\n" + "=" * 90)
    print("COMPARAÇÃO ENTRE ALGORITMOS KRUSKAL E PRIM (COM E SEM CLUSTER HEADS)")
    print("=" * 90)
    print(f"Instância: {instancia}")
    print(f"Rodadas máximas: {rodadas}")
    print(f"Beta: {beta}")
    print(f"Porcentagem de Cluster Heads: {porcentagem_ch * 100}%")
    print("=" * 90)
    
    # Carrega nós para Kruskal COM cluster heads
    nodes_kruskal_ch = v.leitura(instancia)
    total_motes = len([n for n in nodes_kruskal_ch if isinstance(n, Mote)])
    c.exibir_relatorio_robustez(nodes_kruskal_ch)
    
    # Clona nós para as outras simulações (simulações independentes)
    nodes_kruskal_sem_ch = clonar_nodes(nodes_kruskal_ch)
    nodes_prim_ch = clonar_nodes(nodes_kruskal_ch)
    nodes_prim_sem_ch = clonar_nodes(nodes_kruskal_ch)
    
    print(f"\nTotal de motes: {total_motes}")
    print("-" * 90)
    
    # Simulação com Kruskal COM cluster heads
    print("\n>>> Executando simulação com KRUSKAL COM Cluster Heads...")
    rodadas_kruskal_ch = simular_descarga_kruskal(nodes_kruskal_ch, rodadas, beta, porcentagem_ch, verbose, usar_cluster_heads=True)
    
    # Simulação com Kruskal SEM cluster heads
    print("\n>>> Executando simulação com KRUSKAL SEM Cluster Heads...")
    rodadas_kruskal_sem_ch = simular_descarga_kruskal(nodes_kruskal_sem_ch, rodadas, beta, porcentagem_ch, verbose, usar_cluster_heads=False)
    
    # Simulação com Prim COM cluster heads
    print("\n>>> Executando simulação com PRIM COM Cluster Heads...")
    rodadas_prim_ch = simular_descarga_prim(nodes_prim_ch, rodadas, beta, porcentagem_ch, verbose, usar_cluster_heads=True)
    
    # Simulação com Prim SEM cluster heads
    print("\n>>> Executando simulação com PRIM SEM Cluster Heads...")
    rodadas_prim_sem_ch = simular_descarga_prim(nodes_prim_sem_ch, rodadas, beta, porcentagem_ch, verbose, usar_cluster_heads=False)
    
    # Calcula bateria final restante e motes ativos para cada simulação
    bateria_final_kruskal_ch = sum(n.bateria for n in nodes_kruskal_ch if isinstance(n, Mote))
    bateria_final_kruskal_sem_ch = sum(n.bateria for n in nodes_kruskal_sem_ch if isinstance(n, Mote))
    bateria_final_prim_ch = sum(n.bateria for n in nodes_prim_ch if isinstance(n, Mote))
    bateria_final_prim_sem_ch = sum(n.bateria for n in nodes_prim_sem_ch if isinstance(n, Mote))
    
    motes_ativos_kruskal_ch = sum(1 for n in nodes_kruskal_ch if isinstance(n, Mote) and n.bateria > 0)
    motes_ativos_kruskal_sem_ch = sum(1 for n in nodes_kruskal_sem_ch if isinstance(n, Mote) and n.bateria > 0)
    motes_ativos_prim_ch = sum(1 for n in nodes_prim_ch if isinstance(n, Mote) and n.bateria > 0)
    motes_ativos_prim_sem_ch = sum(1 for n in nodes_prim_sem_ch if isinstance(n, Mote) and n.bateria > 0)
    
    # Resultado da comparação
    print("\n" + "=" * 90)
    print("RESULTADO DA COMPARAÇÃO")
    print("=" * 90)
    print(f"{'Métrica':<35} {'Kruskal CH':>12} {'Kruskal':>12} {'Prim CH':>12} {'Prim':>12}")
    print("-" * 90)
    print(f"{'Rodadas executadas':<35} {rodadas_kruskal_ch:>12} {rodadas_kruskal_sem_ch:>12} {rodadas_prim_ch:>12} {rodadas_prim_sem_ch:>12}")
    print(f"{'Motes ativos ao final':<35} {motes_ativos_kruskal_ch:>12} {motes_ativos_kruskal_sem_ch:>12} {motes_ativos_prim_ch:>12} {motes_ativos_prim_sem_ch:>12}")
    print(f"{'Bateria total restante':<35} {bateria_final_kruskal_ch:>12.2f} {bateria_final_kruskal_sem_ch:>12.2f} {bateria_final_prim_ch:>12.2f} {bateria_final_prim_sem_ch:>12.2f}")
    print("-" * 90)
    
    # Comparações entre abordagens
    print("\n" + "-" * 90)
    print("ANÁLISE COMPARATIVA")
    print("-" * 90)
    
    # Kruskal: Com CH vs Sem CH
    dif_kruskal = rodadas_kruskal_ch - rodadas_kruskal_sem_ch
    if dif_kruskal > 0:
        print(f"KRUSKAL: COM Cluster Heads executou {dif_kruskal} rodadas A MAIS que SEM Cluster Heads")
    elif dif_kruskal < 0:
        print(f"KRUSKAL: SEM Cluster Heads executou {-dif_kruskal} rodadas A MAIS que COM Cluster Heads")
    else:
        print("KRUSKAL: Ambas abordagens executaram o MESMO número de rodadas")
    
    # Prim: Com CH vs Sem CH
    dif_prim = rodadas_prim_ch - rodadas_prim_sem_ch
    if dif_prim > 0:
        print(f"PRIM: COM Cluster Heads executou {dif_prim} rodadas A MAIS que SEM Cluster Heads")
    elif dif_prim < 0:
        print(f"PRIM: SEM Cluster Heads executou {-dif_prim} rodadas A MAIS que COM Cluster Heads")
    else:
        print("PRIM: Ambas abordagens executaram o MESMO número de rodadas")
    
    # Melhor algoritmo geral (Com CH)
    dif_com_ch = rodadas_kruskal_ch - rodadas_prim_ch
    if dif_com_ch > 0:
        print(f"\nCOM Cluster Heads: KRUSKAL executou {dif_com_ch} rodadas A MAIS que PRIM")
    elif dif_com_ch < 0:
        print(f"\nCOM Cluster Heads: PRIM executou {-dif_com_ch} rodadas A MAIS que KRUSKAL")
    else:
        print("\nCOM Cluster Heads: Ambos algoritmos executaram o MESMO número de rodadas")
    
    # Melhor algoritmo geral (Sem CH)
    dif_sem_ch = rodadas_kruskal_sem_ch - rodadas_prim_sem_ch
    if dif_sem_ch > 0:
        print(f"SEM Cluster Heads: KRUSKAL executou {dif_sem_ch} rodadas A MAIS que PRIM")
    elif dif_sem_ch < 0:
        print(f"SEM Cluster Heads: PRIM executou {-dif_sem_ch} rodadas A MAIS que KRUSKAL")
    else:
        print("SEM Cluster Heads: Ambos algoritmos executaram o MESMO número de rodadas")
    
    # Determina o vencedor geral
    todas_rodadas = {
        "Kruskal COM CH": rodadas_kruskal_ch,
        "Kruskal SEM CH": rodadas_kruskal_sem_ch,
        "Prim COM CH": rodadas_prim_ch,
        "Prim SEM CH": rodadas_prim_sem_ch
    }
    vencedor = max(todas_rodadas, key=todas_rodadas.get)
    
    print("\n" + "=" * 90)
    print(f">>> MELHOR DESEMPENHO: {vencedor} com {todas_rodadas[vencedor]} rodadas")
    print("=" * 90)
    
    return {
        "kruskal_com_ch": {
            "rodadas": rodadas_kruskal_ch,
            "motes_ativos": motes_ativos_kruskal_ch,
            "bateria_final": bateria_final_kruskal_ch
        },
        "kruskal_sem_ch": {
            "rodadas": rodadas_kruskal_sem_ch,
            "motes_ativos": motes_ativos_kruskal_sem_ch,
            "bateria_final": bateria_final_kruskal_sem_ch
        },
        "prim_com_ch": {
            "rodadas": rodadas_prim_ch,
            "motes_ativos": motes_ativos_prim_ch,
            "bateria_final": bateria_final_prim_ch
        },
        "prim_sem_ch": {
            "rodadas": rodadas_prim_sem_ch,
            "motes_ativos": motes_ativos_prim_sem_ch,
            "bateria_final": bateria_final_prim_sem_ch
        },
        "vencedor": vencedor
    }


def main():

    # Permite ao usuário selecionar qual arquivo de rede usar
    arquivo_rede = selecionar_arquivo_rede()
    
    if arquivo_rede is None:
        print("Erro: Nenhum arquivo de rede disponível.")
        return None

    # Executa comparação entre Kruskal e Prim
    comparar_algoritmos(arquivo_rede, rodadas=2000, porcentagem_ch=0.1)

    return None

if __name__ == "__main__":

    main()