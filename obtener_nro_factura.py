import pdfplumber
import re
import cx_Oracle

# --- CONFIGURACIÓN DE CONEXIÓN (Reutilizable) ---
DB_CONFIG = {
    'user': 'pro',
    'password': 'oracle',
    'dsn': cx_Oracle.makedsn('130.10.10.16', '1521', service_name='LONDON1')
}

def extraer_numeros_factura(ruta_pdf):
    """Extrae números de 13 dígitos del PDF."""
    patron = re.compile(r'\b\d{13}\b')
    facturas = set()
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    facturas.update(patron.findall(texto))
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
    return list(facturas)

def procesar_datos_oracle(lista_facturas):
    """
    1. Consulta facturas en SF2010 y agrupa tiendas (F2_LOJA).
    2. Consulta universo de tiendas en SA1010.
    3. Compara y retorna las tiendas faltantes.
    """
    tiendas_con_factura = set()
    tiendas_totales = set()
    
    try:
        # Abrimos una única conexión para todas las operaciones
        with cx_Oracle.connect(**DB_CONFIG) as conn:
            cursor = conn.cursor()
            
            # --- PASO 1: Obtener tiendas que ya tienen factura en el PDF ---
            sql_sf2 = """
                SELECT DISTINCT F2_LOJA 
                FROM SF2010 
                WHERE F2_DOC = :nro_doc 
                  AND F2_CLIENTE = '4573' 
                  AND F2_SERIE IN ('VAF', 'ACF') 
                  AND D_E_L_E_T_ <> '*'
            """
            for nro in lista_facturas:
                cursor.execute(sql_sf2, nro_doc=nro)
                row = cursor.fetchone()
                if row:
                    # .strip() es vital para evitar errores por espacios en blanco
                    tiendas_con_factura.add(str(row[0]).strip())
            
            print(f"Tiendas encontradas en SF2010 con estas facturas: {len(tiendas_con_factura)}")
            # for a in tiendas_con_factura:
            #     print(f" - Tienda con factura: {a}")

            # --- PASO 2: Obtener universo total de tiendas para el cliente ---
            sql_sa1 = "SELECT DISTINCT A1_LOJA FROM SA1010 WHERE A1_COD='4573' AND D_E_L_E_T_<>'*'"
            cursor.execute(sql_sa1)
            for row in cursor:
                tiendas_totales.add(str(row[0]).strip())
            
            print(f"Total de tiendas registradas para el cliente 4573 (SA1010): {len(tiendas_totales)}")


            # --- PASO 3: Comparación (Diferencia de conjuntos) ---
            # Tiendas que están en el universo total pero NO en las facturas procesadas
            tiendas_faltantes = sorted(list(tiendas_totales - tiendas_con_factura))
            
            return tiendas_faltantes

    except cx_Oracle.Error as e:
        print(f"Error en la base de datos: {e}")
        return []

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    archivo = "London Import S.A.30-01.pdf"
    
    # 1. Extracción
    nros_factura = extraer_numeros_factura(archivo)
    print(f"Números de factura detectados en PDF: {len(nros_factura)}")
    
    if nros_factura:
        # 2. Procesamiento y Comparación
        faltantes = procesar_datos_oracle(nros_factura)
        
        # 3. Resultados
        print(f"\nSe identificaron {len(faltantes)} tiendas sin facturas en este documento.")
        print("Primeras 20 tiendas faltantes (ordenadas):")
        for i, tienda in enumerate(faltantes[:100], 1):
            print(f"[{i:02d}] Código Tienda: {tienda}")
    else:
        print("No se encontraron números de factura en el PDF para procesar.")