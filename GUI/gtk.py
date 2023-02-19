import gi, sys, os, threading
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Pango, GLib, GObject
from modules.funcs import jsonEx, files_handler, finder, compress
from shutil import move
Adw.init()

        
class DialogSelecFolder(Gtk.FileChooserDialog):
    # Definindo o diretório padrão.
    def __init__(self, parent, inputx=None, folder=True, func=None, cmp=False, label_widget=None,files=None):
        self.input = inputx
        self.folder = folder
        self.func = func
        self.cmp = cmp
        self.complete = False
        self.label_widget = label_widget

        super().__init__(transient_for=parent, use_header_bar=True)
        if folder:
            self.set_action(action=Gtk.FileChooserAction.SELECT_FOLDER)
            title = 'Selecciona la carpeta en donde se buscaran los archivos'
        else:
            self.set_action(action=Gtk.FileChooserAction.SAVE)
            title = 'Selecciona en donde quieres guardar los resultados'
        self.set_title(title=title)
        self.set_modal(modal=True)
        self.connect('response', self.dialog_response)

        self.add_buttons(
            '_Cancelar', Gtk.ResponseType.CANCEL,
            '_Seleccionar', Gtk.ResponseType.OK
        )

        self.show()
    def dialog_response(self, widget, response):
        if response == Gtk.ResponseType.OK:
            if self.folder:
                glocalfile = self.get_file()
                if self.input:
                    self.input.set_text(glocalfile.get_path())
                if self.func:
                    self.func(glocalfile)
            else:
                self.folder = self.get_file()
                if self.cmp:
                    self.destroy()
                    self.label_widget.set_text("Operacion: Comprimir  Progreso: ")
                    self.func(self.get_file().get_path())
                else:
                    self.func(self.get_file())
                    self.complete = True
        widget.close()

