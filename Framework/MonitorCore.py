"""
    This file contains the live logs page sub-class
"""

#####################################
# Imports
#####################################
# Python native imports
from PyQt5 import QtCore, QtWidgets, QtGui
import serial.tools.list_ports as list_ports

#####################################
# Global Variables
#####################################


#####################################
# Monitor Class Definition
#####################################
class Monitor(QtCore.QThread):
    setup_tray__signal = QtCore.pyqtSignal()
    update_tray__signal = QtCore.pyqtSignal()
    show_message__signal = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super(Monitor, self).__init__()

        # ########## Thread Flags ##########
        self.run_thread_flag = True
        self.update_needed = False
        self.only_update_tray_list = True

        # ########## Class Variables ##########
        self.system_tray_icon = QtWidgets.QSystemTrayIcon(QtGui.QIcon("Resources/port.png"))
        self.tray_menu = QtWidgets.QMenu()

        self.ports = []
        self.ports_prev = []

        self.num_usb_serial_devices = 0
        self.num_usb_serial_devices_prev = 0

        # ########## Get Initial Ports ##########
        self.get_usb_serial_devices()
        self.ports_prev = self.ports
        self.num_usb_serial_devices_prev = self.num_usb_serial_devices

        # ########## Make signal/slot connections ##########
        self.__connect_signals_to_slots()

        # ########## Setup tray icon ##########
        self.setup_tray__signal.emit()

        # ########## Start Thread ##########
        self.start()

    def run(self):
        print("Monitor Thread Starting...")

        while self.run_thread_flag:
            self.watch_and_update_serial_devices()
            self.msleep(1000)

        print("Monitor Thread Stopping...")

    # noinspection PyUnresolvedReferences
    def __connect_signals_to_slots(self):
        self.setup_tray__signal.connect(self.setup_tray_icon)
        self.update_tray__signal.connect(self.list_tray_menu_items)
        self.show_message__signal.connect(self.show_message)

    def setup_tray_icon(self):
        self.system_tray_icon.setContextMenu(self.tray_menu)
        self.system_tray_icon.show()
        self.show_message__signal.emit("Serial Watchdog", "Application started.\nSerial updates will be shown here.")

    # noinspection PyUnresolvedReferences
    def watch_and_update_serial_devices(self):
        # Get the current device listing
        self.get_usb_serial_devices()

        # If the new number of devices is larger than the last known, get ready to update
        if self.num_usb_serial_devices > self.num_usb_serial_devices_prev:
            self.update_needed = True
        elif self.num_usb_serial_devices != self.num_usb_serial_devices_prev:
            self.only_update_tray_list = True

        # If there's an update to show
        if self.update_needed:
            new_port = self.port_difference(self.ports, self.ports_prev)

            message = new_port["port_num"] + " : " + new_port["description"]

            self.show_message__signal.emit("New Serial Device Detected", message)

            self.only_update_tray_list = True
            self.update_needed = False

        if self.only_update_tray_list:
            self.update_tray__signal.emit()
            self.only_update_tray_list = False

        # Set the previous number of devices to the current number, so the update only happens when things change
        self.num_usb_serial_devices_prev = self.num_usb_serial_devices

        self.ports_prev = self.ports

    def get_usb_serial_devices(self):
        self.num_usb_serial_devices = 0

        all_ports = list(list_ports.comports())

        self.ports = []

        for com_ports, description, address in all_ports:
            if 'USB' in address:
                if isinstance(com_ports, str):
                    com_ports = [com_ports]

                for port in com_ports:
                    self.num_usb_serial_devices += 1
                    self.ports.append({"port_num": port, "description": description, "address": address})

    def port_difference(self, new_ports, old_ports):
        if self.num_usb_serial_devices == 1:
            return new_ports[0]

        for port_new in new_ports:
            port_found = False
            for port_old in old_ports:
                if port_new["port_num"] == port_old["port_num"]:
                    port_found = True
                    break

            if not port_found:
                return port_new

    # noinspection PyUnresolvedReferences
    def list_tray_menu_items(self):
        # Update tray menu listing
        self.tray_menu.clear()

        for port in self.ports:
            message = port["port_num"] + " : " + port["description"]
            self.tray_menu.addAction(message)

        self.tray_menu.addSeparator()
        self.tray_menu.addAction("Exit")
        self.tray_menu.triggered.connect(self.on_tray_exit_triggered__slot)

    def show_message(self, title, message):
        self.system_tray_icon.showMessage(title, message,
                                          QtWidgets.QSystemTrayIcon.Information, 1500)

    def on_tray_exit_triggered__slot(self, event):

        if event.text() == "Exit":
            self.run_thread_flag = False
            self.wait()

            self.system_tray_icon.hide()
            QtWidgets.QApplication.quit()

    def on_kill_threads__slot(self):
        self.run_thread_flag = False


