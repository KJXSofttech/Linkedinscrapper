from PyQt5 import QtWidgets
from profile_selector import ProfileSelector
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = ProfileSelector()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
