
###		Macroscopic Health Monitoring Program



This is a program in a python script that assists in the monitoring of an individual's health.

This program is entirely dependent on the use of email and the corresponding SMTP and IMAP protocols.

MHM.py is the primary module, MHM_PAR.py is the referenced parameter file.



### Important Notes/Warnings Regarding Usage (INRU)

		Note	[1]	This program, intended to be continually run on a server, 
					is interfaced with via email message body as follows ::

						To report data, use the following structure, without "[" or "]", "R" abbreviating "Report":
								R~[[code]][[value to report]]

						To request a plot, use the following structure, without "[" or "]", "RD" abbreviating "Request Data":
								RD~[[code]]
				
						List of codes:
						M 	-	mass


		Known Bug	[1]	Will log most recent input (perhaps again) when program is started.

		Warning		[1]	Reports close (>1s) in time proximity to a recent report may be ignored.
		Warning		[2]	Data plotted with order corresponding to log.



###	Revision Potential
		Move to pandas for data handling (for scalability)

