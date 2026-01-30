import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import obtener_nro_factura  # Importamos tu motor

class AppProcesador:
    def __init__(self, root):
        self.root = root
        self.root.title("TIENDAS A EXCLUIR - London Import S.A.")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        
        self.ruta_archivo = ""

        # --- Estilos Minimalistas ---
        fuente_btn = ("Segoe UI", 10, "bold")
        fuente_txt = ("Consolas", 20)

        # --- Contenedor de Botones ---
        frame_btns = tk.Frame(root, pady=20)
        frame_btns.pack()

        self.btn_cargar = tk.Button(frame_btns, text="1. Cargar PDF", command=self.cargar_pdf, 
                                   width=15, height=2, bg="#e1e1e1", font=fuente_btn)
        self.btn_cargar.grid(row=0, column=0, padx=10)

        self.btn_procesar = tk.Button(frame_btns, text="2. Procesar", command=self.procesar, 
                                     width=15, height=2, state=tk.DISABLED, bg="#d4edda", font=fuente_btn)
        self.btn_procesar.grid(row=0, column=1, padx=10)

        # --- Etiqueta de archivo ---
        self.lbl_archivo = tk.Label(root, text="Ningún archivo seleccionado", fg="gray", font=("Segoe UI", 9))
        self.lbl_archivo.pack(pady=(0, 10))

        # --- Cuadro de Resultado con Scroll ---
        tk.Label(root, text="Tiendas Faltantes:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=40)
        self.txt_resultado = scrolledtext.ScrolledText(root, width=55, height=18, font=fuente_txt)
        self.txt_resultado.pack(pady=10, padx=20)
        self.txt_resultado.config(state=tk.DISABLED) # Solo lectura inicialmente

    def cargar_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if file_path:
            self.ruta_archivo = file_path
            nombre_archivo = file_path.split("/")[-1]
            self.lbl_archivo.config(text=f"Archivo: {nombre_archivo}", fg="black")
            self.btn_procesar.config(state=tk.NORMAL) # Habilitamos botón procesar
            self.limpiar_cuadro()

    def limpiar_cuadro(self):
        self.txt_resultado.config(state=tk.NORMAL)
        self.txt_resultado.delete('1.0', tk.END)
        self.txt_resultado.config(state=tk.DISABLED)

    def escribir_resultado(self, texto):
        self.txt_resultado.config(state=tk.NORMAL)
        self.txt_resultado.insert(tk.END, texto + "\n")
        self.txt_resultado.config(state=tk.DISABLED)

    def procesar(self):
        # Deshabilitar botón para evitar re-ejecución y bloqueos de DB
        self.btn_procesar.config(state=tk.DISABLED)
        self.limpiar_cuadro()
        
        try:
            self.escribir_resultado("Iniciando extracción de PDF...")
            docs = obtener_nro_factura.extraer_documentos_pdf(self.ruta_archivo)
            
            if not docs:
                self.escribir_resultado("No se encontraron facturas o notas de crédito.")
                return

            self.escribir_resultado(f"Detectados {len(docs)} documentos. Consultando Oracle...")
            
            faltantes = obtener_nro_factura.obtener_tiendas_faltantes(docs)
            
            self.limpiar_cuadro() # Limpiamos para mostrar la lista final
            if not faltantes:
                self.escribir_resultado("¡Éxito! Todas las tiendas están presentes.")
            else:
                self.escribir_resultado(f"TOTAL TIENDAS FALTANTES: {len(faltantes)}")
                self.escribir_resultado("-" * 30)
                for i, loja in enumerate(faltantes, 1):
                    self.escribir_resultado(f"[{i:03d}] Tienda: {loja}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.escribir_resultado(f"ERROR: {str(e)}")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = AppProcesador(root)
    root.mainloop()