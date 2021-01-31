import os, sys
from PyQt4 import QtCore, QtGui

sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'lib'))
sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'gui_scripts'))

class setup():
    def __init__(self):
        pass

    def settings(self, fme_object):
        # set fme version
        fme_object.xce_version = 'v0.1'

        # general settings
        # set current directory and direct log to it
        fme_object.current_directory = os.getcwd()
        fme_object.xce_logfile = os.path.join(fme_object.current_directory, 'xce.log')
        fme_object.project_directory = None
        fme_object.process_directory = None
        fme_object.results_directory = None


    def tables(self, fme_object):

        fme_object.datasets_summary_table_columns = ['Sample ID',
                                                     'Resolution\nHigh',
                                                     'DataProcessing\nSpaceGroup',
                                                     'Refinement\nRfree',
                                                     'Rmerge\nLow'
                                                     ]

        # functions that use tables.data_collection_table_columns:
        #
        # - show_results_from_all_pipelines() - appears in populate_datasets_summary_table()

        fme_object.data_collection_table_columns = ['Sample ID',
                                                    'Visit',
                                                    'Run',
                                                    'Program',
                                                    'Resolution\nOverall',
                                                    'Resolution\nHigh',
                                                    'DataProcessing\nSpaceGroup',
                                                    'Mn<I/sig(I)>\nHigh',
                                                    'Rmerge\nLow',
                                                    'Completeness\nOverall',
                                                    'DataProcessing\nUnitCell',
                                                    'DataProcessing\nRfree'
                                                    'DataProcessing\nScore']

