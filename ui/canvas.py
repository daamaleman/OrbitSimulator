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
    Usa pyqtgraph.opengl.GLViewWidget con mallas reales 3D (esferas)
    y colores procedurales para simular texturas.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CanvasContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # GLViewWidget para 3D
        self.view = gl.GLViewWidget()
        bg = QColor(Palette.BG_PRIMARY)
        self.view.setBackgroundColor(bg)
        
        # Grilla estelar
        grid = gl.GLGridItem()
        grid.scale(2, 2, 2)
        grid.setDepthValue(10)
        self.view.addItem(grid)

        # Diccionarios de elementos 3D
        self.planet_meshes: dict = {}
        self.trail_curves: dict = {}

        # Generar mesh base en mayor resolucion (40x40) para mejores detalles
        self.base_sphere_data = gl.MeshData.sphere(rows=40, cols=40)

        layout.addWidget(self.view)
        
        # Camara inicial
        self.view.setCameraPosition(distance=50, elevation=30, azimuth=45)
        
        # Diccionario para mapear BodyName -> Preset (se deduce por el color aprox, pero lo ideal seria pasarlo)
        # Como no tenemos el preset name en el body, lo adivinamos por masa o simplemente
        # usaremos un mapeo rudimentario. Vamos a mapear por color para el procedural.
        self.color_preset_map = {
            "#FBBF24": "Sol",
            "#F97316": "Júpiter",
            "#3B82F6": "Tierra",
            "#EF4444": "Marte",
            "#D1D5DB": "Luna",
            Palette.BODY_1_COLOR: "Tierra", # Default aprox
            Palette.BODY_2_COLOR: "Marte",
        }

    def _get_gl_color(self, hex_color: str, alpha: float) -> tuple:
        col = QColor(hex_color)
        return (col.redF(), col.greenF(), col.blueF(), alpha)

    def _generate_procedural_colors(self, hex_color: str, meshdata: gl.MeshData) -> np.ndarray:
        """Genera colores por vértice simulando océanos, continentes y bandas."""
        verts = meshdata.vertexes()
        colors = np.zeros((len(verts), 4))
        preset = self.color_preset_map.get(hex_color.upper(), "Generico")
        
        for i, v in enumerate(verts):
            x, y, z = v
            r = np.sqrt(x*x + y*y + z*z)
            lat = np.arcsin(z / r) if r != 0 else 0
            lon = np.arctan2(y, x)
            
            if preset == "Tierra":
                noise = np.sin(5*lat) * np.cos(5*lon) + 0.5 * np.sin(10*lat)
                if noise > 0.2:
                    colors[i] = [0.13, 0.54, 0.13, 1.0] # Continente verde
                elif noise > 0.0:
                    colors[i] = [0.76, 0.70, 0.50, 1.0] # Arena / tierra seca
                elif lat > 1.2 or lat < -1.2:
                    colors[i] = [0.95, 0.95, 0.98, 1.0] # Polos nevados
                else:
                    colors[i] = [0.11, 0.35, 0.65, 1.0] # Océano profundo
                    
            elif preset == "Marte":
                noise = np.sin(8*lat) + np.cos(8*lon)
                if noise > 0.5:
                    colors[i] = [0.75, 0.25, 0.1, 1.0] # Polvo claro
                elif lat > 1.3 or lat < -1.3:
                    colors[i] = [0.9, 0.9, 0.9, 1.0] # Polos de hielo seco
                else:
                    colors[i] = [0.55, 0.15, 0.05, 1.0] # Rojo oscuro cráteres
                    
            elif preset == "Júpiter":
                # Bandas atmosféricas gaseosas
                noise = np.sin(12*lat) + 0.3 * np.sin(24*lat + lon*2)
                if noise > 0.6:
                    colors[i] = [0.7, 0.6, 0.5, 1.0]
                elif noise > -0.2:
                    colors[i] = [0.8, 0.7, 0.6, 1.0]
                else:
                    colors[i] = [0.6, 0.4, 0.3, 1.0]
                    
            elif preset == "Sol":
                noise = np.random.random()
                colors[i] = [1.0, 0.7 + 0.3 * noise, 0.0, 1.0] # Superificie solar inestable
                
            elif preset == "Luna":
                noise = np.sin(15*lat) * np.cos(15*lon)
                if noise > 0.5:
                    colors[i] = [0.4, 0.4, 0.4, 1.0] # Mares lunares oscuros
                else:
                    colors[i] = [0.6, 0.6, 0.6, 1.0] # Tierras altas
            else:
                colors[i] = self._get_gl_color(hex_color, 1.0)
                
        return colors

    def update_bodies(self, bodies: List[CelestialBody]) -> None:
        """Refresca posiciones y escala, con texturizado procedural."""
        for b in bodies:
            if b.name not in self.planet_meshes:
                # Copiar malla base
                import copy
                mdata = copy.deepcopy(self.base_sphere_data)
                
                # Asignar colores procedimentales
                v_colors = self._generate_procedural_colors(b.color, mdata)
                mdata.setVertexColors(v_colors)
                
                mesh = gl.GLMeshItem(meshdata=mdata, smooth=True, shader='shaded')
                mesh._mdata = mdata
                self.view.addItem(mesh)
                self.planet_meshes[b.name] = mesh
                # Guardamos el color procesado
                self.planet_meshes[b.name]._current_hex = b.color
            
            mesh = self.planet_meshes[b.name]
            
            # Si el preset/color cambio desde la UI, recalcular texturas procedurales
            if getattr(mesh, '_current_hex', None) != b.color:
                v_colors = self._generate_procedural_colors(b.color, mesh._mdata)
                mesh._mdata.setVertexColors(v_colors)
                mesh.meshDataChanged()
                mesh._current_hex = b.color
            
            # Escala astronómica visual
            # Si la masa es masiva (Sol, > 500) le damos gran tamaño, si es chica, mas chico
            if b.mass >= 1000:
                size = 12.0
            elif b.mass > 200:
                size = 5.0
            elif b.mass > 0.5:
                size = 2.0
            else:
                size = 0.8
                
            mesh.resetTransform()
            mesh.scale(size, size, size)
            mesh.translate(b.position[0], b.position[1], b.position[2])

    def update_trails(self, bodies: List[CelestialBody]) -> None:
        """Refresca las trayectorias 3D."""
        for b in bodies:
            if b.name not in self.trail_curves:
                col = self._get_gl_color(b.color, Palette.TRAIL_ALPHA / 255.0)
                curve = gl.GLLinePlotItem(color=col, width=1.5)
                curve.setGLOptions('translucent')
                self.view.addItem(curve)
                self.trail_curves[b.name] = curve
            
            curve = self.trail_curves[b.name]
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
