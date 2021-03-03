#!/usr/bin/env python
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import datetime
import prioriteti as p
import os
#import RPi.GPIO as GPIO
import time
#from hx711 import HX711
#GPIO.setwarnings(False)

silos_pin = 5              # 1. relej 
dotur_pin = 6	     # 2. relej
hrana1_pin = 19	     # 3. relej
hrana2_pin = 16		     # 4. relej LINIJA HRANE BR 3 NEMA KLAPNU NA 24V
alarm_pin = 8

kos1_ulaz = 12
kos2_ulaz = 20
kos3_ulaz = 21

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(silos_pin,GPIO.OUT)
#GPIO.setup(dotur_pin,GPIO.OUT)
#GPIO.setup(hrana1_pin,GPIO.OUT)
#GPIO.setup(hrana2_pin,GPIO.OUT)
#GPIO.setup(alarm_pin,GPIO.OUT)

#GPIO.setup(kos1_ulaz, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(kos2_ulaz, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(kos3_ulaz, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

greska = 0
tara = 144
jel_pise = 0

delta_kilaza_za_kos = 10 #korak punjenja po malim kosevima
minimum_glavni_kos = delta_kilaza_za_kos + 20
maksimum_glavni_kos = 100

offset = 0

sekunde_vremenske_rucne_komande = 30
masa_rucne_komande = 40

#hx = HX711(24, 8)
#hx.set_reference_unit(tara) #bilo je 92
#hx.reset()
val = 10
#val = round((hx.get_weight(5) - greska), 1)
#val = round((val/46), 1)#bilo 10 ili 100
val = val*4#za kile bez 10 broj koliko nogu ima
val = round(val, 1) #bilo pod int
val = val - 5076.8 #offset kod prvog merenja, sjebe ga jako
print "prvo merenje: " + str(val)
kos1_ulaz_vrednost = 0
kos2_ulaz_vrednost = 0
kos3_ulaz_vrednost = 0

dnevni_unos = 900

#GPIO.output(5 ,1)
#GPIO.output(6 ,1)
#GPIO.output(19 ,1)
#GPIO.output(16 ,1)
#GPIO.output(8 ,1)


hrana_kos_prethodna_vrednost = val
hrana_silos = 21000
hrana_dnevni_kos = 0
hrana_kos1 = 500
hrana_kos2 = 500
hrana_kos3 = 500
punjenje1 = 0
punjenje2 = 0
punjenje3 = 0
vreme_rada_kos1 = 0
vreme_rada_kos2 = 0
vreme_rada_kos3 = 0

temp_hrana_silos = 0
temp_hrana_kos1 = 0
temp_hrana_kos2 = 0
temp_hrana_kos3 = 0
jel_nam_treba_strelica = 1

kos1_brojac = 0
kos1_ostatak = 0
kos2_brojac = 0
kos2_ostatak = 0
kos3_brojac = 0
kos3_ostatak = 0

ukljuceno = False
nema_dosta_hrane_glavni_kos = False
rucne_komande_ukljucene = False

logo_string = "JOMAPEKS"

try:
	citaj = file("kos1_hrana.txt", "r")
	hrana_kos1 = int(citaj.readline())
	kos1_ostatak = hrana_kos1
	print "Dnevno hrana 1: " + str(hrana_kos1)
	citaj.close()
except:
	print "nema fajla kos1_hrana.txt"

try:
	citaj = file("kos2_hrana.txt", "r")
	hrana_kos2 = int(citaj.readline())
	kos2_ostatak = hrana_kos2
	print "Dnevno hrana 2: " + str(hrana_kos2)
	citaj.close()
except:
	print "Nema fajla kos2_hrana.txt"

try:
	citaj = file("kos3_hrana.txt", "r")
	hrana_kos3 = int(citaj.readline())
	kos3_ostatak = hrana_kos3
	print "Dnevno hrana 3: " + str(hrana_kos3)
	citaj.close()
except:
	print "nema fajl kos3_hrana.txt"

try:
	citaj = file("silos_hrana.txt", "r")
	hrana_silos = int(citaj.readline())
	print "Hrana u silosu: " + str(hrana_silos)
	citaj.close()
except:
	print "nema fajl silos_hrana.txt"

try:
	citaj = file("delta_kilaza.txt", "r")
	delta_kilaza_za_kos = int(citaj.readline())
	minimum_glavni_kos = delta_kilaza_za_kos + 20
	print "Delta kilaza: " + str(delta_kilaza_za_kos)
	print "Minimum glavni kos: " + str(minimum_glavni_kos)
	citaj.close()
except:
	print "nema fajla delta_kilaza.txt"


try:
	citaj = file("maksimum_glavni_kos.txt", "r")
	maksimum_glavni_kos = int(citaj.readline())
	print "Maksimum glavni kos: " + str(maksimum_glavni_kos)
	citaj.close()
except:
	print "Nema fajl maksimum_glavni_kos.txt"

