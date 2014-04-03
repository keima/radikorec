import os
import os.path
import re
import commands

import xml.etree.ElementTree as ET

cookiefile = "/tmp/radiko_cookie"

def login(config):
	if os.path.exists(cookiefile):
		is_login = check(config)
		if is_login:
			config.P("INFO: already logged-in")
			return
		else:
			config.P("WARN: cookie is expired or not login")

	login_id = config.args.id
	login_pass = config.args.password

	command = """\
wget -q \
--header="pragma: no-cache" \
--post-data='mail=%s&pass=%s' \
--no-check-certificate \
--save-cookies=%s \
https://radiko.jp/ap/member/login/login
""".strip() % (login_id, login_pass, cookiefile)

	r = config.R(command)

	if (r is not 0) or not os.path.exists(cookiefile):
		config.P("ERROR login failed")
		exit(1)

	config.P("login OK")


def logout(config):
	if not os.path.exists(cookiefile):
		return

	command = """\
wget -q \
--header="pragma: no-cache" \
--no-check-certificate \
--load-cookies=%s \
http://radiko.jp/ap/member/webapi/member/logout
""".strip() % (cookiefile)
	
	r = config.R(command)

	if (r is not 0):
		config.P("WARN: logout failed (not logged-in?)")

	config.R("rm " + cookiefile)
	config.P("logout OK")


def check(config):
	command = """\
wget -q \
--header="pragma: no-cache" \
--no-check-certificate \
--load-cookies=%s \
--save-cookies=%s \
http://radiko.jp/ap/member/webapi/member/login/check
""".strip() % (cookiefile,cookiefile)

	r = config.R(command)

	if(r is not 0):
		config.P("check is failed(LOGOUT or EXPIRED?)")
		return False
	else:
		config.P("check is success")
		return True


def getCommand1(config):
	playerurl="http://radiko.jp/player/swf/player_4.1.0.00.swf"
	playerfile="/tmp/radiko_player.swf"
	keyfile="/tmp/radiko_authkey.png"

	if not os.path.exists(playerfile):
		command = "wget -q -O %s %s" % (playerfile, playerurl)
		r = config.R(command)
		
		if r is not 0:
			config.P("ERROR failed to get player")
			exit(1)
			
	if not os.path.exists(keyfile):
		command = "swfextract -b 14 %s -o %s" % (playerfile, keyfile)
		r = config.R(command)	
		
		if r is not 0:
			config.P("ERROR failed to get key")
			exit(1)
			
	if os.path.exists("auth1_fms"):			
		config.R("rm auth1_fms")
	
	command = """\
wget -q \
--header="pragma: no-cache" \
--header="X-Radiko-App: pc_1" \
--header="X-Radiko-App-Version: 2.0.1" \
--header="X-Radiko-User: test-stream" \
--header="X-Radiko-Device: pc" \
--post-data='\r\n' \
--no-check-certificate \
--load-cookies=%s \
--save-headers \
https://radiko.jp/v2/api/auth1_fms
""".strip() % (cookiefile)

	r = config.R(command)

	if (r is not 0) or not os.path.exists("auth1_fms"):
		config.P("ERROR auth1 failed")
		exit(1)
		
	config.P("auth1 OK")			

	f = open("auth1_fms")
	text = f.read()
	config.P(text)
	f.close()	

	p1 = re.compile(r"x-radiko-authtoken: (.*)", re.I)
	m1 = p1.search(text)
	if not m1:
		config.P("ERROR authtoken not parsed")
		exit(1)
	authtoken = m1.group(1).strip()
	config.P("authtoken: %s" % authtoken)

	p2 = re.compile(r"x-radiko-keyoffset: (.*)", re.I)
	m2 = p2.search(text)
	if not m2:
		config.P("ERROR keyoffset not parsed")
		exit(1)
	keyoffset = int(m2.group(1))
	config.P("keyoffset: %d" % keyoffset)

	p3 = re.compile(r"x-radiko-keylength: (.*)", re.I)
	m3 = p3.search(text)
	if not m3:
		config.P("ERROR keylength not parsed")
		exit(1)
	keylength = int(m3.group(1))		
	config.P("keylength: %d" % keylength)
	
	command = """ \
dd \
if=%s \
bs=1 \
skip=%d \
count=%d \
2> /dev/null | base64
""".strip() % (keyfile, keyoffset, keylength)
	config.P(command)		
	partialkey = commands.getoutput(command)
	config.P("partialkey: %s" % (partialkey))

	config.R("rm auth1_fms")

	if os.path.exists("auth2_fms"):
		config.R("rm auth2_fms")
		
	command = """ \
wget -q \
--header="pragma: no-cache" \
--header="X-Radiko-App: pc_1" \
--header="X-Radiko-App-Version: 2.0.1" \
--header="X-Radiko-User: test-stream" \
--header="X-Radiko-Device: pc" \
--header="X-Radiko-Authtoken: %s" \
--header="X-Radiko-Partialkey: %s" \
--post-data='\r\n' \
--no-check-certificate \
--load-cookies=%s \
https://radiko.jp/v2/api/auth2_fms
""".strip() % (authtoken, partialkey, cookiefile)
	r = config.R(command)

	if (r is not 0) or not os.path.exists("auth2_fms"):
		config.P("ERROR auth2 failed")
		exit(1)
			
	config.P("auth2 OK")		

	f = open("auth2_fms")
	text = f.read()
	config.P(text)
	f.close()

	areaid = text.split(",")[0].strip()
	config.P("areaid: %s" % areaid)

	config.R("rm auth2_fms")

	channel = config.args.channel
	xmlFile = "%s.xml" % channel
	if os.path.exists(xmlFile):
		config.R("rm %s" % xmlFile)
		
	command = """ \
wget \
-q "http://radiko.jp/v2/station/stream_multi/%s"
""".strip() % xmlFile
	config.R(command)	

	f = open(xmlFile)		
	text = f.read()
	config.P(text)
	f.close()

	root = ET.fromstring(text)

	if config.args.premium:
		stream_url = root.find(".//item[@areafree='1']").text
	else:
		stream_url = root.find(".//item[@areafree='0']").text

	config.P("stream_url: %s" % stream_url)

	pat = re.compile(r"^(.+)://(.+?)/(.*)/(.*?)$")
	mat = pat.search(stream_url)
	A = mat.group(1)
	B = mat.group(2)
	C = mat.group(3)
	D = mat.group(4)	
	config.P("A: %s, B:%s, C:%s, D:%s" % (A, B, C, D))
	
	config.R("rm %s" % xmlFile)

	command = """ \
%s \
--rtmp %s \
--app %s \
--playpath %s \
-W %s \
-C S:"" -C S:"" -C S:"" -C S:%s \
--live \
-o %s \
--stop %d \
""".strip() % (
		config.args.rtmpbin,
		"%s://%s" % (A, B), C, D,
		playerurl, authtoken, config.filename, config.duration_sec)

	return command
