from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class BandColorMapping:
    band: str
    normalized_band: str
    color_name: str
    hex_color: str
    channel: str


UNKNOWN_COLOR = BandColorMapping(
    band="",
    normalized_band="Unknown",
    color_name="Medium gray",
    hex_color="#808080",
    channel="-",
)


PHOTOMETRIC_COLORS = {
    "U": ("Violet", "#7B2CBF", "B"),
    "B": ("Blue", "#1E5BFF", "B"),
    "V": ("Green", "#2EAD4A", "G"),
    "G": ("Green-cyan", "#00A88F", "G"),
    "R": ("Red", "#E53935", "R"),
    "I": ("Dark red", "#8B1E1E", "R"),
    "z": ("Dark wine", "#4A2C2A", "R"),
    "Y": ("Dark brown", "#5A3A22", "R"),
    "J": ("Dark orange", "#A05A1F", "R"),
    "H": ("Brown", "#6B3F1D", "R"),
    "Ks": ("Very dark gray", "#303030", "-"),
    "Luminance": ("White", "#FFFFFF", "L"),
    "Clear": ("Light gray", "#D0D0D0", "L"),
    "Unknown": ("Medium gray", "#808080", "-"),
}


SMART_DEFAULT_COLORS = {
    "Luminance": ("White", "#FFFFFF", "L"),
    "Clear": ("Light gray", "#D0D0D0", "L"),
    "U": ("Violet", "#7B2CBF", "B"),
    "B": ("Blue", "#1E5BFF", "B"),
    "V": ("Green", "#2EAD4A", "G"),
    "G": ("Green-cyan", "#00A88F", "G"),
    "R": ("Red", "#E53935", "R"),
    "I": ("Dark red", "#8B1E1E", "R"),
    "z": ("Dark wine", "#4A2C2A", "R"),
    "Y": ("Dark brown", "#5A3A22", "R"),
    "J": ("Dark orange", "#A05A1F", "R"),
    "H": ("Brown", "#6B3F1D", "R"),
    "Ks": ("Very dark gray", "#303030", "-"),
    "Hα": ("Red", "#D92525", "R"),
    "Hβ": ("Light blue", "#3FA7FF", "B"),
    "O III": ("Blue-cyan", "#00B7FF", "G+B"),
    "S II": ("Deep red", "#8B0000", "R"),
    "N II": ("Red", "#C62828", "R"),
    "IR": ("Dark brown", "#5A2D0C", "R"),
    "CH4": ("Dark purple", "#4A148C", "B"),
    "Unknown": ("Medium gray", "#808080", "-"),
}


SHO_COLORS = {
    "S II": ("Red", "#8B0000", "R"),
    "Hα": ("Green", "#2EAD4A", "G"),
    "O III": ("Blue", "#00B7FF", "B"),
}


HOO_COLORS = {
    "Hα": ("Red", "#D92525", "R"),
    "O III": ("Cyan", "#00B7FF", "G+B"),
}


WAVELENGTH_ORDER = {
    "U": 365,
    "B": 445,
    "Hβ": 486,
    "V": 551,
    "G": 520,
    "O III": 501,
    "R": 658,
    "Hα": 656,
    "N II": 658,
    "S II": 672,
    "I": 806,
    "z": 900,
    "Y": 1020,
    "J": 1220,
    "H": 1630,
    "Ks": 2190,
    "IR": 2500,
    "CH4": 889,
    "Luminance": 550,
    "Clear": 550,
}


CHROMATIC_PALETTE = [
    ("Blue", "#1E5BFF", "B"),
    ("Cyan", "#00B7FF", "B"),
    ("Green", "#2EAD4A", "G"),
    ("Dark orange", "#A05A1F", "R"),
    ("Red", "#E53935", "R"),
]


def normalize_band_name(raw: str | None) -> str:
    if raw is None:
        return "Unknown"

    text = str(raw).strip()

    if not text or text == "-":
        return "Unknown"

    compact = text.strip()
    upper = compact.upper()

    upper = upper.replace("FILTER_", "")
    upper = upper.replace("FILT_", "")
    upper = upper.replace("BAND_", "")
    upper = upper.replace(" ", "")
    upper = upper.replace("_", "")
    upper = upper.replace("-", "")
    upper = upper.replace("'", "")
    upper = upper.replace('"', "")

    if upper in {"HA", "HALPHA", "HΑ", "HΑLPHA"}:
        return "Hα"

    if upper in {"HB", "HBETA", "HΒ", "HΒETA"}:
        return "Hβ"

    if upper in {"OIII", "O3"}:
        return "O III"

    if upper in {"SII", "S2"}:
        return "S II"

    if upper in {"SIII", "S3"}:
        return "S III"

    if upper in {"NII", "N2"}:
        return "N II"

    if upper in {"L", "LUM", "LUMINANCE"}:
        return "Luminance"

    if upper in {"C", "CLEAR"}:
        return "Clear"

    if upper in {"R", "RED"}:
        return "R"

    if upper in {"G", "GREEN"}:
        return "G"

    if upper in {"B", "BLUE"}:
        return "B"

    if upper in {"U"}:
        return "U"

    if upper in {"V"}:
        return "V"

    if upper in {"I"}:
        return "I"

    if upper in {"Z"}:
        return "z"

    if upper in {"Y"}:
        return "Y"

    if upper in {"J"}:
        return "J"

    if upper in {"H"}:
        return "H"

    if upper in {"K", "KS", "KSHORT"}:
        return "Ks"

    if upper in {"IR", "INFRARED"}:
        return "IR"

    if upper in {"CH4", "METHANE"}:
        return "CH4"

    return compact


