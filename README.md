# radikorec
A Simple Radiko/Radiru Recorder

## Example
The command below nicely helps you learn English. Enjoy your life!
```
radikorec
--channel=NHK2
--duration=15
--prefix=BUSINESS_ENGLISH
--directory=/home/akira/radio
```

## Dependencies
* [rtmpdump](http://rtmpdump.mplayerhq.hu/) >= 2.4  
* [swftools](http://www.swftools.org/download.html)  
* ffmpeg   

## Install
`#make install`(recommended) or `#pip install radikorec`.

There are few programs you may have to build by yourself.  
run `$./compile` and then `#./setup`.

### Install at Ubuntu Server 14.04 LTS

- Before Install dependencies, install libraries
 + zlib1g-dev
 + libssl-dev
- Build and Install dependencies (rtmpdump and swftools)
 + `$ sudo ./compile`
 + `$ sudo ./setup`
- Install ffmpeg (not Libav)
 + `$ sudo add-apt-repository ppa:mc3man/trusty-media`
 + `$ sudo apt-get update`
 + `$ sudo apt-get install ffmpeg`
- Install radikorec
 + `$ sudo make install`
- If occur "ImportError: No module named setuptools" error when running make, try following instruction and retry `Install radikorec` section.
 + `$ wget http://peak.telecommunity.com/dist/ez_setup.py`
 + `$ sudo python ez_setup.py`
- Is install successful? Check it out!
 + `$ ./runtest`

## Test
First, `$./runtest` to see if it works.  
Starts to record streaming for 1 minute and stores it in /tmp is the correct behavior.  
Check for /tmp/radikorec.log which might help you.  
Any question will be welcome. Feel free to e-mail me (Japanese OK).

## Claim
Don't share the downloaded files with other persons.  
This program is only for self-use.

## Author
Akira Hayakawa (@akiradeveloper)  
ruby.wktk@gmail.com
