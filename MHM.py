#!/usr/bin/env python2.7

###												###
###		Macroscopic Health Monitoring Program	###
###												###

###
###	This is a program in a python script that assists
###	in the monitoring of an individual's health 
###	
###	This program is entirely dependent on the use of email
###	and the corresponding SMTP and IMAP protocols
###
###	MHM.py is the primary module, MHM_PAR.py is the 
###	referenced parameter file.

###
### Important Notes/Warnings Regarding Usage (INRU)
###
###		Note	[1]	This program, intended to be continually run on a server, 
###					is interfaced with via email message body as follows ::
###
###						To report data, use the following structure, without "[" or "]", "R" abbreviating "Report":
###								R~[[code]][[value to report]]
###
###						To request a plot, use the following structure, without "[" or "]", "RD" abbreviating "Request Data":
###								RD~[[code]]
###				
###						List of codes:
###						M 	-	mass
###
###
###		Known Bug	[1]	Will perform most recent command (perhaps again) when program is started.
###
###		Warning	[1]	Reports close (>1s) in time proximity to a recent report may be ignored.
###		Warning [2] Data plotted with order corresponding to log.
###

###
###	Revision Potential
###
###		Move to pandas for data handling (for scalability)
###

###
### Import necessary packages and scripts
###
import os
import sys
import imaplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
import smtplib
import time as t
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.dates as dates
from matplotlib.ticker import AutoMinorLocator as aml
import datetime as dt
from datetime import timedelta as dtd


###
### Initialize necessary values
###
import MHM_PAR as par
latestEmail_time	=	0
emailTimeKeeper		=	0
initialTimeStamp	=	t.time()

###
### Define Important Functions
###

def d(list_a,list_b,index,secToDay):
	###
	###	Calculates the derivative of _a with respect to _b at specified index via
	###	the changes of both from index provided less one to index provided.
	###
	### Thus, for i representing the index, calculated is (da/di)/(db/di), however
	###	the change in i, di, is unity in both ratios thus da/db is calculated.
	###
	###		Notes
	###
	###		If an index is not obtainable a value of zero is returned indicating that 
	###		no change is calculable at the index provided.
	###
	###		If secToDay is set to 1, _b is assumed to be of the dimension of time in
	###		the SI unit of seconds, and will be converted to the unit of days.
	###
	###		A return of errFlag indicates an index handling error or a change in _b of
	###		zero and data is deemed invalid.
	###
	errFlag = 999.321
	try :
		if ((index-1) >= 0) :
			numerator 	= (list_a[index]-list_a[index-1])
			denominator	= (list_b[index]-list_b[index-1])
			if (denominator == 0) :
				d = errFlag
			if (secToDay != 1)&(denominator != 0) :
				d = numerator/denominator
			if (secToDay == 1)&(denominator != 0) :
				d = numerator/( denominator/(60*60*24) )
		if ((index-1) < 0) :
			d = errFlag
	except IndexError :
		d = errFlag
	return d

def maxIndex(list):
	### Returns largest list index and the last list index
	return (len(list)-1)

def path():
	### Returns current directory in string format
	return os.path.dirname(os.path.realpath(sys.argv[0]))

