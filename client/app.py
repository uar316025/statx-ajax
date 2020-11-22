"""Client Application"""
# pylint: disable=too-few-public-methods
import getpass
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QHBoxLayout, QApplication, QLineEdit, \
    QCheckBox, QDateTimeEdit, QWidget, QPushButton, QVBoxLayout, QSpinBox, \
    QToolBar, QMainWindow, QAction, QTableView, QAbstractItemView, QMessageBox, QStatusBar

from api_client import ApiException, StatxAPIv1


class _ActionWindow(QMainWindow):
    """General class for action windows"""

    def __init__(self, name, statx_api: StatxAPIv1, parent=None):
        super().__init__(parent)
        self.setWindowTitle(name)
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowStaysOnTopHint
        )

        self.statx_api = statx_api

        self.widget = QWidget()

        self.setCentralWidget(self.widget)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)


class AddWindow(_ActionWindow):
    """AddWindow"""

    DEFAULT_USER = getpass.getuser()

    def __init__(self, statx_api: StatxAPIv1, parent=None):
        super().__init__('Add test result', statx_api, parent)

        self.dev_type = QLineEdit()
        self.operator = QLineEdit(AddWindow.DEFAULT_USER)
        self.dt = QDateTimeEdit(datetime.now())
        self.success = QCheckBox()
        self.button = QPushButton('Add')
        self.button.clicked.connect(self.onAdd)

        layout = QGridLayout()
        layout.setSpacing(3)
        layout.addWidget(QLabel('Device type'), 0, 0)
        layout.addWidget(self.dev_type, 0, 1)
        layout.addWidget(QLabel('Operator'), 1, 0)
        layout.addWidget(self.operator, 1, 1)
        layout.addWidget(QLabel('Date'), 0, 2)
        layout.addWidget(self.dt, 0, 3)
        layout.addWidget(QLabel('Is success'), 1, 2)
        layout.addWidget(self.success, 1, 3)
        layout.addWidget(self.button, 2, 3)

        self.widget.setLayout(layout)

    def onAdd(self):
        """Handle add button click"""
        operator = self.operator.text()
        AddWindow.DEFAULT_USER = operator
        dt = self.dt.dateTime().toPyDateTime()
        try:
            res = self.statx_api.test_result_add(
                dev_type=self.dev_type.text(),
                operator=operator,
                dt=dt,
                success=self.success.isChecked(),
            )
        except ApiException as exc:
            _show_err_message(self, 'API Exception', exc.args[0])
            return

        message = f"Successfully added ID#{res['id']} [{dt}]"
        self.statusBar.showMessage(message, 15000)


class StatxDisplayFrame(QFrame):
    """StatxDisplayFrame"""

    def __init__(self, statx_api: StatxAPIv1):
        super().__init__()

        self.statx_api = statx_api

        self.operator = QLineEdit()
        self.button = QPushButton('Query')
        self.button.clicked.connect(self.onQuery)

        self.table = QTableView()
        self.table.setMinimumWidth(440)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.model = QStandardItemModel()
        self.table.setModel(self.model)

        q_layout = QHBoxLayout()
        q_layout.addWidget(QLabel('Operator'))
        q_layout.addWidget(self.operator)
        q_layout.addWidget(self.button)

        frame = QFrame()
        frame.setLayout(q_layout)

        layout = QVBoxLayout()
        layout.addWidget(frame)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def onQuery(self):
        """Handle query button click"""
        try:
            rows = self.statx_api.stat(self.operator.text() or None)
        except ApiException as exc:
            _show_err_message(self, 'API Exception', exc.args[0])
            return

        # cleanup model
        self.model.clear()
        self.model.setHorizontalHeaderLabels([
            'Device type', 'Tests count', 'Successfully', 'Failed'
        ])

        order = ['dev_type', 'count', 'successful', 'failed']
        for row in rows:
            # prepare for model
            prepared = [str(row[field]) for field in order]
            # add to model
            self.model.appendRow(map(QStandardItem, prepared))


class RemoveWindow(_ActionWindow):
    """RemoveWindow"""

    def __init__(self, statx_api: StatxAPIv1, parent=None):
        super().__init__('Remove test item', statx_api, parent)
        self.test_result_id = spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(1 << 30)

        self.button = QPushButton('Remove')
        self.button.clicked.connect(self.onRemove)

        layout = QHBoxLayout()
        layout.addWidget(QLabel('Test result ID'))
        layout.addWidget(self.test_result_id)
        layout.addWidget(self.button)

        self.widget.setLayout(layout)

    def onRemove(self):
        """Handle remove button click"""
        value_id = self.test_result_id.value()
        try:
            self.statx_api.test_result_delete(value_id)
        except ApiException as exc:
            _show_err_message(self, 'API Exception', exc.args[0])
            return

        message = f'Successfully removed ID#{value_id}'
        self.statusBar.showMessage(message, 15000)


class MainWindow(QMainWindow):
    """MainWindow"""

    def __init__(self, statx_api: StatxAPIv1):
        super().__init__()
        self.statx_api = statx_api
        self.setWindowTitle('StatxAPIv1 Client')

        self.add_button = QAction('Add Test Result')
        self.add_button.triggered.connect(self.onClickAdd)

        self.remove_button = QAction('Remove Test Result')
        self.remove_button.triggered.connect(self.onClickRemove)

        toolbar = QToolBar('toolbar')
        toolbar.addAction(self.add_button)
        toolbar.addAction(self.remove_button)

        self.addToolBar(toolbar)

        layout = QVBoxLayout()
        layout.addWidget(StatxDisplayFrame(statx_api))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def onClickAdd(self):
        """Handle remove add click"""
        # yep, I know here possible to create many windows :)
        AddWindow(self.statx_api, self).show()

    def onClickRemove(self):
        """Handle remove button click"""
        # yep, I know here possible to create many windows :)
        RemoveWindow(self.statx_api, self).show()


def _show_err_message(parent, title, message):
    """Show error message"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setText('Error')
    msg.setInformativeText(message)
    msg.setWindowTitle(title)
    msg.show()


def main():
    """Just main"""
    app = QApplication([])

    statx_api = StatxAPIv1('http://localhost:5000/api_v1')
    window = MainWindow(statx_api)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
