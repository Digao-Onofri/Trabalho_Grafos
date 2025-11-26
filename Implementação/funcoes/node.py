import math

MAX_BATERIA = 50.00
MAX_RAIO = 100.00

# Classes

class Node():

    def __init__(self, id: int, x: float, y: float) -> None:
        self.__id = id
        self.__x = x
        self.__y = y

    @property
    def id(self) -> int:
        return self.__id
    
    @property
    def x(self) -> float:
        return self.__x
    
    @property
    def y(self) -> float:
        return self.__y

class Mote(Node):

    def __init__(self, id, x, y, bateria: float):
        super().__init__(id, x, y)
        self.__bateria = bateria

    @property
    def bateria(self) -> float:
        return self.__bateria
    
    @bateria.setter
    def bateria(self, value: float) -> None:
        self.__bateria = max(0.0, min(value, MAX_BATERIA))
    
    @property
    def bateriaPct(self) -> float:
        return (self.__bateria / MAX_BATERIA) * 100.0
    
    def consumir(self, distancia: float, fator: float = 1.0, custo_base: float = 0.01):
        consumo = custo_base * distancia * fator
        self.bateria -= consumo

class Station(Node):

    def __init__(self, id, x, y):
        super().__init__(id, x, y)

    @property
    def bateria(self) -> float:
        return MAX_BATERIA 
    
    @bateria.setter
    def bateria(self, value: float) -> None:
        pass 

def dist(a: Node, b: Node) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


