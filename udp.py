"""	

This function starts a UDP server and client on a specific host and port.

On the server:

>>> import udp 
>>> udp.start(host=host,port=port) # starts server in a non-blocking thread
>>> udp.stop(host=host,port=port)  # stops the server
 
On the client:
 
>>> import udp
>>> udp.send(filename,host=host,port=port)   # sends a file named filename or a text string called filename to the server
 
Note: host and port are optional parameters that default to localhost and 8500, respectively.
Ensure using same host and port on server and client.

Written: Zarro (dmzarro@gmail.com) - 24 October, 2025

"""

import socket,os,hashlib,threading
from tools import get_address,str_random,is_local_address

DOWNLOAD_DIR='C:\Python\Downloads'     # change this to desired download directory on server

######################################################################################

def start(**kwargs):
	"""Starts the server"""

	global saved
	address=get_address(**kwargs)
	
	if 'saved' not in globals():
		saved={}
			
	if address in saved:
		s_thread,started=saved[address]
		if s_thread.is_alive():
			print(f"Server: Socket already listening on {address}")
			return
			
	if not is_local_address(address):
		print(f"Server: Socket unavailable on {address}")
		return
		
	event=threading.Event()
	thread=threading.Thread(target=run,args=(address,))
	thread.start()
	saved[address]=(thread,True)
		
#####################################################################################

def stop(**kwargs):
	"""Stops the server"""

	address=get_address(**kwargs)
	
	override = False
	if 'override' in kwargs:
		temp = kwargs['override']
		if isinstance(temp,bool):
			override=temp
		
	if override:
		send('Stop',host=address[0],port=address[1])
		return
		
	if 'saved' not in globals():
		print("Server: No sockets open")
		return
		
	if address not in saved:
		print(f"Server: No socket open on {address}")
		return
		
	thread,status=saved[address]
	if not thread.is_alive() and not status:
		print(f"Server: Socket already closed on {address}")
		del saved[address]
		return

	saved[address]=(thread,False)
	send('Stop',host=address[0],port=address[1])
  
#######################################################################################	

def run(address):
	"""Opens a socket listening in a thread"""
	
	PACKET_SIZE = 1024 + 50 
	
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(address)
		print(f"Server: Socket listening for UDP packets on {address}")
	
		received_packets = {}
		total_packets = -1
		filename = None
		file_size = 0
	
		while True:
		
# Check for stop signal

			if 'saved' in globals():
				if address not in saved:
					break
				thread,status=saved[address]
				if not status:
					break
			
			try:
				data, addr = s.recvfrom(PACKET_SIZE+50)
		
# Handle different packet types
 
				if data.startswith(b'HEADER:'):
					header_data = data[7:]
					ftype,filename,fsize,total_packets,MESSAGE_ID = header_data.decode().split(',')
					file_size = int(fsize)
					total_packets = int(total_packets)
					if ftype == 'ASCII':
						print(f'Received text: "{filename}" on {address}')
					ack_packet = b'HACK:'+MESSAGE_ID.encode()
					s.sendto(ack_packet, addr)
					continue
					
# Separate packet components
# Verify MESSAGE_ID

				elif data.startswith(b'DATA:') and ftype == 'FILE':
					#print(f"Receiving file: {filename} with size: {file_size} bytes, # packets: {total_packets}")
					message_id = data[5:22]
					received_message_id=message_id.decode()
					if received_message_id != MESSAGE_ID:
						print("MESSAGE ID mismatch")
						continue 
					
# Verify checksum

					seq_num_bytes = data[22:30]
					checksum_start = data.find(b'CHKSUM:')
					chunk = data[30:checksum_start]
					received_checksum = data[checksum_start+7:]
			#	calculated_checksum = hashlib.md5(data[:checksum_start+7]).digest()\
					calculated_checksum = hashlib.md5(chunk).digest()
				
					if received_checksum != calculated_checksum:
						print(f"Checksum mismatch for packet {seq_num_bytes.decode()}. Packet corrupted.")
						continue
# Save chunk
					seq_num = int(seq_num_bytes)
					received_packets[seq_num] = chunk
                
# Send acknowledgement

					ack_packet = b'ACK:' + message_id + seq_num_bytes
					s.sendto(ack_packet, addr)
					#print(f"Acknowledged packet {seq_num}/{total_packets}")
				
