from typing import List, Tuple, Optional
import numpy as np
from PyQt6.QtCore import pyqtSignal, QObject
from models.celestial_body import CelestialBody

class PhysicsEngine(QObject):
    """
    [DOCUMENTACIÓN DE FÍSICA Y MATEMÁTICAS]
    =======================================
    Motor de cálculo físico principal. Controla el avance del tiempo y la gravedad.
    
    1. Integración Cinemática (Velocity Verlet):
       - ¿Dónde se usa?: En el método `integrate_step()` de esta misma clase.
       - ¿Cómo se usa?: Se utiliza para actualizar la posición `r(t+dt)` y la 
         velocidad `v(t+dt)` en pasos discretos de tiempo (`dt`). A diferencia del
         método de Euler, Velocity Verlet es un "integrador simpléctico", lo que significa
         que conserva la energía mecánica total del sistema orbital a largo plazo. 
         Evita que los planetas salgan disparados al infinito por acumulación de errores de 
         punto flotante.
         
    2. Singularidades y Validación (Anti-Infinito):
       - ¿Dónde se usa?: En el método `_compute_accelerations()` de esta misma clase.
       - ¿Cómo se usa?: La Ley de Gravitación dice que F es inversamente proporcional
         a la distancia al cuadrado (r^2). Si r=0 (colisión exacta), la fuerza tiende 
         al infinito matemático. En el código, detectamos si `dist < MIN_DISTANCE` y 
         usamos la palabra clave `continue` para detener la atracción, emulando un choque 
         y salvando al procesador de una división por cero.
         
    Esta clase emite una señal `step_computed` cada vez que calcula un nuevo
    fotograma matemático para ser dibujado en la UI (Arquitectura Model-View).
    """

    step_computed = pyqtSignal(list)

    G_CONSTANT = 0.005
    MIN_DISTANCE = 0.5

    def __init__(self, bodies: Optional[List[CelestialBody]] = None):
        super().__init__()
        self.bodies: List[CelestialBody] = bodies or []
        self.time_factor: float = 1.0     
        self.dt: float = 0.01             
        self.is_running: bool = False
        self.elapsed_time: float = 0.0
        
        # Vectores internos para computación rapida con numpy, ahora en 3D
        self._positions = np.zeros((0, 3))
        self._velocities = np.zeros((0, 3))
        self._masses = np.zeros(0)
        self._accelerations = np.zeros((0, 3))
        
        if self.bodies:
            self._sync_to_internal()

    def _sync_to_internal(self) -> None:
        self._positions = np.array([b.position for b in self.bodies], dtype=float)
        self._velocities = np.array([b.velocity for b in self.bodies], dtype=float)
        self._masses = np.array([b.mass for b in self.bodies], dtype=float)
        self._accelerations = self._compute_accelerations(self._positions)

    def _sync_to_external(self) -> None:
        for i, b in enumerate(self.bodies):
            b.position = self._positions[i].tolist()
            b.velocity = self._velocities[i].tolist()

    def set_bodies(self, bodies: List[CelestialBody]) -> None:
        self.bodies = bodies
        self._sync_to_internal()

    def set_time_factor(self, factor: float) -> None:
        self.time_factor = factor

    def _compute_accelerations(self, positions: np.ndarray) -> np.ndarray:
        """
        [DOCUMENTACIÓN DE FÍSICA Y MATEMÁTICAS]
        =======================================
        Calcula la aceleración neta sobre cada cuerpo debida a la gravedad mutua de TODOS los demás.
        
        - Ley Gravitacional (Newton): F = G * (m1 * m2) / r^2
        - Despejando Aceleración (a = F / m1): a = G * m2 / r^2
        
        ¿Dónde y cómo se aplica en el código?
        - `delta = positions[j] - positions[i]` obtiene el vector distancia en el espacio 3D.
        - `dist = np.linalg.norm(delta)` es nuestra r (magnitud euclidiana pitagórica).
        - `acc_mag = self.G_CONSTANT * self._masses[j] / (dist**2)` es literalmente la ecuación 
          'a = G * M / r^2' trasladada a código puro, procesada de forma vectorizada gracias a Numpy.
        """
        n = len(self._masses)
        accelerations = np.zeros_like(positions)
        for i in range(n):
            for j in range(n):
                if i != j:
                    # delta es el vector distancia entre el cuerpo j (atractor) y i (atraído)
                    delta = positions[j] - positions[i]
                    # linalg.norm calcula la magnitud del vector (distancia euclidiana r)
                    dist = np.linalg.norm(delta)
                    
                    # Validación de Singularidad: si colisionan (r ~ 0), evitamos dividir por cero
                    if dist < self.MIN_DISTANCE:
                        continue
                    
                    # Magnitud de la aceleración: a = G * M / r^2
                    acc_mag = self.G_CONSTANT * self._masses[j] / (dist**2)
                    
                    # Protect against division by zero or infinite forces
                    acc_mag = np.nan_to_num(acc_mag, posinf=0.0, neginf=0.0)
                    
                    # Direccionamos la aceleración multiplicándola por el vector unitario (delta / dist)
                    vec = (delta / dist) * acc_mag
                    accelerations[i] += np.nan_to_num(vec, posinf=0.0, neginf=0.0)
        return accelerations

    def integrate_step(self) -> None:
        if not self.bodies:
            return

        self._masses = np.array([b.mass for b in self.bodies], dtype=float)

        effective_dt = self.dt * self.time_factor
        
        # Validación de Diferencial de Tiempo: dt debe ser estrictamente positivo
        if effective_dt <= 0:
            return
        MAX_DT_PER_STEP = 0.01
        num_steps = max(1, int(np.ceil(effective_dt / MAX_DT_PER_STEP)))
        step_dt = effective_dt / num_steps

        for _ in range(num_steps):
            v_mid = self._velocities + 0.5 * self._accelerations * step_dt
            self._positions += v_mid * step_dt
            new_accelerations = self._compute_accelerations(self._positions)
            self._velocities = v_mid + 0.5 * new_accelerations * step_dt
            self._accelerations = new_accelerations

        self.elapsed_time += effective_dt
        self._sync_to_external()
        
        for b in self.bodies:
            b.trail.append(tuple(b.position))
            if len(b.trail) > 2000:
                b.trail.pop(0)

        self.step_computed.emit(self.bodies)

    def start(self) -> None:
        self.is_running = True

    def pause(self) -> None:
        self.is_running = False

    def reset(self) -> None:
        self.elapsed_time = 0.0
        for b in self.bodies:
            b.trail.clear()
        self._sync_to_internal()
