# ANL utils package for analysis
# S.Chekanov. chakanau@hep.anl.gov

from ROOT import *
import sys
from array import *
import math
import csv


class parray:
     "a class to keep data. Can be loaded from histograms"
     def __init__(self, ntot=0, h1=None, Title="parray"):
      self.Ntot = ntot 
      self.x = array( 'f', [0]*self.Ntot ) 
      self.ex = array( 'f', [0]*self.Ntot )
      self.y  = array( 'f', [0]*self.Ntot )
      self.yup  = array( 'f', [0]*self.Ntot )
      self.ydown= array( 'f', [0]*self.Ntot )
      self.title = Title

      if (h1 != None):
     	if (h1.GetNbinsX() != self.Ntot):
     		         print "Histogram has different number of bins than the input!"
     		         sys.exit()
        if (h1.GetTitle() != None):
                  s=h1.GetTitle().strip()
                  if (len(s)): self.title=h1.GetTitle()

     	for i in range(h1.GetNbinsX()):
          self.y[i]=h1.GetBinContent(i+1)
          self.x[i]=h1.GetBinCenter(i+1)
          self.ex[i]=0.5*h1.GetBinWidth(i+1)
          # symmetric errors
     	  self.yup[i]=h1.GetBinError(i+1) 
     	  self.ydown[i]=h1.GetBinError(i+1)

     def Copy(self):
         tmp = parray(self.size()) 
         tmp.setArrayX(self.getArrayX)
         tmp.setArrayY(self.getArrayY)
         tmp.setArrayXE(self.getArrayXE)
         tmp.setArrayYUP(self.getArrayYUP)
         tmp.setArrayYDOWN(self.getArrayYDOWN)
         return tmp;
 
     def Print(self):
        print 'parray='+self.title
     	for i in range(self.Ntot):
            print "i=",i," x=",self.x[i]," y=",self.y[i]," eyUP=",self.yup[i]," yDOWN=",self.ydown[i] 
     def Inv(self): # invert 
           for i in range(self.Ntot): 
             self.y[i]= -1*self.y[i] 
     def PrintCompare(self, p):
       print "Compare parrays",self.title 
       for i in range(self.Ntot):
            print "i=",i," x=",self.x[i]," y1=",self.y[i]," y2=",p.getY(i)," diff=",self.y[i]-p.getY(i) 
     def title(self):
        return self.title
     def size(self):
        return self.Ntot
     def getArrayX(self):
        return self.x
     def getArrayXE(self):
        return self.ex 
     def getArrayY(self):
        return self.y
     def getArrayYUP(self):
        return self.yup 
     def getArrayYDOWN(self):
        return self.ydown 
     def setArrayX(self,x):
        self.x=x 
     def setArrayXE(self,x):
        self.ex=x
     def setArrayY(self,y):
        self.y=y 
     def setArrayYUP(self,x):
        self.yup=x 
     def setArrayYDOWN(self,x):
        self.ydown=x 
     def getX(self, i):
       return  self.x[i] 
     def getXE(self, i):
       return  self.ex[i]
     def getY(self, i):
       return  self.y[i]
     def  setY(self, i, xx):
       self.y[i]=xx
     def  setX(self, i, xx):
       self.x[i]=xx
     def  setYUP(self, i, xx):
       self.yup[i]=xx
     def  setYDOWN(self, i, xx):
       self.ydown[i]=xx
     def  getYUP(self, i):
       return self.yup[i]
     def  getYDOWN(self, i):
       return self.ydown[i]
 
 
# convert array to TGraph
# error is taken from Upper level
def getTGraphErrors( p, ErrorOnX=True ):
         x=p.getArrayX()
         y=p.getArrayY()
         ex=p.getArrayXE() 
	 # if (ErrorOnX==False): ex = array( 'f', [0]*p.size() )
         ey=p.getArrayYUP()
         return TGraphErrors( p.size(), x, y, ex, ey )

# convert array to TGraph
def getTGraph( p):
         x=p.getArrayX()
         y=p.getArrayY()
         return TGraph( p.size(), x, y)

# convert array to TGraph
def getTGraphAsymmErrors( p, ErrorOnX=True ):
         x=p.getArrayX()
         y=p.getArrayY()
         ex=p.getArrayXE()
         # if (ErrorOnX==False): ex = array( 'f', [0]*p.size() )
         ydown=p.getArrayYDOWN()
         yup=p.getArrayYUP()
         return TGraphAsymmErrors( p.size(), x, y, ex, ex, ydown, yup )


