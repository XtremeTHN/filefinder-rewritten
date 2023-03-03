import gi, threading, time, os, requests
gi.require_versions({'Adw':'1','Gtk':'4.0'})
from gi.repository import Gtk, Adw, Gio, GLib, GObject
from modules.funcs import jsonEx, finder, files_handler, compress, Drive
from modules.libupd import libupd
from shutil import move

Adw.init()

configs = jsonEx.get('modules/configs.json')
exts = jsonEx.get('modules/exts.json')
def add_to_expander_row(widget: Gtk.Widget, properties: dict, icon=Gtk.Image.new_from_icon_name(icon_name='open-menu-symbolic')):
    adw_expander_row = Adw.ExpanderRow.new()
    adw_expander_row.add_prefix(widget=icon)
    adw_expander_row.set_title(title=properties['title'])
    adw_expander_row.set_subtitle(subtitle=properties['subtitle'])
    if type(widget) in [tuple, list]:
        for x in widget:
            adw_expander_row.add_row(child=x)
    else:
        adw_expander_row.add_row(child=widget)
    return adw_expander_row
    
def add_to_action_row(widget: Gtk.Widget, signal: str, callback: object, properties: dict, icon=Gtk.Image.new_from_icon_name(icon_name='open-menu-symbolic'), connect=True, return_icon=False):
    if type(widget) in [tuple, list]:
        for x in widget:
            x.set_valign(align=Gtk.Align.CENTER)
    else:
        widget.set_valign(align=Gtk.Align.CENTER)
        if connect:
            widget.connect(signal, callback)

    adw_action_row = Adw.ActionRow.new()
    adw_action_row.set_title(title=properties['title'])
    adw_action_row.set_subtitle(subtitle=properties['subtitle'])
    adw_action_row.add_prefix(widget=icon)
    if type(widget) in [tuple, list]:
        for x in widget:
            adw_action_row.add_suffix(widget=x)
    else:
        adw_action_row.add_suffix(widget=widget)
        
    if not return_icon:
        return adw_action_row
    else:
        return adw_action_row, icon

class MessageDialog(Gtk.MessageDialog):
    def __init__(self, **kwargs) -> None:
        self.callback = kwargs.get("callback")
        self.args = kwargs.get("args")
        del kwargs['callback'], kwargs['args']
        super().__init__(**kwargs)
        if self.args:
            temp_list = ['"{}"'.format(elem) for elem in self.args]
            exec("self.callback({})".format(', '.join(temp_list)))
        if self.callback:
            self.connect('response', self.callback)

class NotIterableError(Exception):
    pass

class SelcFolder(Gtk.FileChooserDialog):
    def __init__(self, **kwargs):
        super().__init__(transient_for=kwargs.get("parent"), use_header_bar=kwargs.get("use_header_bar"))
        try:
            self.callback = kwargs.get("callback")
            self.args = kwargs.get("args")
        except:
            self.callback = self.placeholder
            self.args = []
        self.type = kwargs.get("dialog_type")
        if type(self.args) not in [list,tuple]:
            raise NotIterableError("No es iterable")
        self.set_action(action=self.type)
        self.set_title(title=kwargs.get("title"))
        self.set_modal(modal=True)

        self.connect('response', self.response)
        self.add_buttons('_Cancelar', Gtk.ResponseType.CANCEL,
                         '_Seleccionar', Gtk.ResponseType.OK)
        self.show()
    
    def response(self, widget, response_w):
        if response_w == Gtk.ResponseType.OK:
            if self.args:
                temp_list = ['"{}"'.format(elem) for elem in self.args]
                exec("self.callback(self.get_file().get_path(), {})".format(', '.join(temp_list)))
            else:
                self.callback(self.get_file().get_path())
        widget.close()
    
    def placeholder(self, file):
        pass

