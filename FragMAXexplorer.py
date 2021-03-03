import os, sys
from PyQt4 import QtGui, QtCore
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
import time

sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'lib'))
sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'gui_scripts'))

from settings_preferences import *
from stylesheet import set_stylesheet
from layout import *

import fme_db
import fme_parse

class FragMAXexplorer(QtGui.QApplication):
    def __init__(self, args):

        QtGui.QApplication.__init__(self, args)
        self.start_gui()

        set_stylesheet(self)

#        self.show_splash_screen()

#        self.projectDir = '/data/visitors/biomax/20200593/20210223'
#        print('hallooooooo')
#        self.dbFile = '/home/tobkro/tmp/fme.sqlite'
#        self.db = fme_db.data_source('/home/tobkro/tmp/fme.sqlite')
#        self.db = fme_db.data_source('/Users/tobiaskrojer/tmp/fme_update_4.sqlite')
        self.exec_()

    def start_gui(self):

        try:
            self.fragMaxDir = sys.argv[1]
            self.fmeDir = sys.argv[2]
        except IndexError:
            print('ERROR: please specify fragmax & project directory')
            quit()

#        self.projectDir = '/data/visitors/biomax/20200593/20210223'
#        self.dbFile = os.path.join(self.projectDir,'fragmax','db','nsp10.sqlite')
#        self.dbFile = '/Users/tobiaskrojer/tmp/tmp.sqlite'
        self.projectDir = os.path.join(self.fmeDir, 'refine')
        print('>>>',self.projectDir)
        if not os.path.isdir(self.fmeDir):
            os.mkdir(self.fmeDir)
        if not os.path.isdir(self.projectDir):
            os.mkdir(self.projectDir)
        if not os.path.isdir(os.path.join(self.fmeDir, 'db')):
            os.mkdir(os.path.join(self.fmeDir, 'db'))
        self.dbFile = os.path.join(self.fmeDir,'db','fme.sqlite')
        if not os.path.isfile(self.dbFile):
            self.db = fme_db.data_source(self.dbFile).create_empty_data_source_file()
            print('ERROR: should be here ' + self.dbFile)
            quit()

        self.db = fme_db.data_source(self.dbFile)


        setup().settings(self)
        setup().tables(self)
        self.window = QtGui.QWidget()
        self.window.setWindowTitle("FragMAXexplorer")
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        LayoutObjects(self).main_layout(self)
#        self.db = fme_db.data_source('/home/tobkro/tmp/fme.sqlite')
#        self.populate_datasets_summary_table()


    def start_coot(self):
        self.work_thread = fme_parse.start_COOT(self.projectDir)
        self.connect(self.work_thread, QtCore.SIGNAL("finished()"), self.thread_finished)
        self.work_thread.start()



    def show_splash_screen(self):

        splash_pix = QtGui.QPixmap(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'img','fragmax_logo.png'))
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        splash.show()
        time.sleep(2)
        splash.close()


    def parse_process_directory(self):
        self.work_thread = fme_parse.read_process_dir(self.fragMaxDir, self.projectDir, self.dbFile)
        self.connect(self.work_thread, QtCore.SIGNAL("update_progress_bar"), self.update_progress_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("update_status_bar(QString)"), self.update_status_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("finished()"), self.thread_finished)
        self.connect(self.work_thread, QtCore.SIGNAL("datasource_menu_reload_samples"),
                         self.datasource_menu_reload_samples)
        self.work_thread.start()

    def score_datasets(self):
        self.select_datasets('score')

    def select_ap_dimple(self):
        self.select_datasets('ap_dimple')

    def select_ap(self):
        self.select_datasets('ap')

    def select_datasets(self, selection):
        self.work_thread = fme_parse.select_highest_score(self.projectDir, self.dbFile, selection)
        self.connect(self.work_thread, QtCore.SIGNAL("update_progress_bar"), self.update_progress_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("update_status_bar(QString)"), self.update_status_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("finished()"), self.thread_finished)
        self.connect(self.work_thread, QtCore.SIGNAL("datasource_menu_reload_samples"),
                         self.datasource_menu_reload_samples)
        self.work_thread.start()


    def datasource_menu_reload_samples(self):
        print('hallo')

    def populate_datasets_summary_table(self):
        self.status_bar.showMessage(
            'Building summary table for data processing results; be patient this may take a while')
        collectedXtalsDict = self.db.xtals_in_db()

        # instead of using dictionaries, query table of which crystals are in table
        samples_in_table = self.get_sample_list_from_table(self.datasets_summary_table)
        for xtal in sorted(collectedXtalsDict):
            if xtal not in samples_in_table:
                row = self.datasets_summary_table.rowCount()
                self.datasets_summary_table.insertRow(row)
            else:
                row = self.get_row_of_sample_in_table(self.datasets_summary_table,xtal)
            db_dict = collectedXtalsDict[xtal]
            self.update_row_in_table(xtal, row, db_dict, self.datasets_summary_table,
                                     self.datasets_summary_table_columns)
        self.datasets_summary_table.resizeRowsToContents()
        self.datasets_summary_table.resizeColumnsToContents()
        self.status_bar.showMessage('updating Overview table')
        self.status_bar.showMessage('idle')

    def get_sample_list_from_table(self,table):
        sampleList = []
        allRows = table.rowCount()
        for row in xrange(0, allRows):
            sample_id = str(table.item(row, 0).text())
            sampleList.append(sample_id)
        return sorted(sampleList)

    def get_row_of_sample_in_table(self,table,xtal):
        allRows = table.rowCount()
        sampleRow = allRows
        for n,row in enumerate(xrange(0, allRows)):
            sample_id = str(table.item(row, 0).text())
            if sample_id == xtal:
                sampleRow = n
                break
        return sampleRow


    def update_row_in_table(self,sample,row,db_dict,table,columns_to_show):
        xtal = str(sample)
        column_name = self.db.translate_xce_column_list_to_sqlite(columns_to_show)
        print '>>',column_name
        print columns_to_show
        for column, header in enumerate(column_name):

            if header[0] == 'Sample ID':
                cell_text = QtGui.QTableWidgetItem()
                cell_text.setText(str(xtal))
                cell_text.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
                table.setItem(row, column, cell_text)

            else:
                cell_text = QtGui.QTableWidgetItem()
                try:
                    print('>>>',str(db_dict[header[1]]))
                    cell_text.setText(str(db_dict[header[1]]))
                except KeyError:  # older pkl files may not have all the columns
                    cell_text.setText('n/a')
                cell_text.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
                table.setItem(row, column, cell_text)

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)

    def update_status_bar(self, message):
        self.status_bar.showMessage(message)

    def thread_finished(self):
        self.explorer_active = 0
        self.update_progress_bar(0)
        self.update_status_bar('idle')



    def show_results_from_all_pipelines(self):
        selected_row=self.get_selected_row(self.datasets_summary_table)
        xtal = self.datasets_summary_table.item(selected_row, 0).text()
        # get details of currently selected autoprocessing result
        selectedResultDict = self.db.get_db_dict_for_sample(xtal)

        dbList=self.db.all_autoprocessing_results_for_xtal_as_dict(xtal)

        self.make_data_collection_table()
        self.msgBox = QtGui.QMessageBox()   # needs to be created here, otherwise the cellClicked function
                                            # will reference it before it exists
        for db_dict in dbList:
            if str(db_dict['DataProcessingSpaceGroup']).lower() == 'null' or str(db_dict['DataProcessingSpaceGroup']).lower() == 'none':
                continue
            row = self.data_collection_table.rowCount()
            self.data_collection_table.insertRow(row)
            self.update_row_in_table(xtal, row, db_dict, self.data_collection_table, self.data_collection_table_columns)
