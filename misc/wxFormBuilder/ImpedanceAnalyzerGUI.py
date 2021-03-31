import GUITemplate
import wx

class CalcFrame(GUITemplate.MyFrame1): 
   def __init__(self,parent): 
      GUITemplate.MyFrame1.__init__(self,parent)  
		
   def findsquare(self,event): 
      num = int(self.m_textCtrl1.GetValue()) 
      self.m_textCtrl2.SetValue (str(num*num)) 
        
app = wx.App(False) 
frame = CalcFrame(None) 
frame.Show(True) 

app.MainLoop()
