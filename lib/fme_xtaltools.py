import gemmi
import json
import math

class pdbtools(object):

    def __init__(self,pdb):
        self.pdb = gemmi.read_pdb(pdb)

    def get_refinement_stats_dict(self):
        block = self.pdb.make_mmcif_headers()
        r = block.get_mmcif_category('_refine')
        db_dict = {}
        db_dict['RefinementResolutionHigh'] = str(r['ls_d_res_high'][0])
        db_dict['RefinementResolutionLow'] = str(r['ls_d_res_low'][0])
        db_dict['RefinementRcryst'] = str(r['ls_R_factor_R_free'][0])
        db_dict['RefinementRfree'] = str(r['ls_R_factor_R_work'][0])

        return db_dict


class mtztools(object):

    def __init__(self,mtz):
        try:
            self.mtz = gemmi.read_mtz_file(mtz)
        except RuntimeError:
            pass

#        self.info = {
#            'DataProcessingPointGroup':     None,
#            'DataProcessingSpaceGroup':     None,
#            'DataProcessingUnitCell':       None,
#            'DataProcessingUnitCellVolume': None,
#            'DataProcessingLattice':        None,
#            'DataCollectionWavelength':     None,
#            'DataProcessingNsymop':         None
#        }

        self.info = {
            'DataProcessingPointGroup':     '',
            'DataProcessingSpaceGroup':     '',
            'DataProcessingUnitCell':       '',
            'DataProcessingUnitCellVolume': '',
            'DataProcessingLattice':        '',
            'DataCollectionWavelength':     '',
            'DataProcessingNsymop':         ''
        }


    def read_mtz_header(self):
        self.info['DataProcessingSpaceGroup'] = str(self.mtz.spacegroup.short_name())
        self.info['DataProcessingPointGroup'] = str(self.mtz.spacegroup.point_group_hm())
        self.info['DataProcessingNsymop'] = str(self.mtz.nsymop)
        self.info['DataProcessingUnitCellVolume'] = str(self.mtz.cell.volume)
        self.info['DataProcessingLattice'] = str(self.mtz.spacegroup.crystal_system_str())
        self.info['DataCollectionWavelength'] = self.mtz.dataset(1).wavelength
        self.info['DataProcessingUnitCell'] = (
            str(self.mtz.cell.a) + ' ' + str(self.mtz.cell.b) + ' ' + str(self.mtz.cell.c) + ' ' +
            str(self.mtz.cell.alpha) + ' ' + str(self.mtz.cell.beta) + ' ' + str(self.mtz.cell.gamma)
        )

        return self.info





class logtools(object):

    def __init__(self,logfile):
        self.logfile = logfile

