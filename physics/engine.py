from typing import List, Tuple, Optional
import numpy as np
from PyQt6.QtCore import pyqtSignal, QObject
from models.celestial_body import CelestialBody

class PhysicsEngine(QObject):
    """
    Motor de cálculo físico basado en la Ley de Gravitación Universal de Newton.
    Actualizado a integración Velocity Verlet y soporte 3D.
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
        n = len(self._masses)
        accelerations = np.zeros_like(positions)
        for i in range(n):
            for j in range(n):
                if i != j:
                    delta = positions[j] - positions[i]
                    dist = np.linalg.norm(delta)
                    if dist < self.MIN_DISTANCE:
                        dist = self.MIN_DISTANCE
                    
                    acc_mag = self.G_CONSTANT * self._masses[j] / (dist**2)
                    accelerations[i] += acc_mag * (delta / dist)
        return accelerations

    def integrate_step(self) -> None:
        if not self.bodies:
            return

        self._masses = np.array([b.mass for b in self.bodies], dtype=float)

        effective_dt = self.dt * self.time_factor
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
