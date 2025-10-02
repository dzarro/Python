import socket,time,threading,client
buffer=1024

def stop(**kwargs):
	ip = "127.0.0.1"
	if 'ip' in kwargs:
		ip=kwargs['ip']   
		
	port=8500
	if 'port' in kwargs:
		sport=kwargs['port']   
		if isinstance(sport,int): 
			port=sport
	
	if 'saved' not in globals():
		return
		
	if (ip,port) in saved:
		event=saved[(ip,port)]
		event.set()	
		client.send('stop.txt',ip=ip,port=port)
	
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
		
#####################################################################################		
def run(event,ip,port):
	
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.bind((ip, port))
		while not event.is_set():
			try:
				data, addr = s.recvfrom(buffer)
				fname = data.decode()
				data, addr = s.recvfrom(buffer)
				asize=data.decode()
				print(f'Receiving file "{fname}" with size {asize} bytes from {addr}')
				bsize=int(asize)
				data, addr = s.recvfrom(bsize)
				print(f"Received {len(data)} bytes from {addr}: {data.decode()}")
				print(f"Socket completed reading from {ip}:{port}")
			except Exception as e:              		
					print(f"Error: {e}")
					continue
			
		
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		if 'saved' in globals():
			del saved[(ip,port)]
		print("Server stopped")
		
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
		print(f"Socket already listening on {ip}:{port}")
		return
		
	print(f"Socket listening for UDP packets on {ip}:{port}")
	event=threading.Event()
	thread=threading.Thread(target=run,args=(event,ip,port,))
	thread.start()
	
	if (ip,port) not in saved:
		saved[(ip,port)]=event
		
#####################################################################################
if __name__ == "__main__":
    start()