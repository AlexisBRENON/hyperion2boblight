import xbmc

def log_info(message):
	if message:
		xbmc.log(message, xbmc.LOGNOTICE)
	else:
		xbmc.log("", xbmc.LOGNOTICE)

def log_error(message):
	if message:
		xbmc.log(message, xbmc.LOGSEVERE)
	else:
		xbmc.log("", xbmc.LOGNOTICE)

def log_debug(message):
	if message:
		xbmc.log(message, xbmc.LOGDEBUG)
	else:
		xbmc.log("", xbmc.LOGNOTICE)

def log_warning(message):
	if message:
		xbmc.log(message, xbmc.LOGERROR)
	else:
		xbmc.log("", xbmc.LOGNOTICE)
