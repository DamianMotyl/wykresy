import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QGridLayout, QWidget,
    QPushButton, QComboBox, QLabel, QGroupBox, QLineEdit, QCheckBox, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.setParent(parent)
        self.color = "blue"
        self.title = "Przykładowy wykres"
        self.xlabel = "Oś X"
        self.ylabel = "Oś Y"
        self.x_data = []  # Domyślne puste dane
        self.y_data = []
        self.plot_type = "liniowy"
        self.plot_data(self.x_data, self.y_data)  # Rysowanie pustego wykresu na początku

    def plot_data(self, x_data, y_data, plot_type=None):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        plot_type = plot_type or self.plot_type  # Domyślnie używamy aktualnego typu wykresu

        if plot_type == "liniowy":
            ax.plot(x_data, y_data, marker='o', linestyle='--', color=self.color)
        elif plot_type == "punktowy":
            ax.scatter(x_data, y_data, color=self.color, marker='o')
        elif plot_type == "słupkowy":
            ax.bar(x_data, y_data, color=self.color)
        elif plot_type == "histogram":
            ax.hist(x_data, bins=10, color=self.color, alpha=0.7)

        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        self.draw()

    def update_color(self, new_color):
        self.color = new_color
        self.plot_data(self.x_data, self.y_data)

    def update_title(self, new_title):
        self.title = new_title
        self.plot_data(self.x_data, self.y_data)

    def update_xlabel(self, new_xlabel):
        self.xlabel = new_xlabel
        self.plot_data(self.x_data, self.y_data)

    def update_ylabel(self, new_ylabel):
        self.ylabel = new_ylabel
        self.plot_data(self.x_data, self.y_data)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matplotlib w PyQt - Wybór koloru wykresu")
        self.setGeometry(100, 100, 900, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;  
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-size: 12px;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #d4d4d4;
                padding: 5px;
            }
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)

        # Wykres
        self.canvas = MatplotlibCanvas(self)
        main_layout.addWidget(self.canvas, 0, 0, 10, 6)

        font_naglowki = QFont()
        font_naglowki.setPointSize(10)
        font_naglowki.setBold(True)

        self.button_wczytajDane = QPushButton("Wczytaj Dane")
        self.button_wczytajDane.setFixedSize(120, 40)
        self.button_wczytajDane.pressed.connect(self.load_data)
        main_layout.addWidget(self.button_wczytajDane, 1, 6, alignment=Qt.AlignCenter)

        # Grupa kontrolna
        control_group = QGroupBox("Opcje Wykresu")
        group_layout = QVBoxLayout(control_group)

        # Typ wykresu
        self.typ_label = QLabel("Wybierz typ wykresu:")
        self.typ_label.setFont(font_naglowki)
        self.typ_selector = QComboBox()
        self.typ_selector.addItems(["liniowy", "punktowy", "słupkowy", "histogram"])
        self.typ_selector.currentTextChanged.connect(self.update_plot_type)
        group_layout.addWidget(self.typ_label)
        group_layout.addWidget(self.typ_selector)

        # Kolor wykresu
        self.color_label = QLabel("Wybierz kolor wykresu:")
        self.color_label.setFont(font_naglowki)
        self.color_selector = QComboBox()
        self.color_selector.addItems(["blue", "red", "green", "orange", "purple", "black"])
        self.color_selector.currentTextChanged.connect(self.canvas.update_color)
        group_layout.addWidget(self.color_label)
        group_layout.addWidget(self.color_selector)

        self.tytul_label = QLabel("Wpisz tytuł wykresu:")
        self.tytul_label.setFont(font_naglowki)
        group_layout.addWidget(self.tytul_label)
        self.input_tytul = QLineEdit()
        self.input_tytul.textChanged.connect(self.canvas.update_title)
        group_layout.addWidget(self.input_tytul)

        self.xlabel_label = QLabel("Wpisz nazwę osi X:")
        self.xlabel_label.setFont(font_naglowki)
        group_layout.addWidget(self.xlabel_label)
        self.input_xlabel = QLineEdit()
        self.input_xlabel.textChanged.connect(self.canvas.update_xlabel)
        group_layout.addWidget(self.input_xlabel)

        self.ylabel_label = QLabel("Wpisz nazwę osi Y:")
        self.ylabel_label.setFont(font_naglowki)
        group_layout.addWidget(self.ylabel_label)
        self.input_ylabel = QLineEdit()
        self.input_ylabel.textChanged.connect(self.canvas.update_ylabel)
        group_layout.addWidget(self.input_ylabel)
        main_layout.addWidget(control_group, 3, 6, 1, 1)

        self.button_zapiszWykres = QPushButton("Zapisz Wykres")
        self.button_zapiszWykres.setFixedSize(120, 40)
        self.button_zapiszWykres.pressed.connect(self.save_plot)
        main_layout.addWidget(self.button_zapiszWykres, 7, 6, alignment=Qt.AlignCenter)

    def load_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik z danymi", "", "Wszystkie pliki (*)", options=options)

        if file_path:
            data = pd.read_csv(file_path)
            if data.shape[1] >= 1:
                self.canvas.x_data = data.iloc[:, 0].values
                if self.canvas.plot_type != "histogram" and data.shape[1] > 1:
                    self.canvas.y_data = data.iloc[:, 1].values
                else:
                    self.canvas.y_data = []
                self.canvas.plot_data(self.canvas.x_data, self.canvas.y_data)
            else:
                print("Nieprawidłowy format danych")

    def update_plot_type(self, plot_type):
        self.canvas.plot_type = plot_type
        self.canvas.plot_data(self.canvas.x_data, self.canvas.y_data)

    def save_plot(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz wykres jako...",
            "",
            "JPEG Files (*.jpg);;PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                # Zapisujemy wykres do pliku w wybranym formacie
                self.canvas.fig.savefig(file_path, format=file_path.split('.')[-1], dpi=300)
                print(f"Wykres zapisano jako {file_path}")
            except Exception as e:
                print(f"Nie udało się zapisać wykresu: {e}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
