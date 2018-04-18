#!/usr/bin/env python
import os,sys,optparse,logging,math,array,datetime
logger = logging.getLogger(__name__)
import ROOT
#from rootpy.tree import TreeChain
#from rootpy.plotting import Hist2D
#ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(1)

def main():
   logging.basicConfig(level=logging.INFO)

   parser = optparse.OptionParser(description='')
   parser.add_option('-i','--input',dest='input',help='input')
   options,args = parser.parse_args()

   if options.input is None:
      parser.error('Must specify -i')
   files = []
   files.append(options.input)
   logger.info('loading tree')
   tree = ROOT.TChain('calocells')
   for file in files:
      tree.AddFile(file)
   nevts = tree.GetEntriesFast()
   logger.info('looping')

   can = ROOT.TCanvas("can","can",0,0,800,600)
   energy_vs_radius = ROOT.TH1F('energy_vs_radius',';#Delta R; E_{T} (GeV)',100,0,0.4)
   
   evtnum = 0
   last_date = datetime.datetime.now()
   for event in tree:
      if evtnum % 10 == 0:
         logger.info(' event ' + str(evtnum) + ' of ' + str(nevts) + ' in ' + str(datetime.datetime.now() - last_date))
         last_date = datetime.datetime.now()
      evtnum += 1
      electron = None
      positron = None
      for pid,peta,pphi,ppt,pstat in zip(event.particle_id,event.particle_eta,event.particle_phi,event.particle_pt,event.particle_status):
         if pstat == 3:
            logger.info(' pid = %8i eta = %8.2f phi = %8.2f pT = %8.2f stat = %8i' % (pid,peta,pphi,ppt,pstat)) 
         if electron is None and pid == 11:
            electron = array.array('d',[peta,pphi,ppt])
         if positron is None and pid == -11:
            positron = array.array('d',[peta,pphi,ppt])
         #if electron is not None and positron is not None: 
         #   break
      print electron,positron

      #for ip in range(40):
      #   print event.particle_id[ip],event.particle_status[ip]

      lar_map = ROOT.TH2D('lar_map',';#eta;#phi',59,-1.5,1.5,64,-1*math.pi,math.pi)
      tile_map = ROOT.TH2D('tile_map',';#eta;#phi',59,-1.5,1.5,64,-1*math.pi,math.pi)
      #h1 = ROOT.TH1I("h1","h1",1000,-10,100)
      #g = ROOT.TGraph2D()
      #g.SetName("graphA")
      #g.SetMarkerStyle(20)
      #g.SetMarkerSize(0.1)
      #logger.info('lar cells: ' + str(event.lar_n_cells))
      for cell_eta,cell_phi,cell_Et in zip(event.lar_eta,event.lar_phi,event.lar_Et):
         #print 'lar: ',icell,event.lar_x[icell],event.lar_y[icell],event.lar_z[icell],event.lar_Et[icell],event.lar_eta[icell],event.lar_phi[icell],event.lar_bad_cell[icell],event.lar_barrel_ec[icell],event.lar_sampling[icell],event.lar_region[icell],event.lar_hw_eta[icell],event.lar_hw_phi[icell]
         #if is_my_layer(event.lar_barrel_ec[icell],event.lar_sampling[icell],event.lar_region[icell],event.lar_hw_eta[icell],event.lar_hw_phi[icell]):
         if cell_Et > 0:
            lar_map.Fill(cell_eta,cell_phi,cell_Et)
         #h1.Fill(event.lar_Et[icell])
         
         if -0.1 < cell_eta-electron[0]:
            if cell_eta-electron[0] < 0.1:
               e_dEta = cell_eta-electron[0]
               e_dPhi = math.fabs(cell_phi-electron[1])
               if e_dPhi < 0.1:
                  energy_vs_radius.Fill(math.sqrt(e_dEta*e_dEta + e_dPhi*e_dPhi),cell_Et)

         #e_dR = math.sqrt(e_dEta**2 + e_dPhi**2)
         p_dEta = math.fabs(cell_eta-positron[0])
         if p_dEta < 0.1:
            p_dPhi = math.fabs(cell_phi-positron[1])
            if p_dPhi < 0.1:
               energy_vs_radius.Fill(math.sqrt(p_dEta*p_dEta + p_dPhi*p_dPhi),cell_Et)
         #p_dR = math.sqrt(p_dEta**2 + p_dPhi**2)


         #g.SetPoint(icell,event.lar_eta[icell],event.lar_phi[icell],event.lar_Et[icell])

      
      lar_map.Draw('colz')
      #can.SetLogz()
      can.Update()
      #h1.Draw()
      raw_input('...')
      #print g.GetN()
      

      for cell_eta,cell_phi,cell_Et in zip(event.tile_eta,event.tile_phi,event.tile_Et):
         if cell_Et > 0:
            tile_map.Fill(cell_eta,cell_phi,cell_Et)

      tile_map.Draw('colz')
      can.Update()
      raw_input('...')
      #print g.GetN()
      
      #energy_vs_radius.Draw()
      #can.Draw()
      #can.Update()
      
      
      raw_input('...')
   
   energy_vs_radius.Draw()
   can.SaveAs("energy_vs_radius.png")
   #raw_input('...')
   


if __name__ == "__main__":
   main()
