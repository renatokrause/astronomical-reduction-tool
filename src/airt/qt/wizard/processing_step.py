from __future__ import annotations

import os
import subprocess
import sys
from contextlib import suppress
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QProgressBar, QScrollArea, QVBoxLayout, QWidget

from airt.core.final_render import build_final_image, output_folder_for_project, save_final_outputs
from airt.project import autosave_project


class ProcessingStep(QWidget):
    def __init__(self, wizard):
        super().__init__()

        self.wizard = wizard
        self.generated_files: list[Path] = []
        self.processing = False
        self.finished = False

        self.setObjectName("processingPage")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setObjectName("pageScroll")

        content = QWidget()
        self.scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(48, 42, 48, 42)
        root.setSpacing(22)

        self.progress_card = QFrame()
        self.progress_card.setObjectName("processingCard")

        progress_layout = QVBoxLayout(self.progress_card)
        progress_layout.setContentsMargins(34, 28, 34, 30)
        progress_layout.setSpacing(18)

        title = QLabel("Process & Save")
        title.setObjectName("pageTitle")

        self.status_label = QLabel("Processing will start automatically.")
        self.status_label.setObjectName("pageSubtitle")
        self.status_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        progress_layout.addWidget(title)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)

        root.addStretch(1)
        root.addWidget(self.progress_card)
        root.addStretch(2)

        outer.addWidget(self.scroll)

    def on_enter(self):
        self.finished = False
        self.generated_files = []
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing will start automatically.")
        self.progress_card.setProperty("processing", True)
        self.refresh_processing_style()

        self.wizard.footer.back_button.setEnabled(False)

        if hasattr(self.wizard.footer, "cancel_button"):
            self.wizard.footer.cancel_button.setVisible(False)

        self.wizard.footer.next_button.setText("Finish")
        self.wizard.footer.next_button.setEnabled(False)
        self.wizard.footer.set_status("Processing final outputs.")

        QTimer.singleShot(250, self.start_processing)

    def on_leave(self, target_index: int):
        if hasattr(self.wizard.footer, "cancel_button"):
            self.wizard.footer.cancel_button.setVisible(True)

        self.wizard.footer.next_button.setText("Next")

    def refresh_processing_style(self):
        for widget in [self.progress_card]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def report_progress(self, value: int, message: str):
        clean_message = " ".join(str(message).splitlines())
        self.progress_bar.setValue(int(value))
        self.status_label.setText(clean_message)
        QApplication.processEvents()

    def start_processing(self):
        if self.processing:
            return

        project = self.wizard.project

        if not project:
            self.fail_processing("No project is loaded.")
            return

        export = project.output_options.get("final_export", {}) or {}
        formats = export.get("formats", {}) or {}

        if not any(formats.values()):
            self.fail_processing("No output format selected.")
            return

        self.processing = True
        self.finished = False
        self.generated_files = []

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            self.report_progress(5, "Starting final processing.")
            self.wizard.footer.set_status("Processing final image.")

            result = build_final_image(project, progress_callback=self.report_progress)

            self.report_progress(85, "Saving selected output formats.")
            self.generated_files = save_final_outputs(project, result, export)

            self.report_progress(100, "Done. Final files generated.")

            self.finished = True
            self.progress_card.setProperty("processing", False)
            self.refresh_processing_style()

            self.wizard.footer.next_button.setEnabled(True)
            self.wizard.footer.back_button.setEnabled(True)
            self.wizard.footer.set_status("Processing finished. Click Finish to close.")

            if export.get("open_output_folder", False):
                self.open_output_folder()

        except Exception as exc:
            self.fail_processing(str(exc))
        finally:
            while QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()

            self.processing = False

    def fail_processing(self, message: str):
        clean_message = " ".join(str(message).splitlines())
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Processing failed: {clean_message}")
        self.finished = False
        self.progress_card.setProperty("processing", False)
        self.refresh_processing_style()

        self.wizard.footer.back_button.setEnabled(True)
        self.wizard.footer.next_button.setEnabled(False)
        self.wizard.footer.set_status(f"Processing failed: {clean_message}")

    def open_output_folder(self):
        project = self.wizard.project

        if not project:
            return

        folder = output_folder_for_project(project)
        folder.mkdir(parents=True, exist_ok=True)

        with suppress(Exception):
            if sys.platform.startswith("win"):
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])

    def on_next(self) -> bool:
        if not self.finished:
            return False

        project = self.wizard.project

        if project and project.project_file:
            with suppress(Exception):
                autosave_project(project)

        self.wizard.close()
        return False
