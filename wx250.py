import telnetlib
import smtplib
import httplib
import urllib
import time
import serial
import os

# Since the port may change at reboot, get the location.
# This is because there is a modem on the bus as well.
# If using telnet, set HOST to an ip address instead.

print "Getting converter name:"
#r = open ('/mnt/common/conv.txt','r')
#cn = r.read(7)
#r.close
#conv = "/dev/" + cn
conv = "/dev/ttyUSB0"
print conv

# At one time, I had a reverse-telnet serial to ethernet converter
# It was unreliable, so I just have a cheap Belkin "PDA" 
# serial to USB converter instead. It works well.

# conv should contain the full path of the converter
# open the appropriate port:

ser = serial.Serial(conv, 9600, timeout=120)
#tn = telnetlib.Telnet(HOST, port=1024, timeout=120)

# Time to open the files

f = open('/mnt/syno/weather/wx250.log','a')
s = open('/mnt/syno/weather/wx250.sig','a')

# Use WXFRQ to test
# Use WXALT for run
# Comment out one of the wx read lines, telnet OR serial.

# Set up the post method to Chirper

def fetch_url(url, params, method):
  params = urllib.urlencode(params)
  if method=="GET":
    f = urllib.urlopen(url+"?"+params)
  else:
    # Usually a POST
    f = urllib.urlopen(url, params)
  return (f.read(), f.code)

# The part that gets the serial data.
# When the radio sends WXALT, the data after is the alert.

def getwx():
        global wx
        global tmx
        global msg
        tmx="%.0f" % time.time()
#       wx = tn.read_until("\n")
        wx = ser.readline()
        xx=wx[:-1]
        yx=tmx + "     " + wx
#       f.write(yx)
        if "WXALT" in wx:
                f.write(yx)
                sendAlert()
                sendsms()
                pushover()
                chirper()
                f.flush()
        if "WXSIG" in wx:
                s.write(yx)
                s.flush()

        # done with processing (for now)
        # print the result to the screen. If 'screen' not active, then text is lost.
        print tmx + "     " + xx

def sendAlert():
        # Credentials (if needed)
        # Pulled from firstname.lastname program
        username = "agmailuser@gmail.com"
        password = "application-specific-password"

	# gmail now refuses "less secure applications"
	# I created a specific address for this sort of thing,
	# Since you ***MUST*** use 2FA and that's a pain
	# for a low-value email address.

        # Add some stuff
        msg = "Subject: Pi SAME Alert " + tmx + "\r\n\r\n"
        msg = msg + wx

        # The actual mail send
        fromaddr = "agmailuser@gmail.com"
        toaddrs = ["anaddress@somdomain.com"]
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
	
	# I don't use my internal email relay because
	# I want something external for this application.
	# Google has issues, but has excellent uptime.

        print "Message Sent"
        return

def pushover():
        # Directly from pushover's examples
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
          urllib.urlencode({
            "token": "pushover-token",
            "user": "pushover-user-id",
            "title": "Pi SAME Alert",
            "message": wx,
            "sound": "gamelan",
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        return

def chirper():
        # Yeah, it works. Don't be harsh on me
        url = "this wouldn't really matter to you"
        method = "POST"
        params = [("author_id", "5"), ("wall_id", "5"), ("privacy", "public"), ("content", wx)]

        [content, response_code] = fetch_url(url, params, method)

        if (response_code == 200):
          print content
        else:
          print response_code
        return
	
	# This is for an old self-hosted twitter-alike called socialstrap, and relies on an obsolete api plugin. Chances are if you're using
	# anything > Jessie, you will be unable to use this. Simply delete this section. I don't think you can even find the scripts nowadays. 


def sendsms():
        # The python stuff for sending xmpp refers to google talk...wtf?
        passcommand = "echo \"Pi SAME: " + wx + "\" | /usr/bin/sendxmpp -f ~/.senddisr -t --tls-ca-path=/etc/ssl/certs -- +11234567890@cheogram.com"
        os.system(passcommand)
        passcommand = "echo \"Pi SAME Alert: " + wx + "\" | /usr/bin/sendxmpp -f ~/.senddisr -t --tls-ca-path=/etc/ssl/certs -- some@xmpp.service"
        os.system(passcommand)
        msg = ""
        return

	# Cheogram is a cheap sms over xmpp service.
	# I called my home directory by name in the original, but ~ ***should*** work.
	# .senddisr is just my config file for sendxmpp

def tellmenow():
        # The python stuff for sending xmpp refers to google talk...wtf?
        passcommand = "echo \"WXS250 Weather Radio Monitor Program Initialize.\" | /usr/bin/sendxmpp -f ~/.senddisr -t --tls-ca-path=/etc/ssl/certs -- +11234567890@cheogram.com"
        os.system(passcommand)
        passcommand = "echo \"WXS250 Weather Radio Monitor Program Initialize.\" | /usr/bin/sendxmpp -f ~/.senddisr -t --tls-ca-path=/etc/ssl/certs -- some@xmpp.service"
        os.system(passcommand)
        msg = ""
        return

	# The reason this calls shell commands is because this was literally my first python program. I never changed it.
	# I realize I could have simply passed the message and avoided dual code blocks. 

# Tell the user we're running...

print "WXS250 Monitor Program"
print " "

msg = "WXS250 Monitor Program Initialize"
tellmenow()

# Start the program loop
while 1:
        getwx()

# All done...close it all thrice and be nice!

f.close()
s.close()
close()
quit()
