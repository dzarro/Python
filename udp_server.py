import socket,time,threading,client
buffer=1024

def stop(**kwargs):
	global jumble
	ip = "127.0.0.1"
	if 'ip' in kwargs:
		ip=kwargs['ip']   
		
	port=8500
	if 'port' in kwargs:
		sport=kwargs['port']   
		if isinstance(sport,int): 
			port=sport
	
	if 'saved' not in globals():
		print("Server: No sockets open")
		return
		
	if (ip,port) not in saved:
		print(f"Server: No socket open on {ip}:{port}")
		return
		
	s_thread=saved[(ip,port)]
	if not s_thread.is_alive():
		print(f"Server: Socket already closed on {ip}:{port}")
		del saved[(ip,port)]
		return
			
	jumble=random_string(10)
	client.send(jumble,ip=ip,port=port)
	
#####################################################################################
def valid(*args):
	if len(args) == 0:
		return False
	try:
		args[0]
	except NameError:
		return False
	else:
		return True
		
######################################################################################
def random_string(length):
	import random, string
	characters = string.ascii_letters + string.digits
	random_string = ''.join(random.choice(characters) for _ in range(length))
	return random_string
			
#####################################################################################		
def run(ip,port):
	
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.bind((ip, port))
		
		while True:
			try:
				data, addr = s.recvfrom(buffer)
				fname = data.decode()
				data, addr = s.recvfrom(buffer)
				asize=data.decode()
				bsize=int(asize)
				if bsize == 0:
					print(f'Server: Received text "{fname}"')
					if 'jumble' in globals():
						if fname == jumble:
							break
					continue
				print(f'Server: Receiving file "{fname}" with size {asize} bytes')
				data, addr = s.recvfrom(bsize)
				print(f"Server: Received {len(data)} bytes: {data.decode()}")
				
			except Exception as e:              		
					print(f"Error: {e}")
					continue
			
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		if 'saved' in globals():
			del saved[(ip,port)]
		print(f"Server: Socket closed on {ip}:{port}")
		
#####################################################################################	
def start(**kwargs):
	global event,saved
	
	ip = "127.0.0.1"
	if 'ip' in kwargs:
		ip=kwargs['ip']   
		
	port=8500
	if 'port' in kwargs:
		sport=kwargs['port']   
		if isinstance(sport,int): 
			port=sport
	
	if 'saved' not in globals():
		saved={}
			
	if (ip,port) in saved:
		s_thread=saved[(ip,port)]
		if s_thread.is_alive():
			print(f"Server: Socket already listening on {ip}:{port}")
			return
		else: 
			del saved[(ip,port)]
		
	print(f"Server: Socket listening for UDP packets on {ip}:{port}")
	event=threading.Event()
	thread=threading.Thread(target=run,args=(ip,port,))
	thread.start()
	saved[(ip,port)]=thread
		
#####################################################################################
if __name__ == "__main__":
    start()