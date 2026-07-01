from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QSlider

class LabeledSlider(QWidget):
    """Combina un QLabel + QSlider + QDoubleSpinBox sincronizados,
    con un rango configurable. Emite valueChanged(float)."""

    valueChanged = pyqtSignal(float)

    def __init__(self, label: str, min_val: float, max_val: float,
                 default: float, step: float = 1.0, suffix: str = "", parent=None):
        super().__init__(parent)
        self._scale = 1000  # precisión interna del QSlider (entero)
        self.min_val = min_val
        self.max_val = max_val

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 4)
        outer.setSpacing(4)

        header = QHBoxLayout()
        self.title_label = QLabel(label)
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(min_val, max_val)
        self.value_spin.setSingleStep(step)
        self.value_spin.setDecimals(2)
        self.value_spin.setSuffix(f" {suffix}" if suffix else "")
        self.value_spin.setValue(default)
        self.value_spin.setFixedWidth(140)
        self.value_spin.setAlignment(Qt.AlignmentFlag.AlignRight)

        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.value_spin)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, self._scale)
        self.slider.setValue(self._to_slider(default))

        outer.addLayout(header)
        outer.addWidget(self.slider)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.value_spin.valueChanged.connect(self._on_spin_changed)

    def _to_slider(self, value: float) -> int:
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return int(ratio * self._scale)

    def _to_value(self, slider_pos: int) -> float:
        ratio = slider_pos / self._scale
        return self.min_val + ratio * (self.max_val - self.min_val)

    def _on_slider_changed(self, pos: int) -> None:
        value = self._to_value(pos)
        self.value_spin.blockSignals(True)
        self.value_spin.setValue(value)
        self.value_spin.blockSignals(False)
        self.valueChanged.emit(value)

    def _on_spin_changed(self, value: float) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(self._to_slider(value))
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)

    def value(self) -> float:
        return self.value_spin.value()
