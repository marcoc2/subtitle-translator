import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QFileDialog, QProgressBar, QLabel,
    QMenuBar, QMenu, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

# Define um Worker Thread para rodar o pipeline para manter a GUI responsiva
class Worker(QThread):
    finished_video = pyqtSignal(str, str) # video_file (basename), status ("success" or "error")
    progress = pyqtSignal(int)            # Overall progress percentage
    log_output = pyqtSignal(str)          # To send incremental output from the pipeline
    all_tasks_finished = pyqtSignal()     # Emitted when all videos are processed

    def __init__(self, video_files, target_language, api_key, pipeline_script_path, parent=None):
        super().__init__(parent)
        self.video_files = video_files
        self.target_language = target_language
        self.api_key = api_key
        self.pipeline_script_path = pipeline_script_path

    def run(self):
        total_videos = len(self.video_files)
        pipeline_script_dir = os.path.dirname(self.pipeline_script_path)

        for i, video_file_path in enumerate(self.video_files):
            video_basename = os.path.basename(video_file_path)
            self.log_output.emit(f"\n=== Iniciando processamento para: {video_basename} ===\n")
            
            command = [
                "python",
                self.pipeline_script_path,
                os.path.abspath(video_file_path), # Pass absolute path to pipeline
                "--lang", self.target_language
            ]
            if self.api_key:
                command.extend(["--api-key", self.api_key])

            process_successful = False
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, # Merge stderr into stdout
                    text=True,
                    cwd=pipeline_script_dir, # Run pipeline from its directory
                    bufsize=1, # Line-buffered output
                    universal_newlines=True
                )

                for line in process.stdout:
                    self.log_output.emit(line.strip())

                process.wait()
                return_code = process.returncode

                if return_code == 0:
                    self.log_output.emit(f"\n--- Processamento concluído para {video_basename} ---\n")
                    process_successful = True
                else:
                    self.log_output.emit(f"\n--- Processamento falhou para {video_basename} com código de saída {return_code} ---\n")
                    
            except FileNotFoundError:
                self.log_output.emit(f"Erro: Comando Python ou script da pipeline não encontrado. Verifique sua instalação ou PATH.")
            except Exception as e:
                self.log_output.emit(f"Erro inesperado durante o processamento de {video_basename}: {e}")
            
            finally:
                if process_successful:
                    self.finished_video.emit(video_basename, "success")
                else:
                    self.finished_video.emit(video_basename, "error")

                # Update overall progress
                progress_value = int(((i + 1) / total_videos) * 100)
                self.progress.emit(progress_value)
        
        self.all_tasks_finished.emit() # Signal that all videos are done


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini SRT Translator GUI")
        self.setGeometry(100, 100, 800, 700)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Enable drag and drop for the main window (and list widget)
        self.setAcceptDrops(True)

        # Menu Bar
        self._create_menu_bar()

        # Input for Gemini API Key
        hbox_api = QHBoxLayout()
        hbox_api.addWidget(QLabel("Gemini API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Deixe em branco para usar a variável de ambiente GEMINI_API_KEY (recomendado)")
        hbox_api.addWidget(self.api_key_input)
        self.layout.addLayout(hbox_api)

        # Language Input
        hbox_lang = QHBoxLayout()
        hbox_lang.addWidget(QLabel("Idioma de Destino:"))
        self.lang_input = QLineEdit()
        self.lang_input.setText("Brazilian Portuguese") # Default language
        hbox_lang.addWidget(self.lang_input)
        self.layout.addLayout(hbox_lang)

        # Video List
        self.video_list_widget = QListWidget()
        self.video_list_widget.setDragDropMode(QListWidget.DragDropMode.DropOnly) # Makes the list widget itself a drop target
        self.video_list_widget.setAcceptDrops(True) # Ensure it accepts drops
        self.layout.addWidget(QLabel("Vídeos a Processar (Arraste e Solte ou Adicione via Arquivo -> Abrir): "))
        self.layout.addWidget(self.video_list_widget)

        # Translate Button
        self.translate_button = QPushButton("Traduzir Vídeos")
        self.translate_button.clicked.connect(self._start_translation)
        self.layout.addWidget(self.translate_button)

        # Log Output Area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFontPointSize(9) # Smaller font for logs
        self.layout.addWidget(QLabel("Logs dos Processamento:"))
        self.layout.addWidget(self.log_output)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.worker = None # Initialize worker thread

        # Get the path to full_translation_pipeline.py (in the scripts directory)
        self.pipeline_script_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "scripts",
            "full_translation_pipeline.py"
        )
        if not os.path.exists(self.pipeline_script_path):
            QMessageBox.critical(self, "Erro Crítico", f"Script da pipeline 'full_translation_pipeline.py' não encontrado em: {self.pipeline_script_path}")
            sys.exit(1)

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Arquivo")

        open_action = file_menu.addAction("Abrir Vídeo(s)...")
        open_action.triggered.connect(self._open_files)

        exit_action = file_menu.addAction("Sair")
        exit_action.triggered.connect(self.close)

    def _open_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Vídeos (*.mkv *.mp4 *.avi);;Todos os arquivos (*)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self._add_video_to_list(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Main window drag enter event to accept file URLs
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Main window drop event to process dropped files
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self._add_video_to_list(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _add_video_to_list(self, file_path):
        # Add video file to the list widget if not already present
        # Ensure the file exists and is a file
        if not os.path.isfile(file_path):
            self.log_output.append(f"Aviso: '{file_path}' não é um arquivo válido.")
            return

        # Check if already in list to prevent duplicates
        for i in range(self.video_list_widget.count()):
            if self.video_list_widget.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                return # Already in list

        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path) # Store full path in UserRole for processing
        self.video_list_widget.addItem(item)
        self.log_output.append(f"Adicionado vídeo: {os.path.basename(file_path)}")


    def _start_translation(self):
        video_files_to_process = []
        for i in range(self.video_list_widget.count()):
            item = self.video_list_widget.item(i)
            video_files_to_process.append(item.data(Qt.ItemDataRole.UserRole))

        if not video_files_to_process:
            QMessageBox.warning(self, "Atenção", "Por favor, adicione vídeos à lista para processar.")
            return

        target_lang = self.lang_input.text().strip()
        if not target_lang:
            QMessageBox.warning(self, "Atenção", "Por favor, insira o Idioma de Destino.")
            return

        api_key = self.api_key_input.text().strip()
        # If API key input is empty, rely on environment variable. If that's also not set, pipeline will likely fail.
        # The pipeline itself will handle the case where no API key is found/valid.
        if not api_key and "GEMINI_API_KEY" not in os.environ:
            QMessageBox.critical(self, "Erro de API Key", "Nenhuma Gemini API Key fornecida e a variável de ambiente GEMINI_API_KEY não está definida. " +
                                                             "Por favor, insira sua chave ou defina a variável de ambiente.")
            return
        # If api_key is empty here, we pass None so the pipeline relies on the env var.
        api_key_for_worker = api_key if api_key else None

        # Disable controls during processing
        self.translate_button.setEnabled(False)
        self.lang_input.setEnabled(False)
        self.api_key_input.setEnabled(False)
        self.video_list_widget.setEnabled(False)
        self.menuBar().setEnabled(False)

        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.log_output.append("Iniciando pipeline de tradução para vídeos selecionados...")

        self.worker = Worker(video_files_to_process, target_lang, api_key_for_worker, self.pipeline_script_path)
        self.worker.finished_video.connect(self._on_video_processed) # Called for each video
        self.worker.progress.connect(self.progress_bar.setValue) # Updates overall progress bar
        self.worker.log_output.connect(self._append_to_log) # Updates log area in real-time
        self.worker.all_tasks_finished.connect(self._on_all_translations_finished) # Called once all videos are done
        self.worker.start()

    def _on_video_processed(self, video_basename: str, status: str):
        # For now, just append to log. The UI for specific video items can be enhanced later if needed.
        if status == "success":
            self.log_output.append(f"Status: \'{video_basename}\' processado com SUCESSO.")
        else:
            self.log_output.append(f"Status: \'{video_basename}\' falhou durante o processamento.")
        QApplication.processEvents() # Ensure GUI updates are processed

    def _on_all_translations_finished(self):
        # Re-enable controls when all tasks are complete
        self.translate_button.setEnabled(True)
        self.lang_input.setEnabled(True)
        self.api_key_input.setEnabled(True)
        self.video_list_widget.setEnabled(True)
        self.menuBar().setEnabled(True)
        self.log_output.append("\n=== Processamento de tradução de legenda concluído para todos os vídeos ===\n")
        self.worker = None # Clear worker reference

    def _append_to_log(self, text):
        self.log_output.append(text)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum()) # Scroll to bottom
        QApplication.processEvents() # Ensure GUI updates are processed


if __name__ == "__main__":
    # Ensure PyQt6 is installed: pip install PyQt6
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