def _mapping_from_dict(band: str, table: dict[str, tuple[str, str, str]]) -> BandColorMapping:
    normalized = normalize_band_name(band)
    color_name, hex_color, channel = table.get(
        normalized,
        table.get("Unknown", ("Medium gray", "#808080", "-")),
    )

    return BandColorMapping(
        band=band,
        normalized_band=normalized,
        color_name=color_name,
        hex_color=hex_color,
        channel=channel,
    )


def photometric_mapping(bands: list[str]) -> list[BandColorMapping]:
    return [_mapping_from_dict(band, PHOTOMETRIC_COLORS) for band in bands]


def smart_default_mapping(bands: list[str]) -> list[BandColorMapping]:
    return [_mapping_from_dict(band, SMART_DEFAULT_COLORS) for band in bands]


def sho_mapping(bands: list[str]) -> list[BandColorMapping]:
    result = []

    for band in bands:
        normalized = normalize_band_name(band)

        if normalized in SHO_COLORS:
            color_name, hex_color, channel = SHO_COLORS[normalized]
        else:
            color_name, hex_color, channel = SMART_DEFAULT_COLORS.get(
                normalized,
                SMART_DEFAULT_COLORS["Unknown"],
            )

        result.append(
            BandColorMapping(
                band=band,
                normalized_band=normalized,
                color_name=color_name,
                hex_color=hex_color,
                channel=channel,
            )
        )

    return result


def hoo_mapping(bands: list[str]) -> list[BandColorMapping]:
    result = []

    for band in bands:
        normalized = normalize_band_name(band)

        if normalized in HOO_COLORS:
            color_name, hex_color, channel = HOO_COLORS[normalized]
        else:
            color_name, hex_color, channel = SMART_DEFAULT_COLORS.get(
                normalized,
                SMART_DEFAULT_COLORS["Unknown"],
            )

        result.append(
            BandColorMapping(
                band=band,
                normalized_band=normalized,
                color_name=color_name,
                hex_color=hex_color,
                channel=channel,
            )
        )

    return result


def chromatic_order_mapping(bands: list[str]) -> list[BandColorMapping]:
    normalized_pairs = [(band, normalize_band_name(band)) for band in bands]

    def wavelength(pair):
        return WAVELENGTH_ORDER.get(pair[1], 10_000)

    ordered = sorted(normalized_pairs, key=wavelength)

    if not ordered:
        return []

    if len(ordered) == 1:
        band, normalized = ordered[0]
        color_name, hex_color, channel = CHROMATIC_PALETTE[2]
        return [
            BandColorMapping(
                band=band,
                normalized_band=normalized,
                color_name=color_name,
                hex_color=hex_color,
                channel=channel,
            )
        ]

    result_by_band: dict[str, BandColorMapping] = {}

    for index, (band, normalized) in enumerate(ordered):
        palette_index = round(index * (len(CHROMATIC_PALETTE) - 1) / (len(ordered) - 1))
        color_name, hex_color, channel = CHROMATIC_PALETTE[palette_index]

        result_by_band[band] = BandColorMapping(
            band=band,
            normalized_band=normalized,
            color_name=color_name,
            hex_color=hex_color,
            channel=channel,
        )

    return [result_by_band[band] for band in bands]


def custom_mapping(
    bands: list[str],
    saved_custom: dict[str, dict[str, str]] | None = None,
) -> list[BandColorMapping]:
    saved_custom = saved_custom or {}
    defaults = {item.band: item for item in smart_default_mapping(bands)}

    result = []

    for band in bands:
        default = defaults[band]
        saved = saved_custom.get(band, {})

        result.append(
            BandColorMapping(
                band=band,
                normalized_band=saved.get("normalized_band", default.normalized_band),
                color_name=saved.get("color_name", default.color_name),
                hex_color=saved.get("hex_color", default.hex_color),
                channel=saved.get("channel", default.channel),
            )
        )

    return result


def build_color_mapping(
    bands: list[str],
    mode: str,
    saved_custom: dict[str, dict[str, str]] | None = None,
) -> list[BandColorMapping]:
    mode = mode or "photometric"

    if mode == "photometric":
        return photometric_mapping(bands)

    if mode == "chromatic_order":
        return chromatic_order_mapping(bands)

    if mode == "sho":
        return sho_mapping(bands)

    if mode == "hoo":
        return hoo_mapping(bands)

    if mode == "custom":
        return custom_mapping(bands, saved_custom)

    return photometric_mapping(bands)


def mapping_to_project_dict(mapping: list[BandColorMapping]) -> dict[str, dict[str, str]]:
    return {
        item.band: {
            "band": item.band,
            "normalized_band": item.normalized_band,
            "color_name": item.color_name,
            "hex_color": item.hex_color,
            "channel": item.channel,
        }
        for item in mapping
    }


def is_valid_hex_color(value: str) -> bool:
    return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", value.strip()))
