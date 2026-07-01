from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
)


class AlignmentStep(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("pageScroll")

        content = QWidget()
        scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(48, 42, 48, 42)
        root.setSpacing(22)

        title = QLabel("Alignment")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Choose how bands should be aligned. Manual offsets are available for cases where automatic alignment fails."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        root.addWidget(title)
        root.addWidget(subtitle)

        mode_card = QFrame()
        mode_card.setObjectName("contentCard")
        mode_layout = QGridLayout(mode_card)
        mode_layout.setContentsMargins(28, 24, 28, 28)
        mode_layout.setHorizontalSpacing(16)
        mode_layout.setVerticalSpacing(16)
        mode_layout.setColumnMinimumWidth(0, 160)
        mode_layout.setColumnStretch(1, 1)

        mode_title = QLabel("Alignment mode")
        mode_title.setObjectName("sectionTitle")
        mode_layout.addWidget(mode_title, 0, 0, 1, 2)

        label = QLabel("Mode")
        label.setObjectName("fieldLabel")

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Automatic alignment", "automatic")
        self.mode_combo.addItem("Manual adjustment", "manual")
        self.mode_combo.addItem("Skip alignment", "skip")
        self.mode_combo.currentIndexChanged.connect(self.update_manual_enabled)

        mode_layout.addWidget(label, 1, 0)
        mode_layout.addWidget(self.mode_combo, 1, 1)

        root.addWidget(mode_card)

        offsets_card = QFrame()
        offsets_card.setObjectName("contentCard")
        offsets_layout = QVBoxLayout(offsets_card)
        offsets_layout.setContentsMargins(28, 24, 28, 28)
        offsets_layout.setSpacing(12)

        offsets_title = QLabel("Manual offsets")
        offsets_title.setObjectName("sectionTitle")

        self.offset_table = QTableWidget(0, 3)
        self.offset_table.setHorizontalHeaderLabels(["Band", "X offset", "Y offset"])
        self.offset_table.verticalHeader().setVisible(False)
        self.offset_table.setMinimumHeight(260)
        self.offset_table.horizontalHeader().setStretchLastSection(True)

        offsets_layout.addWidget(offsets_title)
        offsets_layout.addWidget(self.offset_table)

        root.addWidget(offsets_card)

        info = QFrame()
        info.setObjectName("infoCard")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(20, 14, 20, 14)

        self.info_label = QLabel(
            "Automatic alignment is recommended. Manual offsets will be improved later with a visual preview."
        )
        self.info_label.setObjectName("infoText")
        self.info_label.setWordWrap(True)

        info_layout.addWidget(self.info_label)
        root.addWidget(info)
        root.addStretch(1)

        outer.addWidget(scroll)

    def on_enter(self):
        self.wizard.footer.back_button.setEnabled(True)
        self.wizard.footer.next_button.setEnabled(True)
        self.wizard.footer.set_status("Choose alignment mode.")

        self.load_from_project()
        self.populate_offsets()
        self.update_manual_enabled()

    def detected_bands(self) -> list[str]:
        result = getattr(self.wizard, "scan_result", None)
        if not result:
            return []

        return sorted(
            {
                item.band
                for item in result.files
                if item.kind == "object" and item.band != "-"
            }
        )

    def load_from_project(self):
        project = self.wizard.project
        if not project:
            return

        mode = getattr(project, "alignment_mode", "automatic") or "automatic"
        index = self.mode_combo.findData(mode)
        if index >= 0:
            self.mode_combo.setCurrentIndex(index)

    def populate_offsets(self):
        bands = self.detected_bands()
        project = self.wizard.project
        offsets = project.manual_offsets if project else {}

        self.offset_table.setRowCount(len(bands))

        for row, band in enumerate(bands):
            band_item = QTableWidgetItem(band)
            band_item.setTextAlignment(Qt.AlignCenter)
            self.offset_table.setItem(row, 0, band_item)

            x_spin = QDoubleSpinBox()
            x_spin.setRange(-9999, 9999)
            x_spin.setDecimals(2)
            x_spin.setSingleStep(0.5)
            x_spin.setValue(float(offsets.get(band, {}).get("x", 0.0)))

            y_spin = QDoubleSpinBox()
            y_spin.setRange(-9999, 9999)
            y_spin.setDecimals(2)
            y_spin.setSingleStep(0.5)
            y_spin.setValue(float(offsets.get(band, {}).get("y", 0.0)))

            self.offset_table.setCellWidget(row, 1, x_spin)
            self.offset_table.setCellWidget(row, 2, y_spin)
            self.offset_table.setRowHeight(row, 42)

        self.offset_table.resizeColumnsToContents()

    def update_manual_enabled(self):
        manual = self.mode_combo.currentData() == "manual"
        self.offset_table.setEnabled(manual)

        if manual:
            self.info_label.setText("Manual mode: enter X/Y offsets per band. Visual manual alignment will be added in a later refinement.")
        else:
            self.info_label.setText("Automatic alignment is recommended. Manual offset fields are disabled unless Manual adjustment is selected.")

    def save_to_project(self):
        project = self.wizard.ensure_project()
        project.alignment_mode = self.mode_combo.currentData() or "automatic"
        project.manual_offsets = {}

        for row in range(self.offset_table.rowCount()):
            band_item = self.offset_table.item(row, 0)
            if not band_item:
                continue

            band = band_item.text()
            x_spin = self.offset_table.cellWidget(row, 1)
            y_spin = self.offset_table.cellWidget(row, 2)

            project.manual_offsets[band] = {
                "x": float(x_spin.value()) if x_spin else 0.0,
                "y": float(y_spin.value()) if y_spin else 0.0,
            }

        project.update_timestamp()

    def on_next(self) -> bool:
        self.save_to_project()
        self.wizard.footer.set_status("Alignment settings saved.")
        self.wizard.go_to_step(6)
        return False

