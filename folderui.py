import sys
import maya.cmds as cmds
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from shiboken2 import wrapInstance
from PySide2 import QtUiTools
import maya.OpenMayaUI as omui
import os
import re
import subprocess
import shutil
import json

_NAMEPROJECT_ = "Folder Structure Projects"
_VERSION_ = "V.0.0.1"

pathDir = os.path.dirname(sys.modules[__name__].__file__)
fileUi = '%s/folderui_widget_new.ui' % pathDir
config_file_path = "D:/Work_Year3/Work_3/Code/folder_structure/folder_ui/_config.json"


class MainUi(QMainWindow):

    with open(config_file_path, 'r') as f:
        config = json.load(f)
        
    root_path = config['root_path']
    
    def __init__(self, *args, **kwargs):
        super(MainUi, self).__init__(*args, **kwargs)

        self.mainwidget = setup_ui_maya(fileUi, self)
        self.setCentralWidget(self.mainwidget)

        self.resize(800, 500)
        self.setWindowTitle('{} - {}'.format(_NAMEPROJECT_, _VERSION_))
        self.populate_projects_combobox()

        self.mainwidget.close_Button.clicked.connect(self.close)
        self.mainwidget.search_Button.clicked.connect(self.search_name)
        self.mainwidget.refresh_Button.clicked.connect(self.refresh) 
        self.mainwidget.proj_comboBox.currentIndexChanged.connect(self.open_project_folder)
        self.mainwidget.proj_comboBox.currentIndexChanged.connect(self.on_project_selected)
        self.mainwidget.save_Button.clicked.connect(self.save_selected_item)
        self.mainwidget.open_Button.clicked.connect(self.open_file)
  
        self.mainwidget.assetshot_listWidget.itemClicked.connect(self.on_assetshot_selected)
        self.mainwidget.char_listWidget.itemClicked.connect(self.on_char_selected)
        self.mainwidget.astsht_listWidget.itemClicked.connect(self.on_astsht_selected)
        self.mainwidget.department_listWidget.itemClicked.connect(self.on_department_selected)
        self.mainwidget.verpub_listWidget.itemClicked.connect(self.on_verpub_selected)
        
        self.mainwidget.create_assetshot_pushButton.clicked.connect(self.create_assetshot_folder)
        self.mainwidget.create_char_pushButton.clicked.connect(self.create_char_folder)
        self.mainwidget.create_astsht_pushButton.clicked.connect(self.create_astsht_folder)
        self.mainwidget.create_department_pushButton.clicked.connect(self.create_department_folder)
        self.mainwidget.create_verpub_pushButton.clicked.connect(self.create_verpub_folder)
  
    def populate_projects_combobox(self):
        project_folders = [folder for folder in os.listdir(self.root_path) if os.path.isdir(os.path.join(self.root_path, folder))]
        self.mainwidget.proj_comboBox.clear()
        self.mainwidget.proj_comboBox.addItem("(None)")
        self.mainwidget.proj_comboBox.addItems(project_folders)

    def on_project_selected(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        if selected_project != "(None)":
            index = self.mainwidget.proj_comboBox.findText("(None)")
            if index != -1:
                self.mainwidget.proj_comboBox.removeItem(index)
            self.create_asset_listWidget(selected_project)
            self.update_path_lineedit(os.path.join(self.root_path, selected_project))
        else:
            self.mainwidget.proj_comboBox.clear()
            self.populate_projects_combobox()

    def open_project_folder(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        if selected_project == "(None)":
            return
        
        project_folder_path = os.path.join(self.root_path, selected_project)
        
        if os.path.exists(project_folder_path):
            asset_folders = [folder for folder in os.listdir(project_folder_path) if os.path.isdir(os.path.join(project_folder_path, folder))]
            self.mainwidget.assetshot_listWidget.clear()
            self.mainwidget.char_listWidget.clear()
            self.mainwidget.astsht_listWidget.clear()
            self.mainwidget.department_listWidget.clear()
            self.mainwidget.verpub_listWidget.clear()
            self.mainwidget.result_listWidget.clear()
            self.mainwidget.assetshot_listWidget.addItems(asset_folders)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for project '{}' does not exist.".format(selected_project))

    def search_name(self):
        search_name = self.mainwidget.path_lineEdit_2.text()
        selected_project = self.mainwidget.proj_comboBox.currentText()
        project_path = os.path.join(self.root_path, selected_project)
        search_results = self.search_files_and_folders(project_path, search_name)

        if not search_results:
            QMessageBox.warning(self, "No Results Found", "No folder or file found with the name '{}'.".format(search_name))
        else:
            self.display_search_results(search_results)

        self.mainwidget.path_lineEdit_2.clear()

    def search_files_and_folders(self, base_path, search_name):
        results = []
        for root, dirs, files in os.walk(base_path):
            for name in dirs + files:
                if search_name.lower() in name.lower():
                    results.append(os.path.join(root, name))
        return results

    def display_search_results(self, search_results):
        self.mainwidget.assetshot_listWidget.clear()
        self.mainwidget.char_listWidget.clear()
        self.mainwidget.astsht_listWidget.clear()
        self.mainwidget.department_listWidget.clear()
        self.mainwidget.verpub_listWidget.clear()
        self.mainwidget.result_listWidget.clear()

        for result in search_results:
            relative_path = os.path.relpath(result, self.root_path)
            path_segments = relative_path.split(os.sep)

            if len(path_segments) > 1:
                self.mainwidget.assetshot_listWidget.addItem(path_segments[1])
            if len(path_segments) > 2:
                self.mainwidget.char_listWidget.addItem(path_segments[2])
            if len(path_segments) > 3:
                self.mainwidget.astsht_listWidget.addItem(path_segments[3])
            if len(path_segments) > 4:
                self.mainwidget.department_listWidget.addItem(path_segments[4])
            if len(path_segments) > 5:
                self.mainwidget.verpub_listWidget.addItem(path_segments[5])
            if len(path_segments) > 6:
                self.mainwidget.result_listWidget.addItem(path_segments[6])


    def find_folders(self, root_folder, search_name):
        matching_folders = []
        for dirpath, dirnames, filenames in os.walk(root_folder):
            for dirname in dirnames:
                if search_name.lower() in dirname.lower():
                    matching_folders.append(os.path.relpath(os.path.join(dirpath, dirname), root_folder))
        return matching_folders
    
    def refresh(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        if selected_project:
            self.open_project_folder()
            if self.mainwidget.assetshot_listWidget.currentItem():
                self.on_assetshot_selected(self.mainwidget.assetshot_listWidget.currentItem())
            if self.mainwidget.char_listWidget.currentItem():
                self.on_char_selected(self.mainwidget.char_listWidget.currentItem())
            if self.mainwidget.astsht_listWidget.currentItem():
                self.on_astsht_selected(self.mainwidget.astsht_listWidget.currentItem())
            if self.mainwidget.department_listWidget.currentItem():
                self.on_department_selected(self.mainwidget.department_listWidget.currentItem())
            if self.mainwidget.verpub_listWidget.currentItem():
                self.on_verpub_selected(self.mainwidget.verpub_listWidget.currentItem())

    def create_asset_listWidget(self, project_name):
        project_path = os.path.join(self.root_path, project_name)
        assetshot_folders = [folder for folder in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, folder))]
        self.mainwidget.assetshot_listWidget.clear()
        self.mainwidget.assetshot_listWidget.addItems(assetshot_folders)

    def on_assetshot_selected(self, item):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = item.text()
        
        # Clear dependent list widgets
        self.mainwidget.char_listWidget.clear()
        self.mainwidget.astsht_listWidget.clear()
        self.mainwidget.department_listWidget.clear()
        self.mainwidget.verpub_listWidget.clear()
        self.mainwidget.result_listWidget.clear()
        
        # Populate the next list widget if the folder exists
        self.populate_char_list(selected_project, assetshot_folder)
        self.update_path_lineedit(os.path.join(self.root_path, selected_project, assetshot_folder))


    def populate_char_list(self, project_name, assetshot_folder):
        assetshot_path = os.path.join(self.root_path, project_name, assetshot_folder)
        if os.path.exists(assetshot_path):
            char_folders = [folder for folder in os.listdir(assetshot_path) if os.path.isdir(os.path.join(assetshot_path, folder))]
            self.mainwidget.char_listWidget.clear()
            self.mainwidget.char_listWidget.addItems(char_folders)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for asset/shot '{}' does not exist.".format(assetshot_folder))

    def on_char_selected(self, item):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem().text()
        char_folder = item.text()
        self.populate_astsht_list(selected_project, assetshot_folder, char_folder)
        self.update_path_lineedit(os.path.join(self.root_path, selected_project, assetshot_folder, char_folder))

    def populate_astsht_list(self, project_name, assetshot_folder, char_folder):
        char_path = os.path.join(self.root_path, project_name, assetshot_folder, char_folder)
        if os.path.exists(char_path):
            astsht_folders = [folder for folder in os.listdir(char_path) if os.path.isdir(os.path.join(char_path, folder))]
            self.mainwidget.astsht_listWidget.clear()
            self.mainwidget.department_listWidget.clear()
            self.mainwidget.verpub_listWidget.clear()
            self.mainwidget.result_listWidget.clear()
            self.mainwidget.astsht_listWidget.addItems(astsht_folders)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for char '{}' does not exist.".format(char_folder))

    def on_astsht_selected(self, item):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem().text()
        char_folder = self.mainwidget.char_listWidget.currentItem().text()
        astsht_folder = item.text()
        self.populate_department_list(selected_project, assetshot_folder, char_folder, astsht_folder)
        self.update_path_lineedit(os.path.join(self.root_path, selected_project, assetshot_folder, char_folder, astsht_folder))

    def populate_department_list(self, project_name, assetshot_folder, char_folder, astsht_folder):
        astsht_path = os.path.join(self.root_path, project_name, assetshot_folder, char_folder, astsht_folder)
        if os.path.exists(astsht_path):
            department_folders = [folder for folder in os.listdir(astsht_path) if os.path.isdir(os.path.join(astsht_path, folder))]
            self.mainwidget.department_listWidget.clear()
            self.mainwidget.verpub_listWidget.clear()
            self.mainwidget.result_listWidget.clear()
            self.mainwidget.department_listWidget.addItems(department_folders)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for asset/shot '{}' does not exist.".format(astsht_folder))

    def on_department_selected(self, item):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem().text()
        char_folder = self.mainwidget.char_listWidget.currentItem().text()
        astsht_folder = self.mainwidget.astsht_listWidget.currentItem().text()
        department_folder = item.text()
        self.populate_verpub_list(selected_project, assetshot_folder, char_folder, astsht_folder, department_folder)
        self.update_path_lineedit(os.path.join(self.root_path, selected_project, assetshot_folder, char_folder, astsht_folder, department_folder))

    def populate_verpub_list(self, project_name, assetshot_folder, char_folder, astsht_folder, department_folder):
        department_path = os.path.join(self.root_path, project_name, assetshot_folder, char_folder, astsht_folder, department_folder)
        if os.path.exists(department_path):
            verpub_folders = [folder for folder in os.listdir(department_path) if os.path.isdir(os.path.join(department_path, folder))]
            self.mainwidget.verpub_listWidget.clear()
            self.mainwidget.verpub_listWidget.addItems(verpub_folders)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for department '{}' does not exist.".format(department_folder))

    def on_verpub_selected(self, item):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem().text()
        char_folder = self.mainwidget.char_listWidget.currentItem().text()
        astsht_folder = self.mainwidget.astsht_listWidget.currentItem().text()
        department_folder = self.mainwidget.department_listWidget.currentItem().text()
        verpub_folder = item.text()
        self.populate_result_list(selected_project, assetshot_folder, char_folder, astsht_folder, department_folder, verpub_folder)
        self.update_path_lineedit(os.path.join(self.root_path, selected_project, assetshot_folder, char_folder, astsht_folder, department_folder, verpub_folder))

    def populate_result_list(self, project_name, assetshot_folder, char_folder, astsht_folder, department_folder, verpub_folder):
        verpub_path = os.path.join(self.root_path, project_name, assetshot_folder, char_folder, astsht_folder, department_folder, verpub_folder)
        if os.path.exists(verpub_path):
            files = [f for f in os.listdir(verpub_path) if os.path.isfile(os.path.join(verpub_path, f))]
            self.mainwidget.result_listWidget.clear()
            self.mainwidget.result_listWidget.clear()
            self.mainwidget.result_listWidget.addItems(files)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for verpub '{}' does not exist.".format(verpub_folder))

    def create_folder(self, base_path, folder_type):
        folder_name, ok = QInputDialog.getText(self, "Create {0} Folder".format(folder_type), "Enter {0} folder name:".format(folder_type))
        if ok and folder_name:
            new_folder_path = os.path.join(base_path, folder_name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                return new_folder_path
            else:
                QMessageBox.warning(self, "Error", "{0} folder '{1}' already exists.".format(folder_type, folder_name))
        return

    def create_assetshot_folder(self):
            selected_project = self.mainwidget.proj_comboBox.currentText()
            new_assetshot_folder_name, ok = QInputDialog.getText(self, "Create Asset/Shot Folder", "Enter the name for the new asset/shot folder:")
            if ok and new_assetshot_folder_name:
                new_assetshot_folder_path = os.path.join(self.root_path, selected_project, new_assetshot_folder_name)
                try:
                    os.makedirs(new_assetshot_folder_path)
                    self.mainwidget.assetshot_listWidget.addItem(new_assetshot_folder_name)
                except Exception as e:
                    QMessageBox.warning(self, "Error Creating Folder", str(e))

    def create_char_folder(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem()
        assetshot_folder_name = assetshot_folder.text()
        new_char_folder_name, ok = QInputDialog.getText(self, "Create Character Folder", "Enter the name for the new character folder:")
        if ok and new_char_folder_name:
            new_char_folder_path = os.path.join(self.root_path, selected_project, assetshot_folder_name, new_char_folder_name)
            try:
                os.makedirs(new_char_folder_path)
                self.mainwidget.char_listWidget.addItem(new_char_folder_name)
            except Exception as e:
                QMessageBox.warning(self, "Error Creating Folder", str(e))

    def create_astsht_folder(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem()
        char_folder = self.mainwidget.char_listWidget.currentItem()
        assetshot_folder_name = assetshot_folder.text()
        char_folder_name = char_folder.text()
        new_astsht_folder_name, ok = QInputDialog.getText(self, "Create Asset/Shot Folder", "Enter the name for the new asset/shot folder:")
        if ok and new_astsht_folder_name:
            new_astsht_folder_path = os.path.join(self.root_path, selected_project, assetshot_folder_name, char_folder_name, new_astsht_folder_name)
            try:
                os.makedirs(new_astsht_folder_path)
                self.mainwidget.astsht_listWidget.addItem(new_astsht_folder_name)
            except Exception as e:
                QMessageBox.warning(self, "Error Creating Folder", str(e))

    def create_department_folder(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem()
        char_folder = self.mainwidget.char_listWidget.currentItem()
        astsht_folder = self.mainwidget.astsht_listWidget.currentItem()
        assetshot_folder_name = assetshot_folder.text()
        char_folder_name = char_folder.text()
        astsht_folder_name = astsht_folder.text()
        new_department_folder_name, ok = QInputDialog.getText(self, "Create Department Folder", "Enter the name for the new department folder:")
        if ok and new_department_folder_name:
            new_department_folder_path = os.path.join(self.root_path, selected_project, assetshot_folder_name, char_folder_name, astsht_folder_name, new_department_folder_name)
            try:
                os.makedirs(new_department_folder_path)
                self.mainwidget.department_listWidget.addItem(new_department_folder_name)
            except Exception as e:
                QMessageBox.warning(self, "Error Creating Folder", str(e))

    def create_verpub_folder(self):
        selected_project = self.mainwidget.proj_comboBox.currentText()
        assetshot_folder = self.mainwidget.assetshot_listWidget.currentItem()
        char_folder = self.mainwidget.char_listWidget.currentItem()
        astsht_folder = self.mainwidget.astsht_listWidget.currentItem()
        department_folder = self.mainwidget.department_listWidget.currentItem()
        assetshot_folder_name = assetshot_folder.text()
        char_folder_name = char_folder.text()
        astsht_folder_name = astsht_folder.text()
        department_folder_name = department_folder.text()
        new_verpub_folder_name, ok = QInputDialog.getText(self, "Create Version/Publish Folder", "Enter the name for the new version/publish folder:")
        if ok and new_verpub_folder_name:
            new_verpub_folder_path = os.path.join(self.root_path, selected_project, assetshot_folder_name, char_folder_name, astsht_folder_name, department_folder_name, new_verpub_folder_name)
            try:
                os.makedirs(new_verpub_folder_path)
                self.mainwidget.verpub_listWidget.addItem(new_verpub_folder_name)
            except Exception as e:
                QMessageBox.warning(self, "Error Creating Folder", str(e))
                
    def save_selected_item(self):
        selected_item = self.mainwidget.result_listWidget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No File Selected", "Please select a file to save.")
            return

        current_file_name = selected_item.text()
        current_path = self.mainwidget.path_lineEdit.text()
        current_file_path = os.path.join(current_path, current_file_name)
        
        new_file_name = self.mainwidget.save_lineEdit.text().strip()
        base_name, extension = os.path.splitext(current_file_name)
        
        if not new_file_name:
            # Increment version number for existing file
            version_pattern = re.compile(r"^(.*?)(\d{3})$")
            match = version_pattern.match(base_name)
            
            if match:
                base_name, version = match.groups()
                new_version = int(version) + 1
            else:
                base_name = base_name
                new_version = 1
            
            new_file_name = "{}{:03}{}".format(base_name, new_version, extension)
        else:
            if not new_file_name.endswith(extension):
                new_file_name += extension

        new_file_path = os.path.join(current_path, new_file_name)
        
        try:
            if os.path.exists(current_file_path):
                shutil.copy(current_file_path, new_file_path)
            else:
                QMessageBox.warning(self, "File Not Found", "The selected file does not exist on disk.")
            
            self.populate_result_list(*self.get_current_list_context())
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to save file '{}': {}".format(new_file_name, e))

    def open_file(self):
            selected_item = self.mainwidget.result_listWidget.currentItem()

            # If no item is selected in the search results, try to open the selected item from the project
            if not selected_item:
                selected_item = self.mainwidget.result_listWidget.currentItem()

            if selected_item:
                file_name = selected_item.text()
                current_path = self.mainwidget.path_lineEdit.text()
                file_path = os.path.join(current_path, file_name)
                
                _, file_extension = os.path.splitext(file_path)
                
                try:
                    if file_extension in ['.ma', '.mb']:
                        import maya.cmds as cmds
                        if cmds.file(q=True, modified=True):
                            result = QMessageBox.question(self, "Unsaved Changes",
                                                        "There are unsaved changes. Do you want to save them?",
                                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                            if result == QMessageBox.Save:
                                cmds.file(save=True)
                            elif result == QMessageBox.Discard:
                                cmds.file(force=True, new=True)
                            else:
                                return
                        cmds.file(file_path, o=True)
                    else:
                        if sys.platform == "win32":
                            os.startfile(file_path)
                        elif sys.platform == "darwin":
                            subprocess.Popen(['open', file_path])
                        else:
                            subprocess.Popen(['xdg-open', file_path])
                except Exception as e:
                    QMessageBox.critical(self, "Error", "Failed to open file '{}': {}".format(file_name, e))

    def display_search_results(self, search_results):
        widgets = [
            self.mainwidget.assetshot_listWidget,
            self.mainwidget.char_listWidget,
            self.mainwidget.astsht_listWidget,
            self.mainwidget.department_listWidget,
            self.mainwidget.verpub_listWidget,
            self.mainwidget.result_listWidget
        ]
        
        for widget in widgets:
            widget.clear()

        for result in search_results:
            relative_path = os.path.relpath(result, self.root_path)
            path_segments = relative_path.split(os.sep)
            
            for i, segment in enumerate(path_segments[1:7]):
                widgets[i].addItem(segment)
            
            if len(path_segments) > 6:
                item = QListWidgetItem(path_segments[6])
                widgets[5].addItem(item)
                item.setData(Qt.UserRole, result)
                item.setFlags(item.flags() | Qt.ItemIsSelectable)


    def update_path_lineedit(self, path):
        self.mainwidget.path_lineEdit.setText(path)

    def get_current_list_context(self):
        return (
            self.mainwidget.proj_comboBox.currentText(),
            self.mainwidget.assetshot_listWidget.currentItem().text(),
            self.mainwidget.char_listWidget.currentItem().text(),
            self.mainwidget.astsht_listWidget.currentItem().text(),
            self.mainwidget.department_listWidget.currentItem().text(),
            self.mainwidget.verpub_listWidget.currentItem().text()
        )

    def refresh_current_list_widget(self, path):
        """ Refresh the current list widget based on the path. """
        segments = os.path.relpath(path, self.root_path).split(os.sep)
        
        if len(segments) == 1:
            self.on_project_selected()
        elif len(segments) == 2:
            self.populate_char_list(segments[0], segments[1])
        elif len(segments) == 3:
            self.populate_astsht_list(segments[0], segments[1], segments[2])
        elif len(segments) == 4:
            self.populate_department_list(segments[0], segments[1], segments[2], segments[3])
        elif len(segments) == 5:
            self.populate_verpub_list(segments[0], segments[1], segments[2], segments[3], segments[4])
        else:
            self.populate_result_list(segments[0], segments[1], segments[2], segments[3], segments[4], segments[5])


def setup_ui_maya(folderui_widget, parent):
    fileUi = os.path.dirname(folderui_widget)
    qt_loader = QtUiTools.QUiLoader()
    qt_loader.setWorkingDirectory(fileUi)

    f = QFile(folderui_widget)
    f.open(QFile.ReadOnly)

    myWidget = qt_loader.load(f, parent)
    f.close()

    return myWidget


def run():
    global ui
    try:
        ui.close()
    except:
        pass

    ptr = wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)
    ui = MainUi(parent=ptr)
    ui.show()

run()