class Window(QMainWindow):
	def __init__(self, parent = None):
		super(Window, self).__init__(parent)
		self.resize(800, 480)
		#if(jel_nam_treba_strelica == 0):
			#self.setCursor(QCursor(Qt.BlankCursor)) #da nema strelicu
		self.setStyleSheet('''
		background-color:  white;
''')	
		self.btnKgDo = QPushButton("Kg", self)
		self.btnKgDo.setText("")
		self.btnKgDo.resize(160, 50)
		self.btnKgDo.move(5+5, 5+100)
		self.btnKgDo.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')

		self.logo = QPixmap('logo.png')
		self.icon = QIcon(self.logo)

		self.logo_btn = QPushButton("", self)
		self.logo_btn.resize(200, 50)
		self.logo_btn.move(5, 5)
		self.logo_btn.setIcon(self.icon)
		self.logo_btn.setIconSize(QSize(200, 200))
		self.logo_btn.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')

		self.feeding_system = QPushButton("Feeding System", self)
		self.feeding_system.resize(350, 50)
		self.feeding_system.move(800/2-150+50, 5)
		self.feeding_system.setStyleSheet('''
		border: 3px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  #800080;
		font-size: 35px;
		font-weight: bold;
''')

		self.settings = QPixmap('kljuc.jpeg')
		self.icon = QIcon(self.settings)

		self.podesavanja = QPushButton("", self)
		self.podesavanja.resize(55, 55)
		self.podesavanja.setIcon(self.icon)
		self.podesavanja.clicked.connect(self.podesavanja_click)
		self.podesavanja.setIconSize(QSize(55, 55))
		self.podesavanja.move(800-55,5)
		self.podesavanja.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')


		self.btnKgSl = QPushButton("Hrana u silosu", self)
          	self.btnKgSl.resize(160, 50)
		self.btnKgSl.move(5+5, 5+60)
		self.btnKgSl.setStyleSheet('''
		border: 1px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')

		self.kos_image = QPixmap('Silos2.png')
		self.icon = QIcon(self.kos_image)

		self.btnS = QPushButton("", self)
		self.btnS.setIcon(self.icon)
		self.btnS.setIconSize(QSize(330, 300))
		self.btnS.resize(200, 300)
		self.btnS.clicked.connect(self.otvori_tastaturu_silos)
		self.btnS.move(5,80+30+5+40)
		self.btnS.setStyleSheet('''
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.kos_image = QPixmap('kos.png')
		self.icon = QIcon(self.kos_image)

		self.btnK1 = QPushButton("K1", self)
		self.btnK1.setIcon(self.icon)
		self.btnK1.setIconSize(QSize(130, 130))
		self.btnK1.resize(200, 90)
		self.btnK1.clicked.connect(self.otvori_tastaturu_kos1)
		self.btnK1.move(5 + 200,285+90)
		self.btnK1.setStyleSheet('''
		border: 2px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg = QPushButton("Hrana Kos 1", self)
		self.btnKg.resize(160, 50)
		self.btnKg.move(5+200+20, 5+60)
		self.btnKg.setStyleSheet('''
		border: 1px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')
		self.btnKg_sipaj1 = QPushButton("SIPAJ", self)
		self.btnKg_sipaj1.resize(160, 50)
		self.btnKg_sipaj1.move(5+200+20, 5+100)
		self.btnKg_sipaj1.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg1 = QPushButton(str(hrana_kos1) + " Kg", self)
		self.btnKg1.resize(160, 50)
		self.btnKg1.move(5+200+20, 300+25-5)
		self.btnKg1.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
	
		self.kos_image = QPixmap('kos.png')
		self.icon = QIcon(self.kos_image)

		self.btnK2 = QPushButton("K2", self)
		self.btnK2.setIcon(self.icon)
		self.btnK2.setIconSize(QSize(130, 130))
		self.btnK2.resize(200, 90)
		self.btnK2.clicked.connect(self.otvori_tastaturu_kos2)
		self.btnK2.move(5 + 200+200,285+90)
		self.btnK2.setStyleSheet('''
		border: 2px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg = QPushButton("Hrana Kos 2", self)
		self.btnKg.resize(160, 50)
		self.btnKg.move(5+400+20, 5+60)
		self.btnKg.setStyleSheet('''
		border: 1px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')
		self.btnKg_sipaj2 = QPushButton("SIPAJ", self)
		self.btnKg_sipaj2.resize(160, 50)
		self.btnKg_sipaj2.move(5+400+20, 5+100)
		self.btnKg_sipaj2.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg2 = QPushButton(str(hrana_kos2) + " Kg", self)
		self.btnKg2.resize(160, 50)
		self.btnKg2.move(5+400+20, 300+25-5)
		self.btnKg2.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.kos_image = QPixmap('kos.png')
		self.icon = QIcon(self.kos_image)

		self.btnK3 = QPushButton("K3", self)
		self.btnK3.setIcon(self.icon)
		self.btnK3.setIconSize(QSize(130, 130))
		self.btnK3.resize(180, 90)
		self.btnK3.clicked.connect(self.otvori_tastaturu_kos3)
		self.btnK3.move(5 + 200+200+200,285+90)
		self.btnK3.setStyleSheet('''
		border: 2px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg = QPushButton("Hrana Kos 3", self)
		self.btnKg.resize(160, 50)
		self.btnKg.move(600+20, 5+60-5)
		self.btnKg.setStyleSheet('''
		border: 1px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')
		self.btnKg_sipaj3 = QPushButton("SIPAJ", self)
		self.btnKg_sipaj3.resize(160, 50)
		self.btnKg_sipaj3.move(600+20, 5+100)
		self.btnKg_sipaj3.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		self.btnKg3 = QPushButton(str(hrana_kos3) + " Kg", self)
		self.btnKg3.resize(160, 50)
		self.btnKg3.move(600+20, 300+25)
		self.btnKg3.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')


		self.btnStart = QPushButton("ISKLJUCENO", self)
		self.btnStart.resize(260, 80)
		self.btnStart.move(300+75, 300-100)
		self.btnStart.clicked.connect(self.start_def)
		self.btnStart.setStyleSheet('''
		border: 3px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		#self.setCursor(QCursor(Qt.BlankCursor))
		#self.hx = HX711(24, 8)
		#self.hx.set_reference_unit(tara) #bilo je 92
		#self.hx.reset()

		#self.dan = dan

		openn = open("tara.txt", "r")
		self.g = openn.read()

		global greska
		greska = int(self.g)
		openn.close()

		self.meri_tred = QTimer()
		self.meri_tred.timeout.connect(self.meri)
		self.meri_tred.start(500)	#bilo 5 sekundi 5000

		self.indikator_sipanja_u_kos_tred = QTimer()
		self.indikator_sipanja_u_kos_tred.timeout.connect(self.indikator_sipanja_u_kos)
		self.indikator_sipanja_u_kos_tred.start(500)
		self.semafor_sipanja_u_kos = False

		self.otvori_popup = False

	def podesavanja_click(self):
		self.popup = Podesavanja_Form()
		self.popup.showFullScreen()

	def indikator_sipanja_u_kos(self):

		
		if(kos1_ulaz_vrednost == 1):
			if self.semafor_sipanja_u_kos == False:
				self.semafor_sipanja_u_kos = True
				self.btnK1.setStyleSheet('''
			border: 3px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			else:
				self.semafor_sipanja_u_kos = False
				self.btnK1.setStyleSheet('''
			border: 3px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
		elif(kos2_ulaz_vrednost == 1):
			if self.semafor_sipanja_u_kos == False:
				self.semafor_sipanja_u_kos = True
				self.btnK2.setStyleSheet('''
			border: 3px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			else:
				self.semafor_sipanja_u_kos = False
				self.btnK2.setStyleSheet('''
			border: 3px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
		elif(kos3_ulaz_vrednost == 1):
			if self.semafor_sipanja_u_kos == False:
				self.semafor_sipanja_u_kos = True
				self.btnK3.setStyleSheet('''
			border: 3px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			else:
				self.semafor_sipanja_u_kos = False
				self.btnK3.setStyleSheet('''
			border: 3px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
		else:
			self.btnK1.setStyleSheet('''
				border: 3px solid white;
				border-radius: 20px;
				background-color:  white;
				color:  black;
				font-size: 25px;
		''')
			self.btnK2.setStyleSheet('''
				border: 3px solid white;
				border-radius: 20px;
				background-color:  white;
				color:  black;
				font-size: 25px;
		''')
			self.btnK3.setStyleSheet('''
				border: 3px solid white;
				border-radius: 20px;
				background-color:  white;
				color:  black;
				font-size: 25px;
		''')
			

	def start_def(self):
		global ukljuceno

		if ukljuceno == False:
			ukljuceno = True
			self.btnStart.setText("UKLJUCENO")
		else:
			ukljuceno = False
			self.btnStart.setText("ISKLJUCENO")

	def meri(self):

		if(kos1_ostatak == 0 and kos2_ostatak == 0 and kos3_ostatak == 0):

			if self.otvori_popup == False:
				global ukljuceno
				ukljuceno = False
				self.btnStart.setText("ISKLJUCENO")
				self.popup = Popup(self)
				self.popup.showFullScreen()
				self.otvori_popup = True

		s1 = str(hrana_kos1) + " Kg"
		s2 = str(hrana_kos2) + " Kg"
		s3 = str(hrana_kos3) + " Kg"
		self.btnKg1.setText(s1)
		self.btnKg2.setText(s2)
		self.btnKg3.setText(s3)
		self.val = 15
		#self.val = round((self.hx.get_weight(5) - greska), 1)
		self.val = round((self.val/46), 1)#bilo 10 ili 100
		self.val = self.val*4#za kile bez 10 broj koliko nogu ima
		self.val = round(self.val, 1) #bilo pod int
		self.val = self.val - offset
		if(self.val < 0):
			self.val = 0


		global start


		print str(self.val - hrana_kos_prethodna_vrednost)
		if(abs(self.val - hrana_kos_prethodna_vrednost)  < 20):
			global hrana_kos_prethodna_vrednost
			hrana_kos_prethodna_vrednost = self.val
			self.btnKgDo.setText("DK: " + str(int(self.val)) + " Kg")#dk dnevna kolicina
	 		self.btnKgSl.setText("Silos: " + str(hrana_silos - int(self.val)) + " Kg")
			#self.hx.power_down()
			#self.hx.power_up()
		else:
			self.val = hrana_kos_prethodna_vrednost

		global kos1_ulaz_vrednost
		global kos2_ulaz_vrednost
		global kos3_ulaz_vrednost
		
		global temp_hrana_silos
		global temp_hrana_kos1
		global temp_hrana_kos2
		global temp_hrana_kos3

		global nema_dosta_hrane_glavni_kos

		self.zaustavi_male_koseve = False
		if ukljuceno == True:
			if(self.val <= minimum_glavni_kos):
				if(kos1_ulaz_vrednost == 0 and kos2_ulaz_vrednost == 0 and kos3_ulaz_vrednost == 0):
					nema_dosta_hrane_glavni_kos = True
		 			#GPIO.output(dotur_pin, 1) #ugasi dotur kada nema dosta hrane
					self.zaustavi_male_koseve = True
					#GPIO.output(silos_pin, 0)
					#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
					#GPIO.output(hrana2_pin, 1)
					kos1_ulaz_vrednost = 0
					kos2_ulaz_vrednost = 0
					kos3_ulaz_vrednost = 0
			elif(self.val >= maksimum_glavni_kos): #treba 500
				nema_dosta_hrane_glavni_kos = False
	 			#GPIO.output(dotur_pin, 1) #ugasi dotur kada nema dosta hrane
				self.zaustavi_male_koseve = False
				#GPIO.output(silos_pin, 1)
				citaj = file("silos_hrana.txt", "w")
				citaj.write(str(hrana_silos - maksimum_glavni_kos))
				citaj.close()

			
#			p.prioritetizuj(kos1_ulaz_vrednost, kos2_ulaz_vrednost, kos3_ulaz_vrednost, kos1_brojac, kos2_brojac, kos3_brojac)
#			print "(" +str(kos1_ulaz_vrednost) + ", "   + str(kos2_ulaz_vrednost) + ", " + str(kos3_ulaz_vrednost) + ", " + str(kos1_brojac) + ", " + str(kos2_brojac) + ", " + str(kos3_brojac) + ")"

			if(nema_dosta_hrane_glavni_kos == False):
					if(kos1_ulaz_vrednost == 0 and kos3_ulaz_vrednost == 0 and kos2_ulaz_vrednost == 0):
						#state1 = GPIO.input(kos1_ulaz)
						#state2 = GPIO.input(kos2_ulaz)
						#state3 = GPIO.input(kos3_ulaz)
						p.prioritetizuj(state1, state2, state3, kos1_brojac, kos2_brojac, kos3_brojac)
						if (kos1_ostatak != 0):
							if p.koji_puni == 1:
								kos1_ulaz_vrednost =  state1
								temp_hrana_silos = self.val
			  					if(kos1_ulaz_vrednost == 1):
			  						pass
								#	GPIO.output(hrana1_pin, 0) #pali prvi kos ako je ulaz na jedinici
								#	GPIO.output(hrana2_pin, 1)
								#	GPIO.output(dotur_pin, 0)

								print "Kos 1: " + str(kos1_ulaz_vrednost)

					if(kos1_ulaz_vrednost == 0 and kos2_ulaz_vrednost == 0 and kos3_ulaz_vrednost == 0):
						if (kos2_ostatak != 0):
							if p.koji_puni == 2:
								#state = GPIO.input(kos2_ulaz)
								kos2_ulaz_vrednost =  state2
								temp_hrana_silos = self.val
								if(kos2_ulaz_vrednost == 1):
									pass
								#	GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
								#	GPIO.output(hrana2_pin, 0)
								#	GPIO.output(dotur_pin, 0)
								print "Kos 2: " + str(kos2_ulaz_vrednost)

					if(kos1_ulaz_vrednost == 0 and kos3_ulaz_vrednost == 0 and kos2_ulaz_vrednost == 0):
						if (kos3_ostatak != 0):
							if p.koji_puni == 3:
								#state = GPIO.input(kos3_ulaz)
								kos3_ulaz_vrednost =  state3
								temp_hrana_silos = self.val
								if(kos3_ulaz_vrednost == 1):
									pass
								#	GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
								#	GPIO.output(hrana2_pin, 1)
								#	GPIO.output(dotur_pin, 0)
								print "Kos 3: " + str(kos3_ulaz_vrednost)
		
		
			if(punjenje1 < 0):
				punjenje1 = 0
			if(punjenje2 < 0):
				punjenje2 = 0
			if(punjenje3 < 0):
				punjenje3 = 0

			self.btnKg_sipaj1.setText(str(punjenje1) + " Kg")
			self.btnKg_sipaj2.setText(str(punjenje2) + " Kg")
			self.btnKg_sipaj3.setText(str(punjenje3) + " Kg")

			#punjenje kosa 1
			if(kos1_ulaz_vrednost == 1):
				global punjenje1
				punjenje1 = temp_hrana_silos - self.val + kos1_brojac*delta_kilaza_za_kos 

				if(kos1_ostatak > delta_kilaza_za_kos):

					if(temp_hrana_silos - self.val > delta_kilaza_za_kos and temp_hrana_silos - self.val < delta_kilaza_za_kos+10):
						global kos1_brojac
						global kos1_ostatak

						kos1_brojac = kos1_brojac + 1
						kos1_ostatak = kos1_ostatak - delta_kilaza_za_kos
						print "U kosu 1 ostalo: " + str(kos1_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)
						temp_hrana_silos = temp_hrana_silos - delta_kilaza_za_kos
				else:

					if(temp_hrana_silos - self.val > kos1_ostatak):
						global kos1_brojac
						global kos1_ostatak

						kos1_ostatak = 0
						print "U kosu 1 ostalo: " + str(kos1_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						kos1_brojac = kos1_brojac + 1
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)

			#punjenje kosa 2
			if(kos2_ulaz_vrednost == 1):
				global punjenje2
				punjenje2 = temp_hrana_silos - self.val + kos2_brojac*delta_kilaza_za_kos 

				if(kos2_ostatak > delta_kilaza_za_kos):

					if(temp_hrana_silos - self.val > delta_kilaza_za_kos and temp_hrana_silos - self.val < delta_kilaza_za_kos + 10):
						global kos2_brojac
						global kos2_ostatak

						kos2_brojac = kos2_brojac + 1
						kos2_ostatak = kos2_ostatak - delta_kilaza_za_kos
						print "U kosu 2 ostalo: " + str(kos2_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						temp_hrana_silos = temp_hrana_silos - delta_kilaza_za_kos
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)
				else:

					if(temp_hrana_silos - self.val > kos2_ostatak):
						global kos2_brojac
						global kos2_ostatak

						kos2_ostatak = 0
						kos2_brojac = kos2_brojac + 1
						print "U kosu 2 ostalo: " + str(kos2_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)

			#punjenje kosa 3
			if(kos3_ulaz_vrednost == 1):
				global punjenje3
				punjenje3 = temp_hrana_silos - self.val + kos3_brojac*delta_kilaza_za_kos 

				if(kos3_ostatak > delta_kilaza_za_kos):

					if(temp_hrana_silos - self.val > delta_kilaza_za_kos and temp_hrana_silos - self.val < delta_kilaza_za_kos + 10):
						global kos3_brojac
						global kos3_ostatak

						kos3_brojac = kos3_brojac + 1
						kos3_ostatak = kos3_ostatak - delta_kilaza_za_kos
						print "U kosu 3 ostalo: " + str(kos3_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)
						temp_hrana_silos = temp_hrana_silos - delta_kilaza_za_kos
				else:
	
					if(temp_hrana_silos - self.val > kos3_ostatak):
						global kos3_brojac
						global kos3_ostatak

						kos3_ostatak = 0
						kos3_brojac = kos3_brojac + 1
						print "U kosu 3 ostalo: " + str(kos3_ostatak)
						kos1_ulaz_vrednost = 0
						kos2_ulaz_vrednost = 0
						kos3_ulaz_vrednost = 0
						#GPIO.output(hrana1_pin, 1) #pali prvi kos ako je ulaz na jedinici
						#GPIO.output(hrana2_pin, 1)
						#GPIO.output(dotur_pin, 1)

	def back_click(self):
		self.close()

	def tariraj(self):
		self.popup = Tara_Form()
		self.popup.showFullScreen()

	def otvori_tastaturu_silos(self):
		self.popup = Tastatura_Form("silos")
		self.popup.showFullScreen()

	def otvori_tastaturu_kos1(self):
		self.popup = Tastatura_Form("kos1")
		self.popup.showFullScreen()

	def otvori_tastaturu_kos2(self):
		self.popup = Tastatura_Form("kos2")
		self.popup.showFullScreen()


	def otvori_tastaturu_kos3(self):
		self.popup = Tastatura_Form("kos3")
		self.popup.showFullScreen()


class Tara_Form(QMainWindow): #Temperatura
	def __init__(self, parent = None):
		super(Tara_Form, self).__init__(parent)
		self.resize(800, 480)
		self.setStyleSheet('''
	background-color:  black;
''')
		#self.setCursor(QCursor(Qt.BlankCursor))
		#self.hx = HX711(24, 8)
		#self.hx.set_reference_unit(tara) #bilo je 92
		#self.hx.reset()

		openn = open("tara.txt", "r")
		self.g = openn.read()
		global greska
		greska = int(self.g)
		openn.close()

		self.btn9 = QPushButton(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), self)
		self.btn9.resize(260, 70)
		self.btn9.move(5 + 265 + 265,5)
		self.btn9.setStyleSheet('''
		background-color:  black;
		color:  white;
		font-size: 25px;

''')
		self.vreme = QTimer()
		self.vreme.timeout.connect(self.refresh)
		self.vreme.start(1000)

	def refresh(self):
		self.btn9.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
		#self.val = self.hx.get_weight(5) - greska
		self.val = 50
		self.btn2.setText(str(self.val) + " grama")
		#self.hx.power_down()
		#self.hx.power_up()

	def back_click(self):
		self.close()

	def tariraj(self):
		#self.val = self.hx.get_weight(5)
		self.val = 333
		#self.hx.power_down()
		#self.hx.power_up()
		global greska
		greska = self.val
		openn = open("tara.txt", "w")
		openn.write(str(greska))
		openn.close()


class Tastatura_Form(QMainWindow): #TASTATURA
	def __init__(self, naslov, parent = None):
		super(Tastatura_Form, self).__init__(parent)
		if(jel_nam_treba_strelica == 0):
			self.setCursor(QCursor(Qt.BlankCursor)) #da nema strelicu
		self.resize(800, 480)
		self.setStyleSheet('''
			background-color:  white;
''')
		global potvrdi_cmd
		potvrdi_cmd = naslov
		self.y = 85
		self.x = 5 + 265 + 265

		self.stil = ''' 
		border: 4px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
					'''
		self.btn1 = QPushButton("1", self)
		self.btn1.move(self.x, self.y)
		self.btn1.resize(81, 70)
		self.btn1.clicked.connect(self.btn1_click)
		self.btn1.setStyleSheet(self.stil)
		self.btn2 = QPushButton("2", self)
		self.btn2.move(self.x + 86, self.y)
		self.btn2.resize(81, 70)
		self.btn2.clicked.connect(self.btn2_click)
		self.btn2.setStyleSheet(self.stil)

		self.btn3 = QPushButton("3", self)
		self.btn3.move(self.x + 86 + 86, self.y)
		self.btn3.resize(81, 70)
		self.btn3.clicked.connect(self.btn3_click)
		self.btn3.setStyleSheet(self.stil)
		self.btn4 = QPushButton("4", self)
		self.btn4.move(self.x, self.y + 75)
		self.btn4.resize(81, 70)
		self.btn4.clicked.connect(self.btn4_click)
		self.btn4.setStyleSheet(self.stil)

		self.btn5 = QPushButton("5", self)
		self.btn5.clicked.connect(self.btn5_click)
		self.btn5.move(self.x + 86, self.y + 75)
		self.btn5.resize(81, 70)
		self.btn5.setStyleSheet(self.stil)

		self.btn6 = QPushButton("6", self)
		self.btn6.move(self.x + 86 + 86, self.y + 75)
		self.btn6.resize(81, 70)
		self.btn6.clicked.connect(self.btn6_click)
		self.btn6.setStyleSheet(self.stil)

		self.btn7 = QPushButton("7", self)
		self.btn7.move(self.x, self.y + 75 + 75)
		self.btn7.resize(81, 70)
		self.btn7.clicked.connect(self.btn7_click)
		self.btn7.setStyleSheet(self.stil)

		self.btn8 = QPushButton("8", self)
		self.btn8.move(self.x + 86, self.y + 75 + 75)
		self.btn8.resize(81, 70)
		self.btn8.clicked.connect(self.btn8_click)
		self.btn8.setStyleSheet(self.stil)

		self.btn9 = QPushButton("9", self)
		self.btn9.move(self.x + 86 + 86, self.y + 75 + 75)
		self.btn9.resize(81, 70)
		self.btn9.clicked.connect(self.btn9_click)
		self.btn9.setStyleSheet(self.stil)

		self.btn0 = QPushButton("0", self)
		self.btn0.move(self.x, self.y + 75 + 75 + 75)
		self.btn0.resize(167, 70 )
		self.btn0.clicked.connect(self.btn0_click)
		self.btn0.setStyleSheet(self.stil)

		self.btnzarez = QPushButton(".", self)
		self.btnzarez.move(self.x + 86 + 86, self.y + 75 + 75 + 75)
		self.btnzarez.resize(81, 70)
		self.btnzarez.clicked.connect(self.btnzarez_click)
		self.btnzarez.setStyleSheet(self.stil)
		self.setStyleSheet('''
			background-color: white;
''')
		self.back = QPushButton("Nazad", self) #buton za nazad
		self.back.resize(260, 70)
		self.back.move(5+265 + 265, 405)
		self.back.clicked.connect(self.back_click)
		self.back.setStyleSheet("""
		border: 5px solid  #cc0000;
		border-radius: 25px;
		background-color:  white;
		color:  black;
		font-size: 25px;
""")

		self.obrisi = QPushButton("Obrisi", self) #buton za nazad
		self.obrisi.resize(260, 70)
		self.obrisi.move(5+265, 405)
		self.obrisi.clicked.connect(self.obrisi_click)
		self.obrisi.setStyleSheet("""
		border: 5px solid  #cc0000;
		border-radius: 25px;
		background-color:  white;
		color:  black;
		font-size: 25px;
""")

		self.potvrdi = QPushButton("Potvrdi", self) #buton za nazad
		self.potvrdi.resize(260, 70)
		self.potvrdi.move(5, 405)
		self.potvrdi.clicked.connect(self.potvrdi_click)
		self.potvrdi.setStyleSheet(self.stil)

		self.logo = QPixmap('logo.png')
		self.icon = QIcon(self.logo)

		self.logo_btn = QPushButton("", self)
		self.logo_btn.resize(200, 50)
		self.logo_btn.move(5, 5)
		self.logo_btn.setIcon(self.icon)
		self.logo_btn.setIconSize(QSize(200, 200))
		self.logo_btn.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')

		if(naslov == "silos"):
			naslov_string = "Silos"
		elif(naslov == "kos2"):
			naslov_string = "Kos 2"
		elif(naslov == "kos3"):
			naslov_string = "Kos 3"
		elif(naslov == "kos1"):
			naslov_string = "Kos 1"
		elif(naslov == "delta_kilaza"):
			naslov_string = "Delta Kilaza"
		elif(naslov == "broj_koka"):
			naslov_string = "Broj Koka"
		elif(naslov == "broj_petlova"):
			naslov_string = "Broj Petlova"
		elif(naslov == "duzina_dotura"):
			naslov_string = "Duzina Dotura"
		elif(naslov == "maksimum_za_kos"):
			naslov_string = "Maksimum kos"
		elif(naslov == "sekunde"):
			naslov_string = "Podesi sekunde"
		elif(naslov == "masa"):
			naslov_string = "Masa"

		self.naslov = QPushButton(naslov_string, self)
		self.naslov.resize(260, 70)
		self.naslov.move(5 + 265,5)
		self.naslov.setStyleSheet(self.stil)

		self.unos = QPushButton("0", self)
		self.unos.resize(260, 70)
		self.unos.move(5 + 265, 85)
		self.unos.setStyleSheet(self.stil)
		self.radio_button_select = 0 #nula je za kolicinu hrane u kosu
		self.type = ''


	def kolicina_silos_def(self):
		self.radio_button_select = 0

	def centralni_kos_def(self):
		self.radio_button_select = 1
	def back_click(self):
		self.close()

	def btn1_click(self):
		self.type = self.type + '1'
		self.unos.setText(self.type)

	def btn2_click(self):
		self.type = self.type + '2'
		self.unos.setText(self.type)

	def btn3_click(self):
		self.type = self.type + '3'
		self.unos.setText(self.type)

	def btn4_click(self):
		self.type = self.type + '4'
		self.unos.setText(self.type)

	def btn5_click(self):
		self.type = self.type + '5'
		self.unos.setText(self.type)

	def btn6_click(self):
		self.type = self.type + '6'
		self.unos.setText(self.type)

	def btn7_click(self):
		self.type = self.type + '7'
		self.unos.setText(self.type)

	def btn8_click(self):
		self.type = self.type + '8'
		self.unos.setText(self.type)

	def btn9_click(self):
		self.type = self.type + '9'
		self.unos.setText(self.type)

	def btnzarez_click(self):
		self.type = self.type + '.'
		self.unos.setText(self.type)

	def btn0_click(self):
		self.type = self.type + '0'
		self.unos.setText(self.type)

	def obrisi_click(self):
		self.type = ''
		self.unos.setText(self.type)

	def potvrdi_click(self):
		if(potvrdi_cmd == "silos"):
			
			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global hrana_silos
			hrana_silos = int(self.string)

			citaj = file("silos_hrana.txt", "w")
			citaj.write(str(hrana_silos))
			citaj.close()

		if(potvrdi_cmd == "kos1"):

			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global hrana_kos1
			hrana_kos1 = int(self.string)

			citaj = file("kos1_hrana.txt", "w")
			citaj.write(str(hrana_kos1))
			citaj.close()


		if(potvrdi_cmd == "kos2"):
			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global hrana_kos2
			hrana_kos2 = int(self.string)

			citaj = file("kos2_hrana.txt", "w")
			citaj.write(str(hrana_kos2))
			citaj.close()

		if(potvrdi_cmd == "kos3"):
			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global hrana_kos3
			hrana_kos3 = int(self.string)

			citaj = file("kos3_hrana.txt", "w")
			citaj.write(str(hrana_kos3))
			citaj.close()

		if(potvrdi_cmd == "delta_kilaza"):
			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global delta_kilaza_za_kos
			delta_kilaza_za_kos = int(self.string)

			citaj = file("delta_kilaza.txt", "w")
			citaj.write(str(delta_kilaza_za_kos))
			citaj.close()

		if(potvrdi_cmd == "maksimum_za_kos"):
			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global maksimum_glavni_kos
			maksimum_glavni_kos = int(self.string)

			citaj = file("maksimum_glavni_kos.txt", "w")
			citaj.write(str(maksimum_glavni_kos))
			citaj.close()

		if(potvrdi_cmd == "sekunde"):

			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global sekunde_vremenske_rucne_komande
			sekunde_vremenske_rucne_komande = int(self.string)

		if(potvrdi_cmd == "masa"):


			self.string = self.unos.text()
			if(self.string == ''):
				self.string = '0'

			global masa_rucne_komande
			masa_rucne_komande = int(self.string)
			

		self.close()

class Popup(QMainWindow): #TASTATURA
	def __init__(self, naslov, parent = None):
		super(Popup, self).__init__(parent)
		if(jel_nam_treba_strelica == 0):
			self.setCursor(QCursor(Qt.BlankCursor)) #da nema strelicu
		self.resize(800, 480)
		self.setStyleSheet('''
			background-color:  white;
''')

		self.stil = ''' 
		border: 4px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  #800080;
		font-size: 25px;
					'''

		self.poruka = QPushButton("Proces hranjenja \nuspesno zavrsen", self) #buton za nazad
		self.poruka.resize(450 , 300)
		self.poruka.move(800/2 - 225, 480/2 - 150, )
		self.poruka.clicked.connect(self.potvrdi_click)
		self.poruka.setStyleSheet(''' 
		border: 4px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  #800080;
		font-size: 40px;
					''')

		self.potvrdi = QPushButton("Potvrdi", self) #buton za nazad
		self.potvrdi.resize(260, 70)
		self.potvrdi.move(800/2-260/2, 405)
		self.potvrdi.clicked.connect(self.potvrdi_click)
		self.potvrdi.setStyleSheet(self.stil)

	def potvrdi_click(self):
		self.close()

class Podesavanja_Form(QMainWindow): #forma za podesavanja i rucne komande
	def __init__(self, parent = None):
		super(Podesavanja_Form, self).__init__(parent)

		if(jel_nam_treba_strelica == 0):
			self.setCursor(QCursor(Qt.BlankCursor)) #da nema strelicu
		self.resize(800, 480)
		self.setStyleSheet('''
			background-color:  white;
''')


		self.stil = ''' 
		border: 4px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px'''

		self.potvrdi = QPushButton("Podesavanja", self) #buton za nazad
		self.potvrdi.resize(260, 70)
		self.potvrdi.move(5+5+260, 5)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.potvrdi.setStyleSheet(self.stil)


		self.logo = QPixmap('logo.png')
		self.icon = QIcon(self.logo)

		self.logo_btn = QPushButton("", self)
		self.logo_btn.resize(200, 50)
		self.logo_btn.move(5, 5)
		self.logo_btn.setIcon(self.icon)
		self.logo_btn.setIconSize(QSize(200, 200))
		self.logo_btn.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')

		self.konfiguracija_koseva_button = QPushButton("Konfiguracija koseva", self) #buton za nazad
		self.konfiguracija_koseva_button.resize(260, 70)
		self.konfiguracija_koseva_button.move(5, 5+75)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.konfiguracija_koseva_button.setStyleSheet(''' 
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px''')

		self.delta_kilaza = QPushButton("Delta kilaza", self) #buton za nazad
		self.delta_kilaza.resize(260, 70)
		self.delta_kilaza.move(5, 5+75 + 75)
		self.delta_kilaza.clicked.connect(self.delta_kilaza_click)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.delta_kilaza.setStyleSheet(self.stil)


		self.maksimum_za_kos_button = QPushButton("Maksimum glavni kos", self) #buton za nazad
		self.maksimum_za_kos_button.resize(260, 70)
		self.maksimum_za_kos_button.move(5, 5+75+75+75)
		self.maksimum_za_kos_button.clicked.connect(self.maksimum_za_kos_click)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.maksimum_za_kos_button.setStyleSheet(self.stil)

		self.podaci_objekat_button = QPushButton("Podaci o objektu", self) #buton za nazad
		self.podaci_objekat_button.resize(260, 70)
		self.podaci_objekat_button.move(5+265, 5+75)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.podaci_objekat_button.setStyleSheet(''' 
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px''')

		self.broj_kokosaka_button = QPushButton("Broj koka", self) #buton za nazad
		self.broj_kokosaka_button.resize(260, 70)
		self.broj_kokosaka_button.move(5 + 265, 5+75 + 75)
		self.broj_kokosaka_button.clicked.connect(self.broj_kokosaka_click)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.broj_kokosaka_button.setStyleSheet(self.stil)


		self.broj_petlova_button = QPushButton("Broj petlova", self) #buton za nazad
		self.broj_petlova_button.resize(260, 70)
		self.broj_petlova_button.move(5 + 265, 5+75+75+75)
		self.broj_petlova_button.clicked.connect(self.broj_petlova_click)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.broj_petlova_button.setStyleSheet(self.stil)

		self.duzina_dotura_button = QPushButton("Duzina dotura", self) #buton za nazad
		self.duzina_dotura_button.resize(260, 70)
		self.duzina_dotura_button.move(5 + 265, 5+75+75+75 + 75)
		self.duzina_dotura_button.clicked.connect(self.duzina_dotura_click)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.duzina_dotura_button.setStyleSheet(self.stil)

		self.rucno_button = QPushButton("Rucno upravljanje", self) #buton za nazad
		self.rucno_button.resize(260, 70)
		self.rucno_button.move(5+265+265, 5+75)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.rucno_button .setStyleSheet(''' 
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px''')

		self.rucno_ukljuceno_button = QPushButton("Maseno", self) #buton za nazad
		self.rucno_ukljuceno_button.resize(260, 70)
		self.rucno_ukljuceno_button.move(5 + 265 + 265, 5+75 + 75)
		self.rucno_ukljuceno_button.clicked.connect(self.rucne_komande_maseno)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.rucno_ukljuceno_button.setStyleSheet(self.stil)

		self.rucno_kontrola_button = QPushButton("Vremenski", self) #buton za nazad
		self.rucno_kontrola_button.resize(260, 70)
		self.rucno_kontrola_button.move(5 + 265 + 265, 5+75+75+75)
		self.rucno_kontrola_button.clicked.connect(self.rucne_komande_vremenski)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.rucno_kontrola_button.setStyleSheet(self.stil)

		self.vaga_button = QPushButton("Vaga:", self) #buton za nazad
		self.vaga_button.resize(90, 70)
		self.vaga_button.move(5, 5+75+75+75 + 75 + 75)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.vaga_button.setStyleSheet(''' 
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px''')

		self.vaga_vrednost_button = QPushButton("0.0 Kg", self) #buton za nazad
		self.vaga_vrednost_button.resize(90, 70)
		self.vaga_vrednost_button.move(5+120, 5+75+75+75 + 75 + 75)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.vaga_vrednost_button.setStyleSheet(''' 
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px''')

		self.vaga_tara_button = QPushButton("Tara", self) #buton za nazad
		self.vaga_tara_button.resize(260, 70)
		self.vaga_tara_button.move(5   + 265, 5+75+75+75 + 75+75)
		self.vaga_tara_button.clicked.connect(self.tara)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.vaga_tara_button.setStyleSheet(self.stil)

		self.nazad_button = QPushButton("Nazad", self) #buton za nazad
		self.nazad_button.resize(260, 70)
		self.nazad_button.move(5   + 265 + 265, 5+75+75+75 + 75+75)
		self.nazad_button.clicked.connect(self.nazad)
		#self.potvrdi.clicked.connect(self.potvrdi_click)
		self.nazad_button.setStyleSheet("""
		border: 5px solid  #cc0000;
		border-radius: 25px;
		background-color:  white;
		color:  black;
		font-size: 25px;
""")

		#self.hx = HX711(24, 8)
		#self.hx.set_reference_unit(tara) #bilo je 92
		#self.hx.reset()

		self.vaga_meri_tred = QTimer()
		self.vaga_meri_tred.timeout.connect(self.vaga)
		self.vaga_meri_tred.start(500)

	def vaga(self):

		self.val = 300#round((self.hx.get_weight(5) - greska), 1)
		self.val = round((self.val/46), 1)#bilo 10 ili 100
		self.val = self.val*4#za kile bez 10 broj koliko nogu ima
		self.val = round(self.val, 1) #bilo pod int
		self.val = self.val - offset
		if(self.val < 0):
			self.val = 0
		self.vaga_vrednost_button.setText(str(int(self.val)) + " Kg")

	def rucne_komande_maseno(self):
		self.popup = Rucne_komande_form("maseno")
		self.popup.showFullScreen()

	def rucne_komande_vremenski(self):
		self.popup = Rucne_komande_form("vremenski")
		self.popup.showFullScreen()

	def duzina_dotura_click(self):
		self.popup = Tastatura_Form("duzina_dotura")
		self.popup.showFullScreen()

	def broj_petlova_click(self):
		self.popup = Tastatura_Form("broj_petlova")
		self.popup.showFullScreen()

	def broj_kokosaka_click(self):
		self.popup = Tastatura_Form("broj_koka")
		self.popup.showFullScreen()

	def maksimum_za_kos_click(self):
		self.popup = Tastatura_Form("maksimum_za_kos")
		self.popup.showFullScreen()


	def delta_kilaza_click(self):
		self.popup = Tastatura_Form("delta_kilaza")
		self.popup.showFullScreen()

	def tara(self):
		self.val = 11#round((self.hx.get_weight(5) - greska), 1)
		self.val = round((self.val/46), 1)#bilo 10 ili 100
		self.val = self.val*4#za kile bez 10 broj koliko nogu ima
		self.val = round(self.val, 1) #bilo pod int
		self.val = self.val - offset
		if(self.val < 0):
			self.val = 0

		global offset
		offset = self.val
	

	def nazad(self):
		self.close()

class Rucne_komande_form(QMainWindow): #forma za podesavanja i rucne komande
	def __init__(self, arg, parent = None):
		super(Rucne_komande_form, self).__init__(parent)

		if(jel_nam_treba_strelica == 0):
			self.setCursor(QCursor(Qt.BlankCursor)) #da nema strelicu
		self.resize(800, 480)
		self.setStyleSheet('''
			background-color:  white;
''')
		self.cmd = arg
		if(self.cmd == "vremenski"):
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK1 = QPushButton("K1", self)
			self.btnK1.setIcon(self.icon)
			self.btnK1.setIconSize(QSize(130, 130))
			self.btnK1.resize(200, 90)
			self.btnK1.clicked.connect(self.podesi_sekunde)
			self.btnK1.move(5 + 200,285+90)
			self.btnK1.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis1 = QPushButton("Hrana Kos 1", self)
			self.btnKg_ispis1.resize(160, 50)
			self.btnKg_ispis1.move(5+200+20, 5+60)
			self.btnKg_ispis1.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj1 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj1.resize(160, 50)
			self.btnKg_sipaj1.move(5+200+20, 5+100)
			self.btnKg_sipaj1.clicked.connect(self.sipaj1)
			self.btnKg_sipaj1.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg1 = QPushButton(str(sekunde_vremenske_rucne_komande) + " s", self)
			self.btnKg1.resize(160, 50)
			self.btnKg1.move(5+200+20, 300+25-5)
			self.btnKg1.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
	
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK2 = QPushButton("K2", self)
			self.btnK2.setIcon(self.icon)
			self.btnK2.setIconSize(QSize(130, 130))
			self.btnK2.resize(200, 90)
			self.btnK2.clicked.connect(self.podesi_sekunde)
			self.btnK2.move(5 + 200+200,285+90)
			self.btnK2.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis2 = QPushButton("Hrana Kos 2", self)
			self.btnKg_ispis2.resize(160, 50)
			self.btnKg_ispis2.move(5+400+20, 5+60)
			self.btnKg_ispis2.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj2 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj2.resize(160, 50)
			self.btnKg_sipaj2.move(5+400+20, 5+100)
			self.btnKg_sipaj2.clicked.connect(self.sipaj2)
			self.btnKg_sipaj2.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg2 = QPushButton(str(sekunde_vremenske_rucne_komande) + "  s", self)
			self.btnKg2.resize(160, 50)
			self.btnKg2.move(5+400+20, 300+25-5)
			self.btnKg2.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK3 = QPushButton("K3", self)
			self.btnK3.setIcon(self.icon)
			self.btnK3.setIconSize(QSize(130, 130))
			self.btnK3.resize(180, 90)
			self.btnK3.clicked.connect(self.podesi_sekunde)
			self.btnK3.move(5 + 200+200+200,285+90)
			self.btnK3.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis3 = QPushButton("Hrana Kos 3", self)
			self.btnKg_ispis3.resize(160, 50)
			self.btnKg_ispis3.move(600+20, 5+60-5)
			self.btnKg_ispis3.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj3 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj3.resize(160, 50)
			self.btnKg_sipaj3.move(600+20, 5+100)
			self.btnKg_sipaj3.clicked.connect(self.sipaj3)
			self.btnKg_sipaj3.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg3 = QPushButton(str(sekunde_vremenske_rucne_komande) + "  s", self)
			self.btnKg3.resize(160, 50)
			self.btnKg3.move(600+20, 300+25)
			self.btnKg3.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
		elif(self.cmd == "maseno"):
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK1 = QPushButton("K1", self)
			self.btnK1.setIcon(self.icon)
			self.btnK1.setIconSize(QSize(130, 130))
			self.btnK1.resize(200, 90)
			self.btnK1.clicked.connect(self.podesi_sekunde)
			self.btnK1.move(5 + 200,285+90)
			self.btnK1.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis1 = QPushButton("Hrana Kos 1", self)
			self.btnKg_ispis1.resize(160, 50)
			self.btnKg_ispis1.move(5+200+20, 5+60)
			self.btnKg_ispis1.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj1 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj1.resize(160, 50)
			self.btnKg_sipaj1.move(5+200+20, 5+100)
			self.btnKg_sipaj1.clicked.connect(self.sipaj1)
			self.btnKg_sipaj1.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg1 = QPushButton(str(masa_rucne_komande) + " kg", self)
			self.btnKg1.resize(160, 50)
			self.btnKg1.move(5+200+20, 300+25-5)
			self.btnKg1.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
	
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK2 = QPushButton("K2", self)
			self.btnK2.setIcon(self.icon)
			self.btnK2.setIconSize(QSize(130, 130))
			self.btnK2.resize(200, 90)
			self.btnK2.clicked.connect(self.podesi_sekunde)
			self.btnK2.move(5 + 200+200,285+90)
			self.btnK2.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis2 = QPushButton("Hrana Kos 2", self)
			self.btnKg_ispis2.resize(160, 50)
			self.btnKg_ispis2.move(5+400+20, 5+60)
			self.btnKg_ispis2.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj2 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj2.resize(160, 50)
			self.btnKg_sipaj2.move(5+400+20, 5+100)
			self.btnKg_sipaj2.clicked.connect(self.sipaj2)
			self.btnKg_sipaj2.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg2 = QPushButton(str(masa_rucne_komande) + "  kg", self)
			self.btnKg2.resize(160, 50)
			self.btnKg2.move(5+400+20, 300+25-5)
			self.btnKg2.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.kos_image = QPixmap('kos.png')
			self.icon = QIcon(self.kos_image)

			self.btnK3 = QPushButton("K3", self)
			self.btnK3.setIcon(self.icon)
			self.btnK3.setIconSize(QSize(130, 130))
			self.btnK3.resize(180, 90)
			self.btnK3.clicked.connect(self.podesi_sekunde)
			self.btnK3.move(5 + 200+200+200,285+90)
			self.btnK3.setStyleSheet('''
			border: 2px solid white;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg_ispis3 = QPushButton("Hrana Kos 3", self)
			self.btnKg_ispis3.resize(160, 50)
			self.btnKg_ispis3.move(600+20, 5+60-5)
			self.btnKg_ispis3.setStyleSheet('''
			border: 1px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 20px;
	''')
			self.btnKg_sipaj3 = QPushButton("SIPAJ", self)
			self.btnKg_sipaj3.resize(160, 50)
			self.btnKg_sipaj3.move(600+20, 5+100)
			self.btnKg_sipaj3.clicked.connect(self.sipaj3)
			self.btnKg_sipaj3.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')
			self.btnKg3 = QPushButton(str(masa_rucne_komande) + "  kg", self)
			self.btnKg3.resize(160, 50)
			self.btnKg3.move(600+20, 300+25)
			self.btnKg3.setStyleSheet('''
			border: 2px solid #800080;
			border-radius: 20px;
			background-color:  white;
			color:  black;
			font-size: 25px;
	''')

		self.podesavanja = QPushButton("X", self)
		self.podesavanja.resize(55, 55)
		self.podesavanja.clicked.connect(self.nazad)
		self.podesavanja.move(800-55,5)
		self.podesavanja.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  red;
		font-size: 35px;
		font-weight: bold;
''')

	
		self.logo = QPixmap('logo.png')
		self.icon = QIcon(self.logo)

		self.logo_btn = QPushButton("", self)
		self.logo_btn.resize(200, 50)
		self.logo_btn.move(5, 5)
		self.logo_btn.setIcon(self.icon)
		self.logo_btn.setIconSize(QSize(200, 200))
		self.logo_btn.setStyleSheet('''
		border: 4px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 25px;
''')
		if(self.cmd == "vremenski"):
			self.feeding_system = QPushButton("Vremenski", self)
		elif(self.cmd == "maseno"):
			self.feeding_system = QPushButton("Maseno", self)
		self.feeding_system.resize(350, 50)
		self.feeding_system.move(800/2-150+50, 5)
		self.feeding_system.setStyleSheet('''
		border: 3px solid white;
		border-radius: 20px;
		background-color:  white;
		color:  #800080;
		font-size: 35px;
		font-weight: bold;
''')

		self.btnKgSl = QPushButton("Hrana u silosu", self)
          	self.btnKgSl.resize(160, 50)
		self.btnKgSl.move(5+5, 5+60)
		self.btnKgSl.setStyleSheet('''
		border: 1px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')

		self.kos_image = QPixmap('Silos2.png')
		self.icon = QIcon(self.kos_image)

		self.btnS = QPushButton("", self)
		self.btnS.setIcon(self.icon)
		self.btnS.setIconSize(QSize(330, 300))
		self.btnS.resize(200, 300)
		#self.btnS.clicked.connect(self.otvori_tastaturu_silos)
		self.btnS.move(5,80+30+5+40)
		self.btnS.setStyleSheet('''
		background-color:  white;
		color:  black;
		font-size: 25px;
''')

		self.btnKgDo = QPushButton("Kg", self)
		self.btnKgDo.setText("")
		self.btnKgDo.resize(160, 50)
		self.btnKgDo.move(5+5, 5+100)
		self.btnKgDo.setStyleSheet('''
		border: 2px solid #800080;
		border-radius: 20px;
		background-color:  white;
		color:  black;
		font-size: 20px;
''')

		self.glavni_tred = QTimer()
		if(self.cmd == "vremenski"):
			self.glavni_tred.timeout.connect(self.glavni_tred_vreme)
		elif(self.cmd == "maseno"):
			self.glavni_tred.timeout.connect(self.glavni_tred_maseno)
		self.glavni_tred.start(1000)

		self.koji_kos_puni = 0
		self.jel_treba_da_puni = 0
		self.preostalo_sekundi = sekunde_vremenske_rucne_komande
		self.prvi_kos_ukupno = 0
		self.drugi_kos_ukupno = 0
		self.treci_kos_ukupno = 0
		self.temp_glavni_kos = 0

		#self.hx = HX711(24, 8)
		#self.hx.set_reference_unit(tara) #bilo je 92
		#self.hx.reset()

	def glavni_tred_maseno(self):

		self.btnKg1.setText(str(masa_rucne_komande) + "  kg")
		self.btnKg2.setText(str(masa_rucne_komande) + "  kg")
		self.btnKg3.setText(str(masa_rucne_komande) + "  kg")

		self.val = 1#round((self.hx.get_weight(5) - greska), 1)
		self.val = round((self.val/46), 1)#bilo 10 ili 100
		self.val = self.val*4#za kile bez 10 broj koliko nogu ima
		self.val = round(self.val, 1) #bilo pod int
		self.val = self.val - offset
		if(self.val < 0):
			self.val = 0

		print str(self.val - hrana_kos_prethodna_vrednost)
		if(abs(self.val - hrana_kos_prethodna_vrednost)  < 20):
			global hrana_kos_prethodna_vrednost
			hrana_kos_prethodna_vrednost = self.val
			self.btnKgDo.setText("DK: " + str(int(self.val)) + " Kg")#dk dnevna kolicina
	 		self.btnKgSl.setText("Silos: " + str(hrana_silos - int(self.val)) + " Kg")
			#self.hx.power_down()
			#self.hx.power_up()
		else:
			self.val = hrana_kos_prethodna_vrednost

		if (self.jel_treba_da_puni == 0):
			self.preostalo_sekundi = sekunde_vremenske_rucne_komande
			self.temp_glavni_kos = self.val
		else:

			if((self.temp_glavni_kos - self.val) >= masa_rucne_komande):
				#GPIO.output(hrana1_pin, 1)
				#GPIO.output(hrana2_pin, 1)
				#GPIO.output(dotur_pin, 1)

				self.jel_treba_da_puni = 0

				if(self.koji_kos_puni == 1):
					self.prvi_kos_ukupno = self.prvi_kos_ukupno + self.temp_glavni_kos - self.val
					self.btnKg_ispis1.setText(str(self.prvi_kos_ukupno) + " Kg")
				if(self.koji_kos_puni == 2):
					self.drugi_kos_ukupno = self.drugi_kos_ukupno + self.temp_glavni_kos - self.val
					self.btnKg_ispis2.setText(str(self.drugi_kos_ukupno) + " Kg")
				if(self.koji_kos_puni == 3):
					self.treci_kos_ukupno = self.treci_kos_ukupno + self.temp_glavni_kos - self.val
					self.btnKg_ispis3.setText(str(self.treci_kos_ukupno) + " Kg")

		


	def sipaj1(self):
		if self.jel_treba_da_puni == 0:
			self.koji_kos_puni = 1
			self.jel_treba_da_puni = 1
			#GPIO.output(hrana1_pin, 0) 
			#GPIO.output(hrana2_pin, 1)
			#GPIO.output(dotur_pin, 0)

	def sipaj2(self):
		if self.jel_treba_da_puni == 0:
			self.koji_kos_puni = 2
			self.jel_treba_da_puni = 1
			#GPIO.output(hrana1_pin, 1)
			#GPIO.output(hrana2_pin, 0)
			#GPIO.output(dotur_pin, 0)


	def sipaj3(self):
		if self.jel_treba_da_puni == 0:
			self.koji_kos_puni = 3
			self.jel_treba_da_puni = 1
			#GPIO.output(hrana1_pin, 1)
			#GPIO.output(hrana2_pin, 1)
			#GPIO.output(dotur_pin, 0)


	def glavni_tred_vreme(self):
		self.btnKg1.setText(str(sekunde_vremenske_rucne_komande) + "  s")
		self.btnKg2.setText(str(sekunde_vremenske_rucne_komande) + "  s")
		self.btnKg3.setText(str(sekunde_vremenske_rucne_komande) + "  s")

		self.val = 12232#round((self.hx.get_weight(5) - greska), 1)
		self.val = round((self.val/46), 1)#bilo 10 ili 100
		self.val = self.val*4#za kile bez 10 broj koliko nogu ima
		self.val = round(self.val, 1) #bilo pod int
		self.val = self.val - offset
		if(self.val < 0):
			self.val = 0

		print str(self.val - hrana_kos_prethodna_vrednost)
		if(abs(self.val - hrana_kos_prethodna_vrednost)  < 20):
			global hrana_kos_prethodna_vrednost
			hrana_kos_prethodna_vrednost = self.val
			self.btnKgDo.setText("DK: " + str(int(self.val)) + " Kg")#dk dnevna kolicina
	 		self.btnKgSl.setText("Silos: " + str(hrana_silos - int(self.val)) + " Kg")
			#self.hx.power_down()
			#self.hx.power_up()
		else:
			self.val = hrana_kos_prethodna_vrednost


		if (self.jel_treba_da_puni == 0):
			self.preostalo_sekundi = sekunde_vremenske_rucne_komande
			self.temp_glavni_kos = self.val
		else:
			if(self.koji_kos_puni == 1):
				self.btnKg1.setText(str(self.preostalo_sekundi) + "  s")

			elif(self.koji_kos_puni == 2):
				self.btnKg2.setText(str(self.preostalo_sekundi) + "  s")
				
			elif(self.koji_kos_puni == 3):
				self.btnKg3.setText(str(self.preostalo_sekundi) + "  s")

			if(self.preostalo_sekundi <= 0):
				self.jel_treba_da_puni = 0
				#GPIO.output(hrana1_pin, 1)
				#GPIO.output(hrana2_pin, 1)
				#GPIO.output(dotur_pin, 1)
				if(self.koji_kos_puni == 1):

					if ((self.temp_glavni_kos - self.val) > 2):
						self.prvi_kos_ukupno = self.prvi_kos_ukupno + self.temp_glavni_kos - self.val
						self.btnKg_ispis1.setText(str(self.prvi_kos_ukupno) + " Kg")
					else:
						self.btnKg_ispis1.setText(str(self.prvi_kos_ukupno) + " Kg")

				elif(self.koji_kos_puni == 2):

					if ((self.temp_glavni_kos - self.val) > 2):
						self.drugi_kos_ukupno = self.drugi_kos_ukupno + self.temp_glavni_kos - self.val
						self.btnKg_ispis2.setText(str(self.drugi_kos_ukupno) + " Kg")
					else:
						self.btnKg_ispis2.setText(str(self.drugi_kos_ukupno) + " Kg")

				elif(self.koji_kos_puni == 3):

					if ((self.temp_glavni_kos - self.val) > 2):
						self.treci_kos_ukupno = self.treci_kos_ukupno + self.temp_glavni_kos - self.val
						self.btnKg_ispis3.setText(str(self.treci_kos_ukupno) + " Kg")
					else:
						self.btnKg_ispis3.setText(str(self.treci_kos_ukupno) + " Kg")	
									
				self.preostalo_sekundi = sekunde_vremenske_rucne_komande

			self.preostalo_sekundi = self.preostalo_sekundi - 1

			if(self.preostalo_sekundi < 0):
				self.preostalo_sekundi = 0

		


	def podesi_sekunde(self):
		if(self.cmd == "vremenski"):
			self.popup = Tastatura_Form("sekunde")
			self.popup.showFullScreen()
		elif(self.cmd == "maseno"):
			self.popup = Tastatura_Form("masa")
			self.popup.showFullScreen()

	def nazad(self):
		#GPIO.output(hrana1_pin, 1)
		#GPIO.output(hrana2_pin, 1)
		#GPIO.output(dotur_pin, 1)
		self.close()



if __name__ == "__main__":
	app = QApplication(sys.argv)
	main = Window()
	main.showFullScreen()
	app.exec_()