# calculate systematics. 
# Returns:
#        1) original TGraph
#        2) TGraph with modified upper and lower errors from systematic variations 
# with sys. errors on Y (added in quandrature)
# input: central - parray with central measurement
#        diff    - a list with parray with variations
def getSystematics(central,diff,title='data'):

   gr = getTGraphErrors(central,False)
   gr.SetMarkerSize( 0.001)
   gr.SetTitle(title) 
   gr.SetName(title) 

   Ntot=central.size()
   yup=array( 'f', [0]*Ntot )
   ydown=array( 'f', [0]*Ntot )

   SS=[]
   for sys in diff:
      # sys.Print()
      tt=[]
      for j in range( Ntot ):
        if (sys.getY(j)>0): yup[j]   = yup[j] + sys.getY(j)*sys.getY(j);
        if (sys.getY(j)<0): ydown[j] = ydown[j] + sys.getY(j)*sys.getY(j);
        tt.append(sys.getY(j))
      SS.append(tt)

 
   # swap row and colums
   table = map(None,*SS)

   ii=0;
   txtfile='root/sys_'+title+'.txt'
   csvfile='root/sys_'+title+'.csv'
   file=open(txtfile,"w")
   file.write("\\begin{verbatim}\n")
   csvWriter = csv.writer(open(csvfile, 'w'), delimiter=' ',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL)

   print "% contribution"
   s="Nr   "
   k="-----------"
   for i in range(len(diff)):
       s=s+str(i)+"       ";
       k=k+"-------";
   print s 
   print k 
   file.write(s+"\n");
   file.write(k+"\n");

   dd=0
   # write table and CSV
   for line in table:
        s=" "
        XX=central.getY(ii)
        Xcen=central.getX(ii)
        Xmin=central.getX(ii)-central.getXE(ii)
        Xmax=central.getX(ii)+central.getXE(ii)
        ii=ii+1;
        pers=[]
        tt=[]
        for cell in line: 
             ratio=0;
             if (XX>0): ratio=100*(cell/XX) 
             tt.append(ratio)
             ss="%7.3f" % ratio 
             s=s+ss+ "% ";
             pers.append(ss)

        take=0 
        for j in tt:
               take=take+j 
        if (take==0): continue;

        dd=dd+1
        print str(dd)+" "+s 

        if Xmin>10: # this is for ET spectra 
           nr=str(ii).zfill(2) 
           Xmin=int(Xmin)
           Xmax=int(Xmax) 
           file.write(nr+" "+str(Xmin)+"-"+str(Xmax)+" "+s+"\n");
        if Xmin<10: # this is for ETA spectra 
           nr=str(ii).zfill(2)
           Xmin= "%4.2f" % Xmin
           Xmax= "%4.2f" % Xmax
           file.write(nr+"  "+str(Xmin)+"-"+str(Xmax)+" "+s+"\n");

        csvWriter.writerow(pers) 

   # import pprint
   # for item in cols:
   #       pprint.pprint(item, indent=4, depth=2)

   # for ro in SS: 
   #          print ro

   for j in range( Ntot ):
         yup[j]=math.sqrt(yup[j])
         ydown[j]=math.sqrt(ydown[j])


   # combine 
   # central_sys=central.Copy()
   for j in range( Ntot ):
               xx=central.getYUP(j) # for histograms YUP = YDOWN 
               yUP=TMath.Sqrt(yup[j]*yup[j] + xx*xx  )
               yDW=TMath.Sqrt(ydown[j]*ydown[j] + xx*xx)
               central.setYUP(j, yUP)
               central.setYDOWN(j, yDW)

   # get TGraph with 0 errors on X
   grSys = getTGraphAsymmErrors( central, False )
   grSys.SetTitle( title+"_systematics" )
   grSys.SetName(title+"_systematics" )
   grSys.SetMarkerColor( 1 )
   grSys.SetMarkerStyle( 20 )
   grSys.SetMarkerSize( 0.3 )

   file.write("\\end{verbatim}\n")
   file.close()
   print "Write="+txtfile
   print "Write="+csvfile

   return gr,grSys






# convert histogram to TGraph
def TH1toTGraphError(h1): 

 g1=TGraphErrors()
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     ex=h1.GetBinWidth(i+1)/2.0
     g1.SetPoint(i,x,y)
     g1.SetPointError(i,ex,ey)

 g1.SetMarkerColor( 1 )
 g1.SetMarkerStyle( 20 )
 g1.SetMarkerSize( 0.5 )

 # g1->Print();
 return g1


