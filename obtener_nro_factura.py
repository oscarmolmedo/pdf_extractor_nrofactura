import pdfplumber
import re
import cx_Oracle

# --- CONFIGURACIÓN DE CONEXIÓN ---
DB_CONFIG = {
    'user': 'pro',
    'password': 'oracle',
    'dsn': cx_Oracle.makedsn('130.10.10.16', '1521', service_name='LONDON1')
}

def extraer_documentos_pdf(ruta_pdf):
    """Extrae números de 13 dígitos y detecta si son FACTURA o NOTA CRED."""
    re_nro = re.compile(r'\b\d{13}\b')
    documentos = []

    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if not texto: continue
                
                lineas = texto.split('\n')
                for i, linea in enumerate(lineas):
                    nros_encontrados = re_nro.findall(linea)
                    if nros_encontrados:
                        # Analizar contexto (línea actual, anterior y posterior)
                        contexto = " ".join(lineas[max(0, i-1) : min(len(lineas), i+2)]).upper()
                        
                        for nro in nros_encontrados:
                            tipo = None
                            if "NOTA CRED" in contexto:
                                tipo = "NCR"
                            elif "FACTURA" in contexto:
                                tipo = "FAC"
                            
                            if tipo:
                                documentos.append({'tipo': tipo, 'nro': nro})
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
    
    # Eliminar duplicados exactos
    return [dict(t) for t in {tuple(d.items()) for d in documentos}]

def obtener_tiendas_faltantes(lista_docs):
    """Procesa facturas y notas de crédito, compara con SA1010 y halla faltantes."""
    tiendas_con_movimiento = set()
    tiendas_totales = set()
    
    try:
        with cx_Oracle.connect(**DB_CONFIG) as conn:
            cursor = conn.cursor()
            
            # 1. Procesar Documentos (FAC y NCR)
            sql_fac = """
                SELECT DISTINCT F2_LOJA FROM SF2010 
                WHERE F2_DOC = :nro AND F2_CLIENTE = '4573' 
                  AND F2_SERIE IN ('VAF','ACF') AND D_E_L_E_T_ <> '*'
            """
            sql_ncr = """
                SELECT DISTINCT F1_LOJA FROM SF1010 
                WHERE F1_DOC = :nro AND F1_FORNECE = '4573' 
                  AND F1_SERIE IN ('VAC','VAG','ANC','ALC','AAC') AND D_E_L_E_T_ <> '*'
            """
            
            for doc in lista_docs:
                sql = sql_fac if doc['tipo'] == "FAC" else sql_ncr
                cursor.execute(sql, nro=doc['nro'])
                row = cursor.fetchone()
                if row:
                    tiendas_con_movimiento.add(str(row[0]).strip())

            # --- Para verificación ---
            # print(f"Tiendas con movimiento (NCR) detectadas: {len(tiendas_con_movimiento)}")
            # for i, loja in enumerate(sorted(tiendas_con_movimiento)[:25], 1):
            #     print(f"{i:02d}. Tienda: {loja}")

            # 2. Obtener universo de tiendas del cliente
            cursor.execute("SELECT DISTINCT A1_LOJA FROM SA1010 WHERE A1_COD='4573' AND D_E_L_E_T_<>'*'")
            for row in cursor:
                tiendas_totales.add(str(row[0]).strip())
            
            print(f"Total tiendas en maestro (SA1010): {len(tiendas_totales)}")

            # 3. Comparación final
            faltantes = sorted(list(tiendas_totales - tiendas_con_movimiento))
            return faltantes

    except cx_Oracle.Error as e:
        print(f"Error de base de datos: {e}")
        return []

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    archivo = "London Import S.A.30-01.pdf"
    
    # Extracción de documentos con tipo
    documentos = extraer_documentos_pdf(archivo)
    print(f"Documentos identificados en PDF: {len(documentos)}")
    
    if documentos:
        # Validación en DB y obtención de faltantes
        faltantes = obtener_tiendas_faltantes(documentos)
        
        print(f"\n--- TIENDAS FALTANTES (TOP 20) ---")
        if not faltantes:
            print("No se encontraron tiendas faltantes.")
        else:
            for i, loja in enumerate(faltantes[:25], 1):
                print(f"{i:02d}. Tienda: {loja}")
    else:
        print("No se hallaron documentos válidos en el PDF.")