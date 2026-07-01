from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout, QPushButton, QFrame, QSizePolicy, QComboBox, QHBoxLayout
from PyQt6.QtGui import QPixmap

from ui.theme import Palette
from ui.widgets.labeled_slider import LabeledSlider

import os

class ControlPanel(QWidget):
    """
    Panel lateral con controles 3D, Presets y Logo.
    """

    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()

    preset1_changed = pyqtSignal(str)
    preset2_changed = pyqtSignal(str)
    
    mass1_changed = pyqtSignal(float)
    mass2_changed = pyqtSignal(float)
    distance_changed = pyqtSignal(float)
    time_factor_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ControlPanel")
        
        self.setMinimumWidth(340)
        self.setMaximumWidth(450)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 28, 24, 24)
        root.setSpacing(18)

        # --- Cabecera con Logo ---
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        logo_label = QLabel()
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        
        titles_layout = QVBoxLayout()
        title = QLabel("ORBIT SIMULATOR")
        title.setProperty("role", "title")
        subtitle = QLabel("Gravity Engine 3D")
        subtitle.setProperty("role", "subtitle")
        titles_layout.addWidget(title)
        titles_layout.addWidget(subtitle)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(titles_layout)
        header_layout.addStretch()

        root.addLayout(header_layout)
        root.addWidget(self._divider())

        # --- Grupo: Cuerpos Celestes y Presets ---
        bodies_group = QGroupBox("CUERPOS CELESTES")
        bodies_layout = QVBoxLayout()
        bodies_layout.setSpacing(16)

        # Preset 1
        preset1_layout = QHBoxLayout()
        preset1_layout.addWidget(QLabel("Cuerpo 1:"))
        self.preset1_combo = QComboBox()
        self.preset1_combo.addItems(["Personalizado", "Sol", "Júpiter", "Tierra", "Marte", "Luna"])
        self.preset1_combo.setCurrentText("Sol")
        preset1_layout.addWidget(self.preset1_combo)
        
        self.mass1_slider = LabeledSlider("Masa — 1", 0.01, 1000.0, 1000.0, step=1.0, suffix="M⊕")
        
        # Preset 2
        preset2_layout = QHBoxLayout()
        preset2_layout.addWidget(QLabel("Cuerpo 2:"))
        self.preset2_combo = QComboBox()
        self.preset2_combo.addItems(["Personalizado", "Sol", "Júpiter", "Tierra", "Marte", "Luna"])
        self.preset2_combo.setCurrentText("Tierra")
        preset2_layout.addWidget(self.preset2_combo)
        
        self.mass2_slider = LabeledSlider("Masa — 2", 0.01, 1000.0, 1.0, step=0.1, suffix="M⊕")
        self.distance_slider = LabeledSlider("Distancia", 1.0, 100.0, 15.0, step=0.1, suffix="UA")

        bodies_layout.addLayout(preset1_layout)
        bodies_layout.addWidget(self.mass1_slider)
        bodies_layout.addLayout(preset2_layout)
        bodies_layout.addWidget(self.mass2_slider)
        bodies_layout.addWidget(self.distance_slider)
        bodies_group.setLayout(bodies_layout)

        # --- Grupo: Simulación ---
        sim_group = QGroupBox("SIMULACIÓN")
        sim_layout = QVBoxLayout()
        sim_layout.setSpacing(16)

        self.time_factor_slider = LabeledSlider("Velocidad temporal", 0.1, 10.0, 1.0, step=0.1, suffix="x")
        sim_layout.addWidget(self.time_factor_slider)
        sim_group.setLayout(sim_layout)

        # --- Grupo: Controles de reproducción ---
        controls_group = QGroupBox("CONTROLES")
        controls_layout = QGridLayout()
        controls_layout.setSpacing(12)

        self.play_btn = QPushButton("▶  Play")
        self.play_btn.setObjectName("PlayButton")
        self.pause_btn = QPushButton("⏸  Pause")
        self.pause_btn.setObjectName("PauseButton")
        self.reset_btn = QPushButton("⟲  Reset")
        self.reset_btn.setObjectName("ResetButton")

        controls_layout.addWidget(self.play_btn, 0, 0, 1, 2)
        controls_layout.addWidget(self.pause_btn, 1, 0)
        controls_layout.addWidget(self.reset_btn, 1, 1)
        controls_group.setLayout(controls_layout)

        # --- Grupo: Estado ---
        status_group = QGroupBox("ESTADO")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        self.status_label = QLabel("Simulación detenida")
        self.status_label.setProperty("role", "value")
        self.time_label = QLabel("t = 0.00 s")
        self.time_label.setProperty("role", "value")
        self.time_label.setStyleSheet("color: #4ADE80;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.time_label)
        status_group.setLayout(status_layout)

        root.addWidget(bodies_group)
        root.addWidget(sim_group)
        root.addWidget(controls_group)
        root.addWidget(status_group)
        root.addStretch()

        self._connect_signals()

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setObjectName("Divider")
        line.setFrameShape(QFrame.Shape.HLine)
        return line

    def _connect_signals(self) -> None:
        self.play_btn.clicked.connect(self.play_clicked.emit)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)

        self.preset1_combo.currentTextChanged.connect(self.preset1_changed.emit)
        self.preset2_combo.currentTextChanged.connect(self.preset2_changed.emit)

        self.mass1_slider.valueChanged.connect(self.mass1_changed.emit)
        self.mass2_slider.valueChanged.connect(self.mass2_changed.emit)
        self.distance_slider.valueChanged.connect(self.distance_changed.emit)
        self.time_factor_slider.valueChanged.connect(self.time_factor_changed.emit)