def sendEmail(subject,messageBody,recipient,imagePath):
	###
	###	Sends an email.
	###
	### From out of scope accepts par.em_ac : sending account email address,
	###	par.em_pw : email password, par.em_smtp : SMTP server, par.em_smtpPort : SMTP port,
	###	par.em_imap : IMAP server.
	###
	###	Text messages may be sent via email. To do so,
	###	in place of the recipient, store the number 
	###	with _L appended such that "L" is the letter
	###	designated by this function to correspond to
	### the format of the SMS Gateway of the provider.
	###	Image sending not tested via SMS.
	###
	###	Example: recipient = "7894561230_A"
	###
	###	Note: SMS Gateway numbers are 10 digits, negl-
	###			ecting the common prepended "1", "+1"
	###
	###	AT&T: 		A [[Gateway confirmed, format OK]]
	###	Metro PCS:	M [[UNTESTED]]
	###	Sprint:		S [[UNTESTED]]
	###	T-Mobile:	T [[UNTESTED]]
	### Verizon:	V [[Gateway confirmed, potential format issues]]
	###	Virgin:		I [[Gateway confirmed, format OK]]
	###

	###	Prevent empty messages from sending
	if (messageBody != ""):

		###	Process phone number per specified provider
		phone = 0
		SMSG = {"A":"@txt.att.net","V":"@vtext.com","S":"@messaging.sprintpcs.com","T":"@tmomail.net","M":"@mymetropcs.com","I":"@vmobl.com"}
		if ("_" in recipient):
			if (recipient.split("_")[0].isdigit()):
				if (recipient.split("_")[1]):
					if (len(recipient.split("_")[1]) == 1):
						number = recipient.split("_")[0]
						gateway = recipient.split("_")[1]
						gateway = SMSG[gateway]
						recipient = number + gateway
						phone = 1

		### Taxonomical Logistics
		subjectPrepend 	= ""
		subjectAppend	= ""
		fromaddr = par.em_ac
		toaddr = recipient
		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = subjectPrepend + subject + subjectAppend
		
		###	Core Message Construction
		if (phone == 0):
			signature =	""+"\n\n[[ This message was sent by your fridge, it says you need to pick up some milk. ]]"
		if (phone == 1):
			signature =	""
		body = messageBody + signature

		### Attach Image I/A
		if imagePath == "":
			msg.attach(MIMEText(body, 'plain'))
		if imagePath != "":
			msg.attach(MIMEText('<b>%s</b><br><img src="cid:%s"><br>' % (body, imagePath), 'html'))
			fp = open(imagePath, 'rb')
			img = MIMEImage(fp.read())
			fp.close()
			img.add_header('Content-ID', '<{}>'.format(imagePath))
			msg.attach(img)
		
		### Digital Logistics
		server = smtplib.SMTP(par.em_smtp, eval(par.em_smtpPort))
		server.starttls()
		server.login(fromaddr, par.em_pw)
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
		server.quit()

def getFirstTextBlock(self, email_message_instance):
	maintype = email_message_instance.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message_instance.get_payload():
			if part.get_content_maintype() == 'text':
				return part.get_payload()
	elif maintype == 'text':
		return email_message_instance.get_payload()