# convert histogram to TGraph
def TH1toTGraph(h1):
 g1=TGraph()
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     #ex=h1.GetBinWidth(i+1)/2.0
     g1.SetPoint(i,x,y)
     #g1.SetPointError(i,ex,ey)
 g1.SetMarkerColor( 1 )
 g1.SetMarkerStyle( 20 )
 g1.SetMarkerSize( 0.5 )

 # g1->Print();
 return g1


# print histogram  
def Print(h1):
 print "Histogram :",h1.GetName()
 for i in range(h1.GetNbinsX()): 
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1) 
     x=h1.GetBinCenter(i+1)
     ex=h1.GetBinWidth(i+1) 
     print "i=",i, " center=",x," value=",y



# convert histogram to TGraph
def TH1shift(h1,shift):

 ##  g1=h1.Clone();
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1) 
     x=h1.GetBinCenter(i+1)
     ex=h1.GetBinWidth(i+1)
     h1.SetBinContent(i+1,y+shift)

def TH1skip(h1,min,max):
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1) 
     x=h1.GetBinCenter(i+1)
     if (x>=min and x<=max): y=-1; ey=0; 
     ex=h1.GetBinWidth(i+1)
     h1.SetBinContent(i+1,y)
     h1.SetBinError(i+1,ey)

def TH1range(h1,min,max):
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     ex=h1.GetBinWidth(i+1)
     if (x<min or x>max): 
                       y=0
                       ey=0
     h1.SetBinContent(i+1,y)
     h1.SetBinError(i+1,ey)


def TH1integrate(h1,min,max):
 sum=0
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     ex=h1.GetBinWidth(i+1)
     if (x>=min and x<=max): sum=sum+y*ex
 return sum 



# get TGraph in the range
def TGraphRange(g1, indexMin, indexMax):
  """
   g2=g1.Clone();
   g2.SetMarkerColor( 1 )
   g2.SetMarkerStyle( 20 )
   g2.SetMarkerSize( 0.4 )
   g2.SetTitle( g1.GetTitle() )
   g2.SetName( g1.GetName() )
  """
  g2= TGraphAsymmErrors()
  n1=g1.GetN();

  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(indexMin,indexMax-1 ):
      if (i>n1): print  "Error in TGraphRange"
      x1=X1[i]
      y1=Y1[i] 
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# get TGraph without points 
def TGraphSkip(g1,point1, point2):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();

  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      if (i == point1): continue; 
      if (i == point2): continue; 
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# scale one point (inx) by a scale factor 
# (if the cross section outside range, like Eta)
def TGraphPoint(g1,scale,inx):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      if (i == inx): 
                   y1=y1*scale
                   dy1l=dy1l*scale
                   dy1h=dy1h*scale
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# shift a given point by a delta value and 
# adjust the horisontal error bar
def TGraphPointXshift(g1,delta,inx):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      if (i == inx):
                   x1=x1-delta
                   dd=dx1h+dx1l
                   dd=dd-2*delta
                   dx1h=0.5*dd
                   dx1l=0.5*dd
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


def rescaleaxis(g,scale=1.0):
    """This function rescales the x-axis on a TGraph."""
    N = g.GetN()
    x = g.GetX()
    for i in range(N):
        x[i] *= scale
    g.GetHistogram().Delete()
    g.SetHistogram(0)
    return


# scale one point (inx) by a scale factor
# (if the cross section outside range, like Eta)
def TH1Point(h1,scale,inx):
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     if (i == inx):
                   y=y*scale
                   ey=ey*scale
     ex=h1.GetBinWidth(i+1)
     h1.SetBinContent(i+1,y)
     h1.SetBinError(i+1,ey)


# shift one point in X by delta
def TH1PointXshift(h1,delta,inx):
 from array import array
 axis = array( 'd' )
 axis=h1.GetXaxis();
 xx=axis.GetXbins();

 xx = array( 'd');
 xx.append(0);
 xx.append(0.2);
 xx.append(0.4);
 xx.append(0.6);
 xx.append(0.8);
 xx.append(1.0);
 xx.append(1.2);
 xx.append(1.34);
 xx.append(1.6);
 xx.append(1.8);
 xx.append(2.0);
 xx.append(2.2);
 xx.append(2.34);
 xx.append(2.6);
 xx.append(2.8);
 xx.append(3.0);
 hh=TH1D(h1.GetName(),h1.GetName(),h1.GetNbinsX(),xx)
 for i in range(h1.GetNbinsX()):
     y=h1.GetBinContent(i+1)
     ey=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     #if (i == inx):
     #              x=x-0.5*delta
     #ex=h1.GetBinWidth(i+1)
     hh.SetBinContent(i+1,y)
     hh.SetBinError(i+1,ey)
     # hh.SetBinCenter(i+1,x)
 return hh 


