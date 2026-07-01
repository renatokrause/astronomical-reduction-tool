from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QScrollArea,
)


PRESETS = {
    "auto": "Auto",
    "compact_galaxy": "Compact galaxy",
    "extended_galaxy": "Extended galaxy",
    "nebula": "Nebula",
    "star_field": "Star field / cluster",
    "manual_advanced": "Manual advanced",
}


class PresetStep(QWidget):
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

        title = QLabel("Object preset and band mapping")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Choose the processing strategy and define how detected bands should be mapped to RGB output channels."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        root.addWidget(title)
        root.addWidget(subtitle)

        preset_card = QFrame()
        preset_card.setObjectName("contentCard")
        preset_layout = QGridLayout(preset_card)
        preset_layout.setContentsMargins(28, 24, 28, 28)
        preset_layout.setHorizontalSpacing(16)
        preset_layout.setVerticalSpacing(16)
        preset_layout.setColumnMinimumWidth(0, 160)
        preset_layout.setColumnStretch(1, 1)

        section = QLabel("Processing preset")
        section.setObjectName("sectionTitle")
        preset_layout.addWidget(section, 0, 0, 1, 2)

        preset_label = QLabel("Object type")
        preset_label.setObjectName("fieldLabel")

        self.preset_combo = QComboBox()
        for key, label in PRESETS.items():
            self.preset_combo.addItem(label, key)

        preset_layout.addWidget(preset_label, 1, 0)
        preset_layout.addWidget(self.preset_combo, 1, 1)

        self.preset_description = QLabel("")
        self.preset_description.setObjectName("mutedText")
        self.preset_description.setWordWrap(True)
        preset_layout.addWidget(self.preset_description, 2, 0, 1, 2)

        root.addWidget(preset_card)

        mapping_card = QFrame()
        mapping_card.setObjectName("contentCard")
        mapping_layout = QGridLayout(mapping_card)
        mapping_layout.setContentsMargins(28, 24, 28, 28)
        mapping_layout.setHorizontalSpacing(16)
        mapping_layout.setVerticalSpacing(16)
        mapping_layout.setColumnMinimumWidth(0, 160)
        mapping_layout.setColumnStretch(1, 1)

        mapping_title = QLabel("Band to color mapping")
        mapping_title.setObjectName("sectionTitle")
        mapping_layout.addWidget(mapping_title, 0, 0, 1, 2)

        self.red_combo = self._make_band_combo()
        self.green_combo = self._make_band_combo()
        self.blue_combo = self._make_band_combo()
        self.luminance_combo = self._make_band_combo(include_none=True)

        self._add_mapping_row(mapping_layout, 1, "Red channel", self.red_combo)
        self._add_mapping_row(mapping_layout, 2, "Green channel", self.green_combo)
        self._add_mapping_row(mapping_layout, 3, "Blue channel", self.blue_combo)
        self._add_mapping_row(mapping_layout, 4, "Luminance", self.luminance_combo)

        root.addWidget(mapping_card)

        info = QFrame()
        info.setObjectName("infoCard")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(20, 14, 20, 14)

        info_text = QLabel(
            "All detected bands are preserved. RGB mapping only defines how the final color image will be composed."
        )
        info_text.setObjectName("infoText")
        info_text.setWordWrap(True)

        info_layout.addWidget(info_text)
        root.addWidget(info)
        root.addStretch(1)

        outer.addWidget(scroll)

        self.preset_combo.currentIndexChanged.connect(self.update_preset_description)

    def _make_band_combo(self, include_none: bool = False) -> QComboBox:
        combo = QComboBox()
        if include_none:
            combo.addItem("None", "")
        return combo

    def _add_mapping_row(self, layout: QGridLayout, row: int, label_text: str, combo: QComboBox):
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label, row, 0)
        layout.addWidget(combo, row, 1)

    def on_enter(self):
        self.wizard.footer.back_button.setEnabled(True)
        self.wizard.footer.next_button.setEnabled(True)
        self.wizard.footer.set_status("Choose preset and band mapping.")

        self.load_bands()
        self.load_from_project()
        self.update_preset_description()

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

    def load_bands(self):
        bands = self.detected_bands()

        for combo in [self.red_combo, self.green_combo, self.blue_combo]:
            combo.clear()
            for band in bands:
                combo.addItem(band, band)

        self.luminance_combo.clear()
        self.luminance_combo.addItem("None", "")
        for band in bands:
            self.luminance_combo.addItem(band, band)

        self.apply_default_mapping(bands)

    def set_combo_value(self, combo: QComboBox, value: str):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def apply_default_mapping(self, bands: list[str]):
        upper = {band.upper(): band for band in bands}

        self.set_combo_value(self.red_combo, upper.get("R", bands[0] if bands else ""))
        self.set_combo_value(self.green_combo, upper.get("V", upper.get("G", bands[1] if len(bands) > 1 else (bands[0] if bands else ""))))
        self.set_combo_value(self.blue_combo, upper.get("B", bands[2] if len(bands) > 2 else (bands[-1] if bands else "")))

        if "L" in upper:
            self.set_combo_value(self.luminance_combo, upper["L"])

    def load_from_project(self):
        project = self.wizard.project
        if not project:
            return

        preset = getattr(project, "preset", "auto") or "auto"
        index = self.preset_combo.findData(preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)

        mapping = project.output_options.get("band_mapping", {}) if project.output_options else {}

        if mapping:
            self.set_combo_value(self.red_combo, mapping.get("red", ""))
            self.set_combo_value(self.green_combo, mapping.get("green", ""))
            self.set_combo_value(self.blue_combo, mapping.get("blue", ""))
            self.set_combo_value(self.luminance_combo, mapping.get("luminance", ""))

    def update_preset_description(self):
        key = self.preset_combo.currentData()

        descriptions = {
            "auto": "The application will suggest a strategy based on detected bands and object structure.",
            "compact_galaxy": "Best for targets like M104: compact central object and strong surrounding background.",
            "extended_galaxy": "Best for targets like M83, M101 or M33: large diffuse arms that need stronger protection.",
            "nebula": "Conservative background correction to preserve diffuse nebulosity.",
            "star_field": "For clusters and star fields where the background can be modeled more aggressively.",
            "manual_advanced": "Expose advanced parameters in later steps.",
        }

        self.preset_description.setText(descriptions.get(key, ""))

    def save_to_project(self):
        project = self.wizard.ensure_project()
        project.preset = self.preset_combo.currentData() or "auto"

        project.output_options.setdefault("band_mapping", {})
        project.output_options["band_mapping"] = {
            "red": self.red_combo.currentData() or "",
            "green": self.green_combo.currentData() or "",
            "blue": self.blue_combo.currentData() or "",
            "luminance": self.luminance_combo.currentData() or "",
        }

        project.update_timestamp()

    def on_next(self) -> bool:
        self.save_to_project()
        self.wizard.footer.set_status("Preset and band mapping saved.")
        self.wizard.go_to_step(5)
        return False