#            if selectedResultDict['DataCollectionVisit'] == db_dict['DataCollectionVisit'] \
#                and selectedResultDict['DataCollectionRun'] == db_dict['DataCollectionRun'] \
#                and selectedResultDict['DataProcessingProgram'] == db_dict['DataProcessingProgram']:
#                self.current_row = row
#                self.data_collection_table.selectRow(row)
        self.data_collection_table.cellClicked.connect(self.select_different_autoprocessing_result)
        self.data_collection_table_popup()

    def get_selected_row(self,table):
        indexes = table.selectionModel().selectedRows()
        for index in sorted(indexes):
            selected_row = index.row()
        return selected_row

    def make_data_collection_table(self):
        # this creates a new table widget every time
        # more elegant would be to delete or reset an existing widget...
        self.data_collection_table = QtGui.QTableWidget()
        self.data_collection_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_collection_table.setColumnCount(len(self.data_collection_table_columns))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.data_collection_table.setFont(font)
        self.data_collection_table.setHorizontalHeaderLabels(self.data_collection_table_columns)
        self.data_collection_table.horizontalHeader().setFont(font)
        self.data_collection_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def select_different_autoprocessing_result(self):
        selected_row=self.get_selected_row(self.data_collection_table)
        if selected_row != self.current_row:
            xtal =     self.data_collection_table.item(selected_row, 0).text()
            visit =    self.data_collection_table.item(selected_row, 1).text()
            run =      self.data_collection_table.item(selected_row, 2).text()
            autoproc = self.data_collection_table.item(selected_row, 3).text()
            # get db_dict from collectionTable for visit, run, autoproc
            dbDict = self.db.get_db_dict_for_visit_run_autoproc(xtal,visit,run,autoproc)
            dbDict['DataProcessingAutoAssigned'] = 'False'
            self.update_log.insert('%s: changing selected autoprocessing result to %s %s %s' %(xtal,visit,run,autoproc))
            # xtal is QString -> str(xtal)
            XChemMain.linkAutoProcessingResult(str(xtal), dbDict, self.initial_model_directory,self.xce_logfile)
            self.update_log.insert('%s: updating row in Datasets table' %xtal)
            self.db.update_data_source(str(xtal),dbDict)
            self.update_log.insert('%s: getting updated information from DB mainTable' %xtal)
            dbDict = self.db.get_db_dict_for_sample(xtal)
            row = self.get_row_of_sample_in_table(self.datasets_summary_table,xtal)
            self.update_row_in_table(xtal, row, dbDict, self.datasets_summary_table,
                                     self.datasets_summary_table_columns)
        else:
            print 'nothing to change'
        self.msgBox.done(1)

    def data_collection_table_popup(self):
