import pdfplumber
import re
import cx_Oracle

def extraer_numeros_pdf(ruta_pdf):
    # Buscamos patrones de 13 dígitos
    patron = re.compile(r'\b\d{13}\b')
    facturas = set() # Usamos set para evitar duplicados si un nro se repite en el PDF
    
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                encontrados = patron.findall(texto)
                facturas.update(encontrados)
    return list(facturas)

def consultar_oracle(lista_facturas):
    resultados_finales = []
    
    # Configuración de conexión suministrada
    dsn_tns = cx_Oracle.makedsn('130.10.10.16', '1521', service_name='LONDON1')
    
    try:
        connection = cx_Oracle.connect(user='pro', password='oracle', dsn=dsn_tns)
        cursor = connection.cursor()
        
        print(f"Conectado a Oracle. Procesando {len(lista_facturas)} facturas...")

        sql = """
            SELECT F2_DOC, F2_LOJA 
            FROM SF2010 
            WHERE F2_DOC = :nro_doc 
              AND F2_CLIENTE = '4573' 
              AND F2_SERIE IN ('VAF', 'ACF') 
              AND D_E_L_E_T_ <> '*'
        """

        for nro in lista_facturas:
            # Ejecutamos la consulta pasando el número como parámetro
            cursor.execute(sql, nro_doc=nro)
            row = cursor.fetchone()
            
            if row:
                # Guardamos F2_DOC y F2_LOJA en una lista de diccionarios
                resultados_finales.append({
                    'F2_DOC': row[0],
                    'F2_LOJA': row[1]
                })
        
        cursor.close()
        connection.close()
        
    except cx_Oracle.Error as error:
        print(f"Error en la conexión/consulta: {error}")
    
    return resultados_finales

# --- FLUJO PRINCIPAL ---
archivo_pdf = "London Import S.A.30-01.pdf"

# 1. Extraer del PDF
lista_nros = extraer_numeros_pdf(archivo_pdf)
print(f"Se extrajeron {len(lista_nros)} números únicos del PDF.")

# 2. Consultar en DB
datos_obtenidos = consultar_oracle(lista_nros)

# 3. Mostrar o procesar resultados
print(f"\nSe encontraron {len(datos_obtenidos)} registros en la DB:")
for dato in datos_obtenidos:
    print(f"Documento: {dato['F2_DOC']} | Loja: {dato['F2_LOJA']}")