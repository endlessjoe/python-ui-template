"""
Blank UI skeleton — extracted layout/styling only, no application logic.

Everything here is just widgets, layout, and styling. All the buttons,
inputs, and the tree widget are wired to no-op / placeholder handlers
(they just print to the log box or do nothing) so you can see and test
the UI, then replace the placeholder handlers with your own logic.

Run with: python blank_ui.py
Requires: PySide6

Widget layout:

    QMainWindow
    └── central (QWidget)
        ├── main_splitter (QSplitter, vertical)
        │   ├── upper_splitter (QSplitter, horizontal)
        │   │   ├── left_widget (QWidget)
        │   │   └── sidebar_panel (QWidget)
        │   └── log (QTextEdit)
        └── button_row
"""
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QPushButton, QSplitter, QStackedWidget, QTextEdit,
    QVBoxLayout, QWidget,
)


# =============================================================================
# COLORS
# The only place colors are hard-coded; every setStyleSheet() call below
# reads them from here.
# =============================================================================

BG_PANEL = "#2b2b2b"
BG_BUTTON = "#3c3c3c"
BG_BUTTON_HOVER = "#4c4c4c"
BG_THUMBNAIL = "#1f1f1f"
BG_WINDOW = "#232323"
BG_LOG = "#2b2b2b"

BORDER = "#555555"
BORDER_DISABLED = "#444444"
BORDER_THUMBNAIL = "#111111"

TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#cccccc"
TEXT_MUTED = "#999999"
TEXT_FAINT = "#666666"

_BUTTON_BASE = "padding: 5px; border-radius: 3px;"


def sidebar_label_muted_style():
    # Small, secondary-colored text used for the version/status/info
    # labels in the sidebar.
    return f"color: {TEXT_SECONDARY}; font-size: 11px;"


def move_button_style():
    # Style for the Top / Up / Down reorder buttons.
    return (
        f"background-color: {BG_BUTTON}; color: {TEXT_SECONDARY}; "
        f"border: 1px solid {BORDER}; {_BUTTON_BASE}"
    )


def separator_style(margin_top=10, margin_bottom=0):
    # Thin horizontal rule used to divide sections of the sidebar.
    style = f"color: {BORDER_DISABLED}; margin-top: {margin_top}px;"
    if margin_bottom:
        style += f" margin-bottom: {margin_bottom}px;"
    return style


def button_style():
    # Standard push-button style used by the bottom action row
    # (Settings, Exit).
    return (
        f"QPushButton {{ background-color: {BG_BUTTON}; color: {TEXT_SECONDARY}; "
        f"border: 1px solid {BORDER}; {_BUTTON_BASE} }} "
        f"QPushButton:hover {{ background-color: {BG_BUTTON_HOVER}; }}"
    )


def log_style():
    # Background/text for the read-only log text box. BG_LOG matches
    # BG_PANEL, so the log reads as part of the same content surface as
    # the left widget/sidebar above it, rather than a separate block —
    # no border needed.
    return f"background-color: {BG_LOG}; color: {TEXT_SECONDARY}; border: none;"


def splitter_handle_style():
    # Drag handle for the vertical splitter that lets the log box be
    # resized. Deliberately separate from separator_style() above, which
    # colors the static QLabel rules in the sidebar — this only targets
    # the draggable QSplitter::handle, and matching it to the window
    # background keeps it visually quiet at rest (a faint highlight on
    # hover is the only feedback) instead of reading as another divider
    # line.
    return (
        f"QSplitter::handle {{ background-color: {BG_WINDOW}; }} "
        f"QSplitter::handle:hover {{ background-color: {BORDER}; }}"
    )


# =============================================================================
# APP METADATA
# =============================================================================

APP_NAME = "UI Template A"
APP_VERSION = "0.1"


