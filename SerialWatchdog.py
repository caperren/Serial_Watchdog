#!/usr/bin/env python

"""
    Main file used to launch the Serial Watchdog
    No other files should be used for launching this application.
"""

__author__ = "Corwin Perren"
__credits__ = [""]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Corwin Perren"
__email__ = "caperren@caperren.com"
__status__ = "Development"

#####################################
# Imports
#####################################
# Python native imports
import sys
from PyQt5 import QtWidgets, QtCore, uic
import signal

# Custom Imports
from Framework.MonitorCore import Monitor

#####################################
# Global Variables
#####################################


#####################################
# Main Definition
#####################################
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # This allows the keyboard interrupt kill to work  properly
    application = QtWidgets.QApplication(sys.argv)  # Create the base qt gui application
    monitor = Monitor()
    application.exec_()  # Execute launching of the application
