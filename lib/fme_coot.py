import os
import glob
import sys
import pickle

import pygtk, gtk, pango
import coot

sys.path.append(os.path.join(os.getenv('CCP4'),'lib','py2'))
import gemmi

sys.path.append(os.path.join(os.getenv('FragMAXexplorer_DIR'),'/lib'))
import coot_utils_fme

class GUI(object):

    def __init__(self):

        self.index = -1
        self.Todo = []

        self.settings = pickle.load(open(".fme_settings.pkl", "rb"))
        self.projectDir = self.settings['projectDir']

        self.parseProjectDir()


    def StartGUI(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_default_size(400, 600)
        self.window.set_title("FragMAXexplorer")
        self.vbox = gtk.VBox()  # this is the main container

        self.vbox.add(gtk.Label())
        self.PREVbutton = gtk.Button(label="<<<")
        self.NEXTbutton = gtk.Button(label=">>>")
        self.PREVbutton.connect("clicked", self.backward)
        self.NEXTbutton.connect("clicked", self.forward)
        hbox = gtk.HBox()
        hbox.pack_start(self.PREVbutton)
        hbox.pack_start(self.NEXTbutton)
        self.vbox.add(hbox)

        self.vbox.add(gtk.Label())
        frame = gtk.Frame()
        frame.add(gtk.Label('current folder'))
        self.vbox.add(frame)
        frame = gtk.Frame()
        self.current_folder_label = gtk.Label()
        frame.add(self.current_folder_label)
        self.vbox.add(frame)

        self.window.add(self.vbox)
        self.window.show_all()

    def RefreshData(self):
        if self.index < 0:
            self.index = 0
        if self.index > len(self.Todo) - 1:
            self.index = len(self.Todo) - 1

        if len(molecule_number_list()) > 0:
            for item in coot_utils_fme.molecule_number_list():
                coot.close_molecule(item)
        coot.set_nomenclature_errors_on_read("ignore")
        coot.handle_read_draw_molecule_with_recentre(os.path.join(self.projectDir,self.Todo[self.index],'init.pdb'), 0)
        coot.auto_read_make_and_draw_maps(os.path.join(self.projectDir,self.Todo[self.index],'init.mtz'))
        self.current_folder_label.set_label(self.Todo[self.index])

    def backward(self, widget):
        self.index -= 1
        self.RefreshData()

    def forward(self, widget):
        self.index += 1
        self.RefreshData()

    def parseProjectDir(self):
        for pdbFile in sorted(glob.glob(os.path.join(self.projectDir,'*','init.pdb'))):
            sampleID = pdbFile.split('/')[len(pdbFile.split('/'))-2]
            print('checking folder {0!s}'.format(sampleID))
            self.Todo.append(sampleID)



    def CANCEL(self, widget):
        self.window.destroy()





if __name__ == '__main__':
    GUI().StartGUI()