# skip range between min and max
def TGraphSkipRange(g1,min,max):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      if (x1>=min and x1<=max): continue

      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# skip range between min and max
def TGraphUseRange(g1,min,max):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      if (x1<min or x1>max): continue

      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1,y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# get TGraph after scaling 
# scale is a scaling factor


def TGraphScale(g1, scale):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1, y1*scale);
      g2.SetPointError(nn,dx1l,dx1h,dy1l*scale,dy1h*scale);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2



def TGraphScaleError(g1, scale):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1, y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l*scale,dy1h*scale);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# scale factor for the ratio toi scale alpha_s 
def TGraphScaleForRatio(g1, scale):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      yy=y1-1.0;
      yy=yy*scale
      yy=1.0+yy 
      g2.SetPoint(nn, x1, yy);
      g2.SetPointError(nn,dx1l,dx1h,dy1l*scale,dy1h*scale);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2


# scale errors of TGraph using other TGraph
def TGraphScaleErrorTGraph(g1, g1scale):
  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0

  n1x=g1scale.GetN();
  X1x =g1scale.GetX();
  Y1x =g1scale.GetY();


  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1, y1);
      g2.SetPointError(nn,dx1l,dx1h,dy1l*Y1x[i],dy1h*Y1x[i]);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2




# shift Y by some value : shift
def TGraphYShift(g1, shift):

  g2= TGraphAsymmErrors()
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g2.SetPoint(nn, x1, y1+shift);
      g2.SetPointError(nn,dx1l,dx1h,dy1l,dy1h); 
      # print x1,y1,dy1l, dy1h 
      nn=nn+1

  g2.SetFillColor( g1.GetFillColor()  )
  g2.SetLineStyle( g1.GetLineStyle()  )
  g2.SetLineColor( g1.GetLineColor()  )
  g2.SetMarkerColor( g1.GetMarkerColor()  )
  g2.SetMarkerStyle( g1.GetMarkerStyle()  )
  g2.SetMarkerSize( g1.GetMarkerSize() )
  g2.SetTitle( g1.GetTitle() )
  g2.SetName( g1.GetName() )
  return  g2



"""
# shift Y by some value : shift
def TGraphYShift(g1, shift):
  n1=g1.GetN();
  X1 =g1.GetX();
  Y1 =g1.GetY();
  nn=0
  for i in range(n1):
      x1=X1[i]
      y1=Y1[i]
      dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
      dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
      dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
      dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
      g1.SetPoint(nn, x1, y1+shift);
      # g1.SetPointError(nn,dx1l,dx1h,dy1l,dy1h);
      # print x1,y1,dy1l, dy1h 
      nn=nn+1
"""






# subtract 2 TGraphs
def TGraphErrorsSubtract(g1,g2):

  debug=0;

  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  n2=g2.GetN();

  if (n1!=n2) :
     print " vectors do not have same number of entries !  \n";
     return g3;

  x1=0.;   y1=0.; x2=0.; y2=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  dy2h=0.; dy2l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  X2 = g2.GetX();
  Y2 = g2.GetY();
  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    dx2h  = g2.GetErrorXhigh(i) #  EXhigh1[i]
    dx2l  = g2.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy2h  = g2.GetErrorYhigh(i) #  EYhigh1[i];
    dy2l  = g2.GetErrorYlow(i)  #  EYlow2 [i];
    x2=X2[i]
    y2=Y2[i]


    if (y1!=0.): dy1h  = dy1h[i];
    else:        dy1h  = 0.;
    if (y2!=0.): dy2h  = dy2h[i];
    else:        dy2h  = 0.;
    if (y1!=0.): dy1l  = dy1l [i];
    else:        dy1l  = 0.;
    if (y2!=0.): dy2l  = dy2l [i];
    else:        dy2l  = 0.;

    if (y2!=0.): g3.SetPoint(i, x1,y1-y2);
    else:        g3.SetPoint(i, x1,y2);

    el=0.; eh=0.;
    if (y1!=0. and y2!=0.): el=math.sqrt(dy1l*dy1l+dy2l*dy2l);
    if (y1!=0. and y2!=0.): eh=math.sqrt(dy1h*dy1h+dy2h*dy2h);
    g3.SetPointError(i,dx1h,dx1l,el,eh);


  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle()+"-"+g2.GetTitle() )
  g3.SetName( g1.GetName()+"-"+g2.GetName() )

  return g3;


# for checking the relative scale 
def TH1scaleCheck(h1,bin,scale):
     y=h1.GetBinContent(bin)
     h1.SetBinContent(bin,y*scale)


