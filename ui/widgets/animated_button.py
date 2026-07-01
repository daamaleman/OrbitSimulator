from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QVariantAnimation
from PyQt6.QtGui import QColor

class AnimatedButton(QPushButton):
    """Botón con animación suave de cambio de color al hacer hover."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._bg_color = QColor(21, 21, 27)
        self.default_color = QColor(21, 21, 27)
        self.hover_color = QColor(42, 42, 53)
        self.base_style = "border: none; border-radius: 6px; padding: 10px 16px; font-weight: 700; font-size: 13px;"
        
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(150)
        self.anim.valueChanged.connect(self._update_stylesheet)
        
    def set_colors(self, default_hex: str, hover_hex: str, text_color: str = "#000000"):
        self.default_color = QColor(default_hex)
        self.hover_color = QColor(hover_hex)
        self._bg_color = self.default_color
        self.base_style += f" color: {text_color};"
        self._update_stylesheet(self._bg_color)

    def _update_stylesheet(self, color: QColor):
        self._bg_color = color
        self.setStyleSheet(f"AnimatedButton {{ {self.base_style} background-color: {color.name()}; }}")

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._bg_color)
        self.anim.setEndValue(self.hover_color)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._bg_color)
        self.anim.setEndValue(self.default_color)
        self.anim.start()
        super().leaveEvent(event)
