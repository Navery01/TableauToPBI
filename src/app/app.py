import sys
import os
from pathlib import Path
from datetime import datetime
import threading
import time

# Add the extractors module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'extractors', 'TB2PBI'))

from ui_main_window import Ui_MainWindow
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication
from PySide6.QtCore import QStringListModel, QThread, Signal, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

# Import the conversion functionality
from tableau_to_powerbi import (
    TableauToPowerBIConverter, 
    analyze_tableau_workbook,
    TableauToPowerBIError,
    PBIToolsCompiler
)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Tableau to Power BI Converter")
        
        # Initialize data storage
        self.selected_files = []
        self.file_model = QStandardItemModel()
        self.conversion_worker = None
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Statistics tracking
        self.processed_count = 0
        self.failed_count = 0
        
        # Initialize UI components
        self._initialize_widgets()
        self._initialize_file_browser()
        self._check_prerequisites()
    
    def _check_prerequisites(self):
        """Check and display prerequisite status"""
        pass

                

    def _initialize_widgets(self):
        """Initialize and connect UI widgets"""
        # Set up the file list view model
        self.file_list_view.setModel(self.file_model)
        
        # Connect buttons to their respective methods
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.remove_file_btn.clicked.connect(self.remove_selected)
        self.clear_files_btn.clicked.connect(self.clear_all)
        self.browse_export_btn.clicked.connect(self.browse_export_path)
        self.begin_migration_btn.clicked.connect(self.begin_migration)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)
        
        # Set default export path
        default_path = str(Path.cwd() / "output")
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
        from PySide6.QtWidgets import QAbstractItemView
        self.file_list_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list_view.setAlternatingRowColors(True)
        
        # Set model headers
        self.file_model.setHorizontalHeaderLabels(["File Name", "File Path", "Size"])
        
        # Add context menu
        from PySide6.QtCore import Qt
        self.file_list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list_view.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """Show context menu for file list"""
        if not self.file_list_view.indexAt(position).isValid():
            return
        
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        context_menu = QMenu(self)
        
        # Analyze action
        analyze_action = QAction("📊 Analyze Workbook", self)
        analyze_action.triggered.connect(self.analyze_selected_workbook)
        context_menu.addAction(analyze_action)
        
        # Remove action
        remove_action = QAction("🗑️ Remove from List", self)
        remove_action.triggered.connect(self.remove_selected)
        context_menu.addAction(remove_action)
        
        # Show properties action
        properties_action = QAction("ℹ️ Properties", self)
        properties_action.triggered.connect(self.show_file_properties)
        context_menu.addAction(properties_action)
        
        # Show the menu
        context_menu.exec(self.file_list_view.mapToGlobal(position))
    
    def show_file_properties(self):
        """Show detailed properties of selected file"""
        selection_model = self.file_list_view.selectionModel()
        if not selection_model.hasSelection():
            return
        
        selected_indexes = selection_model.selectedRows()
        if len(selected_indexes) != 1:
            QMessageBox.information(self, "Multiple Selection", "Please select only one file to view properties.")
            return
        
        file_index = selected_indexes[0].row()
        if file_index >= len(self.selected_files):
            return
        
        file_path = self.selected_files[file_index]
        path_obj = Path(file_path)
        
        try:
            stat = path_obj.stat()
            
            properties_text = f"FILE PROPERTIES\n"
            properties_text += "=" * 30 + "\n"
            properties_text += f"Name: {path_obj.name}\n"
            properties_text += f"Path: {path_obj.parent}\n"
            properties_text += f"Size: {stat.st_size:,} bytes ({stat.st_size / (1024*1024):.2f} MB)\n"
            properties_text += f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            properties_text += f"Extension: {path_obj.suffix}\n"
            properties_text += f"Type: {'Tableau Workbook' if path_obj.suffix == '.twbx' else 'Tableau Workbook (XML)'}\n"
            
            QMessageBox.information(self, f"Properties: {path_obj.name}", properties_text)
            
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Could not read file properties:\n{str(e)}")
    
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
        """Start the migration process with actual conversion"""
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
        
        # Disable the migration button during processing
        self.begin_migration_btn.setEnabled(False)
        self.begin_migration_btn.setText("Converting...")
        
        # Reset statistics
        self.processed_count = 0
        self.failed_count = 0
        self.progressBar.setValue(0)
        
        # Prepare conversion options
        options = {
            'preserve_connections': self.preserve_conn.isChecked(),
            'preserve_formatting': self.preserve_formatting.isChecked(),
            'create_log': self.create_log.isChecked(),
            'include_data': self.include_data.isChecked(),
            'preserve_temp': False  # Always cleanup temp files
        }
        
        self.log_message("=" * 50)
        self.log_message("STARTING TABLEAU TO POWER BI CONVERSION")
        self.log_message("=" * 50)
        self.log_message(f"Files to convert: {len(self.selected_files)}")
        self.log_message(f"Export directory: {export_path}")
        self.log_message(f"Conversion options: {options}")
        
        # Start the conversion in a separate thread
        self.conversion_worker = ConversionWorker(self.selected_files, export_path, options)
        
        # Connect worker signals
        self.conversion_worker.progress_updated.connect(self.update_progress)
        self.conversion_worker.file_processed.connect(self.on_file_processed)
        self.conversion_worker.conversion_completed.connect(self.on_conversion_completed)
        self.conversion_worker.log_message.connect(self.log_message)
        
        # Start timer and worker
        self.start_time = datetime.now()
        self.timer.start(1000)  # Update every second
        self.conversion_worker.start()
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progressBar.setValue(value)
    
    def on_file_processed(self, filename, success, message):
        """Handle individual file processing completion"""
        if success:
            self.processed_count += 1
        else:
            self.failed_count += 1
        
        self.update_statistics()
    
    def on_conversion_completed(self, successful, failed):
        """Handle conversion completion"""
        self.timer.stop()
        
        # Re-enable the migration button
        self.begin_migration_btn.setEnabled(True)
        self.begin_migration_btn.setText("Begin Migration")
        
        # Show completion message
        total_time = datetime.now() - self.start_time if self.start_time else None
        time_str = str(total_time).split('.')[0] if total_time else "Unknown"
        
        self.log_message("=" * 50)
        self.log_message("CONVERSION COMPLETED")
        self.log_message("=" * 50)
        self.log_message(f"Successfully converted: {successful}")
        self.log_message(f"Failed conversions: {failed}")
        self.log_message(f"Total processing time: {time_str}")
        
        # Show completion dialog
        QMessageBox.information(self, "Conversion Completed", 
                              f"Conversion process completed!\n\n"
                              f"Successful: {successful}\n"
                              f"Failed: {failed}\n"
                              f"Time: {time_str}\n\n"
                              f"Results saved to: {self.export_path_edit.text()}")
    
    def update_timer(self):
        """Update the processing time display"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            time_str = str(elapsed).split('.')[0]  # Remove microseconds
            self.process_time.setText(time_str)
    
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
        self.files_processed.setText(str(self.processed_count))
        self.failures.setText(str(self.failed_count))
        
        # Process time is updated by the timer
        if not hasattr(self, 'start_time') or self.start_time is None:
            self.process_time.setText("00:00:00")
    
    def log_message(self, message):
        """Add a message to the output log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.output_log.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.output_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def analyze_selected_workbook(self):
        """Analyze a selected Tableau workbook"""
        selection_model = self.file_list_view.selectionModel()
        if not selection_model.hasSelection():
            QMessageBox.information(self, "No Selection", "Please select a file to analyze.")
            return
        
        selected_indexes = selection_model.selectedRows()
        if len(selected_indexes) != 1:
            QMessageBox.information(self, "Multiple Selection", "Please select only one file to analyze.")
            return
        
        file_index = selected_indexes[0].row()
        if file_index >= len(self.selected_files):
            return
        
        file_path = self.selected_files[file_index]
        file_name = Path(file_path).name
        
        try:
            self.log_message(f"Analyzing workbook: {file_name}")
            
            # Perform analysis
            workbook_info = analyze_tableau_workbook(file_path)
            
            # Create analysis summary
            analysis_text = f"WORKBOOK ANALYSIS: {file_name}\n"
            analysis_text += "=" * 50 + "\n"
            
            # Data sources
            data_sources = workbook_info.get('datasources', [])
            analysis_text += f"📋 Data Sources: {len(data_sources)}\n"
            for i, ds in enumerate(data_sources[:5], 1):  # Show first 5
                field_count = len(ds.get('fields', []))
                analysis_text += f"  {i}. {ds.get('name', 'Unnamed')} ({field_count} fields)\n"
            if len(data_sources) > 5:
                analysis_text += f"  ... and {len(data_sources) - 5} more\n"
            
            # Worksheets
            worksheets = workbook_info.get('worksheets', [])
            analysis_text += f"\n📈 Worksheets: {len(worksheets)}\n"
            for i, ws in enumerate(worksheets[:10], 1):  # Show first 10
                analysis_text += f"  {i}. {ws.get('name', 'Unnamed')}\n"
            if len(worksheets) > 10:
                analysis_text += f"  ... and {len(worksheets) - 10} more\n"
            
            # Calculated fields
            calc_fields = workbook_info.get('calculated_fields', [])
            analysis_text += f"\n🧮 Calculated Fields: {len(calc_fields)}\n"
            for i, calc in enumerate(calc_fields[:5], 1):  # Show first 5
                analysis_text += f"  {i}. {calc.get('name', 'Unnamed')}\n"
            if len(calc_fields) > 5:
                analysis_text += f"  ... and {len(calc_fields) - 5} more\n"
            
            # Parameters
            parameters = workbook_info.get('parameters', [])
            analysis_text += f"\n⚙️  Parameters: {len(parameters)}\n"
            for i, param in enumerate(parameters, 1):
                param_type = param.get('datatype', 'unknown')
                analysis_text += f"  {i}. {param.get('name', 'Unnamed')} ({param_type})\n"
            
            # Log the analysis
            self.log_message(analysis_text)
            
            # Show in a dialog
            QMessageBox.information(self, f"Analysis: {file_name}", analysis_text)
            
        except Exception as e:
            error_msg = f"Error analyzing {file_name}: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Analysis Error", error_msg)

