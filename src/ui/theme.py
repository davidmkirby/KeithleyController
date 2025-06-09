#!/usr/bin/env python3
# theme.py - Application theme and styling
"""
Provides consistent styling for the Keithley Dual Controller application
Implements a modern dark theme with high contrast and visual clarity
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt

# Color palette
COLORS = {
    # Dark theme base colors
    "background": "#2E2E2E",
    "background_light": "#3A3A3A",
    "background_lighter": "#444444",
    "text": "#FFFFFF",
    "text_secondary": "#CCCCCC",
    "border": "#555555",

    # Status colors
    "success": "#4CAF50",
    "success_light": "#81C784",
    "error": "#F44336",
    "error_light": "#E57373",
    "warning": "#FF9800",
    "warning_light": "#FFB74D",
    "info": "#2196F3",
    "info_light": "#64B5F6",

    # Accent colors
    "accent_blue": "#2196F3",
    "accent_purple": "#9C27B0",
    "accent_teal": "#009688",
    "accent_amber": "#FFC107",

    # Measurement displays
    "voltage_display": "#64B5F6",  # Light blue
    "current_display": "#81C784",  # Light green
}

# Font settings
FONTS = {
    "default": {
        "family": "Arial",
        "size": 10,
        "weight": QFont.Weight.Normal
    },
    "monospace": {
        "family": "Menlo",
        "fallbacks": ["Monaco", "Courier New", "Consolas", "monospace"],
        "size": 9,
        "weight": QFont.Weight.Normal
    },
    "heading": {
        "family": "Arial",
        "size": 12,
        "weight": QFont.Weight.Bold
    },
    "reading": {
        "family": "Arial",
        "size": 14,
        "weight": QFont.Weight.Bold
    },
    "button": {
        "family": "Arial",
        "size": 10,
        "weight": QFont.Weight.Medium
    },
}

# Component styles
STYLES = {
    "window": f"""
        QMainWindow {{
            background-color: {COLORS["background"]};
            color: {COLORS["text"]};
        }}
    """,

    "tab_widget": f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS["border"]};
            background-color: {COLORS["background"]};
        }}

        QTabBar::tab {{
            background-color: {COLORS["background"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text"]};
            border-bottom-color: {COLORS["background_light"]};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {COLORS["background_lighter"]};
        }}
    """,

    "group_box": f"""
        QGroupBox {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            margin-top: 1.5ex;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {COLORS["text"]};
        }}
    """,

    "line_edit": f"""
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {COLORS["background_lighter"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
            selection-background-color: {COLORS["accent_blue"]};
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border: 1px solid {COLORS["accent_blue"]};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {COLORS["background_lighter"]};
            color: {COLORS["text"]};
            selection-background-color: {COLORS["accent_blue"]};
        }}
    """,

    "push_button": f"""
        QPushButton {{
            background-color: {COLORS["background_lighter"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 6px 12px;
        }}

        QPushButton:hover {{
            background-color: {COLORS["border"]};
        }}

        QPushButton:pressed {{
            background-color: {COLORS["background"]};
        }}

        QPushButton:disabled {{
            background-color: {COLORS["background"]};
            color: {COLORS["border"]};
        }}
    """,

    "status_labels": f"""
        QLabel[statusLabel="true"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
        }}
    """,

    "status_connected": f"""
        QLabel[connectionStatus="connected"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["success"]};
            font-weight: bold;
        }}
    """,

    "status_disconnected": f"""
        QLabel[connectionStatus="disconnected"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["error"]};
            font-weight: bold;
        }}
    """,

    "status_partial": f"""
        QLabel[connectionStatus="partial"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["warning"]};
            font-weight: bold;
        }}
    """,

    "log_text": f"""
        QTextEdit[logDisplay="true"] {{
            background-color: {COLORS["background"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 8px;
        }}
    """,

    "hv_enable_button": f"""
        QPushButton[hvButton="enable"] {{
            background-color: {COLORS["success"]};
            color: white;
            border: 2px solid {COLORS["success_light"]};
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
        }}

        QPushButton[hvButton="enable"]:hover {{
            background-color: #45a049;
        }}

        QPushButton[hvButton="enable"]:pressed {{
            background-color: #3e8e41;
        }}

        QPushButton[hvButton="enable"]:disabled {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text_secondary"]};
            border: 2px solid {COLORS["border"]};
        }}
    """,

    "hv_disable_button": f"""
        QPushButton[hvButton="disable"] {{
            background-color: {COLORS["error"]};
            color: white;
            border: 2px solid {COLORS["error_light"]};
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
        }}

        QPushButton[hvButton="disable"]:hover {{
            background-color: #d32f2f;
        }}

        QPushButton[hvButton="disable"]:pressed {{
            background-color: #c62828;
        }}

        QPushButton[hvButton="disable"]:disabled {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text_secondary"]};
            border: 2px solid {COLORS["border"]};
        }}
    """,

    "voltage_reading": f"""
        QLabel[readingType="voltage"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["voltage_display"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "current_reading": f"""
        QLabel[readingType="current"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["current_display"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "hv_status_enabled": f"""
        QLabel[outputStatus="enabled"] {{
            background-color: {COLORS["error"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["error_light"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "hv_status_disabled": f"""
        QLabel[outputStatus="disabled"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "timer_status_inactive": f"""
        QLabel[timerStatus="inactive"] {{
            background-color: {COLORS["background_light"]};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "timer_status_active": f"""
        QLabel[timerStatus="active"] {{
            background-color: {COLORS["info"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["info_light"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "timer_status_expired": f"""
        QLabel[timerStatus="expired"] {{
            background-color: {COLORS["warning"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["warning_light"]};
            border-radius: 4px;
            padding: 5px;
            font-weight: bold;
        }}
    """,

    "log_level_error": f"""
        QLabel[logLevel="error"] {{
            color: {COLORS["error"]};
            font-weight: bold;
        }}
    """,

    "log_level_warning": f"""
        QLabel[logLevel="warning"] {{
            color: {COLORS["warning"]};
            font-weight: bold;
        }}
    """,

    "check_box": f"""
        QCheckBox {{
            color: {COLORS["text"]};
            spacing: 5px;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {COLORS["border"]};
            border-radius: 3px;
            background-color: {COLORS["background_lighter"]};
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLORS["accent_blue"]};
        }}
    """,
}

def get_monospace_font():
    """Get a monospace font suitable for code/logs"""
    font_info = FONTS["monospace"]
    font = QFont(font_info["family"], font_info["size"], font_info["weight"])

    # Try fallbacks if exact match not available
    if not font.exactMatch():
        for fallback in font_info["fallbacks"]:
            font = QFont(fallback, font_info["size"], font_info["weight"])
            if font.exactMatch():
                break

    return font

def get_heading_font():
    """Get a font suitable for headings"""
    font_info = FONTS["heading"]
    return QFont(font_info["family"], font_info["size"], font_info["weight"])

def get_reading_font():
    """Get a font suitable for measurement readings"""
    font_info = FONTS["reading"]
    return QFont(font_info["family"], font_info["size"], font_info["weight"])

def get_button_font():
    """Get a font suitable for buttons"""
    font_info = FONTS["button"]
    return QFont(font_info["family"], font_info["size"], font_info["weight"])

def apply_app_style(app):
    """Apply dark theme to the entire application"""
    # Set application style sheet with combined styles
    stylesheet = "\n".join([
        STYLES["window"],
        STYLES["tab_widget"],
        STYLES["group_box"],
        STYLES["line_edit"],
        STYLES["push_button"],
        STYLES["status_labels"],
        STYLES["status_connected"],
        STYLES["status_disconnected"],
        STYLES["status_partial"],
        STYLES["log_text"],
        STYLES["hv_enable_button"],
        STYLES["hv_disable_button"],
        STYLES["voltage_reading"],
        STYLES["current_reading"],
        STYLES["hv_status_enabled"],
        STYLES["hv_status_disabled"],
        STYLES["timer_status_inactive"],
        STYLES["timer_status_active"],
        STYLES["timer_status_expired"],
        STYLES["log_level_error"],
        STYLES["log_level_warning"],
        STYLES["check_box"]
    ])

    app.setStyleSheet(stylesheet)

    # Set application palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["background"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["background_light"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["background_lighter"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS["background_light"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["background_lighter"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(COLORS["accent_blue"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS["accent_blue"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    # Set disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(COLORS["text_secondary"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(COLORS["text_secondary"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(COLORS["text_secondary"]))

    app.setPalette(palette)

class AppTheme:
    """Static methods for accessing theme styles"""

    @staticmethod
    def get_status_style(status):
        """Get style for status indicators"""
        # This method is retained for backwards compatibility
        # New code should use property-based styling
        if status == "connected":
            return f"color: {COLORS['success']}; font-weight: bold; padding: 5px; background-color: {COLORS['background_light']};"
        elif status == "disconnected":
            return f"color: {COLORS['error']}; font-weight: bold; padding: 5px; background-color: {COLORS['background_light']};"
        elif status == "warning" or status == "partial":
            return f"color: {COLORS['warning']}; font-weight: bold; padding: 5px; background-color: {COLORS['background_light']};"
        else:
            return f"color: {COLORS['text']}; padding: 5px; background-color: {COLORS['background_light']};"

    @staticmethod
    def get_success_button_style():
        """Get style for success buttons"""
        # This method is retained for backwards compatibility
        # New code should use property-based styling with hvButton="enable"
        return f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: 2px solid {COLORS['success_light']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
                border: 2px solid #3e8e41;
            }}
            QPushButton:pressed {{
                background-color: #3e8e41;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
                border: 2px solid #999999;
            }}
        """