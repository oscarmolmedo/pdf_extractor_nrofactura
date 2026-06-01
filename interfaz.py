from pathlib import Path
import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import obtener_nro_factura as motor


CONFIG_NOMBRE = "config.json"


def obtener_directorio_app() -> Path:
    """
    Devuelve la carpeta base de la aplicación.

    - En .exe PyInstaller: carpeta donde está el ejecutable.
    - En modo desarrollo: carpeta donde está este archivo .py.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def obtener_ruta_config() -> Path:
    return obtener_directorio_app() / CONFIG_NOMBRE


def crear_config_si_no_existe() -> Path:
    """Crea config.json junto al ejecutable/script si todavía no existe."""
    ruta_config = obtener_ruta_config()
    if not ruta_config.exists():
        ruta_config.write_text(
            json.dumps({"ruta_guardado": ""}, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )
    return ruta_config


def cargar_ruta_guardado_config() -> str:
    """
    Lee la ruta de guardado desde config.json.
    Si el archivo no existe, lo crea.
    Si la ruta no existe o está vacía, devuelve cadena vacía.
    """
    ruta_config = crear_config_si_no_existe()

    try:
        data = json.loads(ruta_config.read_text(encoding="utf-8"))
    except Exception:
        data = {"ruta_guardado": ""}
        ruta_config.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")

    ruta_guardado = str(data.get("ruta_guardado", "")).strip()
    if ruta_guardado and Path(ruta_guardado).exists() and Path(ruta_guardado).is_dir():
        return ruta_guardado

    return ""


def guardar_ruta_guardado_config(ruta_guardado: str) -> None:
    """Guarda la ruta seleccionada en config.json junto al ejecutable/script."""
    ruta_config = crear_config_si_no_existe()
    data = {"ruta_guardado": str(ruta_guardado or "")}
    ruta_config.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")



class AppProcesador:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Generar Excel de carga desde PDF")
        self.root.geometry("820x680")
        self.root.resizable(False, False)

        self.ruta_pdf = ""
        self.ruta_config = crear_config_si_no_existe()
        self.carpeta_salida = cargar_ruta_guardado_config()

        fuente_btn = ("Segoe UI", 10, "bold")
        fuente_txt = ("Consolas", 10)

        titulo = tk.Label(
            root,
            text="Generador de archivos Excel desde orden de pago PDF",
            font=("Segoe UI", 13, "bold"),
        )
        titulo.pack(pady=(16, 6))

        # Carpeta de salida separada del flujo principal.
        frame_carpeta = tk.LabelFrame(root, text="Carpeta de guardado", padx=12, pady=10, font=("Segoe UI", 9, "bold"))
        frame_carpeta.pack(fill="x", padx=24, pady=(4, 10))

        self.lbl_carpeta = tk.Label(
            frame_carpeta,
            text="No seleccionada",
            fg="gray",
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.lbl_carpeta.pack(side="left", fill="x", expand=True)

        self.btn_carpeta = tk.Button(
            frame_carpeta,
            text="Elegir carpeta",
            command=self.elegir_carpeta_salida,
            width=18,
            bg="#e1e1e1",
            font=fuente_btn,
        )
        self.btn_carpeta.pack(side="right", padx=(10, 0))

        # Botones principales: acciones que el usuario usa siempre.
        frame_acciones = tk.LabelFrame(root, text="Acciones principales", padx=12, pady=14, font=("Segoe UI", 9, "bold"))
        frame_acciones.pack(fill="x", padx=24, pady=(0, 10))

        self.btn_cargar = tk.Button(
            frame_acciones,
            text="1. Abrir PDF",
            command=self.cargar_pdf,
            width=22,
            height=2,
            bg="#e1e1e1",
            font=fuente_btn,
        )
        self.btn_cargar.pack(side="left", padx=(0, 12))

        self.btn_procesar = tk.Button(
            frame_acciones,
            text="2. Generar Excel",
            command=self.procesar,
            width=22,
            height=2,
            state=tk.DISABLED,
            bg="#d4edda",
            font=fuente_btn,
        )
        self.btn_procesar.pack(side="left")

        self.lbl_archivo = tk.Label(
            frame_acciones,
            text="PDF: no seleccionado",
            fg="gray",
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.lbl_archivo.pack(side="left", padx=18, fill="x", expand=True)

        # Resumen visual.
        frame_resumen = tk.LabelFrame(root, text="Comprobación", padx=12, pady=10, font=("Segoe UI", 9, "bold"))
        frame_resumen.pack(fill="x", padx=24, pady=(0, 10))

        self.lbl_pdf_facturas = self.crear_tarjeta(frame_resumen, "PDF Facturas", "0")
        self.lbl_pdf_nc = self.crear_tarjeta(frame_resumen, "PDF Notas crédito", "0")
        self.lbl_excel_facturas = self.crear_tarjeta(frame_resumen, "Excel Facturas", "0")
        self.lbl_excel_nc = self.crear_tarjeta(frame_resumen, "Excel Notas crédito", "0")
        self.lbl_estado = self.crear_tarjeta(frame_resumen, "Estado", "Pendiente", ancho=18)

        tk.Label(root, text="Detalle del proceso:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=32)

        self.txt_resultado = scrolledtext.ScrolledText(root, width=100, height=22, font=fuente_txt)
        self.txt_resultado.pack(pady=8, padx=24)
        self.txt_resultado.config(state=tk.DISABLED)

        self.aplicar_carpeta_guardada()

    def aplicar_carpeta_guardada(self):
        """Muestra en pantalla la carpeta guardada, si existe y sigue disponible."""
        if self.carpeta_salida:
            self.lbl_carpeta.config(text=self.carpeta_salida, fg="black")
            self.escribir_resultado(f"Ruta de guardado recordada: {self.carpeta_salida}")
        else:
            self.lbl_carpeta.config(text="No seleccionada", fg="gray")
            self.escribir_resultado(f"Archivo de configuración listo: {self.ruta_config}")
            self.escribir_resultado("Seleccione una carpeta de guardado para recordarla en próximos usos.")
        self.actualizar_estado_boton()

    def crear_tarjeta(self, parent: tk.Widget, titulo: str, valor: str, ancho: int = 15) -> tk.Label:
        frame = tk.Frame(parent, bd=1, relief="solid", padx=8, pady=6)
        frame.pack(side="left", padx=5, fill="x", expand=True)
        tk.Label(frame, text=titulo, font=("Segoe UI", 8, "bold"), fg="#555555").pack()
        lbl = tk.Label(frame, text=valor, font=("Segoe UI", 12, "bold"), width=ancho)
        lbl.pack()
        return lbl

    def cargar_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if not file_path:
            return

        self.ruta_pdf = file_path
        self.lbl_archivo.config(text=f"PDF: {Path(file_path).name}", fg="black")
        self.limpiar_cuadro()
        self.reiniciar_resumen()
        self.escribir_resultado("PDF cargado correctamente.")
        self.actualizar_estado_boton()

    def elegir_carpeta_salida(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta donde guardar los archivos Excel")
        if not carpeta:
            return

        carpeta_path = Path(carpeta)
        if not carpeta_path.exists() or not carpeta_path.is_dir():
            messagebox.showwarning("Ruta inválida", "La carpeta seleccionada no existe. Seleccione otra carpeta.")
            self.carpeta_salida = ""
            guardar_ruta_guardado_config("")
            self.lbl_carpeta.config(text="No seleccionada", fg="gray")
            self.actualizar_estado_boton()
            return

        self.carpeta_salida = carpeta
        guardar_ruta_guardado_config(carpeta)
        self.lbl_carpeta.config(text=carpeta, fg="black")
        self.escribir_resultado("Carpeta de guardado seleccionada y recordada correctamente.")
        self.actualizar_estado_boton()

    def actualizar_estado_boton(self):
        if self.ruta_pdf and self.carpeta_salida:
            self.btn_procesar.config(state=tk.NORMAL)
        else:
            self.btn_procesar.config(state=tk.DISABLED)

    def reiniciar_resumen(self):
        self.lbl_pdf_facturas.config(text="0")
        self.lbl_pdf_nc.config(text="0")
        self.lbl_excel_facturas.config(text="0")
        self.lbl_excel_nc.config(text="0")
        self.lbl_estado.config(text="Pendiente", fg="black")

    def limpiar_cuadro(self):
        self.txt_resultado.config(state=tk.NORMAL)
        self.txt_resultado.delete("1.0", tk.END)
        self.txt_resultado.config(state=tk.DISABLED)

    def escribir_resultado(self, texto: str):
        self.txt_resultado.config(state=tk.NORMAL)
        self.txt_resultado.insert(tk.END, texto + "\n")
        self.txt_resultado.see(tk.END)
        self.txt_resultado.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def asegurar_carpeta_salida(self) -> bool:
        """Comprueba que la carpeta exista. Si no existe, solicita otra."""
        while True:
            carpeta = Path(self.carpeta_salida) if self.carpeta_salida else None
            if carpeta and carpeta.exists() and carpeta.is_dir():
                return True

            messagebox.showwarning(
                "Carpeta no disponible",
                "La carpeta de guardado no existe o no está disponible. Seleccione otra carpeta.",
            )
            nueva_carpeta = filedialog.askdirectory(title="Seleccionar carpeta donde guardar los archivos Excel")
            if not nueva_carpeta:
                return False

            self.carpeta_salida = nueva_carpeta
            guardar_ruta_guardado_config(nueva_carpeta)
            self.lbl_carpeta.config(text=nueva_carpeta, fg="black")

    def procesar(self):
        self.btn_procesar.config(state=tk.DISABLED)
        self.limpiar_cuadro()
        self.reiniciar_resumen()

        try:
            if not self.ruta_pdf:
                raise ValueError("Primero debe seleccionar un archivo PDF.")
            if not Path(self.ruta_pdf).exists():
                raise FileNotFoundError(f"No existe el archivo PDF seleccionado: {self.ruta_pdf}")
            if not self.asegurar_carpeta_salida():
                self.escribir_resultado("Operación cancelada: no se seleccionó carpeta de guardado.")
                return

            self.escribir_resultado("Leyendo PDF...")
            documentos = motor.extraer_documentos_pdf(self.ruta_pdf)
            facturas, notas_credito = motor.separar_documentos(documentos)

            if not documentos:
                self.lbl_estado.config(text="Sin datos", fg="#b00020")
                self.escribir_resultado("No se encontraron facturas o notas de crédito en el PDF.")
                return

            self.lbl_pdf_facturas.config(text=str(len(facturas)))
            self.lbl_pdf_nc.config(text=str(len(notas_credito)))

            self.escribir_resultado("PDF leído correctamente:")
            self.escribir_resultado(f"  - Facturas: {len(facturas)}")
            self.escribir_resultado(f"  - Notas de crédito: {len(notas_credito)}")
            self.escribir_resultado(f"  - Total documentos: {len(documentos)}")
            self.escribir_resultado("")
            self.escribir_resultado("Generando archivos Excel separados...")

            resultado = motor.procesar_pdf_a_excels_separados(self.ruta_pdf, self.carpeta_salida)

            self.lbl_excel_facturas.config(text=str(resultado.total_facturas_excel))
            self.lbl_excel_nc.config(text=str(resultado.total_notas_credito_excel))

            self.escribir_resultado("")
            self.escribir_resultado(f"Fecha agregada al nombre de archivo: {resultado.fecha_archivo}")
            self.escribir_resultado("Validación leyendo los Excel generados:")
            self.escribir_resultado(f"  - Facturas en Excel: {resultado.total_facturas_excel}")
            self.escribir_resultado(f"  - Notas de crédito en Excel: {resultado.total_notas_credito_excel}")
            self.escribir_resultado("")
            self.escribir_resultado("Archivos generados:")
            self.escribir_resultado(f"  - {resultado.ruta_facturas}")
            self.escribir_resultado(f"  - {resultado.ruta_notas_credito}")

            if (
                resultado.total_facturas_pdf == resultado.total_facturas_excel
                and resultado.total_notas_credito_pdf == resultado.total_notas_credito_excel
            ):
                self.lbl_estado.config(text="OK", fg="#107c10")
                self.escribir_resultado("")
                self.escribir_resultado("Validación OK: los totales del PDF coinciden con los Excel.")
                messagebox.showinfo("Proceso finalizado", "Archivos Excel generados y validados correctamente.")
            else:
                self.lbl_estado.config(text="Revisar", fg="#b00020")
                self.escribir_resultado("")
                self.escribir_resultado("ADVERTENCIA: los totales del PDF no coinciden con los Excel generados.")
                messagebox.showwarning("Validación con diferencias", "Revise los totales mostrados en pantalla.")

        except Exception as e:
            self.lbl_estado.config(text="Error", fg="#b00020")
            messagebox.showerror("Error", str(e))
            self.escribir_resultado(f"ERROR: {str(e)}")
        finally:
            self.actualizar_estado_boton()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppProcesador(root)
    root.mainloop()
