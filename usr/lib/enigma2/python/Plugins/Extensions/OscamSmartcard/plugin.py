from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system, popen
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
import time
import glob
from boxbranding import *
from globalconfig import *

x=getDriverDate()
x1=x[0:4];x2=x[4:6];x3=x[6:8]
DriverDate=str(x3 + '.' + x2 + '.'+x1)

ImageTypeInfo = (getMachineBrand()+ ' - '+getMachineName()+ ' - '+getImageDistro()+ '-'+getImageVersion()+ '  Driver: '+DriverDate+ ' ').title()

ImageType =getImageDistro()
if   'openmips' in ImageType:
	imagename= 'Openmips'
elif 'openatv' in ImageType:
	imagename = 'Openatv'
else:
	imagename = 'unknown System'

def architectures():
	x = popen('uname -a')
	x = x.read(); x=x.strip().split(); system=x[0]
	hostname=x[1]
	kernelversion=x[2]; kerneldate= x[7]+'.' + x[6] +'.'+x[10]
	hardwaretype=x[11]
	ossystem=x[0]
	return ossystem,kernelversion,hardwaretype,hostname

architectures()
arch = architectures()[2]

############################################################################
##for test architectures remove the #
#arch = 'mips'
#arch = 'x86_64'
#arch = 'sh4'
#arch = 'armv7l'
############################################################################

extrainfo=(architectures()[3] +': ' + architectures()[0]+' - '+architectures()[1]+' - '+ arch).title()

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("OscamSmartcard", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/OscamSmartcard/locale/"))

def _(txt):
	t = gettext.dgettext("OscamSmartcard", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

#############################################################

config.plugins.OscamSmartcard = ConfigSubsection()
config.plugins.OscamSmartcard.menufake = ConfigSelection(default="-", choices = [("+", _("-"))])
				# Start Softcam via Script or via Pythonstarter
config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="script", choices = [
				("python", _("Python SoftCamstart (openATV)")),
				("script", _("Script SoftCamstart (openMips)"))
				])
config.plugins.OscamSmartcard.systemclean = ConfigSelection(default="cleanall_yes", choices = [
				#("cleanall_no", _(No)),
				("cleanall_yes", _(' '))
				])
				# Path to config
config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/etc/tuxbox/config/", choices = [
				("/usr/keys/", _("/usr/keys/ (openATV)")),
				("/etc/tuxbox/config/", _("/etc/tuxbox/config/ (openMips)"))
				])
				#Oscam webifPort
config.plugins.OscamSmartcard.WebifPort = ConfigSelection(default="83", choices = [
				("83", _("83")),
				("8888", _("8888"))
				])
				# Oscam binary online update
config.plugins.OscamSmartcard.oscambinary = ConfigSelection(default="No", choices = [
				("no_binaryupdate", _("No")),
				("yes_binaryupdate", _("Yes"))
				])			
# Smartcard oscam.server
cardlist = [
	("V13", _("Sky V13")),
	("V13_fast", _("Sky V13 Fastmode")),
	("V14", _("Sky V14")),
	("V14_fast", _("Sky V14 Fastmode")),
	("S02", _("Sky S02")),
	("HD01", _("HD+ HD01 white")),
	("HD02", _("HD+ HD02 black")),
	("I02-Beta", _("I02 Beta")),
	("I12-Beta", _("I12 Beta")),
	("I12-Nagra", _("I12 Nagra")),
	("V23", _("KabelBW V23")),
	("ORF", _("ORF 0D05")),
	("ORF_ICE_crypto", _("ORF ICE Cryptoworks 0D95")),
	("ORF_ICE_irdeto", _("ORF ICE Irdeto 0648")),
	("SRG-V2", _("SRG V2")),
	("SRG-V4", _("SRG V4")),
	("SRG-V5", _("SRG V5")),
	("UM01", _("UnityMedia UM01")),
	("UM02", _("UnityMedia UM02")),
	("UM03", _("UnityMedia UM03")),
	("D01", _("Kabel Deutschl. D01")),
	("D02", _("Kabel Deutschl. D02")),
	("D09", _("Kabel Deutschl. D09")),
	("MTV", _("MTV")),
	("tivu", _("Tivusat")),
	("JSC", _("JSC-sports - Viaccess")),
	("RedlightHD", _("Redlight Elite HD - Viaccess")),
	("FreeXTV", _("FreeX TV - Viaccess")),
	("none", _("None"))
	]

config.plugins.OscamSmartcard.internalReader0 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.internalReader1 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.externalReader0 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.externalReader1 = ConfigSelection(default="none", choices = cardlist)

