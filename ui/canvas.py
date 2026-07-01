from typing import List
import numpy as np

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor

import pyqtgraph.opengl as gl

from ui.theme import Palette
from models.celestial_body import CelestialBody

class SimulationCanvas(QWidget):
    """
    Lienzo dominante que representa el espacio exterior en 3D.
    Usa pyqtgraph.opengl.GLViewWidget con mallas reales 3D (esferas).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CanvasContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # GLViewWidget para 3D
        self.view = gl.GLViewWidget()
        
        # Configurar color de fondo (rgb)
        bg = QColor(Palette.BG_PRIMARY)
        self.view.setBackgroundColor(bg)
        
        # Grilla estelar/plana tenue
        grid = gl.GLGridItem()
        grid.scale(2, 2, 2)
        grid.setDepthValue(10)  # dibujar atras
        self.view.addItem(grid)

        # Diccionarios de elementos 3D
        self.planet_meshes: dict = {}
        self.trail_curves: dict = {}

        # Generar mesh de esfera base, reutilizable
        self.base_sphere_data = gl.MeshData.sphere(rows=20, cols=20)

        layout.addWidget(self.view)
        
        # Camara inicial
        self.view.setCameraPosition(distance=30, elevation=30, azimuth=45)

    def _get_gl_color(self, hex_color: str, alpha: float) -> tuple:
        """Convierte hex a (r, g, b, a) en rango 0-1"""
        col = QColor(hex_color)
        return (col.redF(), col.greenF(), col.blueF(), alpha)

    def update_bodies(self, bodies: List[CelestialBody]) -> None:
        """Refresca posiciones de los cuerpos y escala sus esferas 3D."""
        for b in bodies:
            if b.name not in self.planet_meshes:
                color = self._get_gl_color(b.color, 1.0)
                mesh = gl.GLMeshItem(meshdata=self.base_sphere_data, smooth=True, color=color, shader='shaded')
                self.view.addItem(mesh)
                self.planet_meshes[b.name] = mesh
            
            mesh = self.planet_meshes[b.name]
            
            # Escala basada en la masa (para visualizacion)
            size = min(4.0, max(0.5, (b.mass / 1000.0) * 3.0 + 0.5))
            
            # Actualizamos transformacion abs: resetear matriz, escalar, mover
            mesh.resetTransform()
            mesh.scale(size, size, size)
            mesh.translate(b.position[0], b.position[1], b.position[2])
            
            # Si el color cambio desde la UI
            new_color = self._get_gl_color(b.color, 1.0)
            mesh.setColor(new_color)

    def update_trails(self, bodies: List[CelestialBody]) -> None:
        """Refresca las trayectorias 3D."""
        for b in bodies:
            if b.name not in self.trail_curves:
                col = self._get_gl_color(b.color, Palette.TRAIL_ALPHA / 255.0)
                curve = gl.GLLinePlotItem(color=col, width=2.0)
                curve.setGLOptions('translucent')
                self.view.addItem(curve)
                self.trail_curves[b.name] = curve
            
            curve = self.trail_curves[b.name]
            
            # Actualizamos el color si cambio en la UI
            col = self._get_gl_color(b.color, Palette.TRAIL_ALPHA / 255.0)
            
            if len(b.trail) > 1:
                pts = np.array(b.trail)
                curve.setData(pos=pts, color=col)
            else:
                curve.setData(pos=np.zeros((0, 3)))

    def clear_trails(self) -> None:
        """Limpia todas las curvas de trayectoria."""
        for curve in self.trail_curves.values():
            curve.setData(pos=np.zeros((0, 3)))
