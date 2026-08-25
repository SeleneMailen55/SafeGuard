# SafeGuard

SafeGuard es una aplicación web orientada a la prevención del grooming y al análisis asistido de conversaciones o capturas de pantalla potencialmente riesgosas. El sistema diferencia accesos por rol y ofrece herramientas específicas para adultos y para niños o adolescentes.

> ⚠️ **Nota:** Este proyecto fue desarrollado con fines académicos y de práctica. Los números de contacto y emergencia incluidos en el código son de ejemplo y deben reemplazarse por los correspondientes a tu región antes de cualquier uso real.


## Vista previa

**Página de inicio**
<img width="1283" height="664" alt="image" src="https://github.com/user-attachments/assets/d3e6c767-6426-4abb-bb80-4fdcdbfa0ac7" />

**Panel de control (Dashboard)**
<img width="1264" height="657" alt="image" src="https://github.com/user-attachments/assets/66f13617-6da3-4697-973b-b9af8c6fc135" />

**Analizador de mensajes con IA**
<img width="1271" height="683" alt="image" src="https://github.com/user-attachments/assets/b8436b08-a450-41b3-b951-a44e785ca75a" />

**Generación de reportes personalizados**
<img width="1273" height="665" alt="image" src="https://github.com/user-attachments/assets/79ed7e09-c3ea-4a18-a903-d14e19ad82ff" />


## Funcionalidades

### Acceso y usuarios
- Registro e inicio de sesión
- Roles de usuario: niño/adolescente y adulto
- Redirección a dashboard según rol

### Funcionalidades para adultos
- Análisis de texto con integración a Gemini
- Análisis de imágenes
- Historial de análisis asociados al usuario
- Reportes PDF
- Dashboard con métricas básicas

### Funcionalidades para niños y adolescentes
- Contenido informativo sobre grooming y seguridad digital
- Quiz de repaso
- Simulador de chat
- Gestión de contactos de confianza

## Tecnologías utilizadas

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite
- Google Generative AI
- Bootstrap
- ReportLab
- Pillow

## Requisitos

- Python 3.10 o superior
- pip
- Conexión a internet para las funciones que dependen de Gemini

## Instalación

1. Crear un entorno virtual:

```bash
python -m venv .venv
```

2. Activarlo:

En Windows:
```bash
.venv\Scripts\activate
```

En Linux/macOS:
```bash
source .venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

La aplicación utiliza una variable de entorno para la clave de Gemini, cargada mediante un archivo `.env`.

1. Creá un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
GEMINI_API_KEY=tu_clave_aqui
```

2. El archivo `.env` no debe subirse al repositorio (ya está incluido en `.gitignore`).

También puede configurarse una clave secreta para Flask si se desea separar la configuración del código.

## Base de datos

La aplicación usa SQLite mediante SQLAlchemy. En desarrollo, la base se crea automáticamente al iniciar la aplicación.

Tablas principales:
- `user`
- `analysis`
- `user_activity`
- `trusted_contact`
- `chat_simulation`

---

*Proyecto SafeGuard - Proyecto de Investigación académica.*
