import sqlite3
import os,sys,glob
import csv
from datetime import datetime
import getpass

#sys.path.append(os.getenv('FragMAXexplorer_DIR')+'/lib')


class data_source:

    def __init__(self,data_source_file):

        self.data_source_file=data_source_file

        self.column_list=[
            # SQLite column name                    XCE column name                             SQLite type             display in overview tab
            # from Lab36
            ['ID',                          'ID',                   'INTEGER PRIMARY KEY',  0],
            ['CrystalName',                 'Sample ID',            'TEXT',                 0],
            ['ProteinName',                 'ProteinName',          'TEXT',                 1],
            ['ProjectDirectory',            'ProjectDirectory',     'TEXT',                 0],
            ['CompoundCode',                'Compound ID',          'TEXT',                 1],
            ['CompoundSMILES',              'Smiles',               'TEXT',                 1],
            ['DataCollectionRun',           'Run',                  'TEXT',                 0],
            ['DataProcessingProgram',       'Program',              'TEXT',                 1],
            ['RefinementProgram',           'Refinement\nProgram',  'TEXT',                 1],
            ['LastUpdated',                 'LastUpdated',          'TEXT',                 0],
            ['LastUpdated_by',              'LastUpdated_by',       'TEXT',                 0]
        ]

        self.data_collection_columns = [
            ['ID',                                      'ID',                                   'INTEGER PRIMARY KEY'],
            ['CrystalName',                             'Sample ID',                            'TEXT',                 0],
            ['DataCollectionRun',                       'Run',                                  'TEXT',                 0],
            ['DataCollectionWavelength',                'Wavelength',                           'TEXT',                 0],
            ['DataProcessingProgram',                   'Program',                              'TEXT',                 1],
            ['DataProcessingPointGroup',                'DataProcessing\nPointGroup',           'TEXT',                 1],
            ['DataProcessingSpaceGroup',                'DataProcessing\nSpaceGroup',           'TEXT',                 1],
            ['DataProcessingNsymop',                    'DataProcessing\nN(symop)',             'TEXT',                 1],
            ['DataProcessingUnitCell',                  'DataProcessing\nUnitCell',             'TEXT',                 0],
            ['DataProcessingUnitCellVolume',            'DataProcessing\nUnit Cell Volume',     'TEXT',                 0],
            ['DataProcessingLattice',                   'DataProcessing\nLattice',              'TEXT',                 0],
            ['DataProcessingResolutionLow',             'Resolution\nLow',                      'TEXT',                 0],
            ['DataProcessingResolutionLowInnerShell',   'Resolution\nLow (Inner Shell)',        'TEXT',                 0],
            ['DataProcessingResolutionHigh',            'Resolution\nHigh',                     'TEXT',                 1],
            ['DataProcessingResolutionHighOuterShell',  'Resolution\nHigh (Outer Shell)',       'TEXT',                 0],
            ['DataProcessingRmergeOverall',             'Rmerge\nOverall',                      'TEXT',                 1],
            ['DataProcessingRmergeLow',                 'Rmerge\nLow',                          'TEXT',                 1],
            ['DataProcessingRmergeHigh',                'Rmerge\nHigh',                         'TEXT',                 1],
            ['DataProcessingIsigOverall',               'Mn<I/sig(I)>\nOverall',                'TEXT',                 1],
            ['DataProcessingIsigLow',                   'Mn<I/sig(I)>\nLow',                    'TEXT',                 1],
            ['DataProcessingIsigHigh',                  'Mn<I/sig(I)>\nHigh',                   'TEXT',                 1],
            ['DataProcessingCompletenessOverall',       'Completeness\nOverall',                'TEXT',                 1],
            ['DataProcessingCompletenessLow',           'Completeness\nLow',                    'TEXT',                 1],
            ['DataProcessingCompletenessHigh',          'Completeness\nHigh',                   'TEXT',                 1],
            ['DataProcessingMultiplicityOverall',       'Multiplicity\nOverall',                'TEXT',                 1],
            ['DataProcessingMultiplicityLow',           'Multiplicity\nLow',                    'TEXT',                 1],
            ['DataProcessingMultiplicityHigh',          'Multiplicity\nHigh',                   'TEXT',                 1],
            ['DataProcessingCChalfOverall',             'CC(1/2)\nOverall',                     'TEXT',                 1],
            ['DataProcessingCChalfLow',                 'CC(1/2)\nLow',                         'TEXT',                 1],
            ['DataProcessingCChalfHigh',                'CC(1/2)\nHigh',                        'TEXT',                 1],
            ['DataProcessingPathToLogfile',             'DataProcessingPathToLogfile',          'TEXT',                 1],
            ['DataProcessingPathToMTZfile',             'DataProcessingPathToMTZfile',          'TEXT',                 1],
            ['DataProcessingUniqueReflectionsOverall',  'Unique Reflections\nOverall',          'TEXT',                 1],
            ['DataProcessingUniqueReflectionsLow',      'Unique Reflections\nlow',              'TEXT',                 1],
            ['DataProcessingUniqueReflectionsHigh',     'Unique Reflections\nhigh',             'TEXT',                 1],
            ['DataProcessingScore',                     'DataProcessing\nScore',                'TEXT',                 1],
            ['DataProcessingStatus',                    'DataProcessing\nStatus',               'TEXT',                 1],
            ['RefinementProgram',                       'Refinement\nProgram',                  'TEXT',                 1],
            ['RefinementOutcome',                       'Refinement\nOutcome',                  'TEXT',                 1],
            ['RefinementResolutionLow',                 'Refinement\nResolution',               'TEXT',                 1],
            ['RefinementResolutionHigh',                'Refinement\nResolution',               'TEXT',                 1],
            ['RefinementRcryst',                        'Refinement\nRcryst',                   'TEXT',                 1],
            ['RefinementRfree',                         'Refinement\nRfree',                    'TEXT',                 1],
            ['RefinementSpaceGroup',                    'Refinement\nSpace Group',              'TEXT',                 1],
            ['RefinementLigandCC',                      'Ligand CC',                            'TEXT',                 0],
            ['RefinementRmsdBonds',                     'RefinementRmsdBonds',                  'TEXT',                 1],
            ['RefinementRmsdAngles',                    'RefinementRmsdAngles',                 'TEXT',                 1],
            ['RefinementMTZfree',                       'RefinementMTZfree',                    'TEXT',                 1],
            ['RefinementCIF',                           'RefinementCIF',                        'TEXT',                 1],
            ['RefinementCIFStatus',                     'Compound\nStatus',                     'TEXT',                 1],
            ['RefinementCIFprogram',                    'RefinementCIFprogram',                 'TEXT',                 1],
            ['RefinementPDB_latest',                    'RefinementPDB_latest',                 'TEXT',                 1],
            ['RefinementMTZ_latest',                    'RefinementMTZ_latest',                 'TEXT',                 1],
            ['RefinementMMCIFmodel_latest',             'RefinementMMCIFmodel_latest',          'TEXT',                 1],
            ['RefinementMMCIFreflections_latest',       'RefinementMMCIFreflections_latest',    'TEXT',                 1],
            ['LastUpdated',                             'LastUpdated',                          'TEXT',                 0],
            ['LastUpdated_by',                          'LastUpdated_by',                       'TEXT',                 0]

        ]

        self.tableDict = {  'mainTable':    self.column_list,
                            'plexTable':    self.data_collection_columns    }

        self.create_missing_columns()


    def create_empty_data_source_file(self):
        connect=sqlite3.connect(self.data_source_file)
        with connect:
            cursor = connect.cursor()
            for table in self.tableDict:
                print table
                cursor.execute("CREATE TABLE "+table+"("+self.tableDict[table][0][0]+' '+self.tableDict[table][0][2]+")")
                for i in range(1,len(self.tableDict[table])):
                    print self.tableDict[table][i][0]
                    cursor.execute("alter table "+table+" add column '"+self.tableDict[table][i][0]+"' '"+self.tableDict[table][i][2]+"'")



