import os
import json
from tkinter import ttk, Tk, messagebox, Menu, filedialog

class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.data_file_a = None  # Variable para almacenar datos de File A
        self.data_file_b = None 
        
        self.file_a_path = None  # Ruta de archivo A
        self.file_b_path = None  # Ruta de archivo B

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

        # Adding Export Menu and commands
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Export', menu=self.edit_menu)
        self.edit_menu.add_command(label='Export', command=self.export_selected_segment, state="disabled")

        # Etiquetas
        label_a = ttk.Label(self, text="File A")
        label_a.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        self.combobox_a = ttk.Combobox(self, width=50, state="readonly")
        self.combobox_a.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.combobox_a.bind("<<ComboboxSelected>>", lambda event: self.clean_table(self.tree_a))

        label_b = ttk.Label(self, text="File B")
        label_b.grid(row=0, column=2, columnspan=2, padx=10, pady=5)

        self.combobox_b = ttk.Combobox(self, width=50, state="readonly")
        self.combobox_b.grid(row=1, column=2, columnspan=2, padx=10, pady=5)
        self.combobox_b.bind("<<ComboboxSelected>>", lambda event: self.clean_table(self.tree_b))

        # Etiquetas de tablas
        table_label_a = ttk.Label(self, text="Content of File A")
        table_label_a.grid(row=2, column=0, columnspan=2)

        table_label_b = ttk.Label(self, text="Content of File B")
        table_label_b.grid(row=2, column=2, columnspan=2)

        self.tree_a = self.setup_tree_view(self)
        self.tree_a.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.tree_b = self.setup_tree_view(self)
        self.tree_b.grid(row=3, column=2, columnspan=2, padx=10, pady=5)

        self.tree_a.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree_b.bind("<<TreeviewSelect>>", self.on_tree_select)


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
        
        self.copy_to_b = ttk.Button(
            self, 
            text="Copy to file B", 
            command= lambda : self.copy_data_to_file(
                src_data=self.data_file_a, 
                dst_data=self.data_file_b,
                dst_file_path=self.file_b_path, 
                src_tree=self.tree_a,
                dst_tree=self.tree_b,
            ), 
            state="disabled"
        ) 
        self.copy_to_b.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.copy_to_a = ttk.Button(
            self, 
            text="Copy to file A", 
            command= lambda : self.copy_data_to_file(
                src_data=self.data_file_b, 
                dst_data=self.data_file_a,
                dst_file_path=self.file_a_path, 
                src_tree=self.tree_b,
                dst_tree=self.tree_a,
            ), 
            state="disabled"
        ) 
        self.copy_to_a.grid(row=5, column=2, columnspan=2, pady=10)
        
        # Cargar nombres de archivos JSON en los comboboxes
        self.load_json_files('config/')

    def get_item_from_tree_by_word(self, tree:ttk.Treeview, word:str, col:int):
        for item in tree.get_children():
            value = tree.item(item, "values")[col]
            if value == word:
                return item
        return None

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
                
                self.file_a_path = file_path

                self.data_file_a = self.process_binary_file(file_path, selected_config, self.tree_a)

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
                self.file_b_path = file_path

                self.data_file_b = self.process_binary_file(file_path, selected_config, self.tree_b)

    def clean_table(self, tree):
        # Limpiamos la tabla antes de agregar los nuevos datos
        if tree == self.tree_a:
            self.data_file_a = None

        elif tree == self.tree_b:
            self.data_file_b = None

        if tree.get_children():
            for item in tree.get_children():
                tree.delete(item)

    def process_binary_file(self, file_path:str, config_name:str, tree:ttk.Treeview) -> bytearray:

        self.clean_table(tree)

        config = self.configurations.get(config_name)
        if config is None:
            messagebox.showerror("Error", "No configuration loaded for the selected file.")
            return

        data = bytearray()

        try:
            with open(file_path, "rb") as file:
                data = bytearray(file.read())  # Cargar todo el contenido del archivo en memoria

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
                        return bytearray()

                    # Insertamos los datos en la tabla
                    tree.insert("", "end", values=(file_name, section_name, start_offset, size))

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
        
        return data
    
    def copy_data_to_file(self, src_data:bytearray, dst_data:bytearray, dst_file_path:str, src_tree:ttk.Treeview, dst_tree:ttk.Treeview):
        
        selection = src_tree.selection()

        if not selection:
            messagebox.showerror("Error", f"Please first select one section to transfer")
            return

        for item in selection:
            item_values = src_tree.item(item)["values"]
            _, section_name, offset, size = item_values
            dst_tree_item = self.get_item_from_tree_by_word(dst_tree, section_name, 1)
            
            if dst_tree_item is None: continue
            
            dst_item_values = dst_tree.item(dst_tree_item)["values"]
            _, _, dst_offset, dst_size = dst_item_values
            
            self.copy_segment_data(dst_data, src_data, dst_offset, dst_file_path, offset, dst_size, size)
        

    def copy_segment_data(self, dst:bytearray, src:bytearray, dst_offset:int, dst_file_path:str, src_offset:int, dst_size:int, src_size:int) -> None:
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


        self.save_file(dst, dst_file_path)


    def save_file(self, file_data, file_path):
        # Guarda los datos modificados en el archivo
        with open(file_path, 'wb') as file:
            file.write(file_data)
            print(f"File saved to {file_path}")


    def on_tree_select(self, event):
        # Obtiene el árbol que generó el evento (tree_a o tree_b)
        selected_tree = event.widget
        has_selection = bool(selected_tree.selection())

        print(f"Selection in {selected_tree}: {has_selection}")
        
        # Determina si la selección activa o desactiva el botón de Export
        self.edit_menu.entryconfig('Export', state="normal" if has_selection else "disabled")

        # Configura los botones de copia según la tabla y los datos asociados
        if selected_tree == self.tree_a:
            self.copy_to_b['state'] = 'normal' if has_selection and self.data_file_b else 'disabled'
        elif selected_tree == self.tree_b:
            self.copy_to_a['state'] = 'normal' if has_selection and self.data_file_a else 'disabled'


    
            
                
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

            data_to_export = self.data_file_a[start_offset : start_offset + size]

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
        



    def on_closing(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the program?"):
            self.destroy()

    def start(self):
        self.mainloop()

def main():
    Gui().start()

if __name__ == '__main__':
    main()