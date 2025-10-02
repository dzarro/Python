
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
		print("Input file name not entered.")
		return 
		
	file_path=arg[0]
	if not isinstance(file_path,str):
		print("Input file name must be a string.")
		return 	
	
	if not os.path.exists(file_path):
		print(f'Input file "{file_path}" not found')
		return
	
	print(f'Sending file "{file_path}"')
	fsize=os.path.getsize(file_path)
	print(f'File size = {fsize} bytes')
	asize=str(fsize)
	bsize=asize.encode()
	fname=file_path.encode()
	
	try:
		with open(file_path, "rb") as f:
			data = f.read()
		print(f"Opening socket on {ip}:{port}")
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.connect((ip, port))
			s.sendall(fname)    # send file name
			s.sendall(bsize)    # send file size in bytes
			s.sendall(data)     # send file data ib bytes
			print("Sent data file")
		
	except Exception as e:
		print(f"Error: {e}")
		return 
		
	finally:
		print("Done")	
	 
if __name__ == "__main__":
    send(file_path)		