# =============================================================================
# MAIN WINDOW
# Layout and styling only — every button/handler below is a placeholder
# meant to be swapped out for real application logic. Styles are applied
# inline as each widget is built (colors never change at runtime, so
# there's no separate theming pass).
# =============================================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 600)
        self.setMinimumSize(1000, 600)

        self._log_header = f"{APP_NAME} v{APP_VERSION} — UI ready"

        self._build_ui()
        self._connect_signals()
        self._reset_log()

    # -- construction ---------------------------------------------------

    def _build_ui(self):
        # Top-level layout: a vertical splitter holding the horizontal
        # splitter (left content + sidebar) above the log box, so the log
        # can be dragged taller/shorter. The bottom action row stays a
        # fixed-height row below the splitter, outside it.
        central = QWidget()
        central.setStyleSheet(f"background-color: {BG_WINDOW};")
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setSpacing(0)

        upper_splitter = QSplitter(Qt.Horizontal)
        upper_splitter.setHandleWidth(4)
        upper_splitter.addWidget(self._build_left_panel())
        upper_splitter.addWidget(self._build_sidebar())
        upper_splitter.setStretchFactor(0, 4)
        upper_splitter.setStretchFactor(1, 1)
        upper_splitter.setSizes([600, 300])
        upper_splitter.setCollapsible(1, False)
        upper_splitter.handle(1).setEnabled(False)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(40)
        self.log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log.customContextMenuRequested.connect(self._on_log_context_menu)
        self.log.setStyleSheet(log_style())

        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.addWidget(upper_splitter)
        self.main_splitter.addWidget(self.log)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizes([450, 150])
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setStyleSheet(splitter_handle_style())
        v.addWidget(self.main_splitter)

        v.addSpacing(6)
        v.addLayout(self._build_button_row())

    def _build_left_panel(self):
        # Main content area: a QStackedWidget so "Settings" can swap in a
        # second page over the default "Hello World" page.
        self.left_widget = QWidget()
        self.left_widget.setAttribute(Qt.WA_StyledBackground, True)
        self.left_widget.setStyleSheet(
            f"background-color: {BG_PANEL}; border: none; border-radius: 5px;"
        )
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_stack = QStackedWidget()
        self.left_stack.setStyleSheet("background: transparent;")
        left_layout.addWidget(self.left_stack)

        hello_page, self.hello_label = self._build_centered_label_page("Hello World")
        settings_page, self.settings_label = self._build_centered_label_page("Settings")
        self.left_stack.addWidget(hello_page)     # index 0
        self.left_stack.addWidget(settings_page)  # index 1

        return self.left_widget

    def _build_centered_label_page(self, text):
        # A page that's just a single centered label — used for both the
        # default "Hello World" page and the "Settings" page.
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 16px; background: transparent;"
        )
        page_layout.addWidget(label, stretch=1, alignment=Qt.AlignCenter)

        return page, label

    def _build_sidebar(self):
        # Right-hand sidebar: app name/version/status, a preview block,
        # two info labels, and the reorder (Top/Up/Down) button row.
        # Fixed-width panel, so it doubles as the widget the splitter's
        # second handle is disabled against (see _build_ui).
        self.sidebar_panel = QWidget()
        self.sidebar_panel.setAttribute(Qt.WA_StyledBackground, True)
        self.sidebar_panel.setFixedWidth(300)
        self.sidebar_panel.setStyleSheet(
            f"background-color: {BG_PANEL}; border: none; border-radius: 5px;"
        )
        layout = QVBoxLayout(self.sidebar_panel)
        layout.setContentsMargins(10, 10, 10, 10)

        self.name_label = QLabel(APP_NAME)
        self.name_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-size: 14px; font-weight: bold;"
        )
        layout.addWidget(self.name_label)

        self.version_label = QLabel(f"v{APP_VERSION}")
        self.version_label.setStyleSheet(sidebar_label_muted_style())
        layout.addWidget(self.version_label)

        self.status_label = QLabel("status: ready")
        self.status_label.setStyleSheet(sidebar_label_muted_style())
        layout.addWidget(self.status_label)

        self.separator = QLabel("―" * 20)
        self.separator.setAlignment(Qt.AlignCenter)
        self.separator.setStyleSheet(separator_style(margin_top=10))
        layout.addWidget(self.separator)

        layout.addWidget(self._build_preview_container())
        layout.addStretch()

        self.info_label_1 = QLabel("Info line 1")
        self.info_label_1.setAlignment(Qt.AlignCenter)
        self.info_label_1.setStyleSheet(sidebar_label_muted_style())
        layout.addWidget(self.info_label_1)

        self.info_label_2 = QLabel("Info line 2")
        self.info_label_2.setAlignment(Qt.AlignCenter)
        self.info_label_2.setStyleSheet(sidebar_label_muted_style())
        layout.addWidget(self.info_label_2)

        self.separator2 = QLabel("―" * 20)
        self.separator2.setAlignment(Qt.AlignCenter)
        self.separator2.setStyleSheet(separator_style(margin_top=6, margin_bottom=6))
        layout.addWidget(self.separator2)

        layout.addLayout(self._build_move_buttons())

        return self.sidebar_panel

    def _build_preview_container(self):
        # Thumbnail + title/subtitle/detail labels, meant to show details
        # for whatever item is currently selected elsewhere in the UI.
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(260, 145)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("No preview")
        self.preview_label.setStyleSheet(
            f"background-color: {BG_THUMBNAIL}; border: 1px solid {BORDER_THUMBNAIL}; "
            f"color: {TEXT_FAINT};"
        )
        c_layout.addWidget(self.preview_label, alignment=Qt.AlignHCenter)

        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-weight: bold; font-size: 12px;"
        )
        c_layout.addWidget(self.title_label, alignment=Qt.AlignHCenter)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setMaximumWidth(260)
        self.subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 10px;")
        c_layout.addWidget(self.subtitle_label, alignment=Qt.AlignHCenter)

        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setMaximumWidth(260)
        self.detail_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
        c_layout.addWidget(self.detail_label, alignment=Qt.AlignHCenter)

        return container

    def _build_move_buttons(self):
        # Top / Up / Down row, intended to reorder a selected item in
        # whatever list/tree widget this template gets connected to.
        # Returned directly as a layout — no wrapper widget needed since
        # the caller adds it via layout.addLayout().
        self.btn_move_top = QPushButton("Top")
        self.btn_move_up = QPushButton("Up")
        self.btn_move_down = QPushButton("Down")
        for btn in (self.btn_move_top, self.btn_move_up, self.btn_move_down):
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setMinimumWidth(80)
            btn.setStyleSheet(move_button_style())

        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(self.btn_move_top, 1)
        row.addWidget(self.btn_move_up, 1)
        row.addWidget(self.btn_move_down, 1)
        return row

    def _build_button_row(self):
        # Bottom action row: Settings (toggles the left-panel page) and
        # Exit (closes the window).
        self.btn_settings = QPushButton("Settings")
        self.btn_exit = QPushButton("Exit")
        for btn in (self.btn_settings, self.btn_exit):
            btn.setMinimumWidth(80)
            btn.setStyleSheet(button_style())

        row = QHBoxLayout()
        row.addWidget(self.btn_settings)
        row.addStretch()
        row.addWidget(self.btn_exit)
        return row

    # -- wiring (placeholders only — replace with real behavior) --------
    # Every handler here is a no-op stand-in: it either logs a message
    # or performs the minimal UI action needed to demonstrate the widget.

    def _connect_signals(self):
        self.btn_settings.clicked.connect(self._toggle_settings)
        self.btn_exit.clicked.connect(self.close)
        self.btn_move_top.clicked.connect(lambda: self._log("Move to top"))
        self.btn_move_up.clicked.connect(lambda: self._log("Move up"))
        self.btn_move_down.clicked.connect(lambda: self._log("Move down"))

    def _toggle_settings(self):
        # Flip the left panel between the Hello World page (0) and the
        # Settings page (1).
        self.left_stack.setCurrentIndex(1 if self.left_stack.currentIndex() == 0 else 0)

    def _on_log_context_menu(self, pos):
        # Right-click menu on the log box: copy everything, or clear it
        # back to just the header line.
        menu = QMenu(self)
        act_copy = menu.addAction("Copy all")
        act_clear = menu.addAction("Clear")
        action = menu.exec(self.log.mapToGlobal(pos))
        if action == act_copy:
            QApplication.clipboard().setText(self.log.toPlainText())
        elif action == act_clear:
            self._reset_log()

    def _reset_log(self):
        # Header line is permanent and always followed by one blank line
        # before any further log output.
        self.log.setPlainText(self._log_header + "\n")

    def _log(self, msg):
        self.log.append(msg)


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()