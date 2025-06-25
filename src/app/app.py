from ui_main_window import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PySide6.QtCore import QStringListModel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from pathlib import Path

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Tableau to Power BI")
        
        # Initialize data storage
        self.selected_files = []
        self.file_model = QStandardItemModel()
        
        # Initialize UI components
        self._initialize_widgets()
        self._initialize_file_browser()
    
    def _initialize_widgets(self):
        """Initialize and connect UI widgets"""
        # Set up the file list view model
        self.file_list_view.setModel(self.file_model)
        
        # Connect buttons to their respective methods
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)  # Add Folder button
        self.remove_file_btn.clicked.connect(self.remove_selected)  # Remove button
        self.clear_files_btn.clicked.connect(self.clear_all)  # Clear All button
        self.browse_export_btn.clicked.connect(self.browse_export_path)
        self.begin_migration_btn.clicked.connect(self.begin_migration)  # Begin Migration button
        self.clear_log_btn.clicked.connect(self.clear_log)  # Clear log button
        self.save_log_btn.clicked.connect(self.save_log)  # Save log button
        
        # Set default export path
        default_path = str(Path.cwd() / "data" / "output")
        self.export_path_edit.setText(default_path)
        
        # Set default checkbox states
        self.preserve_conn.setChecked(True)
        self.preserve_formatting.setChecked(True)
        self.create_log.setChecked(True)
        self.include_data.setChecked(True)
        
        # Initialize progress bar
        self.progressBar.setValue(0)
        
        # Initialize statistics labels
        self.update_statistics()
    
    def _initialize_file_browser(self):
        """Initialize file browser functionality"""
        # Set up file list view properties
        self.file_list_view.setSelectionMode(self.file_list_view.SelectionMode.ExtendedSelection)
        self.file_list_view.setAlternatingRowColors(True)
        
        # Set model headers
        self.file_model.setHorizontalHeaderLabels(["File Name", "File Path", "Size"])
        


    def add_files(self):
        """Open file dialog to select Tableau files"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Tableau Files (*.twb *.twbx);;All Files (*)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.add_file_to_list(file_path)
    
    def add_folder(self):
        """Open folder dialog to select directory containing Tableau files"""
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_path = folder_dialog.selectedFiles()[0]
            self.add_folder_files(folder_path)
    
    def add_file_to_list(self, file_path):
        """Add a single file to the file list"""
        path_obj = Path(file_path)
        
        # Check if file already exists in list
        if file_path in self.selected_files:
            QMessageBox.information(self, "File Already Added", 
                                  f"The file '{path_obj.name}' is already in the list.")
            return
        
        # Validate file extension
        if path_obj.suffix.lower() not in ['.twb', '.twbx']:
            QMessageBox.warning(self, "Invalid File Type", 
                              f"'{path_obj.name}' is not a valid Tableau file.\n"
                              "Please select .twb or .twbx files.")
            return
        
        # Add to internal list
        self.selected_files.append(file_path)
        
        # Add to model for display
        file_name_item = QStandardItem(path_obj.name)
        file_path_item = QStandardItem(str(path_obj.parent))
        
        # Get file size
        try:
            file_size = path_obj.stat().st_size
            size_mb = file_size / (1024 * 1024)
            size_text = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_size} bytes"
        except OSError:
            size_text = "Unknown"
        
        file_size_item = QStandardItem(size_text)
        
        # Add row to model
        self.file_model.appendRow([file_name_item, file_path_item, file_size_item])
        
        # Update statistics
        self.update_statistics()
        
        # Log the addition
        self.log_message(f"Added file: {path_obj.name}")
    
    def add_folder_files(self, folder_path):
        """Add all Tableau files from a folder"""
        folder_obj = Path(folder_path)
        tableau_files = []
        
        # Search for Tableau files
        tableau_files.extend(folder_obj.glob("*.twb"))
        tableau_files.extend(folder_obj.glob("*.twbx"))
        
        if not tableau_files:
            QMessageBox.information(self, "No Files Found", 
                                  f"No Tableau files (.twb or .twbx) found in:\n{folder_path}")
            return
        
        added_count = 0
        for file_path in tableau_files:
            if str(file_path) not in self.selected_files:
                self.add_file_to_list(str(file_path))
                added_count += 1
        
        QMessageBox.information(self, "Files Added", 
                              f"Added {added_count} Tableau files from the selected folder.")
    
    def remove_selected(self):
        """Remove selected files from the list"""
        selection_model = self.file_list_view.selectionModel()
        if not selection_model.hasSelection():
            QMessageBox.information(self, "No Selection", "Please select files to remove.")
            return
        
        selected_indexes = selection_model.selectedRows()
        
        # Sort indexes in reverse order to remove from bottom to top
        rows_to_remove = sorted([index.row() for index in selected_indexes], reverse=True)
        
        for row in rows_to_remove:
            # Remove from internal list
            if row < len(self.selected_files):
                removed_file = self.selected_files.pop(row)
                self.log_message(f"Removed file: {Path(removed_file).name}")
            
            # Remove from model
            self.file_model.removeRow(row)
        
        self.update_statistics()
    
    def clear_all(self):
        """Clear all files from the list"""
        if not self.selected_files:
            return
        
        reply = QMessageBox.question(self, "Clear All Files", 
                                   "Are you sure you want to remove all files from the list?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.selected_files.clear()
            self.file_model.clear()
            self.file_model.setHorizontalHeaderLabels(["File Name", "File Path", "Size"])
            self.update_statistics()
            self.log_message("Cleared all files from the list")
    
    def browse_export_path(self):
        """Browse for export directory"""
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            export_path = folder_dialog.selectedFiles()[0]
            self.export_path_edit.setText(export_path)
            self.log_message(f"Export path set to: {export_path}")
    
    def begin_migration(self):
        """Start the migration process"""
        if not self.selected_files:
            QMessageBox.warning(self, "No Files Selected", 
                              "Please add Tableau files to migrate before starting the process.")
            return
        
        export_path = self.export_path_edit.text().strip()
        if not export_path:
            QMessageBox.warning(self, "No Export Path", 
                              "Please specify an export directory.")
            return
        
        # Create export directory if it doesn't exist
        try:
            Path(export_path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "Export Path Error", 
                               f"Could not create export directory:\n{str(e)}")
            return
        
        self.log_message("Starting migration process...")
        self.log_message(f"Files to migrate: {len(self.selected_files)}")
        self.log_message(f"Export directory: {export_path}")
        
        # TODO: Implement actual migration logic here
        QMessageBox.information(self, "Migration Started", 
                              "Migration process has been initiated.\n"
                              "This is where the actual conversion would begin.")
    
    def clear_log(self):
        """Clear the output log"""
        self.output_log.clear()
    
    def save_log(self):
        """Save the log to a file"""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("Text Files (*.txt);;All Files (*)")
        file_dialog.setDefaultSuffix("txt")
        
        if file_dialog.exec():
            log_file_path = file_dialog.selectedFiles()[0]
            try:
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_log.toPlainText())
                QMessageBox.information(self, "Log Saved", 
                                      f"Log saved successfully to:\n{log_file_path}")
            except OSError as e:
                QMessageBox.critical(self, "Save Error", 
                                   f"Could not save log file:\n{str(e)}")
    
    def update_statistics(self):
        """Update the statistics display"""
        self.files_queued.setText(str(len(self.selected_files)))
        self.files_processed.setText("0")  # TODO: Update during actual processing
        self.process_time.setText("00:00:00")  # TODO: Update during actual processing
        self.failures.setText("0")  # TODO: Update during actual processing
    
    def log_message(self, message):
        """Add a message to the output log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.output_log.append(formatted_message)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())