# Check for completion

					if total_packets > 0 and len(received_packets) == total_packets:
						with open(os.path.join(DOWNLOAD_DIR,filename), 'wb') as f:
							for i in range(total_packets):
								f.write(received_packets[i])		
						print(f'File "{filename}" received successfully on {address}')
						received_packets = {}
						total_packets = -1
						
			except s.timeout:
				print("Socket timeout.")
			except Exception as e:              		
				print(f"Error: {e}")
				print("Transfer failed or incomplete")
			
	print(f"Server: Socket closed on {address}")
	#s.shutdown(socket.SHUT_WR)
	#s.close()
	del saved[address]
	
#######################################################################################		

def send(*arg,**kwargs):
	"""Sends data to the server"""
	
	PACKET_SIZE=1024
	TIMEOUT=0.5
	MESSAGE_ID=str_random(17)
	address=get_address(**kwargs)
	
	verbose=False
	if 'verbose' in kwargs:
		temp = kwargs['verbose']
		if isinstance(temp,bool):
			verbose=temp
	
# Do some input sanity checks

	if len(arg) == 0:
		print("Client: Blank input")
		return 
		
	filename=arg[0]
	if not isinstance(filename,str):
		print("Client: Input argument must be a string")
		return 	

# If filename is not a file, then assume it is text

	if os.path.exists(filename):
		print(f'Client: Sending file "{filename}"')
		fsize=os.path.getsize(filename)
		print(f'Client: File size = {fsize} bytes')
		ftype='FILE'
		fheader=os.path.basename(filename)
	else:
		print("Client: Sending text")
		fsize=len(filename)
		ftype='ASCII'
		fheader=filename
		
# Create header with send metadata

	num_packets=(fsize+PACKET_SIZE-1)//PACKET_SIZE
	print(f"Client: Number of packets = {num_packets}")
	header_data=f"{ftype},{fheader},{fsize},{num_packets},{MESSAGE_ID}".encode()
	
	print(f"Client: Opening socket on {address}")
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(TIMEOUT)
	
# Send header

		print(f"Client: Sending header")
		try:
			sock.sendto(b'HEADER:' + header_data, address)
			ack_packet, _ = sock.recvfrom(PACKET_SIZE)
			if ack_packet.startswith(b'HACK:'):
				print('Client: Received header acknowledgement')  
				message_id = ack_packet[5:]
				if message_id.decode() != MESSAGE_ID:
					print('Client: Header invalid')
					return
			else:
				print('Client: Failed to receive header acknowledgement')
				return
		except socket.timeout:
			print('Client: Timeout waiting for header acknowledgement')
			return
		except Exception as e:              		
			if verbose:
				print(f"Client: Error {e}")
			print(f"Client: No response from {address}")
			print("Client: Send failed")
			return
	
		if ftype == 'ASCII':
			print("Client: Text send successfully")
			
# Send data in chunks

		if ftype == 'FILE':
			f=open(filename, "rb") 
			seq_num=0
			while seq_num < num_packets:
		
				if verbose:
					print(f"Client: Sending packet {seq_num}/{num_packets}")
				chunk=f.read(PACKET_SIZE)
				if not chunk:
					break
		
# Send packet
	
				packet_data = b'DATA:' + MESSAGE_ID.encode() + str(seq_num).encode().zfill(8) + chunk
				checksum = hashlib.md5(chunk).digest()
				full_packet = packet_data + b'CHKSUM:' + checksum
				sock.sendto(full_packet, address)

# Wait for acknowledgement

				try:
					ack_packet, _ = sock.recvfrom(PACKET_SIZE)
					if ack_packet == b'ACK:' + MESSAGE_ID.encode() + str(seq_num).encode().zfill(8):
					#	print(f"Packet {seq_num}/{num_packets} acknowledged.")
						seq_num += 1
					else:
						print(f"Invalid ACK for packet {seq_num}. Retrying...")
				except socket.timeout:
					print(f"Timeout waiting for ACK for packet {seq_num}. Retrying...")
				except Exception as e:              		
					if verbose:
						print(f"Client: Error {e}")
					print("Client: Send failed")
					break
			f.close()
			if seq_num == num_packets:
				print(f'Client: File "{filename}" sent successfully')
	
	print("Client: Closing socket")
	
