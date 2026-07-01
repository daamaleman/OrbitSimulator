class Palette:
    """Paleta centralizada del tema Deep Dark Ultra-Minimalista."""
    BG_PRIMARY = "#050508"        # Fondo principal negro/profundo
    BG_PANEL = "#09090C"          # Fondo del panel lateral
    BG_ELEVATED = "#0D0D11"       # Tarjetas / GroupBox
    BG_INPUT = "#15151B"          # Inputs / sliders track
    BORDER = "#1E1E26"            # Bordes muy sutiles
    BORDER_HOVER = "#2A2A35"      # Borde interactivo

    TEXT_PRIMARY = "#F8F8FA"
    TEXT_SECONDARY = "#8B8B9B"
    TEXT_MUTED = "#555566"

    ACCENT_PRIMARY = "#4D88FF"    
    ACCENT_PRIMARY_HOVER = "#739CFF"
    ACCENT_SECONDARY = "#FF5555"  
    ACCENT_SECONDARY_HOVER = "#FF7A7A"
    ACCENT_SUCCESS = "#22C55E"    
    ACCENT_SUCCESS_HOVER = "#4ADE80"
    ACCENT_WARNING = "#F59E0B"    
    ACCENT_WARNING_HOVER = "#FBBF24"

    BODY_1_COLOR = "#4D88FF"
    BODY_2_COLOR = "#FF5555"
    TRAIL_ALPHA = 120              # Max alpha para el trail 3D

def build_stylesheet() -> str:
    p = Palette
    # Quitamos transition que causaba warnings, forzamos font-size
    return f"""
    * {{
        font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
        font-size: 13px;
    }}

    QMainWindow, QWidget {{
        background-color: {p.BG_PRIMARY};
        color: {p.TEXT_PRIMARY};
    }}

    #ControlPanel {{
        background-color: {p.BG_PANEL};
        border-left: 1px solid {p.BORDER};
    }}

    #CanvasContainer {{
        background-color: {p.BG_PRIMARY};
    }}

    QGroupBox {{
        background-color: {p.BG_ELEVATED};
        border: none;
        border-radius: 8px;
        margin-top: 24px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
        color: {p.TEXT_SECONDARY};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 0px;
        padding: 0 4px;
        color: {p.TEXT_PRIMARY};
        font-size: 12px;
        letter-spacing: 1px;
    }}

    QLabel {{
        color: {p.TEXT_SECONDARY};
        background: transparent;
        border: none;
    }}

    QLabel[role="value"] {{
        color: {p.TEXT_PRIMARY};
        font-family: 'Cascadia Code', 'Consolas', monospace;
        font-size: 14px;
        font-weight: 600;
    }}

    QLabel[role="title"] {{
        color: {p.TEXT_PRIMARY};
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 1px;
    }}
    
    QLabel[role="subtitle"] {{
        color: {p.TEXT_MUTED};
        font-size: 12px;
        font-weight: 500;
    }}

    QSlider::groove:horizontal {{
        height: 4px;
        background: {p.BG_INPUT};
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        background: {p.ACCENT_PRIMARY};
        width: 12px;
        height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {p.ACCENT_PRIMARY_HOVER};
    }}

    QSlider::sub-page:horizontal {{
        background: {p.ACCENT_PRIMARY};
        border-radius: 2px;
    }}

    QDoubleSpinBox, QComboBox {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 6px;
        padding: 6px 10px;
        color: {p.TEXT_PRIMARY};
        font-family: 'Cascadia Code', 'Consolas', monospace;
        selection-background-color: {p.ACCENT_PRIMARY};
    }}

    QDoubleSpinBox:hover, QComboBox:hover {{
        border: 1px solid {p.BORDER_HOVER};
    }}

    QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {p.ACCENT_PRIMARY};
        background-color: {p.BG_ELEVATED};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {p.BG_ELEVATED};
        border: 1px solid {p.BORDER};
        selection-background-color: {p.ACCENT_PRIMARY};
        outline: none;
    }}

    QPushButton {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.BORDER};
        border-radius: 6px;
        padding: 10px 16px;
        color: {p.TEXT_PRIMARY};
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        border: 1px solid {p.ACCENT_PRIMARY};
        background-color: {p.BG_ELEVATED};
    }}

    QPushButton:pressed {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.ACCENT_PRIMARY_HOVER};
    }}

    QPushButton#PlayButton {{
        background-color: {p.ACCENT_SUCCESS};
        color: #000000;
        border: none;
        font-weight: 700;
    }}
    
    QPushButton#PlayButton:hover {{
        background-color: {p.ACCENT_SUCCESS_HOVER};
    }}

    QPushButton#PauseButton {{
        background-color: {p.ACCENT_WARNING};
        color: #000000;
        border: none;
        font-weight: 700;
    }}
    
    QPushButton#PauseButton:hover {{
        background-color: {p.ACCENT_WARNING_HOVER};
    }}

    QPushButton#ResetButton {{
        background-color: transparent;
        color: {p.ACCENT_SECONDARY};
        border: 1px solid {p.ACCENT_SECONDARY};
    }}
    
    QPushButton#ResetButton:hover {{
        background-color: {p.BG_INPUT};
        border: 1px solid {p.ACCENT_SECONDARY_HOVER};
        color: {p.ACCENT_SECONDARY_HOVER};
    }}

    QFrame#Divider {{
        background-color: {p.BORDER};
        max-height: 1px;
        min-height: 1px;
        border: none;
    }}

    QSplitter::handle {{
        background-color: {p.BORDER};
        width: 1px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {p.ACCENT_PRIMARY};
    }}
    """