# just make a copy
def TGraphCopy(g1, pointsStyle=20, pointsSize=1.0):

  g = TGraphAsymmErrors()
  n=g1.GetN();
  X1 = g1.GetX();
  Y1 = g1.GetY();
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    g.SetPoint(i,x1,y1);
    g.SetPointError(i,dx1l,dx1h,dy1l,dy1h);

  g.SetFillColor( 0   )
  g.SetLineStyle( 1   )
  g.SetLineColor( 1  )
  g.SetMarkerColor( 1  )
  g.SetMarkerStyle( pointsStyle  )
  g.SetMarkerSize( pointsSize  )
  g.SetTitle( g1.GetTitle() )
  return g


# divide 2 TGraphs with errors
# mode=0: error on g2 is included 
# mode=1: error on g2 is ignored
# mode=2: error on g1 is ignored
# if style =1, style from second graph is taken
def TGraphErrorsDivide(g1,g2,mode=0,style=0):

  debug=0;

  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  n2=g2.GetN();

  if (n1!=n2) :
     print " vectors do not have same number of entries. Take smallest !  \n";

  min=n1
  if (n2<n1): min=n2


  x1=0.;   y1=0.; x2=0.; y2=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  dy2h=0.; dy2l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  X2 = g2.GetX();
  Y2 = g2.GetY();

  import math
  for i in range(min):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]

    dx2h  = g2.GetErrorXhigh(i) #  EXhigh1[i]
    dx2l  = g2.GetErrorXlow(i)  #  GetErrorXlow EXlow1[i]
    dy2h  = g2.GetErrorYhigh(i) #  EYhigh1[i];
    dy2l  = g2.GetErrorYlow(i)  #  EYlow2 [i];
    x2=X2[i]
    y2=Y2[i]
    if (mode==1):
             dy2h=0
             dy2l=0

    if (mode==2):
             dy1h=0
             dy1l=0

    if (y1!=0.): dy1h  = dy1h/y1;
    else:        dy1h  = 0.;
    if (y2!=0.): dy2h  = dy2h/y2;
    else:        dy2h  = 0.;
    if (y1!=0.): dy1l  = dy1l/y1;
    else:        dy1l  = 0.;
    if (y2!=0.): dy2l  = dy2l/y2;
    else:        dy2l  = 0.;

    if (y2!=0.): g3.SetPoint(i, x1,y1/y2);
    else:        g3.SetPoint(i, x1,y2);

    el=0.; eh=0.;
    if (y1!=0. and y2!=0.): el=TMath.Sqrt(dy1l*dy1l+dy2l*dy2l)*(y1/y2);
    if (y1!=0. and y2!=0.): eh=TMath.Sqrt(dy1h*dy1h+dy2h*dy2h)*(y1/y2);
    g3.SetPointError(i,dx1l,dx1h,el,eh);


  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineWidth( g1.GetLineWidth()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle()+"div"+g2.GetTitle() )
  g3.SetName( g1.GetName()+"div"+g2.GetName() )

  if (style==1):
         g3.SetFillColor( g2.GetFillColor()  )
         g3.SetLineStyle( g2.GetLineStyle()  )
         g3.SetLineColor( g2.GetLineColor()  )
         g3.SetMarkerColor( g2.GetMarkerColor()  )
         g3.SetMarkerStyle( g2.GetMarkerStyle()  )
         g3.SetMarkerSize( g2.GetMarkerSize() )
         g3.SetTitle( g2.GetTitle()+"div"+g1.GetTitle() )
         g3.SetName( g2.GetName()+"div"+g1.GetName() )
         g3.SetLineWidth( g2.GetLineWidth()  )
 
        
  return g3;


# merge 2 tgraphs.
# also skip y=0 for cross sections 
def TGraphMerge(g1,g2):

  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  n2=g2.GetN();

  x1=0.;   y1=0.; x2=0.; y2=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  dy2h=0.; dy2l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  X2 = g2.GetX();
  Y2 = g2.GetY();

  k=0;
  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    if (y1 == 0): continue
    g3.SetPoint(k, x1,y1);
    g3.SetPointError(k,dx1l,dx1h,dy1l,dy1h);
    k=k+1

  for i in range(g2.GetN()):
    dx1h  = g2.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g2.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g2.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g2.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X2[i]
    y1=Y2[i]
    if (y1 == 0): continue
    g3.SetPoint(k, x1,y1);
    g3.SetPointError(k,dx1l,dx1h,dy1l,dy1h);
    k=k+1

  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle() )
  g3.SetName( g1.GetName() )

  return g3;

  



