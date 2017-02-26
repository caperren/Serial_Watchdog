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

    update_other_gui_elements = QtCore.pyqtSignal(str, str)

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

        # ########## Setup tray icon ##########
        self.setup_tray_icon()

        # ########## Get Initial Ports ##########
        self.get_usb_serial_devices()
        self.ports_prev = self.ports
        self.num_usb_serial_devices_prev = self.num_usb_serial_devices

        # ########## Make signal/slot connections ##########
        self.__connect_signals_to_slots()

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
        pass

    def setup_tray_icon(self):
        self.system_tray_icon.setContextMenu(self.tray_menu)
        self.system_tray_icon.show()
        self.system_tray_icon.showMessage("Serial Watchdog", "Application started.\nSerial updates will be " +
                                          "shown here.", QtWidgets.QSystemTrayIcon.Information, 5000)

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

            self.system_tray_icon.showMessage("New Serial Device Detected", message,
                                              QtWidgets.QSystemTrayIcon.Information, 1500)

            self.only_update_tray_list = True

            self.update_needed = False

        if self.only_update_tray_list:
            self.list_tray_menu_items()
            self.only_update_tray_list = False

        # Set the previous number of devices to the current number, so the update only happens when things change
        self.num_usb_serial_devices_prev = self.num_usb_serial_devices

        self.ports_prev = self.ports

    def get_usb_serial_devices(self):
        self.num_usb_serial_devices = 0

        all_ports = list(list_ports.comports())

        self.ports = []

        for port_num, description, address in all_ports:
            if 'USB' in description:
                self.num_usb_serial_devices += 1
                self.ports.append({"port_num": port_num, "description": description, "address": address})

    def port_difference(self, new_ports, old_ports):
        if self.num_usb_serial_devices == 1:
            return new_ports[0]

        for port_new in new_ports:
            # print(port_new)
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

    def on_tray_exit_triggered__slot(self, event):

        if event.text() == "Exit":
            self.run_thread_flag = False
            self.wait()

            self.system_tray_icon.hide()
            QtWidgets.QApplication.quit()

    def on_kill_threads__slot(self):
        self.run_thread_flag = False


