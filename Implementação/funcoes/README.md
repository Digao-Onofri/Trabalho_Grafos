# Funções - Análise de Algoritmos de Roteamento em Redes de Sensores Sem Fio aplicados ao cenário de monitoramento florestal

Este módulo implementa algoritmos de grafos para redes de sensores sem fio, incluindo:
- Algoritmo de Kruskal para árvore geradora mínima
- Algoritmo de Prim para árvore geradora mínima
- Comparação de desempenho entre Kruskal e Prim
- Cálculo de custos energéticos
- Rotação de cluster heads

## Como Executar

### Método 1: Usando run.py (Recomendado)
```bash
cd Implementação
python run.py
```

### Método 2: Usando módulo Python
```bash
cd Implementação
python -m funcoes.main
```

## Estrutura dos Arquivos

- `main.py` - Programa principal com funções de simulação e comparação
- `node.py` - Classes Node, Mote e Station
- `arvoregeradora.py` - Implementação do algoritmo de Kruskal e de Prim
- `leitura.py` - Funções de leitura de arquivos de instância
- `cluster.py` - Módulo de seleção e rotação de cluster heads
- `conectividade.py` - Módulo de verificação de conectividade

## Funções e Classes

### node.py

**Constantes:**
- `MAX_BATERIA = 50.00` - Bateria máxima de um mote
- `MAX_RAIO = 100.00` - Raio máximo de comunicação

**Classes:**

- `Node` - Classe base para nós da rede
  - `__init__(self, id: int, x: float, y: float)` - Construtor
  - `id` (property) - Retorna o ID do nó
  - `x` (property) - Retorna coordenada X
  - `y` (property) - Retorna coordenada Y

- `Mote(Node)` - Classe para sensores (herda de Node)
  - `__init__(self, id, x, y, bateria: float)` - Construtor
  - `bateria` (property/setter) - Retorna/define nível de bateria
  - `bateriaPct` (property) - Retorna porcentagem de bateria
  - `consumir` (método) - Calcula gasto energético

- `Station(Node)` - Classe para estação rádio base (herda de Node)
  - `__init__(self, id, x, y)` - Construtor
  - `bateria` (property/setter) - Retorna bateria máxima (não consome)

**Funções:**
- `dist(a: Node, b: Node) -> float` - Calcula distância euclidiana entre dois nós

---

### arvoregeradora.py

**Funções:**
- `geraArestas(nodes: list[Node], beta=0.5, cluster_heads=None)` - Gera lista de arestas com custo energético ordenadas por peso
- `unionfind_init(n: int)` - Inicializa estrutura Union-Find, retorna (link, size)
- `find(link: list[int], x: int)` - Encontra representante do conjunto com compressão de caminho
- `union(link, size, a, b)` - Une dois conjuntos por rank, retorna True se união ocorreu
- `kruskal(nodes: list[Node], arcs: list[tuple], beta=0.5, cluster_heads=None)` - Constrói MST usando algoritmo de Kruskal com consumo de energia
- `prim(nodes: list[Node], arcs: list[tuple], beta=0.5, cluster_heads=None)` - Constrói MST usando algoritmo de Prim com consumo de energia

---

### cluster.py

**Funções:**
- `selecionar_cluster_heads(nodes, porcentagem=0.1, rodada=0)` - Seleciona cluster heads com rotação baseada em energia (estratégia similar ao LEACH)
- `calcular_custo_com_rotacao(sensor, ch, cluster_heads, beta=0.5, eps=0.0001)` - Calcula custo de associação considerando se destino é cluster head
- `consumir_energia_com_rotacao(sensor, ch, cluster_heads, beta=0.5, custo_base=0.01)` - Consome energia do sensor e cluster head de forma balanceada

---

### leitura.py

**Constantes:**
- `BASE_DIR` - Diretório base do módulo
- `DATA_DIR` - Diretório dos arquivos de instância

**Funções:**
- `leitura(instancia: str) -> list[Node]` - Lê arquivo de instância e retorna lista de nós (Station + Motes)

---

### main.py

**Funções:**
- `listar_arquivos_rede()` - Lista arquivos de rede disponíveis na pasta instancias
- `selecionar_arquivo_rede()` - Exibe menu para seleção do arquivo de rede
- `simular_descarga_kruskal(nodes, rodadas=5, beta=0.5, porcentagem_ch=0.1, verbose=True)` - Simula descarga de bateria usando Kruskal, retorna número de rodadas executadas
- `simular_descarga_prim(nodes, rodadas=5, beta=0.5, porcentagem_ch=0.1, verbose=True)` - Simula descarga de bateria usando Prim, retorna número de rodadas executadas
- `clonar_nodes(nodes)` - Cria cópia profunda dos nós para simulação independente
- `comparar_algoritmos(instancia="rede50.txt", rodadas=2000, beta=0.5, porcentagem_ch=0.1, verbose=False)` - Compara desempenho de Kruskal e Prim em número de rodadas, retorna dicionário com resultados
- `main()` - Função principal que executa a comparação de algoritmos

## Arquivos de Instância

Os arquivos de dados estão em `../instancias/`:
- `rede50.txt` - Rede com 50 motes
- `rede100.txt` - Rede com 100 motes
- `rede200.txt` - Rede com 200 motes
- `rede400.txt` - Rede com 400 motes