class ConversionWorker(QThread):
    """Worker thread for handling file conversion without blocking UI"""
    
    # Signals for communication with main thread
    progress_updated = Signal(int)
    file_processed = Signal(str, bool, str)  # filename, success, message
    conversion_completed = Signal(int, int)  # successful_count, failed_count
    log_message = Signal(str)
    
    def __init__(self, files, export_path, options):
        super().__init__()
        self.files = files
        self.export_path = export_path
        self.options = options
        self.converter = TableauToPowerBIConverter()
        
    def run(self):
        """Main conversion process"""
        successful = 0
        failed = 0
        total_files = len(self.files)
        
        self.log_message.emit(f"Starting batch conversion of {total_files} files...")
        
        # Check if pbi-tools is available
        if not PBIToolsCompiler.is_pbi_tools_available():
            self.log_message.emit("WARNING: pbi-tools not found. .pbit files will not be generated.")
            self.log_message.emit("Project files will still be created for manual compilation.")
        
        for i, file_path in enumerate(self.files):
            try:
                file_name = Path(file_path).name
                self.log_message.emit(f"Processing: {file_name}")
                
                # Generate output paths
                output_name = Path(file_path).stem
                pbit_output = os.path.join(self.export_path, f"{output_name}.pbit")
                project_output = os.path.join(self.export_path, f"{output_name}_project")
                
                # Perform conversion
                success = self.converter.convert(
                    twbx_path=file_path,
                    output_path=pbit_output,
                    project_dir=project_output,
                    cleanup_temp=not self.options.get('preserve_temp', False)
                )
                
                if success:
                    successful += 1
                    self.file_processed.emit(file_name, True, "Conversion completed successfully")
                    self.log_message.emit(f"✅ Successfully converted: {file_name}")
                else:
                    failed += 1
                    self.file_processed.emit(file_name, False, "Conversion failed - check logs")
                    self.log_message.emit(f"❌ Failed to convert: {file_name}")
                
            except Exception as e:
                failed += 1
                error_msg = f"Error: {str(e)}"
                self.file_processed.emit(Path(file_path).name, False, error_msg)
                self.log_message.emit(f"❌ Error processing {Path(file_path).name}: {error_msg}")
            
            # Update progress
            progress = int(((i + 1) / total_files) * 100)
            self.progress_updated.emit(progress)
        
        self.conversion_completed.emit(successful, failed)
        self.log_message.emit(f"Batch conversion completed: {successful} successful, {failed} failed")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())