#######################################################################

class OscamSmartcard(ConfigListScreen, Screen):
	skin = """
<screen name="OscamSmartcard-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#90000000">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#20000000" transparent="0" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="77,645" size="250,33" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="375,645" size="250,33" text="Start" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="682,645" size="250,33" text="E2 Restart" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="989,645" size="250,33" text="Help" transparent="1" />
    <widget name="config" position="61,114" size="590,500" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel position="60,55" size="348,50" text="OscamSmartcard" font="Regular; 40" valign="center" transparent="1" backgroundColor="#20000000" />
    <eLabel position="400,58" size="349,50" text="Setup" foregroundColor="unffffff" font="Regular; 30" valign="center" backgroundColor="#20000000" transparent="1" halign="left" />
    <eLabel position="665,640" size="5,40" backgroundColor="#e5dd00" />
    <eLabel position="360,640" size="5,40" backgroundColor="#61e500" />
    <eLabel position="60,640" size="5,40" backgroundColor="#e61700" />
    <eLabel position="965,640" size="5,40" backgroundColor="#0000ff" />
    <widget name="oscamsmartcardhelperimage" position="669,112" size="550,500" zPosition="1" />
    <widget name="HELPTEXT" position="61,500" size="590,250" zPosition="1" font="Regular; 20" halign="left" valign="top" backgroundColor="#20000000" transparent="1" />
    <eLabel text="OscamSmartcard 2.0 by arn354 and Undertaker" position="692,70" size="540,25" zPosition="1" font="Regular; 15" halign="right" valign="top" backgroundColor="#20000000" transparent="1" />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.oscamconfigpath = config.plugins.OscamSmartcard.ConfigPath.value
		self.oscamcamstartvalue = config.plugins.OscamSmartcard.Camstart.value
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.createoscamsmartcarddata()
		self.oscamsmartcarddata = "/tmp/data/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["oscamsmartcardhelperimage"] = Pixmap()
		self["HELPTEXT"] = Label()
	
		if arch != 'armv7l' and arch != 'mips' and arch != 'sh4' and arch != 'ppc':
			list = []
			list.append(getConfigListEntry(_(message26), config.plugins.OscamSmartcard.menufake, _(message23)))
			list.append(getConfigListEntry(_(message24 +' ' + arch +' '+ message25), ))
			list.append(getConfigListEntry(_(ImageTypeInfo), ))
			list.append(getConfigListEntry(_(extrainfo), ))
			ConfigListScreen.__init__(self, list)
			self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"red": self.exit,"yellow": self.exit,"blue": self.exit,"green":self.exit,"ok": self.exit,"cancel": self.exit}, -1)
			self.onLayoutFinish.append(self.UpdatePicture)
			if not self.selectionChanged in self["config"].onSelectionChanged:
				self["config"].onSelectionChanged.append(self.selectionChanged)
			self.selectionChanged()
			self.exit
		else:
			a=self.checkallcams()
			anzahl = len(a)
			if len(a)>0:
				list = []
				list.append(getConfigListEntry(_(message13 + " :" +str(anzahl) +' '+ message14), config.plugins.OscamSmartcard.systemclean, _('\n' + message08 + '\n' + message28)))
				i=0
				while i < len(a):
					title = a[i].replace("enigma2-plugin-softcams-",'')
					desc = a[i]
					xx = 'config.plugins.OscamSmartcard.installed'+str(i)
					xx = ConfigSelection(default="Yes", choices = [("Yes", _("Yes"))])
					list.append(getConfigListEntry(_(str(i+1) +".)  " + title), xx, _(desc)))
					i = i + 1
				ConfigListScreen.__init__(self, list)
				self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot,"blue": self.showInfo,"green": self.systemcleaning,"cancel": self.exit}, -1)
				self.onLayoutFinish.append(self.UpdatePicture)
				if not self.selectionChanged in self["config"].onSelectionChanged:
					self["config"].onSelectionChanged.append(self.selectionChanged)
				self.selectionChanged()
			else:
				self.downloadurl()
				onlineavaible = self.newversion(arch)
				list = []
				if imagename =='Openatv':
					camstartname='Openatv System'
					config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/usr/keys/", choices = [("/usr/keys/", _("/usr/keys/ (openATV)"))])
					config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="script", choices = [("python", _("Python SoftCamstart (openATV)"))])
				elif imagename =='Openmips':
					camstartname='SoftcamManager'
					config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="script", choices = [("script", _("Script SoftCamstart (openMips)"))])
					config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/etc/tuxbox/config/", choices = [("/etc/tuxbox/config/", _("/etc/tuxbox/config/ (openMips)"))])
				else:
					camstartname='SoftcamManager'
					config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="script", choices = [("script", _("Script SoftCamstart (openMips)"))])
					config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/etc/tuxbox/config/", choices = [("/etc/tuxbox/config/", _("/etc/tuxbox/config/ (openMips)"))])
				
				list.append(getConfigListEntry(_(message26), config.plugins.OscamSmartcard.menufake, _('INFORMATION: '+ message27 +'\n' + message28 )))
				list.append(getConfigListEntry(_(ImageTypeInfo), ))
				list.append(getConfigListEntry(_(extrainfo), ))
				list.append(getConfigListEntry(_(message03 + '\t: '+ config.plugins.OscamSmartcard.ConfigPath.value), ))
				list.append(getConfigListEntry(_(message10 + '\t: ' + camstartname), ))
				list.append(getConfigListEntry(_(message07 + '\t: ' + arch), ))
				list.append(getConfigListEntry(_(message09 + '\t: ' + str(self.readercheck()[4])  ), ))
				list.append(getConfigListEntry(_("------------------------------------------------------------------------------------------------"), ))
				list.append(getConfigListEntry(_("Select OScam WebifPort:"), config.plugins.OscamSmartcard.WebifPort, _("INFORMATION: Select OScam WebifPort\n\nOscam Webif will be accessible on the selected port.\ne.g. http:\\IPOFYOURBOX:83")))
				if self.readercheck()[0] == 'installed':
					list.append(getConfigListEntry(_("Internal Reader /dev/sci0:"), config.plugins.OscamSmartcard.internalReader0, _("INFORMATION: Internal Reader /dev/sci0\n\nAll STB's having only one cardslot.\nOn STB's having two cardslots it is mostly the lower cardslot.")))
				if self.readercheck()[1] == 'installed':
					list.append(getConfigListEntry(_("Internal Reader /dev/sci1:"), config.plugins.OscamSmartcard.internalReader1, _("INFORMATION: Internal Reader /dev/sci1\n\nOn STB's having two cardslots it is mostly the upper cardslot.")))
				if self.readercheck()[2] == 'installed':
					list.append(getConfigListEntry(_("External Reader /dev/ttyUSB0:"), config.plugins.OscamSmartcard.externalReader0, _("INFORMATION: External Reader /dev/ttyUSB0\n\nThis Reader can be used to configure for example a connected easymouse.")))
				if self.readercheck()[3] == 'installed':
					list.append(getConfigListEntry(_("External Reader /dev/ttyUSB1:"), config.plugins.OscamSmartcard.externalReader1, _("INFORMATION: External Reader /dev/ttyUSB1\n\nThis Reader can be used to configure for example a second connected easymouse.")))

				list.append(getConfigListEntry(_(message04),config.plugins.OscamSmartcard.oscambinary,_('INFORMATION: ' + message02 + '\n\ninstalled\t: ' + self.currentversion() + '\n' + message06 + '\t: ' + onlineavaible )))
				
				ConfigListScreen.__init__(self, list)
				self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
				self.onLayoutFinish.append(self.UpdatePicture)
				if not self.selectionChanged in self["config"].onSelectionChanged:
					self["config"].onSelectionChanged.append(self.selectionChanged)
				self.selectionChanged()
	
	def selectionChanged(self):
		self["HELPTEXT"].setText(self["config"].getCurrent()[2])

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/" + returnValue + ".png"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/no.png"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["oscamsmartcardhelperimage"].instance.size().width(),self["oscamsmartcardhelperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#20000000"])
		self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["oscamsmartcardhelperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartSTB,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart STB"))
	
	def systemcleaning(self):
		systemclean = self.session.openWithCallback(self.systemclean,MessageBox,_(message16), MessageBox.TYPE_YESNO)
		systemclean.setTitle(_("System cleaning"))
		self.close()

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)
	
	def save(self):
		self.oscamconfigpath = config.plugins.OscamSmartcard.ConfigPath.value
		self.oscamcamstartvalue = config.plugins.OscamSmartcard.Camstart.value
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.oscamservices = (self.oscamconfigpath + "oscam.services")
		self.oscamservicesTMP = (self.oscamservices + ".tmp")
		self.oscamcamstart = '/etc/oscamsmartcard.emu'
		self.oscamcamstartTMP = (self.oscamcamstart + ".tmp")
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass
		try:
			system('mkdir ' + config.plugins.OscamSmartcard.ConfigPath.value + ' > /dev/null 2>&1')
		except:
			pass
		configfile.save()
		self.makebackup()
		self.saveoscamserver()
		self.saveoscamdvbapi()
		self.saveoscamuser()
		self.saveoscamconf()
		self.saveoscamservices()
		self.saveoscamsrvid2() 
		self.saveoscamprovid()
		if config.plugins.OscamSmartcard.oscambinary.value == 'yes_binaryupdate':
			self.oscambinaryupdate()
		self.savecamstart()
		configfile.save()
		if imagename == 'Openatv':
			system ('/usr/bin/oscam_oscamsmartcard -b -c /usr/keys > /dev/null 2>&1')
		elif imagename == 'Openmips':
			system ('/etc/init.d/softcam start')
		else:
			self.session.open(MessageBox, _(message22), MessageBox.TYPE_INFO,10)
			self.close()
		self.session.open(MessageBox, _(message05 +'\n' + imagename), MessageBox.TYPE_INFO,10)
		self.rmoscamsmartcarddata()
		self.close()
		#Finish ENDE
	
	def createoscamsmartcarddata(self):
		data = 'wget -O /tmp/data.zip '+ server +'data.zip'
		popen(data)
		popen('unzip -o -q -d /tmp /tmp/data.zip')
		popen('rm /tmp/data.zip')
		
	def rmoscamsmartcarddata(self):
		popen('rm -f /tmp/data/*')

	def saveoscamserver(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader0.value + "_internalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader1.value + "_internalReader1.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader0.value + "_externalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader1.value + "_externalReader1.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamserverTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamserver,"w")
			for line in open(self.oscamserverTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamserverTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.server!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamdvbapi(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamdvbapiTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamdvbapi,"w")
			for line in open(self.oscamdvbapiTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamdvbapiTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.dvbapi!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamuser(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.user.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamuserTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamuser,"w")
			for line in open(self.oscamuserTMP):
				if config.plugins.OscamSmartcard.internalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamuserTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.user!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamconf(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.conf.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamconfTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamconf,"w")
			for line in open(self.oscamconfTMP):
				line = line.replace("83", config.plugins.OscamSmartcard.WebifPort.value )
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamconfTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.conf!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamservices(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamservicesTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamservices,"w")
			for line in open(self.oscamservicesTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamservicesTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.services!"), MessageBox.TYPE_ERROR)
			self.config_lines = []
	
	def saveoscamsrvid2(self):
			system('touch ' + config.plugins.OscamSmartcard.ConfigPath.value +'oscam.srvid2')
			system('chmod 644 ' + config.plugins.OscamSmartcard.ConfigPath.value +'oscam.srvid2')
			
	def saveoscamprovid(self):
			system('touch ' + config.plugins.OscamSmartcard.ConfigPath.value +'oscam.provid')
			system('chmod 644 ' + config.plugins.OscamSmartcard.ConfigPath.value +'oscam.provid')

	def oscambinaryupdate(self):
		if self.newversion(arch) != message29:
			system('wget -q -O /tmp/oscam.tar.gz ' + self.downloadurl() +' ' +null)
			system('tar -xzf /tmp/oscam.tar.gz -C /tmp')
			system('mv /tmp/oscam /tmp/oscam_oscamsmartcard')
			system('chmod 777 /tmp/oscam_oscamsmartcard')
			system('killall -9 oscam_oscamsmartcard' + null)
			system('rm -f /usr/bin/oscam_oscamsmartcard' + null)
			system('mv /tmp/oscam_oscamsmartcard /usr/bin/oscam_oscamsmartcard' + null)
			system('rm -f /tmp/oscam.tar.gz')
			print plugin +'binary download ok'
		else:
			print plugin +'no binary download'
		
	def downloadurl(self):
		binary = 'oscam_oscamsmartcard'
		suffix = '.tar.gz?raw=true'
		if arch == 'armv7l' or arch == 'mips' or arch == 'sh4' or arch == 'ppc':
			downloadurl = server + binary + '_' + arch + suffix
		else:downloadurl = 'unknown_' + arch
		return downloadurl

	def newversion(self,arch):
		upgradeinfo = message29
		upgfile = '/tmp/upgrade.log'
		system('touch ' + upgfile)
		useragent = ' -U "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:40.0) Gecko/20100101 Firefox/40.0"'
		system('wget -O ' + upgfile + ' ' + infourl  )
		file = open(upgfile, "r")
		for line in file.readlines():
			line = line.strip().split(',')
			if line[0] == arch:
				upgradeinfo = line[1]
		file.close()
		os.remove(upgfile)
		return upgradeinfo

	def currentversion(self):
		if os.path.exists('/usr/bin/oscam_oscamsmartcard'):
			currentversion = message15 + ' : ' + message11
			f = popen('/usr/bin/oscam_oscamsmartcard -V')
			for line in f:
				if 'Version:' in line:
					line=line.strip().split()
					currentversion= line[1]
			f.close()
		else:
				currentversion=message19
		return currentversion

	def checkallcams(self):
		liste=[]
		f = popen('opkg list-installed |grep -i softcam')
		for line in f:
		        line=line.strip().split()
		        if line[0] != ignore1 and line[0] != ignore2 and line[0] != ignore3:
		            liste.append(line[0])
		f.close()
		return liste

	def readercheck(self):
		sci0 = 'not installed';
		sci1 = sci0
		usb0 = sci0
		usb1 = sci0
		anz = 0
		if os.path.exists('/dev/sci0'):
			sci0='installed'
			anz=anz+1
		if os.path.exists('/dev/sci1'):
			sci1='installed'
			anz=anz+1
		if os.path.exists('/dev/ttyUSB0'):
			usb0='installed'
			anz=anz+1
		if os.path.exists('/dev/ttyUSB1'):
			usb1='installed'
			anz=anz+1
		return sci0,sci1,usb0,usb1,anz
	
	def makebackup(self):
		dd = (time.strftime("%Y-%m-%d-%H-%M-%S"))
		x = glob.glob("/usr/keys/oscam.*")
		if len(x) >0:
			system('tar -czf /usr/keys/backup-oscamsmartcard-'+ dd +'.tar.gz /usr/keys/oscam.*')
			system('rm -f /usr/keys/oscam.*')
		y = glob.glob("/etc/tuxbox/config/oscam.*")
		if len(y) >0:
			system('tar -czf /etc/tuxbox/config/backup-oscamsmartcard-'+ dd +'.tar.gz /etc/tuxbox/config/oscam.*')
			system('rm -f /etc/tuxbox/config/oscam.*')

	def makeclean(self):
		a = self.checkallcams()
		if len(a) >0:
			i = 0
			while i < len(a):
				system('opkg remove --force-remove ' +a[i] + null)
				print plugin + message21 +' ' + a[i]
				i = i + 1
		else:
			print plugin + message18

	def savecamstart(self):
		try:
			if imagename =='Openmips':
				print plugin +'create camstart files for OpenMips..'
				system('/etc/init.d/softcam stop')
				system('/etc/init.d/cardserver stop')
				system('rm -f /etc/init.d/cardserver*')
				system('rm -f /etc/init.d/softcam*')
				system('touch /etc/init.d/softcam.None')
				system('touch /etc/init.d/cardserver.None')
				system('cp -f /usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/data/softcam.OscamSmartcard /etc/init.d/softcam.OscamSmartcard')
				system('cp -f /usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/data/cardserver.OscamSmartcard /etc/init.d/cardserver.OscamSmartcard')
				system('ln -sf /etc/init.d/softcam.OscamSmartcard /etc/init.d/softcam')
				system('ln -sf /etc/init.d/cardserver.None /etc/init.d/cardserver')
				system('chmod 777 /etc/init.d/softcam.*')
				system('chmod 777 /etc/init.d/cardserver.*')
				system('update-rc.d softcam  defaults ' + null)
				system('update-rc.d cardserver defaults ' + null)
				print plugin +'create camstart files  ... done'

			if imagename =='Openatv':
				print plugin +'create camstart files for OpenATV..'
				system('killall -9 oscam_oscamsmartcard' + null)
				system('rm -f /etc/oscamsmartcard.emu')
				system('cp -f /usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/data/oscamsmartcard.emu /etc/oscamsmartcard.emu')
				config.softcam.actCam.setValue("OscamSmartcard")
				config.softcam.actCam2.setValue("None")
				config.softcam.save()
				configfile.save()
				print plugin +'create camstart files  ... done'
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam camstart files!"), MessageBox.TYPE_ERROR)
			self.config_lines = []
		
	def appendconfFile(self,appendFileName):
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()
		for x in file_lines:
			self.config_lines.append(x)

	def systemclean (self, answer):
		if answer is True:
			self.makeclean()
			self.close()
		else:
			self.close()
			
	def restartSTB(self, answer):
		if answer is True:
			configfile.save()
			system('reboot')
		else:
			self.close()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

##################
def main(session, **kwargs):
	session.open(OscamSmartcard,"/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/oscamsmartcard.png")

def Plugins(**kwargs):
	return PluginDescriptor(name="OscamSmartcard v2.0", description=_("Configuration tool for OScam"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)
