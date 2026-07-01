from dataclasses import dataclass, field
from typing import List, Tuple

from ui.theme import Palette

@dataclass
class CelestialBody:
    """
    Clase de Datos (Data Class) que representa un cuerpo celeste en el espacio.
    
    Se utiliza @dataclass de Python para generar automáticamente métodos mágicos 
    como __init__ y __repr__ basados en los atributos definidos.
    
    Atributos:
    ----------
    name : str
        El nombre identificador del cuerpo (ej. "Tierra", "Sol").
    mass : float
        La masa del cuerpo celeste. Fundamental para el cálculo de la fuerza de gravedad.
    position : List[float]
        Vector 3D de la posición actual del cuerpo en el espacio [x, y, z].
    velocity : List[float]
        Vector 3D de la velocidad actual del cuerpo [vx, vy, vz].
    color : str
        Color en formato hexadecimal (ej. "#FFFFFF") usado para el renderizado 3D.
    trail : List[Tuple[float, float, float]]
        Historial de las últimas posiciones. Se utiliza para dibujar la órbita (estela) visualmente.
    """
    name: str
    mass: float
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])   # [x, y, z]
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])   # [vx, vy, vz]
    color: str = Palette.BODY_1_COLOR
    trail: List[Tuple[float, float, float]] = field(default_factory=list)    # [x, y, z]

    def __post_init__(self):
        # Type enforcement
        self.mass = float(self.mass)
        self.position = [float(v) for v in self.position]
        self.velocity = [float(v) for v in self.velocity]
        # Ensure exactly 3 dimensions
        if len(self.position) != 3:
            self.position = [0.0, 0.0, 0.0]
        if len(self.velocity) != 3:
            self.velocity = [0.0, 0.0, 0.0]
            
        if self.mass <= 0:
            raise ValueError("Error de Validación (Física): La masa debe ser estrictamente mayor a cero (m > 0).")
