import sys
import os
import csv
import time
import serial
import threading
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont
import pyqtgraph as pg

# --- CONFIGURAZIONE ---
PORTA = 'COM3'
BAUD = 115200
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
FILE_CSV = os.path.join(DESKTOP_PATH, f"telemetria_{datetime.now().strftime('%H%M%S')}.csv")

class TelemetriaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEEKER-II DASHBOARD")
        self.setStyleSheet("background-color: #050505; color: #00FF88; font-family: 'Segoe UI', sans-serif;")
        
        # Dati interna
        self.data_alt = []
        self.data_time = []
        self.max_alt = 0.0
        self.max_g = 0.0
        self.last_alt = 0.0
        self.last_time = time.time()
        
        # Inizializza CSV
        with open(FILE_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Packet', 'Alt_m', 'Acc_g', 'RSSI_dbm'])

        self.init_ui()
        
        # Timer per aggiornamento orologio e stato
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_clock)
        self.ui_timer.start(100)

        # Thread per la Seriale
        self.thread = threading.Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QGridLayout(main_widget)

        # --- HEADER ---
        header = QHBoxLayout()
        title = QLabel("◈ SEEKER-II | FEDERICO FASSO | V1.2")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.clock_label = QLabel("T + 00:00:00")
        self.clock_label.setStyleSheet("color: #FFBB00; font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.clock_label)
        layout.addLayout(header, 0, 0, 1, 3)

        # --- COLONNA SINISTRA (Dati Storici/Peak) ---
        side_panel = QVBoxLayout()
        self.box_max_alt = self.create_info_box("ALTITUDE MAX", "0.0 m", "#00FF88")
        self.box_max_g = self.create_info_box("G-FORCE MAX", "0.00 G", "#FFAA00")
        self.box_serial = self.create_info_box("SERIAL STATUS", f"{PORTA}\n{BAUD}", "#555555")
        
        side_panel.addWidget(self.box_max_alt)
        side_panel.addWidget(self.box_max_g)
        side_panel.addWidget(self.box_serial)
        side_panel.addStretch()
        layout.addLayout(side_panel, 1, 0)

        # --- CENTRO (Grafico Altitudine) ---
        self.graph = pg.PlotWidget(title="LIVE ALTITUDE PROFILE")
        self.graph.setBackground('#080808')
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.graph.plot(pen=pg.mkPen(color='#00FF88', width=3))
        layout.addWidget(self.graph, 1, 1)

        # --- COLONNA DESTRA (Dati Real-time Grandi) ---
        big_panel = QVBoxLayout()
        self.display_alt = self.create_big_display("ALTITUDE", "0.0", "METERS", "#00FF88")
        self.display_vel = self.create_big_display("VELOCITY", "0.0", "M/S", "#00AAFF")
        big_panel.addWidget(self.display_alt)
        big_panel.addWidget(self.display_vel)
        layout.addLayout(big_panel, 1, 2)

        # --- FOOTER (RSSI, Loss, Acceleration) ---
        footer = QHBoxLayout()
        self.log_label = QLabel("LOG: WAITING FOR TELEMETRY...")
        self.rssi_label = QLabel("RSSI: --- dBm")
        self.rssi_label.setStyleSheet("font-size: 14px; background: #111; padding: 5px; border-radius: 3px;")
        
        self.accel_box = QFrame()
        self.accel_box.setStyleSheet("background: #111; border: 1px solid #FFAA00; padding: 5px;")
        acc_lay = QVBoxLayout(self.accel_box)
        acc_lay.addWidget(QLabel("ACCELERATION Y"))
        self.acc_val = QLabel("9.81 G")
        self.acc_val.setStyleSheet("font-size: 20px; color: #FFAA00; font-weight: bold;")
        acc_lay.addWidget(self.acc_val)

        footer.addWidget(self.log_label, 2)
        footer.addWidget(self.rssi_label)
        footer.addWidget(self.accel_box)
        layout.addLayout(footer, 2, 0, 1, 3)

    def create_info_box(self, label, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"border: 1px solid #222; background: #0A0A0A; margin-bottom: 5px;")
        l = QVBoxLayout(frame)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 9px; color: #666; border: none;")
        val = QLabel(value)
        val.setStyleSheet(f"font-size: 18px; color: {color}; border: none; font-weight: bold;")
        l.addWidget(lbl)
        l.addWidget(val)
        return frame

    def create_big_display(self, label, val, unit, color):
        frame = QFrame()
        frame.setStyleSheet("border: 2px solid #111; background: #080808;")
        l = QVBoxLayout(frame)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {color}; font-size: 12px; border: none;")
        v = QLabel(val)
        v.setStyleSheet(f"color: {color}; font-size: 60px; font-weight: bold; border: none;")
        u = QLabel(unit)
        u.setStyleSheet("color: #444; font-size: 10px; border: none;")
        l.addWidget(lbl)
        l.addWidget(v, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(u, alignment=Qt.AlignmentFlag.AlignRight)
        return frame

    def update_clock(self):
        elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.last_time))
        self.clock_label.setText(f"T + {elapsed}")

    def read_serial(self):
        try:
            ser = serial.Serial(PORTA, BAUD, timeout=0.1)
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 4:
                        # pkt, alt, acc, rssi
                        p_id, alt, acc, rssi = map(float, parts)
                        self.process_data(p_id, alt, acc, rssi)
        except Exception as e:
            self.log_label.setText(f"ERROR: {str(e)}")

    def process_data(self, p_id, alt, acc, rssi):
        now = time.time()
        dt = now - self.last_time
        
        # Calcolo velocità (v = Δs / Δt)
        vel = (alt - self.last_alt) / dt if dt > 0 else 0
        
        # Aggiornamento massimi
        if alt > self.max_alt: self.max_alt = alt
        if abs(acc) > self.max_g: self.max_g = abs(acc)

        # UI Update (Thread-safe via direct calls qui è ok per PyQt6 in piccoli volumi)
        self.display_alt.findChildren(QLabel)[1].setText(f"{alt:.1f}")
        self.display_vel.findChildren(QLabel)[1].setText(f"{vel:.1f}")
        self.box_max_alt.findChildren(QLabel)[1].setText(f"{self.max_alt:.1f} m")
        self.box_max_g.findChildren(QLabel)[1].setText(f"{self.max_g:.2f} G")
        self.acc_val.setText(f"{acc:.2f} G")
        self.rssi_label.setText(f"RSSI: {int(rssi)} dBm")
        self.log_label.setText(f"LOG: RECEIVING PACKET #{int(p_id)}")

        # Grafico
        self.data_alt.append(alt)
        if len(self.data_alt) > 100: self.data_alt.pop(0)
        self.curve.setData(self.data_alt)

        # Salva CSV
        with open(FILE_CSV, 'a', newline='') as f:
            csv.writer(f).writerow([datetime.now().isoformat(), p_id, alt, acc, rssi])

        self.last_alt = alt
        self.last_time = now

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TelemetriaGUI()
    window.showMaximized()
    sys.exit(app.exec())