# combine  2 TGraphs with errors
# x and y errors are the same, but errors will be added
# mode=0: add errors linearly 
# mode=1: add errors in quadrature
def TGraphErrorsAdd(g1,g2,mode=0):

  debug=0;

  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  n2=g2.GetN();

  if (n1!=n2) :
     print " vectors do not have same number of entries !  \n";
     return g3;

  x1=0.;   y1=0.; x2=0.; y2=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  dy2h=0.; dy2l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  X2 = g2.GetX();
  Y2 = g2.GetY();

  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]

    dx2h  = g2.GetErrorXhigh(i) #  EXhigh1[i]
    dx2l  = g2.GetErrorXlow(i)  #  GetErrorXlow EXlow1[i]
    dy2h  = g2.GetErrorYhigh(i) #  EYhigh1[i];
    dy2l  = g2.GetErrorYlow(i)  #  EYlow2 [i];
    x2=X2[i]
    y2=Y2[i]
    
    el=0.; eh=0.;
    if (mode == 0): 
          eh=dy1h+dy2h
          el=dy1l+dy2l


    if (mode == 1): 
          xx1=(dy1h*dy1h+dy2h*dy2h)
          xx2=(dy1l*dy1l+dy2l*dy2l)
          eh=TMath.Sqrt(xx1)
          el=TMath.Sqrt(xx2)
    g3.SetPoint(i, x1,y1); 
    g3.SetPointError(i,dx1l,dx1h,el,eh);


  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle() )
  g3.SetName( g1.GetName() )

  return g3;









# divide 2 histograms to avoid ROOT bugs in Clone() 
def TH1divTH1(h1,h2):
 print "---> Call to TH1divTH1"
 xaxis = h1.GetXaxis();
 Ntot=xaxis.GetNbins()+1 
 xx = array( 'f', [0.]*Ntot )
 for i in range( Ntot ):
     xx[i]=xaxis.GetBinLowEdge(i+1)
 # xx[Ntot]=xaxis.GetBinUpEdge(Ntot)
 # print xx
 ratio=TH1F(h1.GetTitle()+"_div_"+h2.GetTitle(),  h1.GetTitle()+"_div_"+h2.GetTitle(),Ntot-1,xx)
 for i in range( Ntot ):
     y1=h1.GetBinContent(i+1)
     e1=h1.GetBinError(i+1)
     x1=h1.GetBinCenter(i+1)
     ex1=h1.GetBinWidth(i+1)

     y2=h2.GetBinContent(i+1)
     e2=h2.GetBinError(i+1)
     x2=h2.GetBinCenter(i+1)
     ex2=h2.GetBinWidth(i+1)
     r=0.0
     if (y2>0): r=y1/y2 
     dy1h  = 0.
     dy2h  = 0.
     if (y1!=0.): dy1h  = e1/y1;
     if (y2!=0.): dy2h  = e2/y2;

     er=r*TMath.Sqrt(dy1h*dy1h+dy2h*dy2h)
     # print "Ratio=",r
     ratio.SetBinContent(i+1,r)
     ratio.SetBinError(i+1,er)
      
 return ratio


# multiply 2 histograms to avoid ROOT bugs in Clone() 
def TH1timesTH1(h1,h2):
 print "---> Call to TH1divTH1"
 xaxis = h1.GetXaxis();
 Ntot=xaxis.GetNbins()+1 
 xx = array( 'f', [0.]*Ntot )
 for i in range( Ntot ):
     xx[i]=xaxis.GetBinLowEdge(i+1)
 # xx[Ntot]=xaxis.GetBinUpEdge(Ntot)
 # print xx
 ratio=TH1F(h1.GetTitle()+"_div_"+h2.GetTitle(),  h1.GetTitle()+"_div_"+h2.GetTitle(),Ntot-1,xx)
 for i in range( Ntot ):
     y1=h1.GetBinContent(i+1)
     e1=h1.GetBinError(i+1)
     x1=h1.GetBinCenter(i+1)
     ex1=h1.GetBinWidth(i+1)

     y2=h2.GetBinContent(i+1)
     e2=h2.GetBinError(i+1)
     x2=h2.GetBinCenter(i+1)
     ex2=h2.GetBinWidth(i+1)
     r=y1*y2
     dy1h  = 0.
     dy2h  = 0.
     if (y1!=0.): dy1h  = e1/y1;
     if (y2!=0.): dy2h  = e2/y2;

     er=r*TMath.Sqrt(dy1h*dy1h+dy2h*dy2h)
     # print "Multiply=",r
     ratio.SetBinContent(i+1,r)
     ratio.SetBinError(i+1,er)

 return ratio



