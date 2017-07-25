#!/usr/bin/env python2.7

###												###
###		Macroscopic Health Monitoring Program	###
###												###
###					Parameter File				###
###												###

###
### Define email account(s) for use with program
###

###  [[ Account 1 ]]  Email account used to collect and transmit processed data ::
# IMAP server address (gmail's is imap.gmail.com) :
em_imap		=	""
# SMTP server address (gmail's is smtp.gmail.com) :
em_smtp		=	""
# SMTP port (gmail's is 587) :
em_smtpPort	=	""
# Email address corresponding to account :
em_ac		=	""
# Email account password :
em_pw		=	""

###	[[ Account 2 ]] Email account to receive processed data
dataRecipient	=	""

###
###	Define key operative parameters
###

###	Time range in days to plot
plotTimeRange	=	10

### Weight goal
M_goal = 135.0
# NOT IN USE -- An amount to add or subtract from goal
M_tolerance = 5.0
