---
title: DeepFace Análisis Facial
emoji: 🔍
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# DeepFace — Análisis Facial

Aplicación web en Python que analiza rostros en imágenes usando [DeepFace](https://github.com/serengil/deepface). Detecta edad, género, emoción y etnia estimada.

## Requisitos

- Python 3.10+
- Windows, macOS o Linux

## Instalación

### 1. Crear el entorno virtual

```bash
python -m venv venv
```

### 2. Activar el entorno

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota:** TensorFlow pesa ~350 MB. Asegúrate de tener al menos **2 GB libres** en disco antes de instalar.

Si aparece un error de certificado SSL en Windows:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

> La primera ejecución descargará los modelos de DeepFace. Puede tardar varios minutos.

## Uso

```bash
python App.py
```

Abre el navegador en [http://localhost:5000](http://localhost:5000), sube una imagen y haz clic en **Analizar imagen**.

## Estructura del proyecto

```
DeepFacePython/
├── App.py              # Servidor Flask + interfaz web
├── analyzer.py         # Lógica de análisis con DeepFace
├── requirements.txt    # Dependencias
├── README.md
└── venv/               # Entorno virtual (no versionar)
```

## Tareas completadas

- **Tarea 1 — Diseño:** Interfaz oscura, tarjetas por rostro, barras de confianza, drag & drop y diseño responsivo.
- **Tarea 2 — Edad y emoción:** Se muestran `edad_estimada` y `emocion` con emoji en cada tarjeta.

## Tareas pendientes (opcionales)

- **Tarea 3 — Despliegue:** Publicar en [Render](https://render.com), [Railway](https://railway.app) o [Fly.io](https://fly.io).
- **Tarea 4 — Cámara web:** Análisis en tiempo real con `getUserMedia()` enviando frames al backend.

## Notas

- Los resultados de edad, género, emoción y etnia son **estimaciones** del modelo y no deben usarse para decisiones críticas.
- Tamaño máximo de imagen: 16 MB.
