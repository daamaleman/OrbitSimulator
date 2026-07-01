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
    Usa pyqtgraph.opengl.GLViewWidget.
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
        
        # Opcional: Agregar una grilla estelar/plana tenue
        grid = gl.GLGridItem()
        grid.scale(2, 2, 2)
        grid.setDepthValue(10)  # dibujar atras
        self.view.addItem(grid)

        # Scatters para cuerpos (no hay size/glow complejo en GLScatterPlotItem, es mas simple)
        self.bodies_scatter = gl.GLScatterPlotItem()
        self.bodies_scatter.setGLOptions('translucent')
        self.view.addItem(self.bodies_scatter)

        # Curvas de trayectoria (diccionario name -> GLLinePlotItem)
        self.trail_curves: dict = {}

        layout.addWidget(self.view)
        
        # Camara inicial
        self.view.setCameraPosition(distance=30, elevation=30, azimuth=45)

    def _get_gl_color(self, hex_color: str, alpha: float) -> tuple:
        """Convierte hex a (r, g, b, a) en rango 0-1"""
        col = QColor(hex_color)
        return (col.redF(), col.greenF(), col.blueF(), alpha)

    def update_bodies(self, bodies: List[CelestialBody]) -> None:
        """Refresca posiciones de los cuerpos en el espacio 3D."""
        pos = np.array([b.position for b in bodies])
        colors = np.array([self._get_gl_color(b.color, 1.0) for b in bodies])
        
        # Escala visual del tamaño segun la masa (px en pantalla)
        sizes = np.array([min(36.0, max(8.0, (b.mass / 100.0) * 16.0 + 8.0)) for b in bodies])
        
        self.bodies_scatter.setData(pos=pos, color=colors, size=sizes)

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
            
            if len(b.trail) > 1:
                pts = np.array(b.trail)
                curve.setData(pos=pts)
            else:
                # empty
                curve.setData(pos=np.zeros((0, 3)))

    def clear_trails(self) -> None:
        """Limpia todas las curvas de trayectoria."""
        for curve in self.trail_curves.values():
            curve.setData(pos=np.zeros((0, 3)))
