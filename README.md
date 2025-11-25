# Trab_Graphs

Implementação de algoritmos de grafos para análise de redes de sensores sem fio (WSN).

## Descrição

Este projeto compara o desempenho dos algoritmos de Kruskal e Prim para construção de árvores geradoras mínimas (MST) em redes de sensores sem fio, considerando:

- **Rotação de Cluster Heads**: Implementação baseada no protocolo LEACH para distribuir uniformemente o consumo de energia
- **Custo Energético**: Considera tanto a distância quanto a energia residual dos nós
- **Simulação de Descarga**: Simula o consumo de bateria ao longo de múltiplas rodadas

## Estrutura do Projeto

```
Trab_Graphs/
├── Implementação/
│   ├── run.py              # Script de execução principal
│   ├── funcoes/
│   │   ├── main.py         # Programa principal e comparação de algoritmos
│   │   ├── kruskal.py      # Algoritmo de Kruskal
│   │   ├── prim.py         # Algoritmo de Prim
│   │   ├── cluster.py      # Seleção e rotação de cluster heads
│   │   ├── node.py         # Classes Node, Mote e Station
│   │   ├── visualizacao.py # Leitura de dados de rede
│   │   └── README.md       # Documentação das funções
│   └── instancias/
│       ├── rede50.txt      # Rede com 50 sensores
│       ├── rede100.txt     # Rede com 100 sensores
│       ├── rede200.txt     # Rede com 200 sensores
│       └── rede400.txt     # Rede com 400 sensores
├── Info/                   # Documentação e referências
├── README.md               # Este arquivo
└── LICENSE
```

## Como Executar

```bash
cd Implementação
python run.py
```

O programa irá:
1. Exibir menu para seleção do arquivo de rede
2. Executar simulações com Kruskal e Prim
3. Mostrar comparação de desempenho entre os algoritmos

## Resultados

O programa compara os algoritmos em termos de:
- **Rodadas executadas**: Quantas rodadas cada algoritmo conseguiu manter a rede operacional
- **Motes ativos ao final**: Número de sensores com bateria restante
- **Bateria total restante**: Soma da energia restante em todos os sensores

## Algoritmos Implementados

### Kruskal
- Ordena arestas por custo energético
- Usa Union-Find para detectar ciclos
- Consome energia após adicionar cada aresta à MST

### Prim
- Começa pela estação base (vértice 0)
- Expande a MST selecionando a menor aresta disponível
- Consome energia após adicionar cada aresta à MST

### Rotação de Cluster Heads
- Seleciona cluster heads baseado em energia residual
- Implementa rotação por grupos a cada rodada
- Cluster heads recebem bônus no custo das arestas