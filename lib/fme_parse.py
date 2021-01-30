import os, glob

from PyQt4 import QtGui, QtCore

class read_process_dir(QtCore.QThread):

    def __init__(self,processDir,database,projectDir):
        QtCore.QThread.__init__(self)
        self.processeDir =  processDir
        self.projectDir = projectDir

        self.pipelineDict = {
            'autoproc':     ['mtz', 'log'],
            'dials':        ['mtz', 'log'],
            'edna':         ['*_noanom_truncate.mtz', '*_aimless_noanom.log'],
            'fastdp':       ['mtz', 'log'],
            'xdsapp':       ['mtz', 'log'],
            'xdsxscale':    ['mtz', 'log']
        }


    def run(self):
        self.parse_file_system()

    def parse_file_system(self):
        for s in sorted(glob.glob(os.path.join(self.processeDir,'*','*','*','*'))):
            print(s)
            protein = s.split('/')[8]
            xtal = s.split('/')[9]
            run =  s.split('/')[10]
            for p in self.pipelineDict:
                db_dict = {}
                db_dict['DataProcessingProgram'] = p
                db_dict['ProteinName'] = protein
                db_dict['CrystalName'] = xtal
                db_dict['DataCollectionRun'] = run
                mtzFile = None
                mtzDBdict = {}
                logFile = None
                print(p)
                print os.path.join(s,p,self.pipelineDict[p][0])
                quit()
                for mtz in glob.glob(os.path.join(s,p,self.pipelineDict[p][0])):
                    db = fme_xtaltools.mtztools(mtz).get_info()
                    mtzFile = mtz
                    print mtzFile, db
                    break
                for log in glob.glob(os.path.join(s,p,self.pipelineDict[p][1])):
                    db = fme_xtaltools.logtools(log).get_info()
                    logFile = log
                    break

    def update_db(self):
        print('hallo')

    def copy_files(self):
        print('hallo')



class read_results_dir(QtCore.QThread):

    def __init__(self,resultsDir,database,projectDir):
        QtCore.QThread.__init__(self)
        self.resultsDir =  resultsDir
        self.projectDir = projectDir

        self.proc = ['autoproc', 'dials', 'edna', 'fastdp', 'xdsapp', 'xdsxscale']
        self.refi = ['buster', 'dimple' ]


    def run(self):
        # first get samples from DB

#        self.parse_file_system()
        print('hallo')







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
