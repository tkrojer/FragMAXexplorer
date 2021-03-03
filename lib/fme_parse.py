import os, glob
import sys
import shutil
import pickle

from PyQt4 import QtGui, QtCore

sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'), 'lib'))

import fme_xtaltools
import fme_db

class read_process_dir(QtCore.QThread):

    def __init__(self, fragMaxDir, mainDir, dbFile):
        QtCore.QThread.__init__(self)
#        self.fragmaxDir = os.path.join(mainDir,'fragmax')
#        self.projectDir = os.path.join(mainDir,'fragmax','fme')
#        self.compoundDir = os.path.join(mainDir,'fragmax','fragments')

        self.fragmaxDir = fragMaxDir
        self.projectDir = mainDir
#        self.projectDir = os.path.join(mainDir,'fme')
#        self.compoundDir = os.path.join(mainDir,'fragments')

        self.db = fme_db.data_source(dbFile)

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

        if os.path.isdir(self.projectDir):
            self.parse_file_system()
        else:
            print('ERROR: please create project directory ' + self.projectDir)

    def parse_file_system(self):
        out = ''
        for s in sorted(glob.glob(os.path.join(self.fragmaxDir,'process','*','*','*','*'))):
            autoproc_pipeline = s.split('/')[11]
            if not autoproc_pipeline in self.pipelineDict:
                continue
            protein = s.split('/')[8]
            xtal = s.split('/')[9]
            run =  s.split('/')[10]

            out += xtal + '\n'

            db_dict = self.db.get_empty_plexDict()
            db_dict['DataProcessingProgram'] = autoproc_pipeline
            db_dict['ProteinName'] = protein
            db_dict['CrystalName'] = xtal
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), xtal)
            db_dict['DataCollectionRun'] = run
            mtzFile = None
            mtzDBdict = {}
            logFile = None
            db_dict['DataProcessingPathToMTZfile'] = ''
            for mtz in glob.glob(os.path.join(s,self.pipelineDict[autoproc_pipeline][0])):
                out += 'mtz: ' + mtz + '\n'
                mtzDict = fme_xtaltools.mtztools(mtz).read_mtz_header()
                db_dict.update(mtzDict)
                db_dict['DataProcessingPathToMTZfile'] = mtz
                break
            db_dict['DataProcessingPathToLogfile'] = ''
            for log in glob.glob(os.path.join(s,self.pipelineDict[autoproc_pipeline][1])):
                out += 'log: ' +log + '\n'
                if log.endswith('.log'):
                    logDict = fme_xtaltools.logtools(log).read_aimless()
                elif log.endswith('.json'):
                    logDict = fme_xtaltools.logtools(log).read_json()
                db_dict.update(logDict)
                db_dict['DataProcessingPathToLogfile'] = log
                break
            out = self.parse_refinement_results(db_dict, out)
        print('>>> writing logfile')
        os.chdir(self.projectDir)
        f = open('out.txt','w')
        f.write(out)
        f.close()

    def parse_refinement_results(self, db_dict, out):
        db_dict['RefinementPDB_latest'] = ''
        db_dict['RefinementMTZ_latest'] = ''
        for r in self.refi:
            db_dict['RefinementProgram'] = r
            for ref in glob.glob(os.path.join(self.fragmaxDir,'results',db_dict['DataCollectionRun'],
                                              db_dict['DataProcessingProgram'],r,'final.pdb')):
                db_dict['RefinementPDB_latest'] = ref
                out += 'ref: ' + ref + '\n'
                if os.path.isfile(ref.replace('.pdb','.mtz')):
                    db_dict['RefinementMTZ_latest'] = ref.replace('.pdb','.mtz')
                pdbDict = fme_xtaltools.pdbtools(ref).get_refinement_stats_dict()
                db_dict.update(pdbDict)
                db_dict['DataProcessingRefinementScore'] = self.calculate_score(db_dict)
                db_dict['DataProcessingScore'] = self.calculate_processing_score(db_dict)
                break
            if not 'DataProcessingScore' in db_dict:
                db_dict['DataProcessingScore'] = 0.0
            if not 'DataProcessingRefinementScore' in db_dict:
                db_dict['DataProcessingRefinementScore'] = 0.0
            self.update_db(db_dict)
            out = self.copy_files(db_dict, out)
        return out

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
        except TypeError:
            pass

        return score

    def calculate_processing_score(self,db_dict):
        score = 0.0
        try:
            score = (float(db_dict['DataProcessingUniqueReflectionsOverall']) *
                     float(db_dict['DataProcessingCompletenessOverall']) *
                     float(db_dict['DataProcessingIsigOverall']) *
                     float(db_dict['DataProcessingNsymop']) ) / ( float(db_dict['DataProcessingUnitCellVolume']) )
        except KeyError:
            pass
        except TypeError:
            pass

        return score


    def update_db(self,db_dict):
        self.db.update_db('plexTable',db_dict)

    def copy_files(self,db_dict, out):
        out += str(db_dict) + '\n'
        try:
#            if os.path.isfile(db_dict['DataProcessingPathToLogfile']) and os.path.isfile(db_dict['DataProcessingPathToMTZfile']) and os.path.isfile(db_dict['RefinementPDB_latest']) and os.path.isfile(db_dict['RefinementMTZ_latest']):
            out += 'made it to here' + '\n'
            os.chdir(os.path.join(self.projectDir))
            if not os.path.isdir(db_dict['CrystalName']):
                os.mkdir(db_dict['CrystalName'])
                out += 'here...' + '\n'
            os.chdir(db_dict['CrystalName'])
            if not os.path.isdir('auto-processing'):
                os.mkdir('auto-processing')
            os.chdir('auto-processing')
            if not os.path.isdir(db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram']):
                os.mkdir(db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'])
            os.chdir(db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'])
            print('copying ' + db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'])
            if os.path.isfile(db_dict['DataProcessingPathToLogfile']):
                shutil.copy(db_dict['DataProcessingPathToLogfile'], db_dict['CrystalName'] + '.log')
            if os.path.isfile(db_dict['DataProcessingPathToMTZfile']):
                shutil.copy(db_dict['DataProcessingPathToMTZfile'], db_dict['CrystalName'] + '.mtz')
            if os.path.isfile(db_dict['RefinementPDB_latest']):
                shutil.copy(db_dict['RefinementPDB_latest'], 'init.pdb')
            if os.path.isfile(db_dict['RefinementMTZ_latest']):
                shutil.copy(db_dict['RefinementMTZ_latest'], 'init.mtz')

            # compound
#            try:
#                compoundID = db_dict['CrystalName'].split('-')[1]
#                if not 'Apo' in compoundID:
#                    os.chdir(os.path.join(self.projectDir,db_dict['CrystalName']))
#                    if not os.path.isdir('ligand_files'):
#                        os.mkdir('ligand_files')
#                    os.chdir('ligand_files')
#                    if os.path.isfile(os.path.join(self.compoundDir,compoundID+'.cif')):
#                        if not os.path.isfile(compoundID+'.cif'):
#                            shutil.copy(os.path.join(self.compoundDir,compoundID+'.cif'),compoundID+'.cif')
#                    if os.path.isfile(os.path.join(self.compoundDir,compoundID+'.pdb')):
#                        if not os.path.isfile(compoundID+'.pdb'):
#                            shutil.copy(os.path.join(self.compoundDir,compoundID+'.pdb'),compoundID+'.pdb')
#
#            except IndexError:
#                pass

        except TypeError as e:
            out += 'ERROR' + '\n'
            out += str(e) + '\n'
            pass

        return out


class select_highest_score(QtCore.QThread):

    def __init__(self, projectDir, dbFile, selection):
        QtCore.QThread.__init__(self)
#        self.resultsDir = os.path.join(mainDir,'fragmax','results')
#        self.projectDir = os.path.join(mainDir,'fragmax','fme')

#        self.resultsDir = os.path.join(mainDir,'results')
        self.projectDir = projectDir

        self.db = fme_db.data_source(dbFile)

        self.selection = selection

    def run(self):

        # first get samples from DB
        self.allSamples = self.db.get_all_samples_in_plexTable_as_list()

        if self.selection == 'score':
            self.highest_score()
        elif self.selection == 'ap_dimple':
            self.ap_dimple()
        elif self.selection == 'ap':
            self.ap()

    def ap_dimple(self):
        for sample in self.allSamples:
            self.unset_symlinks(sample)
#            print(sample)
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), 'selecting ' + sample)
            # ['xtal-run-proc-refi']
            dbList = self.db.get_dicts_for_xtal_from_plexTable_as_list(sample)
            tmpList = []
            for item in dbList:
                if item['DataProcessingProgram'] == 'autoproc' and item['RefinementProgram'] == 'dimple':
                    db_dict = self.db.get_db_dict_for_sample_run_proc_refi_from_plexTable(sample,run,proc,refine)
                    self.update_db(db_dict)
                    self.set_symlinks(db_dict)

    def ap(self):
        for sample in self.allSamples:
            self.unset_symlinks(sample)
#            print(sample)
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), 'selecting ' + sample)
            # ['xtal-run-proc-refi']
            dbList = self.db.get_dicts_for_xtal_from_plexTable_as_list(sample)
            tmpList = []
            for item in dbList:
                print('>>>>>>>')
                if item['DataProcessingProgram'] == 'autoproc':
                    try:
                        tmpList.append([item['CrystalName']+';'+item['DataCollectionRun']+';'+
                                        item['DataProcessingProgram']+';'+item['RefinementProgram'],
                                       float(item['DataProcessingScore']) ] )
                    except ValueError:
#                    print item['CrystalName']+';'+item['DataCollectionRun']+';'+item['DataProcessingProgram']+';'+item['RefinementProgram']
                        pass

            try:
                print('>>>>>>>> scoring')
                print(str(tmpList))
                best = max(tmpList, key=lambda x: x[1])
                run = best[0].split(';')[1]
                proc = best[0].split(';')[2]
                refine = best[0].split(';')[3]
                print('result',best,run,proc,refine)
                db_dict = self.db.get_db_dict_for_sample_run_proc_refi_from_plexTable(sample,run,proc,refine)
                self.update_db(db_dict)
                self.set_symlinks(db_dict)
            except ValueError:
                pass


    def highest_score(self):

        for sample in self.allSamples:
            self.unset_symlinks(sample)
#            print(sample)
            self.emit(QtCore.SIGNAL('update_status_bar(QString)'), 'scoring ' + sample)
            # ['xtal-run-proc-refi']
            dbList = self.db.get_dicts_for_xtal_from_plexTable_as_list(sample)
            tmpList = []
            for item in dbList:
                print('>>>>>>>>>>>>>>')
#                print 'score',item['DataProcessingScore']
                try:
                    tmpList.append([item['CrystalName']+';'+item['DataCollectionRun']+';'+
                                    item['DataProcessingProgram']+';'+item['RefinementProgram'],
                                   float(item['DataProcessingRefinementScore']) ] )
                except ValueError:
#                    print item['CrystalName']+';'+item['DataCollectionRun']+';'+item['DataProcessingProgram']+';'+item['RefinementProgram']
                    pass
#            print tmpList
        # select combination with highest score
            try:
                print('>>>>>>>> scoring')
                print(str(tmpList))
                best = max(tmpList, key=lambda x: x[1])
                run = best[0].split(';')[1]
                proc = best[0].split(';')[2]
                refine = best[0].split(';')[3]
                db_dict = self.db.get_db_dict_for_sample_run_proc_refi_from_plexTable(sample,run,proc,refine)
                self.update_db(db_dict)
                self.set_symlinks(db_dict)
            except ValueError:
                pass

    def update_db(self,db_dict):
        self.db.update_db('mainTable',db_dict)

    def unset_symlinks(self, sample):
        try:
            os.chdir(os.path.join(self.projectDir,sample))
            print(os.path.join(self.projectDir,sample))
            if os.path.islink('refine.pdb'):
                os.unlink('refine.pdb')
            if os.path.islink('refine.mtz'):
                os.unlink('refine.mtz')
            if os.path.islink(sample + '.log'):
                os.unlink(sample + '.log')
            if os.path.islink(sample + '.mtz'):
                os.unlink(sample + '.mtz')
        except OSError:
            print('ERROR: directory does not exist ' + os.path.join(self.projectDir,sample))
            pass



    def set_symlinks(self,db_dict):
        try:
            os.chdir(os.path.join(self.projectDir,db_dict['CrystalName']))
            print('>>>>>> setting symlinks')
            print('>>>> XXX',os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],db_dict['CrystalName'] + '.mtz'))
            if os.path.isfile(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],'init.pdb')):
                os.symlink(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],'init.pdb'),'init.pdb')
            if os.path.isfile(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],'init.mtz')):
                os.symlink(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],'init.mtz'),'init.mtz')
            if os.path.isfile(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],db_dict['CrystalName'] + '.mtz')):
                os.symlink(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],db_dict['CrystalName'] + '.mtz'),db_dict['CrystalName'] + '.mtz')
            if os.path.isfile(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],db_dict['CrystalName'] + '.log')):
                os.symlink(os.path.join('auto-processing',db_dict['DataCollectionRun']+'_'+db_dict['DataProcessingProgram']+'_'+db_dict['RefinementProgram'],db_dict['CrystalName'] + '.log'),db_dict['CrystalName'] + '.log')
        except OSError:
            print('ERROR: directory does not exist ' + os.path.join(self.projectDir,db_dict['CrystalName']))
            pass



class start_COOT(QtCore.QThread):

    def __init__(self,projectDir):
        QtCore.QThread.__init__(self)
        self.settings = {}
#        self.settings['projectDir'] = os.path.join(projectDir,'fragmax','fme')
        self.settings['projectDir'] = os.path.join(projectDir,'fme')

    def run(self):
        cwd=os.getcwd()
        # coot at Diamond always or sometimes at least open in home directory, so then it won't find the .pkl file
        pickle.dump(self.settings,open(os.path.join(os.getenv('HOME'),'.fme_settings.pkl'),'wb'))
        os.system('cd {0!s}\ncoot --no-guano --no-state-script --script {1!s}'.format(os.getenv('HOME'), os.path.join(os.getenv('FragMAXexplorer_DIR'),'lib','fme_coot.py')))