#        self.aimless = {    'DataProcessingResolutionLow':                  None,
#                            'DataProcessingResolutionLowInnerShell':        None,
#                            'DataProcessingResolutionHigh':                 None,
#                            'DataProcessingResolutionHighOuterShell':       None,
#                            'DataProcessingRmergeOverall':                  None,
#                            'DataProcessingRmergeLow':                      None,
#                            'DataProcessingRmergeHigh':                     None,
#                            'DataProcessingIsigOverall':                    None,
#                            'DataProcessingIsigLow':                        None,
#                            'DataProcessingIsigHigh':                       None,
#                            'DataProcessingCompletenessOverall':            None,
#                            'DataProcessingCompletenessLow':                None,
#                            'DataProcessingCompletenessHigh':               None,
#                            'DataProcessingMultiplicityOverall':            None,
#                            'DataProcessingMultiplicityLow':                None,
#                            'DataProcessingMultiplicityHigh':               None,
#                            'DataProcessingCChalfOverall':                  None,
#                            'DataProcessingCChalfLow':                      None,
#                            'DataProcessingCChalfHigh':                     None,
#                            'DataProcessingUniqueReflectionsLow':           None,
#                            'DataProcessingUniqueReflectionsHigh':          None,
#                            'DataProcessingUniqueReflectionsOverall':       None          }

        self.aimless = {    'DataProcessingResolutionLow':                  '',
                            'DataProcessingResolutionLowInnerShell':        '',
                            'DataProcessingResolutionHigh':                 '',
                            'DataProcessingResolutionHighOuterShell':       '',
                            'DataProcessingRmergeOverall':                  '',
                            'DataProcessingRmergeLow':                      '',
                            'DataProcessingRmergeHigh':                     '',
                            'DataProcessingIsigOverall':                    '',
                            'DataProcessingIsigLow':                        '',
                            'DataProcessingIsigHigh':                       '',
                            'DataProcessingCompletenessOverall':            '',
                            'DataProcessingCompletenessLow':                '',
                            'DataProcessingCompletenessHigh':               '',
                            'DataProcessingMultiplicityOverall':            '',
                            'DataProcessingMultiplicityLow':                '',
                            'DataProcessingMultiplicityHigh':               '',
                            'DataProcessingCChalfOverall':                  '',
                            'DataProcessingCChalfLow':                      '',
                            'DataProcessingCChalfHigh':                     '',
                            'DataProcessingUniqueReflectionsLow':           '',
                            'DataProcessingUniqueReflectionsHigh':          '',
                            'DataProcessingUniqueReflectionsOverall':       ''          }



    def read_aimless(self):
        for line_number, line in enumerate(open(self.logfile)):
            if 'Low resolution limit' in line and len(line.split()) == 6:
                self.aimless['DataProcessingResolutionLow'] = line.split()[3]
                self.aimless['DataProcessingResolutionHighOuterShell'] = line.split()[5]
            if 'High resolution limit' in line and len(line.split()) == 6:
                self.aimless['DataProcessingResolutionHigh'] = line.split()[3]
                self.aimless['DataProcessingResolutionLowInnerShell'] = line.split()[4]
            if 'Rmerge  (all I+ and I-)' in line and len(line.split()) == 8:
                self.aimless['DataProcessingRmergeOverall'] = line.split()[5]
                self.aimless['DataProcessingRmergeLow'] = line.split()[6]
                self.aimless['DataProcessingRmergeHigh'] = line.split()[7]
            if 'Rmerge  (all I+ & I-)' in line and len(line.split()) == 8:
                self.aimless['DataProcessingRmergeOverall'] = line.split()[5]
                self.aimless['DataProcessingRmergeLow'] = line.split()[6]
                self.aimless['DataProcessingRmergeHigh'] = line.split()[7]
            if 'Mean((I)/sd(I))' in line and len(line.split()) == 4:
                self.aimless['DataProcessingIsigOverall'] = line.split()[1]
                self.aimless['DataProcessingIsigHigh'] = line.split()[3]
                self.aimless['DataProcessingIsigLow'] = line.split()[2]
            if 'Mean(I)/sd(I)' in line and len(line.split()) == 4:
                self.aimless['DataProcessingIsigOverall'] = line.split()[1]
                self.aimless['DataProcessingIsigHigh'] = line.split()[3]
                self.aimless['DataProcessingIsigLow'] = line.split()[2]
            if line.startswith('Completeness') and len(line.split()) == 4:
                self.aimless['DataProcessingCompletenessOverall'] = line.split()[1]
                self.aimless['DataProcessingCompletenessHigh'] = line.split()[3]
                self.aimless['DataProcessingCompletenessLow'] = line.split()[2]
            if 'Completeness (ellipsoidal)' in line and len(line.split()) == 5:
                self.aimless['DataProcessingCompletenessOverall'] = line.split()[2]
                self.aimless['DataProcessingCompletenessHigh'] = line.split()[4]
                self.aimless['DataProcessingCompletenessLow'] = line.split()[3]
            if 'Multiplicity' in line and len(line.split()) == 4:
                self.aimless['DataProcessingMultiplicityOverall'] = line.split()[1]
                self.aimless['DataProcessingMultiplicityHigh'] = line.split()[3]
                self.aimless['DataProcessingMultiplicityLow'] = line.split()[3]
            if line.startswith('Mn(I) half-set correlation CC(1/2)') and len(line.split()) == 7:
                self.aimless['DataProcessingCChalfOverall'] = line.split()[4]
                self.aimless['DataProcessingCChalfLow'] = line.split()[5]
                self.aimless['DataProcessingCChalfHigh'] = line.split()[6]
            if line.startswith('     CC(1/2)') and len(line.split()) == 4:
                self.aimless['DataProcessingCChalfOverall'] = line.split()[1]
                self.aimless['DataProcessingCChalfLow'] = line.split()[2]
                self.aimless['DataProcessingCChalfHigh'] = line.split()[3]
            if 'Total number unique' in line and len(line.split()) == 6:
                self.aimless['DataProcessingUniqueReflectionsOverall'] = line.split()[3]
                self.aimless['DataProcessingUniqueReflectionsLow'] = line.split()[4]
                self.aimless['DataProcessingUniqueReflectionsHigh'] = line.split()[5]

        return self.aimless


    def read_json(self):
        with open(self.logfile, 'r') as log:
            data = log.read()
        obj = json.loads(data)
        self.aimless['DataProcessingResolutionLow'] = str(round(math.sqrt(1/float(obj['d_star_sq_max'][0])),2))
        self.aimless['DataProcessingResolutionLowInnerShell'] = str(round(math.sqrt(1/float(obj['d_star_sq_max'][1])),2))
        self.aimless['DataProcessingResolutionHigh'] = str(round(math.sqrt(1/float(obj['d_star_sq_min'][len(obj['d_star_sq_min'])-1])),2))
        self.aimless['DataProcessingResolutionHighOuterShell'] = str(round(math.sqrt(1/float(obj['d_star_sq_min'][len(obj['d_star_sq_min'])-2])),2))
        self.aimless['DataProcessingResolutionOverall'] = self.aimless['DataProcessingResolutionLow'] + '-' + self.aimless['DataProcessingResolutionHigh']
        self.aimless['DataProcessingRmergeOverall'] = str(round(obj['overall']['r_merge'],3))
        self.aimless['DataProcessingRmergeLow'] = str(round(obj['r_merge'][0],3))
        self.aimless['DataProcessingRmergeHigh'] = str(round(obj['r_merge'][len(obj['r_merge'])-1],3))
        self.aimless['DataProcessingIsigOverall'] = str(round(obj['overall']['i_over_sigma_mean'],1))
        self.aimless['DataProcessingIsigLow'] = str(round(obj['i_over_sigma_mean'][0],1))
        self.aimless['DataProcessingIsigHigh'] = str(round(obj['i_over_sigma_mean'][len(obj['i_over_sigma_mean'])-1],1))
        self.aimless['DataProcessingCompletenessOverall'] = str(round(obj['overall']['completeness'],1))
        self.aimless['DataProcessingCompletenessLow'] = str(round(obj['completeness'][0],1))
        self.aimless['DataProcessingCompletenessHigh'] = str(round(obj['completeness'][len(obj['completeness'])-1],1))
        self.aimless['DataProcessingMultiplicityOverall'] = str(round(obj['overall']['multiplicity'],1))
        self.aimless['DataProcessingMultiplicityLow'] = str(round(obj['multiplicity'][0],1))
        self.aimless['DataProcessingMultiplicityHigh'] = str(round(obj['multiplicity'][len(obj['multiplicity'])-1],1))
        self.aimless['DataProcessingCChalfOverall'] = str(round(obj['overall']['cc_one_half'],2))
        self.aimless['DataProcessingCChalfLow'] = str(round(obj['cc_one_half'][0],2))
        self.aimless['DataProcessingCChalfHigh'] = str(round(obj['cc_one_half'][len(obj['cc_one_half'])-1],2))
        self.aimless['DataProcessingUniqueReflectionsLow'] = str(obj['n_uniq'][0])
        self.aimless['DataProcessingUniqueReflectionsHigh'] = str(obj['n_uniq'][len(obj['n_uniq'])-1])
        self.aimless['DataProcessingUniqueReflectionsOverall'] = str(obj['overall']['n_obs'])

        return self.aimless
