<div align="center">

# 🪐 Orbit Simulator - Edu Version
### Simulador 3D de Gravedad y Órbitas Planetarias

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-UI%20Framework-green.svg?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![OpenGL](https://img.shields.io/badge/OpenGL-3D%20Graphics-5586A4.svg?style=for-the-badge&logo=opengl&logoColor=white)](https://opengl.org)
[![NumPy](https://img.shields.io/badge/NumPy-Vectorized%20Math-013243.svg?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)

Un simulador físico-matemático construido desde cero para comprender la dinámica orbital, la ley de la gravitación universal y la generación procedural de texturas en entornos 3D.

</div>

---

## 📖 Acerca del Proyecto

**Orbit Simulator** es una aplicación de escritorio diseñada con propósitos educativos que simula la interacción gravitacional de múltiples cuerpos celestes en el espacio 3D. Combina una interfaz gráfica moderna (Deep Dark Ultra-Minimalista) con un motor físico propio impulsado por **Numpy** y renderizado por hardware a través de **PyOpenGL**.

Este proyecto no utiliza motores gráficos preconstruidos de terceros (como Unity o Unreal); toda la matemática, desde la cinemática de integración hasta la generación de texturas de planetas, está escrita e implementada en Python puro y expuesta para el aprendizaje.

---

## ✨ Características Principales

- 🚀 **Física N-Body en Tiempo Real**: Cálculo preciso de atracciones gravitacionales mutuas entre todos los cuerpos del sistema, vectorizado.
- 🎨 **Texturizado Procedural 3D**: Los planetas no usan imágenes JPG/PNG; sus superficies (océanos, nubes, cráteres lunares) se generan visualmente mediante ruido trigonométrico sobre mallas esféricas.
- 📐 **Integrador Velocity Verlet**: Método de integración numérico simpléctico que conserva la energía del sistema, evitando que las órbitas degeneren o los planetas salgan disparados por acumulación de errores de punto flotante a largo plazo.
- 🛡️ **Protección Anti-Singularidad (Colisiones)**: Los choques directos entre planetas (distancia 0) no rompen el motor, manejando las singularidades de forma matemática para evitar fallos del procesador (ZeroDivisionError).
- 🎛️ **Interfaz Moderna**: Panel de control interactivo con diseño UI premium, sliders matemáticos sincronizados (`LabeledSlider`), botones animados de estado (`AnimatedButton`) y presets astronómicos reales (Sol, Tierra, Júpiter, etc.).
- 📊 **Cálculo de Órbitas Circulares**: Algoritmo en segundo plano que deduce y aplica automáticamente los vectores de velocidad inicial ideales para lograr órbitas estables entre los cuerpos basado en sus masas y distancia.

---

## 🧠 Arquitectura del Sistema

El proyecto sigue rigurosamente el patrón **Modelo-Vista-Controlador (MVC)**, separando las matemáticas de los dibujos en pantalla:

<details>
<summary><b>1. Modelo (Model)</b></summary>
Ubicado en las carpetas <code>models/</code> y <code>physics/</code>. Contiene la pura lógica de simulación.

- `CelestialBody`: Estructura de datos (`@dataclass`) que almacena masa, vector de posición 3D, vector de velocidad 3D, color base y memoria de trail (estela).
- `PhysicsEngine`: Orquestador matemático que computa aceleraciones usando la ley de gravitación vectorizada en matrices de Numpy para alta velocidad de ejecución.
</details>

<details>
<summary><b>2. Vista (View)</b></summary>
Ubicado en la carpeta <code>ui/</code>. Dibuja los componentes en pantalla basado en el modelo.

- `SimulationCanvas`: Lienzo 3D basado en PyOpenGL (`GLViewWidget`) donde se dibujan las esferas, la grilla estelar y las curvas de trayectoria en el espacio.
- `ControlPanel`: Interfaz de menús laterales con agrupaciones semánticas.
- `theme.py`: Configuración unificada de estilos CSS y paleta de colores.
</details>

<details>
<summary><b>3. Controlador (Controller)</b></summary>
Ubicado en <code>main_window.py</code>.

- `MainWindow`: Recibe las señales (Signals) de los inputs del usuario, modifica el motor físico, e invoca los refrescos en pantalla coordinados mediante un reloj interno (`QTimer` a 60 FPS).
</details>

---

## 🧮 Matemáticas y Física del Motor

El motor de simulación (`PhysicsEngine`) y los cálculos iniciales (`MainWindow`) implementan múltiples algoritmos avanzados para garantizar precisión matemática y estabilidad a largo plazo.

### 1. Gravitación Universal
El corazón de la simulación es la **Ley de la Gravitación Universal de Newton**:
`F = G * (m1 * m2) / r^2`

Despejando la fuerza para obtener la aceleración (`a = F / m`), implementamos un cálculo matricial vectorizado de complejidad $O(N^2)$ usando Numpy en `engine.py`. Esto evita el uso de lentos bucles `for` matemáticos iterativos de Python:
```python
# Aceleración escalar = G * Masa_Atractor / distancia^2
acc_mag = self.G_CONSTANT * self._masses[j] / (dist**2)

# Se direcciona la aceleración multiplicándola por el vector unitario (delta / dist)
vector_aceleracion_3d = (delta / dist) * acc_mag
```

### 2. Integrador Numérico (Velocity Verlet)
Para avanzar la simulación en el tiempo discreto (`dt`), **no** usamos el Método de Euler estándar. En su lugar, aplicamos **Velocity Verlet**, un *integrador simpléctico* altamente estable que conserva la energía mecánica y el momento angular del sistema orbital, impidiendo que los planetas salgan despedidos al infinito debido a la acumulación de errores de coma flotante (punto flotante).
El algoritmo funciona en pasos lógicos por cada delta de tiempo:
1. $v_{mid} = v_t + 0.5 \cdot a_t \cdot \Delta t$
2. $r_{t+\Delta t} = r_t + v_{mid} \cdot \Delta t$
3. Se recalcula la nueva aceleración $a_{t+\Delta t}$ a partir de las posiciones actualizadas.
4. $v_{t+\Delta t} = v_{mid} + 0.5 \cdot a_{t+\Delta t} \cdot \Delta t$

### 3. Dinámica de Órbitas Circulares
Cuando cambias la masa o la distancia, el controlador interno calcula e inyecta vectores de velocidad tangenciales exactos para lograr un equilibrio estelar. Utilizando la ecuación orbital circular:
`v_rel = √( G(m1 + m2) / r )`

Para mantener el centro de gravedad compartido de forma estática en el espacio, las magnitudes de velocidad se distribuyen de manera inversamente proporcional a las masas:
```python
# El cuerpo más masivo se mueve poco; el más ligero viaja velozmente
vy1 = -(m2 / total_mass) * v_rel
vy2 = (m1 / total_mass) * v_rel
```
También agregamos un torque tridimensional inyectando un $10\%$ de esta velocidad en el eje `Z` (`vz1 = vy1 * 0.1`), forzando un ángulo 3D espectacular visible desde la cámara OpenGL.

### 4. Protección Anti-Singularidad Computacional
En la astrofísica teórica, a medida que la distancia entre núcleos ($r$) es igual a $0$, la fuerza tiende al infinito, provocando divisiones por cero (`ZeroDivisionError`) que arruinan la memoria (NaN). El simulador protege la CPU incorporando un piso límite suave (`MIN_DISTANCE`), ignorando la perturbación si los planetas han colisionado físicamente, asegurando estabilidad perpetua.

---

## 🎨 Renderizado Procedural y Shaders Similares

Para demostrar conceptos avanzados, ningún planeta es una textura precargada. En la clase `SimulationCanvas`, el color de cada vértice se define matemáticamente evaluando su latitud (`arcsin(z/r)`) y longitud (`arctan2(y,x)`).

*Ejemplo de Generación Procedural (Superficie de la Tierra):*
```python
# Ruido tridimensional usando frecuencias de senos y cosenos
noise = np.sin(5*lat) * np.cos(5*lon) + 0.5 * np.sin(10*lat)

if noise > 0.2: 
    color = [0.13, 0.54, 0.13, 1.0] # Continente
elif noise > 0.0: 
    color = [0.76, 0.70, 0.50, 1.0] # Desierto / Tierra Seca
elif lat > 1.2 or lat < -1.2: 
    color = [0.95, 0.95, 0.98, 1.0] # Polos Nevados
else: 
    color = [0.11, 0.35, 0.65, 1.0] # Océano Profundo
```

---

## 📁 Estructura del Código

```text
OrbitSimulator/
├── assets/                  # Iconos SVG y logos
├── models/                  
│   └── celestial_body.py    # Entidad de planeta/cuerpo celeste
├── physics/                 
│   └── engine.py            # Matemáticas: Euler/Verlet y Gravitación
├── ui/                      
│   ├── widgets/             # Elementos UI personalizados interactivos
│   │   ├── animated_button.py
│   │   └── labeled_slider.py
│   ├── canvas.py            # OpenGL Canvas Rendering
│   ├── control_panel.py     # Disposición de las barras de herramientas
│   ├── main_window.py       # Loop de orquestación de la aplicación
│   └── theme.py             # Colores base CSS
├── main.py                  # Entry Point principal
└── requirements.txt         # Paquetes pip necesarios
```

---

## ⚙️ Instalación

### 1. Requisitos
Asegúrate de contar con **Python 3.8+**.

### 2. Clonar el repositorio
Ingresa a la carpeta del proyecto una vez descargado o clonado.

### 3. Crear el entorno virtual e instalar (Recomendado)
Es preferible aislar las librerías gráficas usando un entorno virtual (`venv`):
```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate
# Activar en MacOS/Linux
source .venv/bin/activate

# Instalar los paquetes matemáticos y visuales
pip install -r requirements.txt
```

### 4. Lanzamiento
Inicia el simulador ejecutando el orquestador principal:
```bash
python main.py
```

---

## 🎮 Controles de la Aplicación

### Navegación 3D del Universo:
- **Click Izquierdo + Arrastrar:** Permite rotar la cámara sobre el sistema estelar en modo libre.
- **Click Derecho + Arrastrar** o **Rueda del Ratón:** Zoom In / Zoom Out.
- **Click en Rueda del Ratón + Arrastrar:** Movimiento de cámara lateral paralelo al sistema (Paneo).

### Interacción UI (Panel Lateral):
- **Cuerpos Celestes:** Usa los combos para asignar rápidamente masas correctas y escalas proporcionales (Sol, Tierra, Luna).
- **Distancia y Magnitudes:** Incrementa o decrementa distancias (medidas en Unidades Astronómicas simplificadas) en tiempo real para visualizar cómo afecta al centro de gravedad.
- **Botones de Simulación:** El panel reacciona de manera responsiva, permitiendo reproducir, pausar la física o resetear completamente el canvas sin perder memoria.

---

<div align="center">
  <i>Construido con 💙 para la visualización matemática interactiva y el diseño avanzado de interfaces de escritorio modernas.</i>
</div>