# divide histogram (MC) by data points
def TH1divTGraph(h,g1):

 print "---> Call to TH1divTGraph"
 # h1=h.Clone()
 X = g1.GetX();
 Y = g1.GetY();

 xaxis = h.GetXaxis();
 Ntot=xaxis.GetNbins()+1 
 xx = array( 'f', [0.]*Ntot ) 

 for i in range( Ntot ):
     xx[i]=xaxis.GetBinLowEdge(i+1)
     # print xx[i]

 # xx[Ntot-1]=xaxis.GetBinUpEdge(Ntot)

 # for i in range(Ntot):
 #      print xx[i]

# h1=TH1F("test","test",h.GetNbinsX(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax())
 h1=TH1F("test","test",Ntot-1,xx)
 h1.SetLineStyle( h.GetLineStyle()  )
 h1.SetLineColor( h.GetLineColor()  )
 h1.SetLineWidth( h.GetLineWidth()  )
 h1.SetMarkerColor( h.GetMarkerColor()  )
 h1.SetMarkerStyle( h.GetMarkerStyle()  )
 h1.SetMarkerSize( h.GetMarkerSize() )
 h1.SetTitle( h.GetTitle() )

 for i in range( Ntot ):
     y1=Y[i]
     y=h.GetBinContent(i+1)
     # e=h1.GetBinError(i+1)
     x=h1.GetBinCenter(i+1)
     # ex=h1.GetBinWidth(i+1)
     r=0.0
     if (y1>0):
             r=y/y1
     # print x, y, y1,  "Ratio=",r
     h1.SetBinContent(i+1,r)
     h1.SetBinError(i+1,0)
     # print h1.GetBinContent(i+1)
     # h1.Print("all")

 # h1.Print("all") 

 return h1


# divide data points by histogram (MC)
def TH1divTGraphInv(h,g1):

 print "---> Call to TH1divTGraph"
 # h1=h.Clone()
 X = g1.GetX();
 Y = g1.GetY();

 xaxis = h.GetXaxis();
 Ntot=xaxis.GetNbins()+1
 xx = array( 'f', [0.]*Ntot )

 for i in range( Ntot ):
     xx[i]=xaxis.GetBinLowEdge(i+1)
 # xx[Ntot-1]=xaxis.GetBinUpEdge(Ntot)

 # for i in range(Ntot):
 #      print xx[i]

# h1=TH1F("test","test",h.GetNbinsX(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax())
 h1=TH1F("test","test",Ntot-1,xx)
 h1.SetLineStyle( h.GetLineStyle()  )
 h1.SetLineColor( h.GetLineColor()  )
 h1.SetLineWidth( h.GetLineWidth()  )
 h1.SetMarkerColor( h.GetMarkerColor()  )
 h1.SetMarkerStyle( h.GetMarkerStyle()  )
 h1.SetMarkerSize( h.GetMarkerSize() )
 h1.SetTitle( h.GetTitle() )

 for i in range( Ntot ):
     y1=Y[i]
     y=h.GetBinContent(i+1)
     # e=h1.GetBinError(i+1)
     # x=h1.GetBinCenter(i+1)
     # ex=h1.GetBinWidth(i+1)
     r=0.0
     if (y>0):
             r=y1/y
     # print "Ratio=",r
     h1.SetBinContent(i+1,r)
     h1.SetBinError(i+1,0)
     # print h1.GetBinContent(i+1)
     # h1.Print("all")

 # h1.Print("all") 

 return h1



# take TGraph, set all Y values to 1. Keep errors
def TGraphErrorsRelativeNull(g1):

  debug=0;
  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  x1=0.;   y1=0.; 
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    g3.SetPoint(i,x1,1.0);

    el=0
    if (y1 !=0): el=dy1l/y1
    eh=0
    if (y1 !=0): eh=dy1h/y1
    g3.SetPointError(i,dx1h,dx1l,el,eh);

  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle() )

  return g3;



# remove errors from Y 
def TGraphErrorsYnone(g1):
  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  x1=0.;   y1=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  X1 = g1.GetX();
  Y1 = g1.GetY();
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    g3.SetPoint(i,x1,y1);
    g3.SetPointError(i,dx1h,dx1l,0,0);
  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle() )
  return g3;







