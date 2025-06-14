import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from AnkiConnector import AnkiConnector
from anki_utils import ensure_anki_running

class AnkiCardReviewer(QWidget):
    def __init__(self, cards):
        super().__init__()
        self.cards = cards
        self.index = 0
        self.front_shown = True
        self.deck_name = "...MyDiscoveries2"
        self.note_type = "Basic"
        self.connector = AnkiConnector(deck_name=self.deck_name, note_type=self.note_type, allow_duplicate=False)
        self.init_ui()
        self.show_card()

    def init_ui(self):
        self.setWindowTitle("JSON to Anki Card Reviewer")
        self.setGeometry(100, 100, 600, 300)
        self.set_dark_theme()

        self.layout = QVBoxLayout()
        self.label = QLabel("", self)
        self.label.setFont(QFont("Arial", 18))
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.reveal_btn = QPushButton("Show Back", self)
        self.reveal_btn.clicked.connect(self.reveal_back)
        self.layout.addWidget(self.reveal_btn)

        self.keep_btn = QPushButton("Keep (Add to Anki)", self)
        self.keep_btn.clicked.connect(self.keep_card)
        self.keep_btn.setVisible(False)
        self.layout.addWidget(self.keep_btn)

        self.reject_btn = QPushButton("Reject", self)
        self.reject_btn.clicked.connect(self.reject_card)
        self.reject_btn.setVisible(False)
        self.layout.addWidget(self.reject_btn)

        self.setLayout(self.layout)

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        self.setPalette(palette)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #fff; }
            QPushButton { background-color: #333; color: #fff; border-radius: 6px; padding: 8px; }
            QPushButton:hover { background-color: #444; }
            QLabel { color: #fff; }
        """)

    def show_card(self):
        if self.index >= len(self.cards):
            QMessageBox.information(self, "Done", "No more cards!")
            self.close()
            return
        self.front_shown = True
        self.label.setText(self.cards[self.index]["front"])
        self.reveal_btn.setVisible(True)
        self.keep_btn.setVisible(False)
        self.reject_btn.setVisible(False)

    def reveal_back(self):
        self.front_shown = False
        back = self.cards[self.index]["back"]
        source = self.cards[self.index].get("source", "")
        if source:
            back += f"\n\nSource: {source}"
        self.label.setText(back)
        self.reveal_btn.setVisible(False)
        self.keep_btn.setVisible(True)
        self.reject_btn.setVisible(True)

    def keep_card(self):
        if not ensure_anki_running():
            QMessageBox.warning(self, "Anki Not Running", "Could not start or connect to Anki. Please start Anki manually.")
            return
        front = self.cards[self.index]["front"]
        back = self.cards[self.index]["back"]
        source = self.cards[self.index].get("source", "")
        # Add source to the back for display, but keep as separate field for Anki
        anki_back = back
        if source:
            anki_back += f"\n\nSource: {source}"
        success = self.connector.add_card(front, anki_back, source)
        if success:
            QMessageBox.information(self, "Added", "Card added to Anki.")
        else:
            QMessageBox.warning(self, "Failed", "Failed to add card to Anki.")
        self.index += 1
        self.show_card()

    def reject_card(self):
        self.index += 1
        self.show_card()

def main():
    # Accept JSON file path as argument, else exit
    if len(sys.argv) < 2:
        QMessageBox.warning(None, "No Cards", "No JSON file provided.")
        sys.exit(0)
    json_path = sys.argv[1]
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cards = [item for item in data if "front" in item and "back" in item]
    if not cards:
        QMessageBox.warning(None, "No Cards", "No valid cards found in JSON.")
        sys.exit(0)
    app = QApplication(sys.argv)
    reviewer = AnkiCardReviewer(cards)
    reviewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()