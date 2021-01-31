import os, glob
import sys

from PyQt4 import QtGui, QtCore

sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'lib'))

import fme_xtaltools
import fme_db

class read_process_dir(QtCore.QThread):

    def __init__(self,fragmaxDir,database,projectDir):
        QtCore.QThread.__init__(self)
        self.fragmaxDir =  fragmaxDir
        self.projectDir = projectDir
        self.db = fme_db.data_source('/home/tobkro/tmp/fme.sqlite')

        self.pipelineDict = {
            'autoproc':     ['truncate-unique.mtz', 'aimless.log'],
            'dials':        ['DataFiles/*_free.mtz', 'LogFiles/*_merging-statistics.json'],
            'edna':         ['*_noanom_truncate.mtz', '*_aimless_noanom.log']
#            'fastdp':       ['*_noanom_fast_dp.mtz', '*_noanom_aimless.log'],
#            'xdsapp':       ['*_data_F.mtz', 'log'],
#            'xdsxscale':    ['mtz', 'log']
        }

        self.refi = ['buster', 'dimple', 'fspipeline' ]


    def run(self):
        self.parse_file_system()

    def parse_file_system(self):
        for s in sorted(glob.glob(os.path.join(self.fragmaxDir,'process','*','*','*','*'))):
            autoproc_pipeline = s.split('/')[11]
            if not autoproc_pipeline in self.pipelineDict:
                continue
            protein = s.split('/')[8]
            xtal = s.split('/')[9]
            run =  s.split('/')[10]

            db_dict = {}
            db_dict['DataProcessingProgram'] = autoproc_pipeline
            db_dict['ProteinName'] = protein
            db_dict['CrystalName'] = xtal
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), xtal)
            db_dict['DataCollectionRun'] = run
            mtzFile = None
            mtzDBdict = {}
            logFile = None
            for mtz in glob.glob(os.path.join(s,self.pipelineDict[autoproc_pipeline][0])):
                mtzDict = fme_xtaltools.mtztools(mtz).read_mtz_header()
                db_dict.update(mtzDict)
                db_dict['DataProcessingPathToMTZfile'] = mtz
                break
            for log in glob.glob(os.path.join(s,self.pipelineDict[autoproc_pipeline][1])):
                if log.endswith('.log'):
                    logDict = fme_xtaltools.logtools(log).read_aimless()
                elif log.endswith('.json'):
                    logDict = fme_xtaltools.logtools(log).read_json()
                db_dict.update(logDict)
                db_dict['DataProcessingPathToLogfile'] = log
                break
            self.parse_refinement_results(db_dict)

    def parse_refinement_results(self,db_dict):
        for r in self.refi:
            db_dict['RefinementProgram'] = r
            for ref in glob.glob(os.path.join(self.fragmaxDir,'results',db_dict['DataCollectionRun'],
                                              db_dict['DataProcessingProgram'],r,'final.pdb')):
                db_dict['RefinementPDB_latest'] = ref
                if os.path.isfile(ref.replace('.pdb','.mtz')):
                    db_dict['RefinementMTZ_latest'] = ref.replace('.pdb','.mtz')
                pdbDict = fme_xtaltools.pdbtools(ref).get_refinement_stats_dict()
                db_dict.update(pdbDict)
                db_dict['DataProcessingScore'] = self.calculate_score(db_dict)
                break
            if not 'DataProcessingScore' in db_dict:
                db_dict['DataProcessingScore'] = 0.0
            self.update_db(db_dict)

    def calculate_score(self,db_dict):
        score = 0.0
        try:
            score = (float(db_dict['DataProcessingUniqueReflectionsOverall']) *
                     float(db_dict['DataProcessingCompletenessOverall']) *
                     float(db_dict['DataProcessingIsigOverall']) *
                     float(db_dict['DataProcessingNsymop']) ) / ( float(db_dict['DataProcessingUnitCellVolume']) *
                                                                  float(db_dict['RefinementRfree']))
        except KeyError:
            pass
        return score

    def update_db(self,db_dict):
        self.db.update_db('plexTable',db_dict)

    def copy_files(self):
        print('hallo')



class select_highest_score(QtCore.QThread):

    def __init__(self,resultsDir,database,projectDir):
        QtCore.QThread.__init__(self)
        self.resultsDir =  resultsDir
        self.projectDir = projectDir

        self.db = fme_db.data_source('/home/tobkro/tmp/fme.sqlite')


    def run(self):
        # first get samples from DB
        allSamples = self.db.get_all_samples_in_data_source_as_list()

        for sample in allSamples:
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), 'scoring ' + sample)
            # ['xtal-run-proc-refi']
            dbList = self.db.get_dicts_for_xtal_from_plexTable_as_list(sample)
            tmpList = []
            for item in dbList:
                tmpList.append([item['CrystalName']+';'+item['DataCollectionRun']+';'+
                                item['DataProcessingProgram']+';'+item['RefinementProgram'],
                               float(item['DataProcessingScore']) ] )

        # select combination with highest score
            print max(tmpList, key=lambda x: x[1])
        # update mainTable

        # set symlinks







#	x = xD[xD.rfind('/')+1:]
#	print x
#	for p in pipeline:
#		for l in glob.glob(os.path.join(xD,'*',p,'results','*noanom*log')):
#			if 'aimless' in l or 'autoPROC' in l:
#				print l
##			print l.split('/')


# /data/visitors/biomax/20200593/20200701/fragmax/process/Nsp5/Nsp5-JC039c1/Nsp5-JC039c1_1
#/data/visitors/biomax/20200593/20200701/fragmax/process/Nsp5/Nsp5-JC039c1/Nsp5-JC039c1_1/autoproc/aimless.log
#/data/visitors/biomax/20200593/20200701/fragmax/process/Nsp5/Nsp5-JC039c1/Nsp5-JC039c1_1/edna/ep_Nsp5-JC039c1_1_aimless_noanom.log


#            progress += progress_step
#            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), 'parsing auto-processing results for '+xtal)
#            self.emit(QtCore.SIGNAL('update_progress_bar'), progress)#
#        self.Logfile.insert('====== finished parsing beamline directory ======')
#        self.emit(QtCore.SIGNAL('read_pinIDs_from_gda_logs'))
#        self.emit(QtCore.SIGNAL("finished()"))



#/data/visitors/biomax/20200593/20200701/fragmax/results/Nsp5-JC001a3_1/autoproc/buster/final.pdb
#/data/visitors/biomax/20200593/20200701/fragmax/results/Nsp5-JC001a3_1/autoproc/dimple/final.pdb