###
###	Operational Loop
###
while 1:

	###	Log into inbox of mailbox
	MHM_mail = imaplib.IMAP4_SSL(par.em_imap)
	MHM_mail.login(par.em_ac,par.em_pw)
	MHM_mail.list()
	MHM_mail.select("inbox")

	### Retrieve raw, most recent email
	sResult, data	=	MHM_mail.uid('search',None,"ALL")
	ID_latest		=	data[0].split(" ")[-1]
	sResult, data	=	MHM_mail.uid('fetch',ID_latest,'(RFC822)')
	latestEmail_raw	=	data[0][1]

	### Parse most recent, raw email
	latestEmail			=	email.message_from_string(latestEmail_raw)
	latestEmail_sender	=	email.utils.parseaddr(latestEmail['From'])[1]
	latestEmail_body 	= 	getFirstTextBlock('',latestEmail)
	latestEmail_time	=	t.mktime(email.utils.parsedate(latestEmail['Date']))

	###	Abstract from latest email if not abstracted
	if (latestEmail_time > emailTimeKeeper) :
		emailTimeKeeper = latestEmail_time
		data = latestEmail_body.split(" ")
		for i in range(0,len(data)):

			###
			###	MHM_M operation
			###

			### If M value in retrieved data
			if ("R~M" in str(data[i])) :
				
				###	Data Acquisition
				data_M = eval(data[i].strip("R~M"))
				data_M = float(data_M)
				MHM_log_M	=	open("%s/MHM_log_M.txt"%(path()),"a+")
				MHM_log_M.write("%f\t%f\t%f\n"%(data_M,latestEmail_time,t.time()))
				MHM_log_M.close()

				###
				### Plotting and Processing Routine
				###

				### Define data
				MHM_log_M		=	open("%s/MHM_log_M.txt"%(path()),"r")
				M,time,logTime	=	np.loadtxt(MHM_log_M , delimiter="\t" , usecols=(0,1,2), unpack=True)

				### Format time into datetime ( : "dt" ) objects
				time_dt  = []
				if isinstance(time, np.float64):
					item = time
					time = []
					time.append(item)
				for j in range(0,len(time)) :
					time_dt.append(dt.datetime.fromtimestamp(time[j]))

				### Form Derivative Data
				max_ = maxIndex(time_dt)
				dMAvgList = []
				for o in range(0,len(time_dt)):		# For each data point -- UNOPTIMIZED -- Change: Remove earliest, append new
					dMAvg = 0
					dMCount = 0
					for e in range(0,(o+1)):		# Calculate rolling average derivative at event "o" with prior events
						if ( time_dt[e] >= (time_dt[o]-dtd(days=par.dM_dayRange)) ) :
							dM = d(M,time,e,1)
							if (dM != 999.321) :
								dMAvg = dMAvg + dM
								dMCount = dMCount +1
					if (dMCount != 0) :
						dMAvg = dMAvg/dMCount
					if (dMCount == 0) :
						dMAvg = 0
					dMAvgList.append(dMAvg)

				### Rebuild expanded ( : "exp" ) log -- UNOPTIMIZED -- Change: Only update, not rebuild
				open("%s/MHM_log_M_exp.txt"%(path()), 'w').close()
				MHM_log_M_exp = open("%s/MHM_log_M_exp.txt"%(path()),"a+")
				if isinstance(M, np.float64):
					item = M
					M = []
					M.append(item)
				if not (isinstance(logTime, list)) :
					item = logTime
					logTime = []
					logTime.append(item)
				if not (isinstance(logTime[0], float)) :
					logTime = logTime[0]
				for m in range(0,len(dMAvgList)):
					if (math.isnan(dMAvgList[m])) :
						dMAvgList[m] = 0.0
				for k in range(0,len(M)):
					MHM_log_M_exp.write("%f\t%f\t%f\t%f\t\n"%(M[k],time[k],dMAvgList[k],logTime[k]))
				MHM_log_M_exp.close()

				### Build plotting object
				canvas,drawn = plt.subplots(figsize=(8,5))
				plt.subplots_adjust(bottom=0.15)

				### Label plotting object
				today = dt.datetime.now()
				plt.title('Macroscopic Health Management')
				plt.xlabel('Day of Year %s [day]'%(today.year))
				
				### Draw primary parameter of plotting object
				drawn.tick_params('both' , length=7 , which='major')
				drawn.plot(time_dt , M , 'b-')
				drawn.set_ylabel('Weight [lbs]' , color='blue')
				# [[ No ylim set ]]

				### Draw derivative parameter of plotting object
				drawnDeriv = drawn.twinx()
				drawnDeriv.tick_params('both' , length=7 , which='major')
				drawnDeriv.plot(time_dt , dMAvgList , 'g-')
				drawnDeriv.set_ylabel('%d Day Average of Change in Weight [lbs/day]'%(par.dM_dayRange) , color="green")
				drawnDeriv.set_ylim(-3,3)

				### Format horizontal axis of plotting object
				plt.setp(drawn.get_xticklabels() , rotation='35')
				daily = dates.DayLocator()
				hourly = aml()
				dailyFormat = dates.DateFormatter('%b%d')
				drawn.xaxis.set_major_locator(daily)
				drawn.xaxis.set_major_formatter(dailyFormat)
				drawn.xaxis.set_minor_locator(hourly)
				prior = today - dtd(days=par.plotTimeRange)
				timeMax = dt.date(today.year , today.month , today.day+1)
				timeMin = dt.date(prior.year , prior.month , prior.day)
				drawn.set_xlim(timeMin,timeMax)

				### Draw primary parameter limit within plotting object
				drawn.axhline(y=par.M_goal , linewidth=10 , color='#00ff00', alpha=0.5)

				### Draw [ dM/dt = 0 ] line
				drawnDeriv.axhline(y=0 , linewidth=1 , color='#000000', alpha=0.5)				

				### Save drawn image and clear drawing frame
				plt.savefig('%s/MHM_plot_M.png'%(path()))
				plt.clf()
				plt.cla()

			### If data request in retrieved data, send plot ###
			if ("RD~M" in str(data[i])):
				sendEmail("MHM Plot Delivery","M[T]",par.dataRecipient,"%s/MHM_plot_M.png"%(path()))

	### End Of Routine operations
	t.sleep(5)
	print "[ MHM Operating ][ Uptime = %fminutes ]"%((t.time()-initialTimeStamp)/(60))
	par = reload(par)

###
###	Features to add:
###
###		-	Develop and implement Smoothing and Interpolation function
###		-	Goal line tolerance
###		-	Add [Software Redundancy]
###		-	Optimize for software performance
###		-	Verify email before program can be utilized against user list
###
