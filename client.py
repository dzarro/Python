
import socket,os

def send(*arg,**kwargs):
	
	ip = "127.0.0.1"
	if 'ip' in kwargs:
		ip=kwargs['ip']   
		
	port=8500
	if 'port' in kwargs:	
		sport=kwargs['port']   
		if isinstance(sport,int): 
			port=sport
	
# do some input sanity checks

	if len(arg) == 0:
		print("Client: Blank input")
		return 
		
	file_path=arg[0]
	if not isinstance(file_path,str):
		print("Client: Non-string input")
		return 	
	
	if os.path.exists(file_path):
		print(f'Client: Sending file "{file_path}"')
		fsize=os.path.getsize(file_path)
		print(f'Client: File size = {fsize} bytes')
		asize=str(fsize)
		file_flag=True
	else:
		print("Client: Sending text")
		asize=str(0)
		fsize=1024
		file_flag=False
	
	bsize=asize.encode()
	fname=file_path.encode()
	
	try:
		if file_flag:
			with open(file_path, "rb") as f:
				data = f.read()
				
		print(f"Client: Opening socket on {ip}:{port}")
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, fsize)
			s.connect((ip, port))
			s.sendall(fname)        # send text or file name
			s.sendall(bsize)        # send size in bytes
			if file_flag:     
				s.sendall(data)     # send file data in bytes
			print("Client: Sent data")
		
	except Exception as e:
		print(f"Client: Error: {e}")
		return 
		
	finally:
		print("Client: Done")	
	 
if __name__ == "__main__":
    send(file_path)		