class ConfigsWindow(Gtk.Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configs = jsonEx.get('modules/configs.json')
        self.set_title(title='Preferencias generales')
        self.set_default_size(width=800, height=300)
        self.set_size_request(width=800, height=300)

        self.set_titlebar(titlebar=Gtk.HeaderBar.new())

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.box.set_margin_top(margin=12)
        self.box.set_margin_end(margin=12)
        self.box.set_margin_bottom(margin=12)
        self.box.set_margin_start(margin=12)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(mode=Gtk.SelectionMode.NONE)
        self.listbox.get_style_context().add_class(class_name='boxed-list')
        self.box.append(self.listbox)

        self.switch_delay = Gtk.Switch.new()
        self.switch_auto = Gtk.Switch.new()
        self.switch_delay.set_active(self.configs['gui_configs']['delay_progress_bar'])
        self.switch_auto.set_active(self.configs['check_updates'])

        adjustment = Gtk.Adjustment(upper=1000, step_increment=1, page_increment=10)
        self.spin_btt1 = Gtk.SpinButton()
        self.spin_btt1.set_adjustment(adjustment)
        self.spin_btt1.set_numeric(True)
        self.spin_btt1.set_value(self.configs['gui_configs']['seconds_delay'] * 1000)

        # Configuraciones de la Interfaz Grafica de Usuario
        self.delay_configs = {
            'set_delay':               add_to_action_row(self.switch_delay, 'notify::active', self.on_switch_delay_activate, 
                                       {'title':"Tiempo", 'subtitle':'Poner delay en barra de progreso (microsegundos)'}),
            'set_delay_miliseconds':  add_to_action_row(self.spin_btt1, 'value-changed', self.on_spinbtt_changed, 
                                       {'title':"Segundos a pausar", 'subtitle':'Cambia los segundos que quieras esperar (en milisegundos)'}, icon=Gtk.Image.new_from_icon_name('appointment-new-symbolic'))
        }
        delay_expander = add_to_expander_row([self.delay_configs['set_delay'], self.delay_configs['set_delay_miliseconds']], 
                                             {'title':'Delay', 'subtitle':'Configuraciones de delay para barra de progreso'})

        gui_configs_expander = add_to_expander_row(delay_expander, 
                            {'title':'GUI Configs', 'subtitle':'Expande para descubrir configuraciones de la interfaz'},
                            icon=Gtk.Image.new_from_icon_name("window-new-symbolic")
                            )
        self.listbox.append(child=gui_configs_expander)
        # Fin de las configuraciones de GUI

        # Configuraciones de la Interfaz de Terminal de Usuario
        self.label = Gtk.Label.new()
        self.label.set_label("Configuraciones no disponibles actualmente")
        tui_configs_expander = add_to_expander_row(self.label,
                                                   {'title':'TUI Configs', 'subtitle':'Expande para descubrir configuraciones de la Interfaz de Usuario de Terminal'},
                                                   icon=Gtk.Image.new_from_icon_name('utilities-terminal-symbolic'))
        self.listbox.append(child=tui_configs_expander)
        # Fin de configuracion de TUI

        # Configuraciones de pydrive2
        self.button_account = Gtk.Button.new()
        if self.configs['gdrive_confs']['account_name'] != "":
            self.button_account.set_label("Desvincular")
            msg = self.configs['gdrive_confs']['account_name']
            if self.configs['gdrive_confs']['account_photo'] != "":
                account_icon = Gtk.Image.new_from_file(self.configs['gdrive_confs']['account_photo'])
            else:
                account_icon = Gtk.Image.new_from_icon_name('avatar-default-symbolic')
        else:
            self.button_account.set_label("Vincular")
            account_icon = Gtk.Image.new_from_icon_name('avatar-default-symbolic')
            msg = "Sin acceder"

        self.account_name, self.account_icon = add_to_action_row(self.button_account, 'clicked', self.on_button_account_clicked,
                                         {'title':f'Cuenta: {msg}', 'subtitle':'Vincula/Desvincula tu cuenta de Google Drive'}, icon=account_icon, return_icon=True)

        self.entry_folder = Gtk.Entry()
        self.entry_btt = Gtk.Button()
        
        if self.configs['gdrive_confs']['default_folder_name'] != "":
            self.entry_folder.set_placeholder_text(self.configs['gdrive_confs']['default_folder_name'])
        self.entry_btt.set_label("✓")
        self.entry_btt.connect('clicked', self.on_edited_entry)

        self.folder_name = add_to_action_row([self.entry_folder, self.entry_btt], "", "",
                                             {'title':'Nombre de carpeta', 'subtitle':'Nombre de la carpeta que se creara en tu cuenta de Google Drive para cuando se suban tus archivos'}, 
                                             icon=Gtk.Image.new_from_icon_name(icon_name='folder-symbolic'))

        drive_expander = add_to_expander_row([self.account_name, self.folder_name],
                                             {'title':'Google Drive Configs', 'subtitle':'Configuraciones variadas de Google Drive'},
                                             icon=Gtk.Image.new_from_icon_name(icon_name='applications-internet-symbolic'))
        self.listbox.append(child=drive_expander)
        # Fin de configuraciones de pydrive2

        # Configuracion de chequeo automatico de actualizaciones
        auto_check_switch = add_to_action_row(self.switch_auto, 'notify::active', self.on_switch_auto_update_activate,
                            {'title':'Chequeo de actualizaciones', 'subtitle':'Checar automaticamente si hay actualizaciones nuevas cada que se abre el programa'})
        self.listbox.append(child=auto_check_switch)
        # Fin de configuracion de auto_check_upd

        self.set_child(self.box)

    def on_switch_delay_activate(self, switch: Gtk.Switch, boolean):
        if switch.get_active():
            self.configs['gui_configs']['delay_progress_bar'] = True
        else:
            self.configs['gui_configs']['delay_progress_bar'] = False
        jsonEx.update_json("modules/configs.json", self.configs)
            

    def on_spinbtt_changed(self, scroll):
        self.configs['gui_configs']['seconds_delay'] = self.spin_btt1.get_value_as_int() / 1000
        jsonEx.update_json("modules/configs.json",self.configs)

    def on_switch_auto_update_activate(self, switch, boolean):
        if switch.get_active():
            self.configs['check_updates'] = True
        else:
            self.configs['check_updates'] = False
        jsonEx.update_json("modules/configs.json", self.configs)
    
    def on_button_account_clicked(self, btt):
        if self.button_account.get_label() == "Desvincular":
            print("Vincular")
            self.button_account.set_label("Vincular")
            self.account_name.set_title("Cuenta: Sin acceder")
            self.configs['gdrive_confs']['account_name'] = ""
            jsonEx.update_json('modules/configs.json', self.configs)
            os.system(f'rm {os.path.join(os.getenv("HOME"), ".local/share/secrets/.pydrive", ".*")}')
            os.system(f'rm -r {os.path.join(os.getenv("HOME"), ".cache", "com.github.FileFinder.XtremeTHN")}')
            self.account_name.remove(self.account_icon)
            self.account_name.add_prefix(widget=Gtk.Image.new_from_icon_name('avatar-default-symbolic'))
        else:
            print("Vinculando")
            self.user_name = Drive().user_info()
            
            self.button_account.set_label("Desvincular")
            self.account_name.set_title("Cuenta: {}".format(self.user_name.get('name')))
            
            self.configs['gdrive_confs']['account_name'] = self.user_name.get('name')
            jsonEx.update_json('modules/configs.json', self.configs)
            thread = threading.Thread(target=self.down_account_photo)
            thread.start()

    def on_edited_entry(self, btt):
        self.configs['gdrive_confs']['default_folder_name'] = self.entry_folder.get_text()
        jsonEx.update_json('modules/configs.json', self.configs)

    def down_account_photo(self):
        path = os.path.join(os.getenv('HOME'), ".cache", "com.github.FileFinder.XtremeTHN")
        if not os.path.exists(os.path.join(path, "account_image.png")):
            print("Downloading account photo...")
            image = requests.get(self.user_name['user']['picture']['url'])
            os.system(f'mkdir -p {path}')
            with open(os.path.join(path, "account_image.png"), 'wb') as file:
                file.write(image.content)
            self.configs['gdrive_confs']['account_photo'] = os.path.join(path, "account_image.png")
            jsonEx.update_json('modules/configs.json', self.configs)
        else:
            self.configs['gdrive_confs']['account_photo'] = os.path.join(path, "account_image.png")
            jsonEx.update_json('modules/configs.json', self.configs)


class ResultsWindow(Gtk.Dialog):
    def __init__(self, **kwargs):
        path = kwargs.get("path")
        ext = kwargs.get("ext")
        del kwargs["path"], kwargs["ext"]
        super().__init__(**kwargs)

        self.set_title(title='Resultados')
        self.set_default_size(width=600, height=400)
        self.set_size_request(width=600, height=400)

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        vbox = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(margin=12)
        vbox.set_margin_end(margin=12)
        vbox.set_margin_bottom(margin=12)
        vbox.set_margin_start(margin=12)
        self.set_child(child=vbox)

        self.configs = jsonEx.get('modules/configs.json')

        # Janela com rolagem onde será adicionado o Gtk.TreeView().
        scrolled_window = Gtk.ScrolledWindow.new()
        vbox.append(child=scrolled_window)

        # Criando um modelo com `Gtk.ListStore()`.
        self.list_store = Gtk.ListStore.new(
            [GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_INT, GObject.TYPE_INT],
        )

        self.find_obj = finder(path, ext)
        self.files = self.find_obj.find()
        for x in self.find_obj.generalize():
            self.list_store.append(files_handler.stat(x))

        # Criando um `Gtk.TreeView()`.
        tree_view = Gtk.TreeView.new_with_model(model=self.list_store)
        tree_view.set_vexpand(expand=True)
        scrolled_window.set_child(child=tree_view)

        # Nome das colunas (title).
        cols = ('Nombre', 'Directorio', 'Extension', 'Fecha de modificacion', 'Tamaño', 'UID')
        for i, col in enumerate(cols):
            # Renderizador
            cell_render = Gtk.CellRendererText.new()

            treeviewcolumn = Gtk.TreeViewColumn(
                title=col,
                cell_renderer=cell_render,
                text=i,
            )

            # Agregando al Gtk.TreeView
            tree_view.append_column(column=treeviewcolumn)

        hbuton_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.progressbar = Gtk.ProgressBar()
        self.files_btt = Gtk.Button.new()
        self.comp_btt = Gtk.Button.new()
        self.drive_btt =  Gtk.Button.new()
        self.mv_btt = Gtk.Button.new()

        self.progressbar.set_show_text(True)
        self.progressbar.set_pulse_step(1 / len(self.find_obj.generalize()))

        self.files_btt.set_label("Guardar resultados")
        self.comp_btt.set_label("Comprimir")
        self.drive_btt.set_label("Subir archivos a Google Drive")
        self.mv_btt.set_label("Mover")

        self.files_btt.connect('clicked', self.on_files_btt_clicked)
        self.comp_btt.connect('clicked', self.on_comp_btt_clicked)
        self.drive_btt.connect('clicked', self.on_drive_btt_clicked)
        self.mv_btt.connect('clicked', self.on_mv_btt_clicked)

        hbuton_box.set_homogeneous(True)
        hbuton_box.append(self.files_btt)
        hbuton_box.append(self.comp_btt)
        hbuton_box.append(self.drive_btt)
        hbuton_box.append(self.mv_btt)
        vbox.append(child=hbuton_box)
        vbox.append(child=self.progressbar)
    
    def disable_buttons(self, current_btt):
        if current_btt == "mv":
            self.comp_btt.set_sensitive(False)
            self.files_btt.set_sensitive(False)
            self.drive_btt.set_sensitive(False)
        if current_btt == "comp":
            self.mv_btt.set_sensitive(False)
            self.files_btt.set_sensitive(False)
            self.drive_btt.set_sensitive(False)
        if current_btt == "drive":
            self.mv_btt.set_sensitive(False)
            self.files_btt.set_sensitive(False)
            self.comp_btt.set_sensitive(False)
            
        
    
    def enable_buttons(self, current_btt):
        if current_btt == "mv":
            self.comp_btt.set_sensitive(True)
            self.files_btt.set_sensitive(True)
            self.drive_btt.set_sensitive(True)
        if current_btt == "comp":
            self.mv_btt.set_sensitive(True)
            self.files_btt.set_sensitive(True)
            self.drive_btt.set_sensitive(True)
        if current_btt == "drive":
            self.mv_btt.set_sensitive(True)
            self.files_btt.set_sensitive(True)
            self.comp_btt.set_sensitive(True)
    
    def on_files_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona en donde quieres guardar el archivo",
                   dialog_type=Gtk.FileChooserAction.SAVE, callback=self.files_btt_callback, args=[])

    def files_btt_callback(self, filepath):
        files_handler.save(filepath,self.find_obj.generalize())
    
    def on_comp_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona como quieres guardar tu archivo comprimido",
                   dialog_type=Gtk.FileChooserAction.SAVE, callback=self.comp_btt_callback, args=())
    
    def comp_btt_callback(self, filename):
        self.comp_obj = compress(filename, format='zip')
        threading.Thread(target=self.compress_thread).start()
    
    def compress_thread(self):
        self.disable_buttons("comp")
        for x,v in enumerate(self.find_obj.generalize()):
            self.comp_obj.add_single(v)
            GLib.idle_add(self.progressbar.set_fraction, x / len(self.find_obj.generalize()))
            GLib.idle_add(self.progressbar.set_text, v)
            if self.configs['gui_configs']['delay_progress_bar']:
                time.sleep(self.configs['gui_configs']['seconds_delay'])

        self.comp_obj.finish()
        self.enable_buttons("comp")
        time.sleep(5)
        GLib.idle_add(self.progressbar.set_fraction, 0)
        GLib.idle_add(self.progressbar.set_text, "Listo!")
    
    def on_mv_btt_clicked(self, btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona la carpeta en donde quieras mover los archivos",
                   dialog_type=Gtk.FileChooserAction.SELECT_FOLDER, callback=self.mv_btt_callback, args=[])
    
    def mv_btt_callback(self, filepath):
        self.disable_buttons("mv")
        for x,v in enumerate(self.find_obj.generalize()):
            try:
                move(v, filepath)
                GLib.idle_add(self.progressbar.set_fraction, x / len(self.find_obj.generalize()))
                GLib.idle_add(self.progressbar.set_text, v)
            except:
                continue
        self.enable_buttons("mv")
    
    def upload_files_finded(self):
        # Deshabilitando los botones para evitar problemas de la barra de progreso e hilos
        self.disable_buttons("drive")

        # Inicializando la funcion automatizada de Google Drive hecha por mi
        drive_obj = Drive()

        # Convirtiendo los archivos encontrados a un formato legible para la funcion creada por mi
        files = self.find_obj.drive_format()

        # Creando una carpeeta
        folder_id = drive_obj.create_folder(self.configs['gdrive_confs']['default_folder_name'])
        
        # Preparando la barra de progreso
        GLib.idle_add(self.progressbar.set_text, "Subiendo...")
        
        # Subiendo archivos
        for x,v in enumerate(files['names']):
            # Ver si el boton cancelar ha sido presionado
            if self.cancel:
                # Reestablecer todo
                GLib.idle_add(self.progressbar.set_fraction, 0)
                GLib.idle_add(self.progressbar.set_text, "Cancelado")
                GLib.idle_add(self.drive_btt.set_label, "Subir archivos a Google Drive")
                self.enable_buttons("drive")
                break
            # Si no actualizar la barra de progreso y seguir con la subida de archivos
            # Operacion para calcular el progreso de la subida
            GLib.idle_add(self.progressbar.set_fraction, x / len(self.find_obj.generalize()))

            # Mostrando que archivo esta siendo subido
            GLib.idle_add(self.progressbar.set_text, f"Subiendo: {v}")

            # Subiendo el archivo
            drive_obj.upload(v, files['paths'][x], folder_id, label="", endx='')
        
        # Final de la subida de archivos
        GLib.idle_add(self.progressbar.set_fraction, 0)
        GLib.idle_add(self.progressbar.set_text, "Completado")
        GLib.idle_add(self.drive_btt.set_label, "Subir archivos a Google Drive")
        self.enable_buttons("drive")

        # Funcion anterior utilizada (No cumple con mis requerimientos de el boton para cancelar)
        # drive_obj.uploads(files, folder_id, normal_callback=False, callback=self.upload_callback, args=None)
    
    def on_drive_btt_clicked(self, btt):
        if self.drive_btt.get_label() == "Cancelar":
            self.cancel = True
        else:
            if self.configs['gdrive_confs']['show_alert_dialog_folder']:
                MessageDialog(transient_for=self, message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK,
                            text=f"Se estan subiendo los archivos a la carpeta {self.configs['gdrive_confs']['default_folder_name']}, puedes cambiar el nombre de carpeta predeterminado en las configuraciones",
                            callback=None,
                            args=None).present()
            self.cancel = False
            self.drive_btt.set_label("Cancelar")
            self.drive_thread = threading.Thread(target=self.upload_files_finded)
            self.drive_thread.start()
        

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.configs = jsonEx.get('modules/configs.json')

        self.set_title(title='PyFileFinder')
        self.set_default_size(width=500, height=100)
        self.set_size_request(width=500, height=100)

        headerbar = Gtk.HeaderBar.new()
        self.set_titlebar(titlebar=headerbar)

        menu_button_model = Gio.Menu()
        menu_button_model.append('Preferencias', 'app.preferences')

        menu_button = Gtk.MenuButton.new()
        menu_button.set_icon_name(icon_name='open-menu-symbolic')
        menu_button.set_menu_model(menu_model=menu_button_model)
        headerbar.pack_end(child=menu_button)

        self.box = Gtk.Box()
        self.button_box = Gtk.Box()
        self.center_box = Gtk.CenterBox()
        self.center_box2 = Gtk.CenterBox()
        self.label_input = Gtk.Label()
        self.label_combo = Gtk.Label()
        self.input = Gtk.Entry()
        self.button1 = Gtk.Button()
        self.button2 = Gtk.Button()
        self.button3 = Gtk.Button()
        self.combobox = Gtk.ComboBox()

        self.label_input.set_label("Directorio a buscar")
        self.label_combo.set_label("Extensiones por filtrar")
        self.button1.set_label("...")
        self.button2.set_label("Otra extension")
        self.button3.set_label("Buscar")
        self.center_box.set_start_widget(child=self.label_input)
        self.center_box.set_center_widget(child=self.input)
        self.center_box.set_end_widget(child=self.button1)

        self.button1.connect('clicked', self.on_exam_clicked)
        self.button2.connect('clicked', self.on_other_ext_clicked)
        self.button3.connect('clicked', self.on_find_clicked)

        

        self.center_box2.set_start_widget(child=self.label_combo)
        self.center_box2.set_center_widget(child=self.combobox)
        self.center_box2.set_end_widget(child=self.button2)

        self.center_box.set_margin_top(margin=12)
        self.center_box.set_margin_end(margin=12)
        self.center_box.set_margin_bottom(margin=12)
        self.center_box.set_margin_start(margin=12)
        self.center_box2.set_margin_top(margin=12)
        self.center_box2.set_margin_end(margin=12)
        self.center_box2.set_margin_bottom(margin=12)
        self.center_box2.set_margin_start(margin=12)

        self.button_box.set_margin_top(margin=10)
        self.button_box.set_margin_start(margin=20)
        self.button_box.set_margin_end(margin=20)
        self.button_box.set_margin_bottom(margin=20)
        self.box.set_margin_top(margin=10)

        self.archive = Gtk.ListStore(str)
        for v in exts:
            self.archive.append([v])
        renderer_text = Gtk.CellRendererText()
        self.combobox.pack_start(renderer_text, True)
        self.combobox.add_attribute(renderer_text, "text", 0)
        self.combobox.set_model(self.archive)

        self.combobox.connect('changed', self.combo_on_changed)

        self.combo_selected = None

        self.box.append(child=self.center_box)
        self.box.append(child=self.center_box2)
        self.button_box.append(child=self.button3)
        self.button_box.set_homogeneous(True)
        self.box.append(child=self.button_box)
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_child(child=self.box)
        if self.configs['check_updates']:
            threading.Thread(target=self.check_updates_gui).start()
    
    def combo_on_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.combo_selected = model[tree_iter][:2][0]
    
    def on_exam_clicked(self,btt):
        SelcFolder(parent=self, use_header_bar=True, title="Selecciona la carpeta en donde quieras buscar los archivos", 
                   dialog_type=Gtk.FileChooserAction.SELECT_FOLDER, callback=self.exam_callback, args=[])
        
    def exam_callback(self,filename):
        self.input.set_text(filename)

    def on_other_ext_clicked(self, btt):
        pass

    def on_find_clicked(self, btt):
        if self.combo_selected:
            ResultsWindow(path=self.input.get_text(), ext=self.combo_selected, transient_for=self).present()
        else:
            print("Error debug")
    
    def check_updates_gui(self):
        print("[INFO] Checking updates")
        self.upd_obj = libupd(["https://raw.githubusercontent.com/XtremeTHN/filefinder-rewritten/main/VERSION", "https://raw.githubusercontent.com/XtremeTHN/filefinder-rewritten/main/modules/repo.json"])
        ver = self.upd_obj.checkupd(self.configs['version'])
        print(ver)
        if ver == 1:
            print("")
            """MessageDialog(transient_for=self, message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO,
                            text=f"Se ha detectado una actualizacion nueva. Deseas actualizar? (Puedes desactivar este mensaje desde las configuraciones)",
                            callback=self.update_gui,
                            args=None).present()"""
            self.update_gui()
    
    def update_gui(self, dialog, response):
        if response == Gtk.ResponseType.NO:
            dialog.destroy()
        elif response == Gtk.ResponseType.YES:
            self.progress = Gtk.ProgressBar()
            self.progress.set_text("Actualizando")
            self.box.append(self.progress)
            self.upd_obj.update(mode=self.upd_obj.JsonLoadMethods.WithBaseUrl, callback=self.update_progress)
    
    def update_progress(self, current, total, file):
        GLib.idle_add(self.progress.set_fraction(current / total))
        GLib.idle_add(self.progress.set_text, file)

class MainApplication(Adw.Application):

    def __init__(self):
        super().__init__(application_id="com.github.FileFinder.XtremeTHN",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.create_action('quit', self.exit_app, ['<primary>q'])
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = MainWindow(application=self)
        self.win.present()
        

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_preferences_action(self, action, param):
        ConfigsWindow(transient_for=self.win).present()

    def exit_app(self, action, param):
        self.quit()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)

def init():
    MainApplication().run()