from dataclasses import dataclass, field
from typing import List, Tuple

from ui.theme import Palette

@dataclass
class CelestialBody:
    """
    Representa un cuerpo celeste dentro de la simulación.
    Actualizado a 3D.
    """
    name: str
    mass: float
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])   # [x, y, z]
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])   # [vx, vy, vz]
    color: str = Palette.BODY_1_COLOR
    trail: List[Tuple[float, float, float]] = field(default_factory=list)    # [x, y, z]
