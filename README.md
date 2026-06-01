# Generador de Archivos de Carga desde PDF

Aplicación de escritorio desarrollada en Python para extraer Facturas y Notas de Crédito desde archivos PDF y generar archivos Excel compatibles con el sistema de carga de pagos.

La herramienta procesa automáticamente documentos fiscales contenidos en órdenes de pago, separando Facturas y Notas de Crédito en archivos independientes para facilitar su importación posterior.

---

## Características

### Extracción automática desde PDF

La aplicación identifica líneas con el formato:

```text
274287835 - FACTURA - 0020010011951 1.480.920 0
277342043 - NOTA CRED. - 0010010005107 -190.801 0
```

Extrayendo:

* Tipo de documento (FACTURA o NOTA DE CRÉDITO)
* Número de documento
* Importe de factura

### Formateo automático

Convierte automáticamente:

```text
0020010011951
```

en:

```text
002-001-0011951
```

### Separación por tipo

Genera dos archivos Excel independientes:

```text
NombreArchivo_FACTURA_YYYYMMDD.xlsx
NombreArchivo_NOTA_CREDITO_YYYYMMDD.xlsx
```

Ejemplo:

```text
London Import S.A.12-12_FACTURA_20260601.xlsx
London Import S.A.12-12_NOTA_CREDITO_20260601.xlsx
```

### Tratamiento de importes

* Elimina separadores de miles.
* Las Notas de Crédito se guardan sin signo negativo.
* Todos los valores son exportados en formato General.

Ejemplos:

```text
1.480.920    -> 1480920
-190.801     -> 190801
```

### Validación automática

La aplicación muestra:

* Total de Facturas detectadas en PDF.
* Total de Notas de Crédito detectadas en PDF.
* Total de Facturas exportadas al Excel.
* Total de Notas de Crédito exportadas al Excel.

Esto permite verificar rápidamente que la información exportada coincide con la información leída.

### Configuración persistente

La carpeta de salida seleccionada por el usuario se almacena automáticamente en:

```text
config.json
```

El archivo se crea junto al ejecutable o script.

Al iniciar nuevamente la aplicación:

* Si la carpeta sigue existiendo, se utiliza automáticamente.
* Si la carpeta ya no existe, se solicita una nueva ubicación.

---

## Estructura del Proyecto

```text
├── interfaz.py
├── lector_pdf_carga_excel.py
├── config.json
└── README.md
```

### interfaz.py

Contiene:

* Interfaz gráfica Tkinter.
* Selección de PDF.
* Selección de carpeta de salida.
* Lectura y escritura de configuración.
* Visualización de resultados y validaciones.

### lector_pdf_carga_excel.py

Contiene:

* Extracción de documentos desde PDF.
* Clasificación de Facturas y Notas de Crédito.
* Generación de archivos Excel.
* Formateo de documentos e importes.

### config.json

Archivo generado automáticamente para almacenar la ruta de salida utilizada por el usuario.

---

## Requisitos

### Python

```text
Python 3.10 o superior
```

También compatible con Python 3.12.

### Dependencias

Instalar:

```bash
pip install pdfplumber openpyxl
```

---

## Ejecución

```bash
python interfaz.py
```

---

## Generación de Ejecutable

```bash
pyinstaller --noconfirm --onefile --windowed --name "GeneradorCargaPDF" interfaz.py
```

El ejecutable recordará automáticamente la carpeta de salida seleccionada mediante el archivo:

```text
config.json
```

---

## Flujo de Uso

1. Abrir la aplicación.
2. Seleccionar PDF.
3. Generar archivos Excel.
4. Revisar el resumen de validación.
5. Utilizar los archivos generados para la carga en el sistema destino.

---

## Archivos Generados

Cada ejecución genera:

```text
*_FACTURA_YYYYMMDD.xlsx
*_NOTA_CREDITO_YYYYMMDD.xlsx
```

Los archivos se guardan en la carpeta configurada por el usuario.

---

## Estado Actual

Funcionalidades implementadas:

* Lectura de PDF.
* Identificación de Facturas.
* Identificación de Notas de Crédito.
* Separación por tipo.
* Formateo de documentos.
* Limpieza de importes.
* Exportación a Excel.
* Validación PDF vs Excel.
* Persistencia de configuración mediante JSON.
* Compatibilidad con ejecutable Windows.

```
```