class ResultsWindow(Gtk.Dialog):

    # Variável auxiliar que armazena o valor do filtro.
    current_filter_language = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(title='Resultados')
        self.set_default_size(width=int(1366 / 2), height=int(768 / 2))
        self.set_size_request(width=int(1366 / 2), height=int(768 / 2))

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        self.set_child(child=vbox)

        # Janela com rolagem onde será adicionado o Gtk.TreeView().
        scrolled_window = Gtk.ScrolledWindow.new()
        vbox.append(child=scrolled_window)

        # Criando um modelo com `Gtk.ListStore()`.
        self.list_store = Gtk.ListStore(str, str, str, str, float, int)

        self.find_obj = finder(input1.get_text(),combo_selected)
        _ = self.find_obj.find()
        self.general = []
        # Adicionando os dados no `Gtk.ListStore()`.
        for x in self.find_obj.generalize():
            self.list_store.append(files_handler.stat(x))
            self.general.append(files_handler.stat(x))

        # Criando um `Gtk.TreeView()`.
        tree_view = Gtk.TreeView.new_with_model(model=self.list_store)
        tree_view.set_vexpand(expand=True)
        scrolled_window.set_child(child=tree_view)

        # Nome das colunas (title)

        cols = ('Nombre', 'Directorio', 'Extension', 'Fecha de modificacion', 'Tamaño', 'UID')
        for i, col in enumerate(cols):
            # Criando um rederizador com para o tipo de dado que será exibido.
            cell_render = Gtk.CellRendererText.new()

            # Configurando o rederizador da primeira coluna.
            if i == 0:
                cell_render.set_property('weight_set', True)
                cell_render.set_property('weight', Pango.Weight.BOLD)

            # Criando a coluna.
            treeviewcolumn = Gtk.TreeViewColumn(
                # Titulo da coluna.
                title=col,
                # Rederizador que será utilizado na coluna.
                cell_renderer=cell_render,
                # Posição (index) da coluna.
                text=i,
            )

            # Adicionando a coluna no `Gtk.TreeView()`.
            tree_view.append_column(column=treeviewcolumn)

        hbuton_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        progress_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        vbox.append(child=hbuton_box)
        vbox.append(child=progress_box)

        self.btt1 = Gtk.Button.new()
        self.btt2 = Gtk.Button.new()
        self.btt3 = Gtk.Button.new()
        self.btt4 = Gtk.Button.new()
        self.label_info = Gtk.Label.new()
        self.label_prog = Gtk.Label.new()
        self.progress = Gtk.ProgressBar.new()
        
        self.progress.set_pulse_step(1 / len(self.find_obj.generalize()))
        self.progress.set_show_text(True)
        self.btt1.set_label("Guardar resultados")
        self.btt2.set_label("Comprimir archvios")
        self.btt3.set_label("Mover archivos")
        self.btt4.set_label("Filtrar por nombre")
        self.label_info.set_label("Operacion: N/A ")
        self.label_prog.set_label("Progreso: N/A")
        self.progress.set_text("N/A")
        self.btt1.connect('clicked',self.btt_clicked)
        self.btt2.connect('clicked', self.comp_clicked)
        self.btt3.connect('clicked', self.mv_clicked)
        self.btt4.connect('clicked', self.filter_clicked)

        labels_box.append(child=self.label_info)
        labels_box.append(child=self.label_prog)

        hbuton_box.append(child=self.btt1)
        hbuton_box.append(child=self.btt2)
        hbuton_box.append(child=self.btt3)
        hbuton_box.append(child=self.btt4)
        hbuton_box.append(child=labels_box)

        progress_box.append(child=self.progress)
        progress_box.set_homogeneous(True)
    
    def unable_btts(self):
        self.btt2.set_sensitive(False)
        self.btt3.set_sensitive(False)
    
    def enable_btts(self):
        self.btt2.set_sensitive(True)
        self.btt3.set_sensitive(True)
    
    def update_prog(self):
        self.unable_btts()
        for x,v in enumerate(self.find_obj.generalize()):
            self.comp.add_single(v)
            GLib.idle_add(self.progress.set_fraction, x / len(self.find_obj.generalize()))
            GLib.idle_add(self.progress.set_text, v)
            GLib.idle_add(self.label_prog.set_label,f"Progreso: {int(x * 100 / len(self.find_obj.generalize()))}%")
        self.comp.finish()
        self.enable_btts()

    def asd(self,a):
        self.comp = compress(a, format='zip')

        threading.Thread(target=self.update_prog).start()

    def new_file(self,file):
        files_handler.save(file.get_path(),self.find_obj.generalize())



    def btt_clicked(self, btt):
        DialogSelecFolder(self.get_parent(),folder=False, func=self.new_file)
        
    def comp_clicked(self,btt):
        DialogSelecFolder(self.get_parent(),folder=False, cmp=True, func=self.asd, label_widget=self.label_info, files=self.find_obj.generalize())

    def filter_clicked(self,btt):
        #self.find_obj.
        pass
    
    def move_runner(self,path):
        self.label_info.set_label("Operacion: Mover")
        self.path = path.get_path()
        self.unable_btts()
        threading.Thread(target=self.move).start()
    
    def move(self):
        self.unable_btts()
        for x,v in enumerate(self.find_obj.generalize()):
            try:
                move(v,self.path)
            except:
                continue
            GLib.idle_add(self.progress.set_fraction, x / len(self.find_obj.generalize()))
            GLib.idle_add(self.progress.set_text, v)
            GLib.idle_add(self.label_prog.set_label,f"Progreso: {int(x * 100 / len(self.find_obj.generalize()))}%")
        GLib.idle_add(self.progress.set_fraction, 1.0)
        GLib.idle_add(self.label_prog.set_label,"Progreso: 100%")
        self.enable_btts()
            
    def mv_clicked(self,btt):
        DialogSelecFolder(self.get_parent(),folder=True, func=self.move_runner)

