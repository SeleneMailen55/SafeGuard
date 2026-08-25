# SafeGuard

SafeGuard es una aplicación web orientada a la prevención del grooming y al análisis asistido de conversaciones o capturas de pantalla potencialmente riesgosas. El sistema diferencia accesos por rol y ofrece herramientas específicas para adultos y para niños o adolescentes.

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
- conexión a internet para las funciones que dependen de Gemini

## Instalación

1. Crear un entorno virtual:



```bash
python -m venv .venv


##Activarlo:

En Windows:

.venv\Scripts\activate

En Linux/macOS:

source .venv/bin/activate

Instalar dependencias:

pip install -r requirements.txt
Configuración

La aplicación utiliza una variable de entorno para la clave de Gemini.

En PowerShell:

$env:GEMINI_API_KEY="TU_API_KEY"

En CMD:

set GEMINI_API_KEY=TU_API_KEY

También puede configurarse una clave secreta para Flask si se desea separar la configuración del código.

Activarlo:

En Windows:

.venv\Scripts\activate

En Linux/macOS:

source .venv/bin/activate

Instalar dependencias:

pip install -r requirements.txt
Configuración

La aplicación utiliza una variable de entorno para la clave de Gemini.

En PowerShell:

$env:GEMINI_API_KEY="TU_API_KEY"

En CMD:

set GEMINI_API_KEY=TU_API_KEY

También puede configurarse una clave secreta para Flask si se desea separar la configuración del código.


##
## Base de datos

La aplicación usa SQLite mediante SQLAlchemy.
En desarrollo, la base se crea automáticamente al iniciar la aplicación.

Tablas principales:

user

analysis

user_activity

trusted_contact

chat_simulation


#Proyecto SafeGuard de Investigacion