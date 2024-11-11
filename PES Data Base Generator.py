import os
import json
from tkinter import ttk, Tk, messagebox, Menu, filedialog

class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.file_a_data = None  # Variable para almacenar datos de File A
        self.file_b_data = None 

        self.appname = 'PES/WE/JL Data Base Generator - Converter'
        self.version = '0.7'
        self.author = 'Gerardo Contreras'
        self.title(self.appname)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables para la configuración
        self.configurations = {}

        # Creating Menubar
        self.menubar = Menu(self)
        self.config(menu=self.menubar)

        # Adding File Menu and commands
        file = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=file)
        file.add_command(label='Open File A', command = self.load_file_a)
        file.add_command(label='Open File B', command = self.load_file_b)
        file.add_separator()
        file.add_command(label='Exit', command=self.on_closing, accelerator="Ctrl+Q")

        # Adding Export/Import Menu and commands
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Export/Import', menu=self.edit_menu)
        self.edit_menu.add_command(label='Export', command=self.export_selected_segment, state="disabled")
        self.edit_menu.add_command(label='Import', command=self.import_selected_segment, state="disabled")

        # Etiquetas
        label_a = ttk.Label(self, text="File A")
        label_a.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        self.combobox_a = ttk.Combobox(self, width=50, state="readonly")
        self.combobox_a.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        label_b = ttk.Label(self, text="File B")
        label_b.grid(row=0, column=2, columnspan=2, padx=10, pady=5)

        self.combobox_b = ttk.Combobox(self, width=50, state="readonly")
        self.combobox_b.grid(row=1, column=2, columnspan=2, padx=10, pady=5)

        # Etiquetas de tablas
        table_label_a = ttk.Label(self, text="Content of File A")
        table_label_a.grid(row=2, column=0, columnspan=2)

        table_label_b = ttk.Label(self, text="Content of File B")
        table_label_b.grid(row=2, column=2, columnspan=2)

        self.tree_a = self.setup_tree_view(self)
        self.tree_a.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.tree_b = self.setup_tree_view(self)
        self.tree_b.grid(row=3, column=2, columnspan=2, padx=10, pady=5)

        # Bind para habilitar exportación
        self.tree_a.bind("<ButtonRelease-1>", self.on_tree_select)

        # Input y botón para cargar archivos
        self.entry_a = ttk.Entry(self, width=45)
        self.entry_a.grid(row=4, column=0, columnspan=1, padx=10, pady=5)
        self.entry_a.insert(0, "Path to File A")

        # Botones para cargar archivos binarios
        load_button_a = ttk.Button(self, text="Load File A", command=self.load_file_a)
        load_button_a.grid(row=4, column=1, padx=5, pady=5)

        # Input y botón para cargar File B
        self.entry_b = ttk.Entry(self, width=45)
        self.entry_b.grid(row=4, column=2, columnspan=1, padx=10, pady=5)
        self.entry_b.insert(0, "Path to File B")

        load_button_b = ttk.Button(self, text="Load File B", command=self.load_file_b)
        load_button_b.grid(row=4, column=3, padx=5, pady=5)
        
        copy_to_b = ttk.Button(
            self, 
            text="Copy to file B", 
            command= lambda _ : self.copy_data_to_file(
                src_file=self.file_a_data, 
                dst_file=self.file_b_data,
                src_tree=self.tree_a,
                dst_tree=self.tree_b,
            ), 
            state="disabled"
        ) 
        copy_to_b.grid(row=5, column=0, columnspan=2, pady=10)
        copy_to_a = ttk.Button(
            self, 
            text="Copy to file A", 
            command= lambda _ : self.copy_data_to_file(
                src_file=self.file_b_data, 
                dst_file=self.file_a_data,
                src_tree=self.tree_a,
                dst_tree=self.tree_a,

            ), 
            state="disabled"
        ) 
        copy_to_a.grid(row=5, column=2, columnspan=2, pady=10)
        
        # Cargar nombres de archivos JSON en los comboboxes
        self.load_json_files('config/')

    def get_item_from_tree_by_word(self, tree:ttk.Treeview, word:str, col:str):
        for item in tree.get_children():
            value = tree.item(item, "values")[col]
            if value == word:
                return item
        return None

    def copy_data_to_file(self, src_file:bytearray, dst_file:bytearray, src_tree:ttk.Treeview, dst_tree:ttk.Treeview):
        
        selection = src_tree.selection()

        if not selection:
            messagebox.showerror("Error", f"Please first select one section to transfer")
            return

        for item in selection:
            item_values = src_tree.item(item).values
            _, section_name, offset, size = item_values
            dst_tree_item = self.get_item_from_tree_by_word(dst_tree, section_name, "Section Name")
            
            if dst_tree_item is None: continue
            
            dst_item_values = dst_tree.item(dst_tree_item).values
            _, _, dst_offset, dst_size = dst_item_values
            
            self.copy_segment_data(dst_file, src_file, dst_offset, offset, dst_size, size)

    def setup_tree_view(self, parent, **kwargs):
        tree = ttk.Treeview(parent, columns=("File", "Section Name", "Offset", "Size"), show="headings", height=14, **kwargs)
        for col, width in zip(("File", "Section Name", "Offset", "Size"), (100, 240, 65, 50)):
            tree.heading(col, text=col)
            tree.column(col, width=width)
        return tree

    def load_json_files(self, directory):
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        file_names = [f[:-5] for f in json_files]  # Eliminar la extensión .json

        # Cargar configuraciones de cada archivo JSON
        for file_name in file_names:
            file_path = os.path.join(directory, f"{file_name}.json")
            with open(file_path, 'r') as json_file:
                try:
                    self.configurations[file_name] = json.load(json_file)

                except json.JSONDecodeError as e:
                    print(e)
                    messagebox.showerror("Error", f"Failed to parse JSON file: {file_path}\n{str(e)}")
        
        # Cargar en los comboboxes
        self.combobox_a['values'] = file_names
        self.combobox_b['values'] = file_names

    def load_file_a(self):
        if not self.combobox_a.get():
            messagebox.showwarning("Warning", "Please select a configuration file for File A before loading.")
            return
    
        file_path = filedialog.askopenfilename(title="Select File A", filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
        if file_path:
            # Extraer solo el nombre del archivo
            file_name = os.path.basename(file_path)

            # Actualizar el campo de texto (Entry) con el nombre del archivo
            self.entry_a.delete(0, "end")  # Limpiar cualquier texto anterior
            self.entry_a.insert(0, file_name)  # Insertar la nueva ruta

            selected_config = self.combobox_a.get()
            if selected_config:
                self.process_binary_file(file_path, selected_config, self.tree_a)

    def load_file_b(self):
        if not self.combobox_b.get():
            messagebox.showwarning("Warning", "Please select a configuration file for File B before loading.")
            return
    
        file_path = filedialog.askopenfilename(title="Select File B", filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
        if file_path:
            # Extraer solo el nombre del archivo
            file_name = os.path.basename(file_path)

            # Actualizar el campo de texto (Entry) con el nombre del archivo
            self.entry_b.delete(0, "end")  # Limpiar cualquier texto anterior
            self.entry_b.insert(0, file_name)  # Insertar la nueva ruta

            selected_config = self.combobox_b.get()
            if selected_config:
                self.process_binary_file(file_path, selected_config, self.tree_b)

    def clean_table(self, tree):
        # Limpiamos la tabla antes de agregar los nuevos datos
        for item in tree.get_children():
            tree.delete(item)

    def process_binary_file(self, file_path, config_name, tree):

        self.clean_table(tree)

        config = self.configurations.get(config_name)
        if config is None:
            messagebox.showerror("Error", "No configuration loaded for the selected file.")
            return

        try:
            with open(file_path, "rb") as file:
                data = file.read()  # Cargar todo el contenido del archivo en memoria
                self.file_a_data = data  # Almacenar datos de File A

                # Verificamos el tamaño del archivo
                file_size = len(data)

                for section in config["dataSections"]:
                    file_name = section["fileName"]
                    section_name = section["sectionName"]
                    start_offset = section["offsetRange"]["start"]
                    size = section["offsetRange"]["size"]

                    # Verificamos si los offsets están dentro del rango
                    if start_offset < 0 or (start_offset + size) > file_size or size <= 0:
                        self.clean_table(tree)
                        messagebox.showerror("Error", f"Offsets for section '{section_name}' are out of range in the binary file.")
                        return

                    # Insertamos los datos en la tabla
                    tree.insert("", "end", values=(file_name, section_name, start_offset, size))

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
            

    def on_tree_select(self, event):
        # Habilitar la opción de exportar si hay un segmento seleccionado
        if self.tree_a.selection():
            self.edit_menu.entryconfig('Export', state="normal")
            self.edit_menu.entryconfig('Import', state="normal")

        else:
            self.edit_menu.entryconfig('Export', state="disabled")
            self.edit_menu.entryconfig('Import', state="disabled")
                
    def export_selected_segment(self):
        selected_items = self.tree_a.selection()
        
        if not selected_items:
            messagebox.showwarning("Warning", "Please select one or more segments to export.")
            return

        save_directory = filedialog.askdirectory(title="Select Directory to Save Segments")
        if not save_directory:
            return
        
        error_list = []
        for item in selected_items:
            segment_info = self.tree_a.item(item)["values"]
            file_name, _ , start_offset, size = segment_info

            if file_name.lower() == "unknown":
                continue

            data_to_export = self.file_a_data[start_offset : start_offset + size]

            save_path = os.path.join(save_directory, f"{file_name}.bin")
            try:
                with open(save_path, "wb") as output_file:
                    output_file.write(data_to_export)
            except Exception as e:
                error_list.append(f"Failed to export segment '{file_name}': {e}")
            
        if error_list:
            s = "\n".join(error_list)
            messagebox.showerror("Error", s)
        

        messagebox.showinfo("Success", f"Selected segments exported to {save_directory}")
        
            
    def import_selected_segment(self):
        # Obtener elementos seleccionados en la tabla
        selected_items = self.tree_a.selection()
        
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a segment to import.")
            return

        # Caso de selección única
        if len(selected_items) == 1:
            # Solo un elemento seleccionado: preguntar por un archivo individual
            segment_info = self.tree_a.item(selected_items[0])["values"]
            section_name = segment_info[1]  # Nombre de la sección

            # Pedir al usuario que seleccione el archivo para importar
            file_path = filedialog.askopenfilename(title="Select File to Import", initialfile=f"{section_name}.bin",
                                                filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])

            if file_path:
                self.process_imported_file(file_path, segment_info)

        # Caso de selección múltiple
        else:
            # Múltiples elementos seleccionados: preguntar por el directorio
            directory_path = filedialog.askdirectory(title="Select Directory to Import Files From")
            if not directory_path:
                return  # El usuario canceló la selección

            missing_files = []
            for item in selected_items:
                
                segment_info = self.tree_a.item(item)["values"]
                section_name = segment_info[1]  # Nombre de la sección

                file_name = segment_info[0]  # Nombre de la sección
                
                # Construir la ruta esperada del archivo
                expected_file_path = os.path.join(directory_path, f"{section_name}.bin")
                
                if os.path.exists(expected_file_path):
                    # Importar si el archivo existe
                    self.process_imported_file(expected_file_path, segment_info)
                else:
                    # Si falta el archivo, agregarlo a la lista de archivos faltantes
                    missing_files.append(f"{section_name}.bin")

            # Si hay archivos faltantes, preguntar al usuario si desea buscarlos manualmente
            for missing_file in missing_files:
                result = messagebox.askyesno("File Not Found", f"The file '{missing_file}' was not found in the selected directory. Do you want to search for it manually?")
                if result:
                    file_path = filedialog.askopenfilename(title=f"Locate {missing_file}", initialfile=missing_file, filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
                    if file_path:
                        segment_info = next((self.tree_a.item(item)["values"] for item in selected_items 
                                            if self.tree_a.item(item)["values"][1] + ".bin" == missing_file), None)
                        if segment_info:
                            self.process_imported_file(file_path, segment_info)

    def process_imported_file(self, file_path, segment_info):

        file_name = segment_info[0]  # 
        section_name = segment_info[1]  # Nombre de la sección
        start_offset = segment_info[2]        # Offset de inicio

        try:
            # Abrir el archivo en modo binario y leer los datos en el rango específico
            with open(file_path, "rb") as file:
                file.seek(start_offset)  # Ir al offset específico del segmento
                new_data = file.read()  # Leer el tamaño específico de datos

            # Aquí puedes realizar el procesamiento específico del segmento.
            # En este ejemplo, asumimos que tienes una función `update_segment_data` que actualiza el segmento en la interfaz o en la estructura de datos.
            self.update_segment_data(start_offset, new_data)

            # Mensaje de éxito
            messagebox.showinfo("Success", f"The segment '{section_name}' has been successfully imported.")

        except FileNotFoundError:
            messagebox.showerror("File Error", f"The file '{file_path}' was not found.")
        except IOError as e:
            messagebox.showerror("Read Error", f"An error occurred while reading the file: {e}")
        except Exception as e:
            print(e)
            messagebox.showerror("Processing Error", f"An unexpected error occurred: {e}")

    def update_segment_data(self, start_offset, new_data):

        end_offset = start_offset + len(new_data)
        
        # Verifica que los offsets están dentro del rango de self.file_a_data
        #if start_offset < 0 or end_offset > len(self.file_a_data):
        #    messagebox.showerror("Error", "Offset fuera de los límites de los datos.")
        #    return

        # Verifica que la longitud de new_data coincida con el tamaño esperado
        expected_size = end_offset - start_offset
        if len(new_data) != expected_size:
            messagebox.showerror("Error", f"El tamaño de los datos nuevos ({len(new_data)} bytes) no coincide con el tamaño esperado ({expected_size} bytes).")
            return
        
        # Actualiza el rango correspondiente en self.file_a_data con los nuevos datos
        self.file_a_data = (self.file_a_data[:start_offset] + new_data + self.file_a_data[end_offset:])
        
        messagebox.showinfo("Success", "Segmento actualizado exitosamente.")

    def copy_segment_data(self, dst:bytearray, src:bytearray, dst_offset:int, src_offset:int, dst_size:int, src_size:int) -> None:
        """This function will copy the data from one byte array into another given the following arguments

        Args:
            dst (bytearray): the destination byte array
            src (bytearray): the source byte array
            dst_offset (int): the destination offset from where the data starts
            src_offset (int): the source offset from where the data starts
            dst_size (int): the size of the destination data
            src_size (int): the size of the source data

        Raises:
            Exception: Raise when the sizes dont match
        """
        if dst_size != src_size:
            raise Exception("Source and destionation sizes don't match!")

        dst[dst_offset:dst_offset + dst_size] = src[src_offset:src_offset + src_size]

    def on_closing(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the program?"):
            self.destroy()

    def start(self):
        self.mainloop()

def main():
    Gui().start()

if __name__ == '__main__':
    main()