#                cursor.execute("CREATE TABLE "+table+"("+self.column_list[0][0]+' '+self.column_list[0][2]+")")
#                for i in range(1,len(self.column_list)):
#                    print self.column_list[i][0]
#                    cursor.execute("alter table "+table+" add column '"+self.column_list[i][0]+"' '"+self.column_list[i][2]+"'")
        connect.commit()

    def create_missing_columns(self):
        connect=sqlite3.connect(self.data_source_file)
        connect.row_factory = sqlite3.Row
        cursor = connect.cursor()
        for table in self.tableDict:
            cursor.execute("create table if not exists "+table+" (ID INTEGER);")
            existing_columns = []
            cursor.execute("SELECT * FROM "+table)
            for column in cursor.description:
                existing_columns.append(column[0])
            for column in self.tableDict[table]:
                if column[0] not in existing_columns:
                    cursor.execute("alter table " + table + " add column '" + column[0] + "' '" + column[2] + "'")
                    connect.commit()


    def update_db(self, table, data_dict):
        data_dict['LastUpdated'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by'] = getpass.getuser()
        connect = sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()

        sql = (
            'select * from {0!s}'.format(table) +
            ' where'
            ' CrystalName = "{0!s}" and '.format(data_dict['CrystalName']) +
            ' DataCollectionRun = "{0!s}" and '.format(data_dict['DataCollectionRun']) +
            ' DataProcessingProgram = "{0!s}" and '.format(data_dict['DataProcessingProgram']) +
            ' RefinementProgram = "{0!s}" '.format(data_dict['RefinementProgram'])
        )

        cursor.execute(sql)

        query = cursor.fetchall()

        columns_in_table = []
        for c in self.tableDict[table]:
            columns_in_table.append(c[0])

        if not query:
            value_string=''
            column_string=''
            for key in data_dict:
                print key,data_dict[key]
                if not key in columns_in_table:
                    print 'oirfurughru'
                    continue
                value = data_dict[key]
                value_string += "'" + str(value) + "'" + ','
                column_string += key + ','
            print("INSERT INTO "+table+" (" + column_string[:-1] + ") VALUES (" + value_string[:-1] + ");")
            cursor.execute("INSERT INTO "+table+" (" + column_string[:-1] + ") VALUES (" + value_string[:-1] + ");")
        else:
            update_string=''
            for key in data_dict:
                if not key in columns_in_table:
                    continue
                value = data_dict[key]
                update_string += str(key) + '=' + "'" + str(value) + "',"
            cursor.execute(
                "UPDATE " + table +
                " SET " + update_string[:-1] +
                ' WHERE '
                ' CrystalName = "{0!s}" and '.format(data_dict['CrystalName']) +
                ' DataCollectionRun = "{0!s}" and '.format(data_dict['DataCollectionRun']) +
                ' DataProcessingProgram = "{0!s}" and '.format(data_dict['DataProcessingProgram']) +
                ' RefinementProgram = "{0!s}" ;'.format(data_dict['RefinementProgram'])
            )
        connect.commit()



    def xtals_in_db(self):
        collectedXtals = self.collected_xtals_during_visit()
        xtalDict = {}
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
#        cursor = connect.cursor()
        for xtal in sorted(collectedXtals):
#            db_dict = self.get_db_dict_for_sample(xtal)
            db_dict = self.get_db_dict_for_sample_from_plexTable(xtal)
            xtalDict[xtal] = db_dict
        return xtalDict

    def collected_xtals_during_visit(self):
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("select CrystalName from mainTable")
        collectedXtals=[]
        samples = cursor.fetchall()
        for sample in samples:
            if str(sample[0]) not in collectedXtals:
                collectedXtals.append(str(sample[0]))
        return collectedXtals

    def get_run_proc_refi_from_mainTable(self,sampleID):
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("select DataCollectionRun,DataProcessingProgram,RefinementProgram from mainTable where CrystalName='{0!s}';".format(sampleID))
        data = cursor.fetchall()
        outList = []
        for n,item in enumerate(data[0]):
            outList.append(item)
        return outList[0],outList[1],outList[2]

    def get_db_dict_for_sample_from_plexTable(self,sampleID):
        run,proc,refine = self.get_run_proc_refi_from_mainTable(sampleID)
        db_dict={}
        header=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
#        cursor.execute("select * from plexTable where CrystalName='{0!s}';".format(sampleID))

        sql = (
            "select * from plexTable where CrystalName='{0!s}' ".format(sampleID) +
            " and DataCollectionRun='{0!s}'".format(run) +
            " and DataProcessingProgram='{0!s}'".format(proc) +
            " and RefinementProgram='{0!s}'".format(refine)
        )

        cursor.execute(sql)
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        try:
            for n,item in enumerate(data[0]):
                db_dict[header[n]]=str(item)
        except IndexError:
            pass
        return db_dict


    def get_db_dict_for_sample(self,sampleID):
        db_dict={}
        header=[]
#        data=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("select * from mainTable where CrystalName='{0!s}';".format(sampleID))
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        for n,item in enumerate(data[0]):
            db_dict[header[n]]=str(item)
        return db_dict



    def translate_xce_column_list_to_sqlite(self,column_list):
        out_list=[]
        for item in column_list:
            found = False
            for entry in self.column_list:
                if entry[1]==item:
                    out_list.append([item,entry[0]])
                    found = True
                    break
            if not found:
                for entry in self.data_collection_columns:
                    if entry[1]==item:
                        out_list.append([item,entry[0]])
                        found = True
                        break
        return out_list


    def get_all_samples_in_data_source_as_list(self):
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("SELECT CrystalName FROM mainTable")
        existing_samples_in_db=[]
        samples = cursor.fetchall()
        for sample in samples:
            existing_samples_in_db.append(str(sample[0]))
        return existing_samples_in_db

    def get_all_samples_in_plexTable_as_list(self):
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("SELECT DISTINCT CrystalName FROM plexTable order by CrystalName")
        existing_samples_in_db=[]
        samples = cursor.fetchall()
        for sample in samples:
            existing_samples_in_db.append(str(sample[0]))
        return existing_samples_in_db



    def get_dicts_for_xtal_from_plexTable_as_list(self,xtal):
        dbList = []
        header=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute('select * from plexTable where CrystalName = "{0!s}"'.format(xtal))
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        for result in data:
            db_dict = {}
            for n,item in enumerate(result):
                db_dict[header[n]]=str(item)
            dbList.append(db_dict)
        return dbList


    def get_db_dict_for_sample_run_proc_refi_from_plexTable(self,sampleID,run,proc,refine):
        db_dict={}
        header=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
#        cursor.execute("select * from plexTable where CrystalName='{0!s}';".format(sampleID))

        sql = (
            "select * from plexTable where CrystalName='{0!s}' ".format(sampleID) +
            " and DataCollectionRun='{0!s}'".format(run) +
            " and DataProcessingProgram='{0!s}'".format(proc) +
            " and RefinementProgram='{0!s}'".format(refine)
        )

        cursor.execute(sql)
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        try:
            for n,item in enumerate(data[0]):
                db_dict[header[n]]=str(item)
        except IndexError:
            pass
        return db_dict

    def all_autoprocessing_results_for_xtal_as_dict(self,xtal):
        dbList = []
        header=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute("select * from plexTable where CrystalName='{0!s}';".format(xtal))
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        for result in data:
            db_dict = {}
            for n,item in enumerate(result):
                db_dict[header[n]]=str(item)
            dbList.append(db_dict)
        return dbList


    def get_empty_plexDict(self):
        db_dict = {}
        for item in self.data_collection_columns:
            if not item[0] == 'ID':
                db_dict[item[0]] = None
        return db_dict



















    def columns_not_to_display(self):
        do_not_display = []
        for column in self.column_list:
            if column[3]==0:
                do_not_display.append(column[1])
        return do_not_display
        
    def get_empty_db_dict(self):
        db_dict={}
        for column in self.column_list:
            if column[0] != 'ID':
                db_dict[column[0]]=''
        return db_dict


    def execute_statement(self,cmd):
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        cursor.execute(cmd)
        output=cursor.fetchall()
        connect.commit()
        return output


    def get_deposit_dict_for_sample(self,sampleID):
        db_dict={}
        header=[]
        data=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
#        if sampleID == 'ground-state':      # just select first row in depositTable
#            cursor.execute("SELECT * FROM depositTable ORDER BY ROWID ASC LIMIT 1;")
#        else:
#            cursor.execute("select * from depositTable where CrystalName='{0!s}';".format(sampleID))
        cursor.execute("select * from depositTable where CrystalName='{0!s}';".format(sampleID))
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        try:
            for n,item in enumerate(data[0]):
                db_dict[header[n]]=str(item)
        except IndexError:
            pass
        return db_dict

    def update_data_source(self,sampleID,data_dict):
        print 'here'
        data_dict['LastUpdated']=str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by']=getpass.getuser()

        # need to do this since some older sqlite files contain a columnn called
        # DataProcessingResolutionHigh1.5sigma
        # and this does not go down well with the SQLite statement below
        removeKey=''
        for key in data_dict:
            if '.5' in key:
                removeKey=key
                break
        if removeKey != '':
            del data_dict[removeKey]

        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        update_string=''
        for key in data_dict:
            value=data_dict[key]
            if key=='ID' or key=='CrystalName':
                continue
            if not str(value).replace(' ','')=='':  # ignore empty fields
                update_string+=str(key)+'='+"'"+str(value)+"'"+','
            else:
                update_string+=str(key)+' = null,'
        if update_string != '':
#            print "UPDATE mainTable SET "+update_string[:-1]+" WHERE CrystalName="+"'"+sampleID+"'"
            cursor.execute("UPDATE mainTable SET "+update_string[:-1]+" WHERE CrystalName="+"'"+sampleID+"'")
            connect.commit()

    def update_specified_table(self,sampleID,data_dict,table):
        data_dict['LastUpdated']=str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by']=getpass.getuser()
        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        update_string=''
        for key in data_dict:
            value=data_dict[key]
            if key=='ID' or key=='CrystalName':
                continue
            if not str(value).replace(' ','')=='':  # ignore empty fields
                update_string+=str(key)+'='+"'"+str(value)+"'"+','
        if update_string != '':
            cursor.execute("UPDATE "+table+" SET "+update_string[:-1]+" WHERE CrystalName="+"'"+sampleID+"'")
            connect.commit()

    def update_insert_data_source(self,sampleID,data_dict):
        data_dict['LastUpdated']=str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by']=getpass.getuser()
        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        cursor.execute('Select CrystalName FROM mainTable')
        available_columns=[]
        cursor.execute("SELECT * FROM mainTable")
        for column in cursor.description:           # only update existing columns in data source
            available_columns.append(column[0])
        if self.check_if_sample_exists_in_data_source(sampleID):
            for key in data_dict:
                value=data_dict[key]
                if key=='ID' or key=='CrystalName':
                    continue
                if not str(value).replace(' ','')=='':  # ignore empty fields
                    update_string=str(key)+'='+"'"+str(value)+"'"
                    cursor.execute("UPDATE mainTable SET "+update_string+" WHERE CrystalName="+"'"+sampleID+"';")
        else:
            column_string='CrystalName'+','
            value_string="'"+sampleID+"'"+','
            for key in data_dict:
                value=data_dict[key]
                if key=='ID':
                    continue
                if key not in available_columns:
                    continue
                if not str(value).replace(' ','')=='':  # ignore if nothing in csv field
                    value_string+="'"+str(value)+"'"+','
                    column_string+=key+','
            cursor.execute("INSERT INTO mainTable ("+column_string[:-1]+") VALUES ("+value_string[:-1]+");")
        connect.commit()



    def update_insert_any_table(self,table,data_dict,condition_dict):
        data_dict['LastUpdated'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by'] = getpass.getuser()
        connect = sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()

        # columns
        columns = ''
        for c in condition_dict:
            columns+=c+','

        # condition
        condition_string = ''
        for key in condition_dict:
            condition = condition_dict[key]
            condition_string += str(key) + '=' + "'" + str(condition) + "' and "

        cursor.execute('Select %s FROM %s where %s' %(columns[:-1],table,condition_string[:-5]))

        tmp = cursor.fetchall()
        if not tmp:
            data_dict.update(condition_dict)
            value_string=''
            column_string=''
            for key in data_dict:
                value = data_dict[key]
                value_string += "'" + str(value) + "'" + ','
                column_string += key + ','
            cursor.execute("INSERT INTO "+table+" (" + column_string[:-1] + ") VALUES (" + value_string[:-1] + ");")
        else:
            update_string=''
            for key in data_dict:
                value = data_dict[key]
                update_string += str(key) + '=' + "'" + str(value) + "',"
            cursor.execute(
                "UPDATE " + table +
                " SET " + update_string[:-1] +
                " WHERE " + condition_string[:-5] + ";")
        connect.commit()


    def update_insert_not_null_fields_only(self,sampleID,data_dict):
        data_dict['LastUpdated']=str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        data_dict['LastUpdated_by']=getpass.getuser()
        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        cursor.execute('Select CrystalName FROM mainTable')
        available_columns=[]
        cursor.execute("SELECT * FROM mainTable")
        for column in cursor.description:           # only update existing columns in data source
            available_columns.append(column[0])
        if self.check_if_sample_exists_in_data_source(sampleID):
            for key in data_dict:
                value=data_dict[key]
#                print value
                if key=='ID' or key=='CrystalName':
                    continue
                if not str(value).replace(' ','')=='':  # ignore empty fields
                    update_string=str(key)+'='+"'"+str(value)+"'"
#                    cursor.execute("UPDATE mainTable SET "+update_string+" WHERE CrystalName="+"'"+sampleID+"' and "+str(key)+" is null;")
                    cursor.execute("UPDATE mainTable SET "+update_string+" WHERE CrystalName="+"'"+sampleID+"' and ("+str(key)+" is null or "+str(key)+"='');")
        else:
            column_string='CrystalName'+','
            value_string="'"+sampleID+"'"+','
            for key in data_dict:
                value=data_dict[key]
                if key=='ID':
                    continue
                if key not in available_columns:
                    continue
                if not str(value).replace(' ','')=='':  # ignore if nothing in csv field
                    value_string+="'"+str(value)+"'"+','
                    column_string+=key+','
            cursor.execute("INSERT INTO mainTable ("+column_string[:-1]+") VALUES ("+value_string[:-1]+");")
        connect.commit()

    def get_value_from_field(self,sampleID,column):
        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        cursor.execute("SELECT "+column+" FROM  mainTable WHERE CrystalName='"+sampleID+"';")
        return cursor.fetchone()


    def load_samples_from_data_source(self):
        header=[]
        data=[]
        connect=sqlite3.connect(self.data_source_file)
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM mainTable")
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        return header,data


    def get_db_dict_for_visit_run_autoproc(self,xtal,visit,run,autoproc):
        db_dict = {}
        header=[]
        connect=sqlite3.connect(self.data_source_file)     # creates sqlite file if non existent
        cursor = connect.cursor()
        sqlite = (  'select * '
                    'from collectionTable '
                    "where CrystalName ='%s' and" %xtal +
                    "      DataCollectionVisit = '%s' and" %visit +
                    "      DataCollectionRun = '%s' and" %run +
                    "      DataProcessingProgram = '%s'" %autoproc  )
        cursor.execute(sqlite)
        for column in cursor.description:
            header.append(column[0])
        data = cursor.fetchall()
        for n, item in enumerate(data[0]):
            db_dict[header[n]] = str(item)
        return db_dict