class PreferencesDialog(Gtk.Dialog):
    names = list(x for x in jsonEx.get('modules/exts.json'))
    config = jsonEx.get('modules/exts.json')
    items = list(map(lambda x: x.capitalize(), names))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(
            title='Extensiones'
        )
        self.set_default_size(width=int(1366 / 2), height=int(768 / 2))
        self.set_size_request(width=int(1366 / 2), height=int(768 / 2))

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        self.set_child(child=vbox)

        self.listbox = Gtk.ListBox.new()
        self.listbox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.listbox.get_style_context().add_class(class_name='boxed-list')
        vbox.append(child=self.listbox)

        for item in self.items:
            icon = Gtk.Image.new_from_icon_name(
                icon_name='text-x-generic-symbolic'
            )

            switch = Gtk.Switch.new()
            switch.set_valign(align=Gtk.Align.CENTER)
            switch.connect('notify::active', self.on_switch_button_clicked)

            adw_action_row = Adw.ActionRow.new()
            adw_action_row.set_title(title=item)
            adw_action_row.set_subtitle(subtitle='Extension')
            adw_action_row.add_prefix(widget=icon)
            adw_action_row.add_suffix(widget=switch)
            self.listbox.append(child=adw_action_row)

    def on_switch_button_clicked(self, switch, boolean):
        print(switch.get_active())

class CustomDialog(Gtk.Dialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title='Informacion')
        self.use_header_bar = True
        self.connect('response', self.dialog_response)

        self.set_width = 600
        self.set_height = 300

        self.add_buttons(
            '_Aceptar', Gtk.ResponseType.OK,
        )

        btn_ok = self.get_widget_for_response(
            response_id=Gtk.ResponseType.OK,
        )
        btn_ok.get_style_context().add_class(class_name='suggested-action')

        content_area = self.get_content_area()
        content_area.set_orientation(orientation=Gtk.Orientation.VERTICAL)
        content_area.set_spacing(spacing=24)
        content_area.set_margin_top(margin=12)
        content_area.set_margin_end(margin=12)
        content_area.set_margin_bottom(margin=12)
        content_area.set_margin_start(margin=12)

        label = Gtk.Label.new(str=msg)
        content_area.append(child=label)
    def dialog_response(self,dialog,response):
        dialog.close()

class gtk(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.run()

    def combo_on_changed(self,combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.combo_selected = model[tree_iter][:2][0]

    def exam_clicked(self,btt):
        DialogSelecFolder(self.main_win, self.input1)

    def open_response(self,dialog, response):
        print(dialog.get_filename(), response)

    def find(self,btt):
        global msg
        if self.input1.get_text() == '':
            msg = 'Porfavor escribe una direccion en donde se buscaran los archivos'
            CustomDialog().present()
            return None
        elif not self.combo_selected:
            msg = 'Porfavor selecciona una extension de la lista'
            CustomDialog().present()
            return None
        global input1, combo_selected
        combo_selected = self.combo_selected
        input1 = self.input1
        ResultsWindow().present()
    def others_clicked(self,btt):
        print("Debug other")
    
    def config_clicked(self,btt):
        PreferencesDialog().present()

    def on_activate(self,app):  
        # Definicion de objetos   
        self.builder = Gtk.Builder.new_from_file('GUI/.FRONTEND/gui.ui')
        self.main_win = self.builder.get_object('main_window')
        self.organizator = self.builder.get_object('organizator')
        self.input1 = self.builder.get_object("input1")
        self.combobox = self.builder.get_object("combo")
        self.btt1 = self.builder.get_object("exam_bt")
        self.btt2 = self.builder.get_object("other_btt")
        self.btt3 = self.builder.get_object("conf_btt")
        self.find_btt = self.builder.get_object("find")
        self.combo_selected = None

        #Agregando elementos a el ComboBox
        self.archive = Gtk.ListStore(str)
        for v in jsonEx.get('modules/exts.json'):
            self.archive.append([v])
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_model(self.archive)

        # Conectando señales
        self.combobox.connect('changed', self.combo_on_changed)
        self.btt1.connect('clicked', self.exam_clicked)
        self.btt2.connect('clicked', self.others_clicked)
        self.btt3.connect('clicked', self.config_clicked)
        self.find_btt.connect('clicked', self.find)
        self.add_window(self.main_win)
        self.main_win.present()
