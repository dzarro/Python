
# Zarro (ADNET) - last updated 8/9/17

# Read remote data with size bytes from socket and write to filename to current directory
# session - if string, write file to temp_dir/session 
# outdir - if string, write file to outdir


def rdwrt(sock,filename,size,**kwargs):
   
    import os, tempfile, sys
    
    session=None
    if 'session' in kwargs:
        session=kwargs['session']
    
    outdir=None
    if 'outdir' in kwargs:
        outdir=kwargs['outdir']

    verbose=False
    if 'verbose' in kwargs:
        verbose=True

    RECV_BUFFER=4096
    if 'RECV_BUFFER' in kwargs:
        RECV_BUFFER=long(kwargs['RECV_BUFFER'])

    if type(outdir) == str:
        tdir=expand_name(outdir)
    elif type(session) == str:
        tdir=os.path.join(tempfile.gettempdir(),session)
    else: 
        tdir=os.getcwd()

# create output directory if doesn't exist

    try: 
        os.makedirs(tdir)
        os.chmod(tdir,0o777)
    except OSError:
        sys.exc_clear()

# check for write access

    if not os.access(tdir,os.W_OK):
        result=None
        err='No write access to: '+tdir
        return (result,err)

    ifile=os.path.basename(filename)
    dsize=long(size)
    if verbose: print("Reading "+str(dsize)+" bytes of file: "+ifile)

    tfile=os.path.join(tdir,ifile) 
    handle = open(tfile,'wb')
    bsize=RECV_BUFFER
    wsize=0
    osize=dsize
    while True:
       if dsize <= bsize: bsize=dsize
       buff=sock.recv(bsize)
       if not buff: break
       rsize=len(buff) 
       handle.write(buff)
       wsize += rsize
       dsize -= rsize
       if dsize < 0 or wsize == osize: break
    handle.close()
    if wsize != osize:
        err='Error writing '+filename
        result=None
    else:
        result=tfile
        err=''
        if verbose: print("Wrote "+str(wsize)+" bytes to: "+tfile)
    return (result,err)

###########################################################################
# check if input directory exists and is writeable

def valid_dir(*arg):

    import os
    result=(False,False)
    if not valid_arg(*arg,label='Directory name') : return result
    dir=expand_name(arg[0])

    return (os.path.isdir(dir),os.access(dir,os.W_OK))

##############################################################################
# check if input is non-blank string
    
def valid_arg(*arg,**kwargs):

    label='Input'
    if 'label' in kwargs:
        label=kwargs['label']    
    
    if len(arg) == 0:
        print(label+" not entered.")
        return False
		
    input=arg[0]
    
    if not isinstance(input,str):
        print(label+" must be string.")
        return False
		
    if len(input.strip()) == 0:
        print(label+" must be non-blank string.")
        return False

    return True

##############################################################################
# expand path/file name

def expand_name(*arg):

    import os
    if not valid_arg(*arg): return None
    file=os.path.expandvars(arg[0])
    file=os.path.expanduser(file)
    file=os.path.normpath(file)
    return file

#############################################################################
# check if URL file/query has 'Content-Disposition'

def disp_url(*arg):

    import requests,re,sys
    if not valid_arg(*arg): return None

    try:
        r=requests.head(arg[0])
    except:
        return None

    dname=''
    if 'Content-Disposition' in r.headers:
        disp=r.headers['Content-Disposition']
        fname = re.findall("filename=(.+)", disp)
        dname=fname[0].replace('"','').replace(":","_")
        
    return dname

#############################################################################
# check if valid URL

def valid_url(*arg):
 
    from urlparse import urlparse
    if not valid_arg(*arg): return False

    result=urlparse(*arg)
    if result.scheme and result.hostname and result.path: return True 
    return False
    
##############################################################################
# useful socket functions

def send_data(sock, data):
    import struct
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_data(sock):
    import struct
    lengthbuf = recvall(sock, 4)
    if not lengthbuf: return None
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

##############################################################
# create temporary directory

def get_temp_dir():

    import tempfile,os,time,random,sys

    id=int(time.time())+random.randint(1,1000)
    session='s'+str(id)
    tdir=os.path.join(tempfile.gettempdir(),session)
 
# create output directory if doesn't exist

    try:
        os.makedirs(tdir)
        os.chmod(tdir,0o777)
    except OSError:
        sys.exc_clear()

    return tdir
##############################################################
# create random string

def str_random(length):
	import random, string
	characters = string.ascii_letters + string.digits
	random_string = ''.join(random.choice(characters) for _ in range(length))
	return random_string
	
##############################################################
# break string into equal chunks
	
def str_chunk(text, chunk_size):
	return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
	
###############################################################
# check if file is type binary

def is_binary(*args):
	import os
		
	if not valid(*args):
		return False
		
	file=args[0]
	if not isinstance(file,str):
		#print("Non-string input")
		return False
		
	if not os.path.exists(file):
		#print("File not found")
		return False
		
	fsize=os.path.getsize(file)
	buffer=min(fsize,1024)
	try:
		with open(file,'rb') as f:
			data=f.read(buffer)
		data.decode()
		
	except Exception as e:              		
		#print(f"Error: {e}")
		return True

	return False
	
################################################################
# check if input aregument is valid

def valid(*args):
	if len(args) == 0:
		return False
	try:
		args[0]
	except NameError:
		return False
	else:
		return True
	
################################################################
# return (host,port) address tuple
	
def	get_address(**kwargs):
	host = "localhost"
	if 'host' in kwargs:
		temp=kwargs['host']   
		if isinstance(temp,str):
			if len(temp) > 0:
				host=temp
		
	port=8500
	if 'port' in kwargs:	
		temp=kwargs['port']   
		if isinstance(temp,int): 
			port=temp
			
	address=(host,port)
	return address