#        self.msgBox = QtGui.QMessageBox()
        msgBoxLayout = self.msgBox.layout()
        qWid = QtGui.QWidget()
        qWid.setFixedWidth(3000)
        qWid.setFixedHeight(500)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.data_collection_table)
        qWid.setLayout(vbox)
#        msgBoxLayout.addLayout(vbox, 0, 0)
        msgBoxLayout.addWidget(qWid)
        self.msgBox.addButton(QtGui.QPushButton('Cancel'), QtGui.QMessageBox.RejectRole)
        self.msgBox.resize(1000,200)
        self.msgBox.exec_();



#    def populate_datasets_summary_table(self):
#        for xtal in sorted(collectedXtalsDict):
#            if xtal not in samples_in_table:
#                row = self.datasets_summary_table.rowCount()
#                self.datasets_summary_table.insertRow(row)
#            else:
#                row = self.get_row_of_sample_in_table(self.datasets_summary_table,xtal)
#            db_dict = collectedXtalsDict[xtal]
#            self.update_row_in_table(xtal, row, db_dict, self.datasets_summary_table,
#                                     self.datasets_summary_table_columns)
#        self.datasets_summary_table.resizeRowsToContents()
#        self.datasets_summary_table.resizeColumnsToContents()



if __name__ == "__main__":
    app = FragMAXexplorer(sys.argv[1:])