# take TGraph, set all Y values to 1. Keep and invert errors
# usefull to show some ratio plots
def TGraphErrorsRelativeNullInv(g1):

  debug=0;
  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  x1=0.;   y1=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;

  X1 = g1.GetX();
  Y1 = g1.GetY();
  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i]
    y1=Y1[i]
    g3.SetPoint(i,x1,1.0);

    r1=0
    r2=0
    if (y1>0): r1=dy1h/y1;
    if (y1>0): r2=dy1l/y1;
    g3.SetPointError(i,dx1h,dx1l,r1,r2);

  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle() )

  return g3;















# divide g2 graph by g1 TGraphs with errors
# this is apposite to the above script
# g1 is the data, g2 MC. The output is g2/g1 
def TGraphErrorsDivideInv(g1,g2):

  debug=0;

  g3= TGraphAsymmErrors()
  n1=g1.GetN();
  n2=g2.GetN();

  if (n1!=n2) :
     print " vectors do not have same number of entries !  \n";
     return g3;

  x1=0.;   y1=0.; x2=0.; y2=0.;
  dx1h=0.; dx1l=0.;
  dy1h=0.; dy1l=0.;
  dy2h=0.; dy2l=0.;

  # invert this
  X1 = g1.GetX();
  Y1 = g1.GetY();
  # this MC
  X2 = g2.GetX();
  Y2 = g2.GetY();

  import math
  for i in range(g1.GetN()):
    dx1h  = g1.GetErrorXhigh(i) #  EXhigh1[i]
    dx1l  = g1.GetErrorXlow(i)  # GetErrorXlow EXlow1[i]
    dy1h  = g1.GetErrorYhigh(i) #  EYhigh1[i];
    dy1l  = g1.GetErrorYlow(i)  #  EYlow2 [i];
    x1=X1[i] 
    y1=Y1[i]

    dx2h  = g2.GetErrorXhigh(i) #  EXhigh1[i]
    dx2l  = g2.GetErrorXlow(i)  #  GetErrorXlow EXlow1[i]
    dy2h  = g2.GetErrorYhigh(i) #  EYhigh1[i];
    dy2l  = g2.GetErrorYlow(i)  #  EYlow2 [i];
    x2=X2[i]
    y2=Y2[i]


    if (y1!=0.): dy1h  = dy1h/y1;
    else:        dy1h  = 0.;
    if (y2!=0.): dy2h  = dy2h/y2;
    else:        dy2h  = 0.;
    if (y1!=0.): dy1l  = dy1l/y1;
    else:        dy1l  = 0.;
    if (y2!=0.): dy2l  = dy2l/y2;
    else:        dy2l  = 0.;

    if (y2!=0.): g3.SetPoint(i, x1,y2/y1);
    else:        g3.SetPoint(i, x1,y2);

    el=0.; eh=0.;
    if (y1!=0. and y2!=0.): eh=TMath.Sqrt(dy1l*dy1l+dy2l*dy2l)*(y2/y1);
    if (y1!=0. and y2!=0.): el=TMath.Sqrt(dy1h*dy1h+dy2h*dy2h)*(y2/y1);
    g3.SetPointError(i,dx1h,dx1l,el,eh);

  g3.SetFillColor( g1.GetFillColor()  )
  g3.SetLineStyle( g1.GetLineStyle()  )
  g3.SetLineColor( g1.GetLineColor()  )
  g3.SetMarkerColor( g1.GetMarkerColor()  )
  g3.SetMarkerStyle( g1.GetMarkerStyle()  )
  g3.SetMarkerSize( g1.GetMarkerSize() )
  g3.SetTitle( g1.GetTitle()+"div"+g2.GetTitle() )
  g3.SetName( g1.GetName()+"div"+g2.GetName() )

  return g3;


# get histogram and axis
def getH1D(file, name,style=1,col=21,marker_size=0.2,xlab="none",ylab="none"):
           h1=file.Get(name)
           h1.Sumw2()
           h1.SetTitle("");
           h1.SetFillColor(col)
           h1.SetLineStyle(style)
           h1.SetLineWidth(2)
           h1.SetMarkerStyle(20)
           h1.SetMarkerSize(marker_size)
           h1.SetStats(0)
           ax=h1.GetXaxis(); ax.SetTitleOffset(0.8)
           ax.SetTitle( xlab );
           ay=h1.GetYaxis(); ay.SetTitleOffset(0.8)
           ay.SetTitle( ylab );
           ax.SetTitleColor(1); ay.SetTitleColor(1);
           ax.SetTitleOffset(1.1); ay.SetTitleOffset(1.3)
           ax.SetTitleSize(0.04); ay.SetTitleSize(0.04);
           ax.SetLabelSize(0.03); ay.SetLabelSize(0.03);
           ax.SetLabelOffset(.015); ay.SetLabelOffset(.015);
           return h1,ax,ay



