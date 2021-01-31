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

        self.show_splash_screen()

#        self.db = fme_db.data_source('/Users/tobiaskrojer/Scripts/FragMAXexplorer/lib/testx.sqlite')

        self.exec_()

    def start_gui(self):

        setup().settings(self)
        setup().tables(self)
        self.window = QtGui.QWidget()
        self.window.setWindowTitle("FragMAXexplorer")
        self.screen = QtGui.QDesktopWidget().screenGeometry()
        LayoutObjects(self).main_layout(self)
#        self.db = fme_db.data_source('/home/tobkro/tmp/fme.sqlite')
#        self.populate_datasets_summary_table()

    def show_splash_screen(self):

        splash_pix = QtGui.QPixmap(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'img','fragmax_logo.png'))
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        splash.show()
        time.sleep(2)
        splash.close()


    def parse_process_directory(self):
        d = '/data/visitors/biomax/20200592/20200618/fragmax'
        self.work_thread = fme_parse.read_process_dir(d,'db','dir')
        self.connect(self.work_thread, QtCore.SIGNAL("update_progress_bar"), self.update_progress_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("update_status_bar(QString)"), self.update_status_bar)
        self.connect(self.work_thread, QtCore.SIGNAL("finished()"), self.thread_finished)
        self.connect(self.work_thread, QtCore.SIGNAL("datasource_menu_reload_samples"),
                         self.datasource_menu_reload_samples)
        self.work_thread.start()

    def score_datasets(self):
        d = '/data/visitors/biomax/20200592/20200618/fragmax'
        self.work_thread = fme_parse.select_highest_score(d,'db','dir')
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

#        # get information about all samples collected during the current visit
#        visit, beamline = XChemMain.getVisitAndBeamline(self.beamline_directory)
#        if self.read_agamemnon.isChecked():
#            visit = []
#            for v in glob.glob(os.path.join(self.beamline_directory[:self.beamline_directory.rfind('-') + 1] + '*')):
#                visit.append(v[v.rfind('/')+1:])

#        self.update_log.insert('reading information about collected crystals from database...')
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
                # in case data collection failed for whatever reason
                try:
                    print('>>>',str(db_dict[header[1]]))
                    cell_text.setText(str(db_dict[header[1]]))
                except KeyError:  # older pkl files may not have all the columns
                    cell_text.setText('n/a')
                    #                        else:
                    #                            if header[0].startswith('Resolution\n[Mn<I/sig(I)> = 1.5]'):
                    #                                cell_text.setText('999')
                    #                            elif header[0].startswith('DataProcessing\nRfree'):
                    #                                cell_text.setText('999')
                    #                            elif header[0].startswith('Rmerge\nLow'):
                    #                                cell_text.setText('999')
                    #                            else:
                    #                                cell_text.setText('')
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
