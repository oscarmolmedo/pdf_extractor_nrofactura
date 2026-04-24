# Validador de Facturas y Notas de Crédito - Protheus/Oracle

Este proyecto es una herramienta de escritorio desarrollada en **Python** para automatizar la conciliación de documentos fiscales (Facturas y Notas de Crédito) provenientes de archivos PDF con los registros en una base de datos **Oracle 11g (Protheus)**.

La aplicación identifica qué sucursales (tiendas) de un cliente específico no han sido procesadas en el documento actual, facilitando el control de gestión de cobros o pagos.

## 🚀 Características

- **Extracción Inteligente:** Identifica números de 13 dígitos y distingue automáticamente entre "FACTURA" y "NOTA DE CRÉDITO" analizando el contexto del texto.
- **Validación Cruzada:** Consulta las tablas `SF2010` (Ventas) y `SF1010` (Compras/NC) de Protheus.
- **Análisis de Brechas:** Compara los movimientos encontrados contra el universo de tiendas del cliente en la tabla `SA1010`.
- **Interfaz Amigable:** GUI minimalista construida con Tkinter.
- **Arquitectura Específica:** Optimizado para entornos de **32 bits**.

## 🛠️ Requisitos Técnicos

Debido a integraciones con librerías específicas de bases de datos antiguas, este proyecto requiere:

- **Python 3.10.11 (32 bits)**
- **Oracle Instant Client (32 bits)** configurado en las variables de entorno (PATH).
- Bibliotecas de Python:
  - `pdfplumber`: Para la extracción de texto de los PDFs.
  - `cx_Oracle`: Para la comunicación con el servidor Oracle.
  - `tkinter`: Para la interfaz gráfica (incluido en la instalación estándar).

## 📂 Estructura del Proyecto

```text
├── interfaz.py        # Código de la GUI (Tkinter) y lógica de estados.
├── motor_logico.py    # Motor de extracción PDF y consultas SQL.
└── README.md          # Documentación del proyecto.
```

## ⚙️ Instalación y Uso
Clonar el repositorio:

Instalar dependencias:
```
Bash
pip install pdfplumber cx_Oracle python-dotenv
```
Ejecutar la aplicación:

Bash
python interfaz.py
Compilar a EXE (Portable): Si deseas generar el ejecutable para Windows:
```
Bash
pyinstaller --noconfirm --onefile --windowed --name "ValidadorTiendas" --clean interfaz.py
```
🖥️ Interfaz de Usuario
La interfaz consta de un flujo de dos pasos:

Cargar PDF: Selecciona el archivo de extracto o factura.

Procesar: Ejecuta la lógica de extracción y consulta. El botón se bloquea durante la ejecución para proteger la integridad de la conexión a la base de datos.

Desarrollado para entornos industriales con integración Protheus ERP.
