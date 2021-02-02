import sys, os
from PyQt4 import QtGui, QtCore, QtWebKit

class LayoutObjects():
    def __init__(self, fme_object):
        self.layout_funcs = LayoutFuncs()

    def initialise_menu_bar(self, fme_object):
        menu_bar = QtGui.QMenuBar()
        File = menu_bar.addMenu("File")
        File.addAction("Quit")
        Datasource = menu_bar.addMenu("&Datasource")
        parse_process_dir = QtGui.QAction('&Read FragMAX directory', fme_object)
        parse_process_dir.triggered.connect(fme_object.parse_process_directory)
        Datasource.addAction(parse_process_dir)

        score_datasets = QtGui.QAction('&Score auto-processing', fme_object)
        score_datasets.triggered.connect(fme_object.score_datasets)
        Datasource.addAction(score_datasets)

        update_table = QtGui.QAction('&Update table from DB', fme_object)
        update_table.triggered.connect(fme_object.populate_datasets_summary_table)
        Datasource.addAction(update_table)


        Model = menu_bar.addMenu("&Model")
        open_coot = QtGui.QAction('&Open COOT', fme_object)
        open_coot.triggered.connect(fme_object.start_coot)
        Model.addAction(open_coot)



        # "Reload Samples From Datasource"
        return menu_bar


    def main_layout(self, fme_object):
        vbox_main = QtGui.QVBoxLayout()

        # initialise menu bar
        menu_bar = self.initialise_menu_bar(fme_object)
        menu_bar.setMaximumWidth(fme_object.screen.width())
        vbox_main.addWidget(menu_bar)

        # main tab widget
#        fme_object.main_tab_widget = QtGui.QTabWidget()

        ## datasets
        fme_object.datasets_summary_table = QtGui.QTableWidget()
        fme_object.datasets_summary_table.resizeRowsToContents()
        fme_object.datasets_summary_table.resizeColumnsToContents()
        fme_object.datasets_summary_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        fme_object.datasets_summary_table.setColumnCount(len(fme_object.datasets_summary_table_columns))
        fme_object.datasets_summary_table.setHorizontalHeaderLabels(fme_object.datasets_summary_table_columns)
        fme_object.datasets_summary_table.setSortingEnabled(True)
        fme_object.datasets_summary_table.cellClicked.connect(fme_object.show_results_from_all_pipelines)
#        fme_object.main_tab_widget.addTab(fme_object.datasets_summary_table, "Datasets")
#        fme_object.datasets_summary_table.show()
        vbox_main.addWidget(fme_object.datasets_summary_table)

        ## settings
#        fme_object.settings_container = QtGui.QWidget()
#        settings_vbox = QtGui.QVBoxLayout()
#        fme_object.projectDIRbutton = QtGui.QPushButton()
#        fme_object.projectDIRbutton.setText("select project directory")
#        fme_object.projectDIRbutton.clicked.connect(self.select_projectDIRbutton)
#        settings_vbox.addWidget(fme_object.projectDIRbutton)
#        fme_object.settings_container.setLayout(settings_vbox)
#        fme_object.main_tab_widget.addTab(fme_object.settings_container, "Settings")

#        vbox_main.addStretch(-1)

        # status bar
        fme_object.status_bar = QtGui.QStatusBar()
        fme_object.progress_bar = QtGui.QProgressBar()
        fme_object.progress_bar.setMaximum(100)
        fme_object.status_bar.setMaximumWidth(fme_object.screen.width())
        fme_object.progress_bar.setMaximumWidth(fme_object.screen.width())
        hbox_status = QtGui.QHBoxLayout()
        hbox_status.addWidget(fme_object.status_bar)
        hbox_status.addWidget(fme_object.progress_bar)
#        vbox_main.addWidget(fme_object.main_tab_widget)
#        fme_object.main_tab_widget.setMaximumSize(fme_object.screen.width(), fme_object.screen.height() - 245)
#        vbox_main.addWidget(fme_object.main_tab_widget)
        vbox_main.addLayout(hbox_status)

        fme_object.window.setLayout(vbox_main)

        fme_object.status_bar.showMessage('Ready')
        fme_object.window.show()

    def select_projectDIRbutton(self):
        file_name_temp = QtGui.QFileDialog.getOpenFileNameAndFilter(fme_object.window, 'Open file', '/home',
                                                                    '*.csv')
        file_name = tuple(file_name_temp)[0]
        print('hallo')


class LayoutFuncs():
    def __init__(self):
        pass

    def table_setup(self, table, table_columns, sortingopt=True):
        table.setColumnCount(len(table_columns))
        table.setSortingEnabled(sortingopt)
        table.setHorizontalHeaderLabels(table_columns)
        table.resizeRowsToContents()
        table.resizeColumnsToContents()



