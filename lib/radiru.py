CHANNEL_MAP = { 
	"FM"   : ("fm", 63343), 
	"NHK1" : ("r1", 63346), 
	"NHK2" : ("r2", 63342),
	"FM_SENDAI"   : ("hkfm", 108237),
	"NHK1_SENDAI" : ("hkr1", 108442),
	"FM_NAGOYA"   : ("ckfm", 108235),
	"NHK1_NAGOYA" : ("ckr1", 108234),
	"FM_OSAKA"    : ("bkfm", 108233),
	"NHK1_OSAKA"  : ("bkr1", 108232),
}

def getCommand1(config):
	chan, dial = CHANNEL_MAP[config.args.channel]
	config.P((chan, dial))
	
	# make m4a file
	command1 = """
%s \
--rtmp "rtmpe://netradio-%s-flash.nhk.jp" \
--playpath 'NetRadio_%s_flash@%d' \
--app "live" \
-W http://www3.nhk.or.jp/netradio/files/swf/rtmpe.swf \
--live \
-o %s \
--stop %d
""".strip() % (config.args.rtmpbin, chan, chan.upper(), dial, 
			config.filename, config.duration_sec)

	return command1
