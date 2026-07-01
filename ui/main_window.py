from typing import List
import numpy as np

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtGui import QIcon

from models.celestial_body import CelestialBody
from physics.engine import PhysicsEngine
from ui.canvas import SimulationCanvas
from ui.control_panel import ControlPanel
from ui.theme import Palette

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbit Simulator 3D")
        
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        self.canvas = SimulationCanvas()
        self.control_panel = ControlPanel()

        splitter.addWidget(self.canvas)
        splitter.addWidget(self.control_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([1200, 400])

        layout.addWidget(splitter)

        # Planetas base (se actualizaran por los presets inmediatamente despues)
        self.body1 = CelestialBody(name="Body 1", mass=1000.0, position=[-7.5, 0.0, 0.0], color="#FBBF24")
        self.body2 = CelestialBody(name="Body 2", mass=1.0, position=[7.5, 0.0, 0.0], color="#5B8CFF")
        self.engine = PhysicsEngine(bodies=[self.body1, self.body2])

        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(16)
        self.sim_timer.timeout.connect(self._on_timer_tick)

        self._connect_ui_to_engine()
        
        # Aplicamos los presets iniciales elegidos en el control panel
        self._apply_preset(1, self.control_panel.preset1_combo.currentText())
        self._apply_preset(2, self.control_panel.preset2_combo.currentText())
        self._setup_initial_conditions()
        
        # Pantalla completa real
        self.showMaximized()

    def _apply_preset(self, body_index: int, preset_name: str) -> None:
        """Aplica un preset planetario a un cuerpo."""
        presets = {
            "Sol": {"mass": 1000.0, "color": "#FBBF24"},
            "Júpiter": {"mass": 317.0, "color": "#F97316"},
            "Tierra": {"mass": 1.0, "color": "#3B82F6"},
            "Marte": {"mass": 0.1, "color": "#EF4444"},
            "Luna": {"mass": 0.01, "color": "#D1D5DB"}
        }
        
        if preset_name in presets:
            data = presets[preset_name]
            body = self.body1 if body_index == 1 else self.body2
            slider = self.control_panel.mass1_slider if body_index == 1 else self.control_panel.mass2_slider
            combo = self.control_panel.preset1_combo if body_index == 1 else self.control_panel.preset2_combo
            
            # Bloquear señales para que no desencadene recalculos infinitos al actualizar el slider
            slider.blockSignals(True)
            slider.value_spin.setValue(data["mass"])
            slider.blockSignals(False)
            
            body.mass = data["mass"]
            body.color = data["color"]
            
            # Recalcular posiciones si estamos en t=0
            if not self.engine.is_running and self.engine.elapsed_time == 0.0:
                self.engine._sync_to_internal()
                self._setup_initial_conditions()
        else:
            # Personalizado: solo cambiamos el color a uno generico, no la masa actual
            body = self.body1 if body_index == 1 else self.body2
            body.color = Palette.BODY_1_COLOR if body_index == 1 else Palette.BODY_2_COLOR

    def _connect_ui_to_engine(self) -> None:
        cp = self.control_panel

        cp.play_clicked.connect(self._on_play)
        cp.pause_clicked.connect(self._on_pause)
        cp.reset_clicked.connect(self._on_reset)

        cp.preset1_changed.connect(lambda text: self._apply_preset(1, text))
        cp.preset2_changed.connect(lambda text: self._apply_preset(2, text))

        cp.mass1_changed.connect(self._on_mass1_changed)
        cp.mass2_changed.connect(self._on_mass2_changed)
        cp.distance_changed.connect(self._on_distance_changed)
        cp.time_factor_changed.connect(self.engine.set_time_factor)
        
        self.engine.step_computed.connect(self._on_step_computed)

    def _setup_initial_conditions(self) -> None:
        dist = self.control_panel.distance_slider.value()
        m1 = self.body1.mass
        m2 = self.body2.mass
        
        # Posicion 3D (Z=0, X=[-d/2, d/2], Y=0)
        self.body1.position = [-dist / 2, 0.0, 0.0]
        self.body2.position = [dist / 2, 0.0, 0.0]
        
        G = PhysicsEngine.G_CONSTANT
        total_mass = m1 + m2
        v_rel = np.sqrt(G * total_mass / dist)
        
        vy1 = -(m2 / total_mass) * v_rel
        vy2 = (m1 / total_mass) * v_rel
        
        # Le damos un ligero giro en Z para que se vea 3D, un 10% de la velocidad se va a Z
        vz1 = vy1 * 0.1
        vz2 = vy2 * 0.1
        vy1 = vy1 * 0.99
        vy2 = vy2 * 0.99
        
        self.body1.velocity = [0.0, vy1, vz1]
        self.body2.velocity = [0.0, vy2, vz2]
        
        self.engine._sync_to_internal()
        self.canvas.update_bodies([self.body1, self.body2])

    def _on_play(self) -> None:
        self.engine.start()
        self.control_panel.status_label.setText("Simulando 3D…")
        self.control_panel.status_label.setStyleSheet("color: #22C55E;")
        self.sim_timer.start()

    def _on_pause(self) -> None:
        self.engine.pause()
        self.control_panel.status_label.setText("Pausado")
        self.control_panel.status_label.setStyleSheet("color: #F59E0B;")
        self.sim_timer.stop()

    def _on_reset(self) -> None:
        self.engine.pause()
        self.sim_timer.stop()
        self.engine.reset()
        self.canvas.clear_trails()
        self._setup_initial_conditions()
        self.control_panel.status_label.setText("Simulación detenida")
        self.control_panel.status_label.setStyleSheet("color: #F8F8FA;")
        self.control_panel.time_label.setText("t = 0.00 s")

    def _on_mass1_changed(self, value: float) -> None:
        self.body1.mass = value
        self.control_panel.preset1_combo.blockSignals(True)
        self.control_panel.preset1_combo.setCurrentText("Personalizado")
        self.control_panel.preset1_combo.blockSignals(False)
        self.engine._sync_to_internal()
        if not self.engine.is_running and self.engine.elapsed_time == 0.0:
            self._setup_initial_conditions()

    def _on_mass2_changed(self, value: float) -> None:
        self.body2.mass = value
        self.control_panel.preset2_combo.blockSignals(True)
        self.control_panel.preset2_combo.setCurrentText("Personalizado")
        self.control_panel.preset2_combo.blockSignals(False)
        self.engine._sync_to_internal()
        if not self.engine.is_running and self.engine.elapsed_time == 0.0:
            self._setup_initial_conditions()

    def _on_distance_changed(self, value: float) -> None:
        if not self.engine.is_running and self.engine.elapsed_time == 0.0:
            self._setup_initial_conditions()

    def _on_timer_tick(self) -> None:
        self.engine.integrate_step()
        
    def _on_step_computed(self, bodies: List[CelestialBody]) -> None:
        self.canvas.update_bodies(bodies)
        self.canvas.update_trails(bodies)
        self.control_panel.time_label.setText(f"t = {self.engine.elapsed_time:.2f} s")
