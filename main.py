import pandas as pd
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QGridLayout, QWidget,
    QPushButton, QComboBox, QLabel, QGroupBox, QLineEdit, QFileDialog, QHBoxLayout, QRadioButton, QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.setParent(parent)
        self.color = "blue"
        self.title = "Tytuł wykresu"
        self.xlabel = "Oś X"
        self.ylabel = "Oś Y"
        self.x_data = []  # Domyślne puste dane
        self.y_data = []
        self.show_regression=False
        self.plot_type = "liniowy"
        self.plot_data(self.x_data, self.y_data)  # Rysowanie pustego wykresu na początku

    def plot_data(self, x_data, y_data, plot_type="liniowy"):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        plot_type = plot_type or self.plot_type  # Domyślnie używamy aktualnego typu wykresu

        if plot_type == "liniowy":
            ax.plot(x_data, y_data, marker='o', linestyle='--', color=self.color)
        elif plot_type == "punktowy":
            ax.scatter(x_data, y_data, color=self.color, marker='o')

            if self.show_regression and len(x_data) > 1:  # Sprawdzamy, czy regresja ma być rysowana
                coeffs = np.polyfit(x_data, y_data, 1)  # Obliczenie współczynników regresji
                regression_line = np.poly1d(coeffs)  # Tworzenie funkcji linii regresji
                ax.plot(x_data, regression_line(x_data), color='red', label='Regresja liniowa')
                equation = f"y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}"
                ax.text(0.05, 0.95, equation, transform=ax.transAxes, fontsize=12, verticalalignment='top',
                        color='red')

                correlation_matrix = np.corrcoef(x_data, y_data)
                correlation_coefficient = correlation_matrix[0, 1]  # Wartość współczynnika korelacji
                correlation_text = f"r = {correlation_coefficient:.2f}"
                ax.text(0.05, 0.90, correlation_text, transform=ax.transAxes, fontsize=12, verticalalignment='top',
                        color='blue')
                ax.legend()



        elif plot_type == "słupkowy":
            ax.bar(x_data, y_data, color=self.color)
        elif plot_type == "histogram":
            ax.hist(y_data, bins=10, color=self.color, alpha=0.7)

        ax.set_title(self.title, fontsize = 14, fontweight="bold",pad=18)
        ax.set_xlabel(self.xlabel, fontsize = 12)
        ax.set_ylabel(self.ylabel, fontsize = 12)
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

    def toggle_regression(self):
        """Po zaznaczeniu checkboxa rysuje regresję liniową lub ją usuwa."""
        self.show_regression = not self.show_regression
        #self.show_correlation = self.show_regression # Zmieniamy stan flagi
        self.plot_data(self.x_data, self.y_data, self.plot_type)

    def toggle_correlation(self):
        self.show_correlation = not self.show_correlation
        self.plot_data(self.x_data, self.y_data, self.plot_type)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wykres")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("chart.png"))

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;  
            }
            QPushButton {
                background-color: #339999;
                color: white;
                font-size: 13px;
                font-style: bold;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #33cccc;
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

        font_button = QFont()
        font_button.setPointSize(10)
        font_button.setBold(True)

        self.button_wczytajDane = QPushButton("Wczytaj Dane")
        self.button_wczytajDane.setFixedSize(130, 40)
        self.button_wczytajDane.pressed.connect(self.load_data)
        self.button_wczytajDane.setFont(font_button)
        main_layout.addWidget(self.button_wczytajDane, 1, 6, alignment=Qt.AlignCenter)

        # Grupa kontrolna
        control_group = QGroupBox("Opcje Wykresu")
        control_group.setStyleSheet("""
            QGroupBox {
                font: bold 14px;
                color: #444444;
                border: 1px solid #666666;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0px 0px;
            }
        """)
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
        self.input_tytul.setStyleSheet("""
            QLineEdit {
                border: 1px solid #888888;
                border-radius: 5px;
                padding: 5px;
                background: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #5A9;
            }
        """)
        self.input_tytul.textChanged.connect(self.canvas.update_title)
        group_layout.addWidget(self.input_tytul)

        self.xlabel_label = QLabel("Wpisz nazwę osi X:")
        self.xlabel_label.setFont(font_naglowki)
        group_layout.addWidget(self.xlabel_label)
        self.input_xlabel = QLineEdit()
        self.input_xlabel.setStyleSheet("""
            QLineEdit {
                border: 1px solid #888888;
                border-radius: 5px;
                padding: 5px;
                background: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #5A9;
            }
        """)
        self.input_xlabel.textChanged.connect(self.canvas.update_xlabel)
        group_layout.addWidget(self.input_xlabel)

        self.ylabel_label = QLabel("Wpisz nazwę osi Y:")
        self.ylabel_label.setFont(font_naglowki)
        group_layout.addWidget(self.ylabel_label)
        self.input_ylabel = QLineEdit()
        self.input_ylabel.setStyleSheet("""
            QLineEdit {
                border: 1px solid #888888;
                border-radius: 5px;
                padding: 5px;
                background: #f9f9f9;
            }
            QLineEdit:focus {
                border: 2px solid #5A9;
            }
        """)
        self.input_ylabel.textChanged.connect(self.canvas.update_ylabel)
        group_layout.addWidget(self.input_ylabel)
        main_layout.addWidget(control_group, 4, 6, 1, 1)

        self.button_zapiszWykres = QPushButton("Zapisz Wykres")
        self.button_zapiszWykres.setFixedSize(130, 40)
        self.button_zapiszWykres.pressed.connect(self.save_plot)
        self.button_zapiszWykres.setFont(font_button)
        main_layout.addWidget(self.button_zapiszWykres, 7, 6, alignment=Qt.AlignCenter)

        self.histogram_label = QLabel("Wybierz kolumnę do histogramu")
        self.histogram_label.setFont(font_naglowki)
        group_layout.addWidget(self.histogram_label)

        radio_layout = QHBoxLayout()
        self.radio_button_1 = QRadioButton("X")
        self.radio_button_2 = QRadioButton("Y")

        # Ustawienie domyślnego wyboru
        self.radio_button_1.setChecked(True)

        # Dodanie przycisków do układu
        radio_layout.addWidget(self.radio_button_1)
        radio_layout.addWidget(self.radio_button_2)

        # Dodanie układu do głównego układu grupy
        group_layout.addLayout(radio_layout)
        self.radio_button_1.toggled.connect(self.update_histogram)
        self.radio_button_2.toggled.connect(self.update_histogram)

        self.regresja_label = QLabel("Regresja liniowa")
        self.regresja_label.setFont(font_naglowki)
        group_layout.addWidget(self.regresja_label)  # Etykieta

        self.checkbox_regresja = QCheckBox()
        self.checkbox_regresja.stateChanged.connect(self.canvas.toggle_regression)
        group_layout.addWidget(self.checkbox_regresja)
        
    def load_data(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik z danymi", "", "Wszystkie pliki (*)",
                                                   options=options)

        if file_path:
            data = pd.read_csv(file_path)
            if data.shape[1] >= 2:  # Sprawdzamy, czy są co najmniej dwie kolumny
                self.canvas.x_data = data.iloc[:, 0].values
                self.canvas.y_data = data.iloc[:, 1].values  # Druga kolumna danych
                self.canvas.plot_data(self.canvas.x_data, self.canvas.y_data, self.canvas.plot_type)  # Zmieniono
            else:
                print("Nieprawidłowy format danych")

    def update_plot_type(self, plot_type):
        self.canvas.plot_type = plot_type
        if plot_type == "histogram":
            self.radio_button_1.setChecked(True)  # Ustawienie domyślnego wyboru X
            self.canvas.plot_data([], self.canvas.x_data, "histogram")  # Rysowanie histogramu dla X
        else:
            self.canvas.plot_data(self.canvas.x_data, self.canvas.y_data, plot_type)

        if plot_type == "punktowy":
            self.checkbox_regresja.setEnabled(True)
        else:
            self.checkbox_regresja.setEnabled(False)

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

    def update_histogram(self):
        if self.canvas.plot_type == "histogram":
            if self.radio_button_1.isChecked():
                self.canvas.plot_data([], self.canvas.x_data, "histogram")
            elif self.radio_button_2.isChecked():
                self.canvas.plot_data([], self.canvas.y_data, "histogram")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
