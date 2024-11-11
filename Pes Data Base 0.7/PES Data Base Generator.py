#Librerias

from tkinter import Tk, messagebox, ttk, Listbox, Scrollbar, filedialog, Frame, Menu
import webbrowser
#from hurry.filesize import size

class Gui:
    def __init__(self, master):
        self.master= master
        self.appname='PES Data Base Generator'
        self.version = '0.7'
        self.author =  'Gerardo Contreras'
        self.master.title(self.appname+' '+self.version)
        self.master.geometry("450x300")
        self.master.resizable(False, False)

        # Creating Menubar
        menubar = Menu(self.master)
        self.master.config(menu = menubar)
          
        # Adding File Menu and commands
        file = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label ='File', menu = file)
        file.add_command(label='Open', command = self.open_file, accelerator="Ctrl+O")
        file.add_separator()
        file.add_command(label='Exit', command = self.on_closing, accelerator="Ctrl+Q")

        # Adding Edit Menu and commands
        self.edit = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label='Export/Import', menu = self.edit)
        self.edit.add_command(label='Export', command = self.export_data, accelerator="Ctrl+E", state='disable')
        self.edit.add_command(label='Export All', command = self.export_all_data, accelerator="Ctrl+A", state='disable')
        self.edit.add_command(label='Import', command = self.import_data, accelerator="Ctrl+I", state='disable')

        # Adding Help Menu
        help_ = Menu(menubar, tearoff = 0)
        menubar.add_cascade(label ='Help', menu = help_)
        help_.add_command(label ='Donate', command = self.donate)
        help_.add_command(label ='YouTube', command = self.youtube)
        help_.add_separator()
        help_.add_command(label ='About', command = self.about)

        self.lbox_items = Listbox(self.master, exportselection=False, width=65)
        self.lbox_items.grid(column=0,row=0, padx=30, pady=20)

        self.lbox_items.bind("<<ListboxSelect>>", lambda event: self.get_item_info())
        
    def youtube():     
        webbrowser.open_new('https://www.youtube.com/channel/UCzHGN5DBIXVviZQypFH_ieg')

    def donate():     
        webbrowser.open_new('https://www.paypal.com/paypalme/gerardocj11')
     
    def about():
        MessageBox.showinfo(_AppName_+' '+__version__, 'Program developed by Gerardo Contreras')

    def open_file(self):
        file = filedialog.askopenfile(title = "Select files",mode='r+b',filetypes = (("all files","*.*"),("bin files","*.bin")))
        self.content = bytearray(file.read())
        self.file_name = (file.name)

        self.list_offsets = [slice(37684,641811),slice(649818,653268),slice(653268,662164),slice(643644,645369),slice(645369,649817),
                                  slice(642804,643632),slice(745336,775888),slice(775888,860128)]
        
        self.list_items = ['Base de datos de jugadores','Designacion de jugadores en selecciones','Designacion de jugadores en clubes',
                         'Designacion de dorsales en selecciones','Designacion de dorsales en clubes','Configuracion de botas',
                         'Configuracion kits Selecciones','Configuracion kits Clubes']

        self.lbox_items.delete(0,"end")
        #listbox.insert(END, "{:<15s}  {:>5s}  {:<25s}  {:<5s}".format("Name","id","Nationality","Qual") )
        cols = ('name', 'No1', 'No2', 'total sum')
        listBox = ttk.Treeview(self.master, columns=cols, show='headings')
        
        self.lbox_items.insert('end', *self.list_items)
        self.lbox_items.selectedindex = 0
        self.lbox_items.select_set(0)
        self.edit.entryconfig("Export All", state="normal")

    def get_item_info(self):
        if self.lbox_items.curselection() != ():
            self.item_id = self.lbox_items.get(0, "end").index(self.lbox_items.get(self.lbox_items.curselection()))
            self.edit.entryconfig("Export", state="normal")
            self.edit.entryconfig("Import", state="normal")

        else:
            None

    def export_data(self):
        with open(self.list_items[self.item_id]+'.db',"wb") as t:
            t.write(self.content[self.list_offsets[self.item_id]])
        messagebox.showinfo('Export Data', 'The file has been exported successfully')

    def export_all_data(self):
        for i in range(0,len(self.list_offsets)):
            with open(self.list_items[i]+'.db',"wb") as t:
                t.write(self.content[self.list_offsets[i]])

        messagebox.showinfo('Export All', 'The files have been exported successfully')

    def import_data(self):
        file2 = filedialog.askopenfile(title = "Select files",mode='r+b',filetypes = (("all files","*.*"),("bin files","*.bin")))
        new_data = bytearray(file2.read())
        self.content[self.list_offsets[self.item_id]] = new_data

        with open(self.file_name,"wb") as f:
            f.write(self.content)
        messagebox.showinfo('Import Data', 'The file has been imported successfully')

    def youtube(self):     
        webbrowser.open_new('https://www.youtube.com/channel/UCzHGN5DBIXVviZQypFH_ieg')
        
    def about(self):
        messagebox.showinfo(self.appname+' '+self.version, 'This program was developed by'+' '+self.author)

    def donate(self):     
        webbrowser.open_new('https://www.paypal.com/paypalme/gerardocj11')
        
    def on_closing(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the program?"):
            self.master.destroy()
            
    def start(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()
        
def main():
    Gui(Tk()).start()

if __name__ == '__main__':
    main()
