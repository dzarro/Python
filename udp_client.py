
import socket,os,hashlib,tools
PACKET_SIZE=1024
TIMEOUT=0.5

def send(*arg,**kwargs):
	
	address=tools.address(**kwargs)
	MESSAGE_ID=tools.str_random(17)
	verbose = False
	if 'verbose' in kwargs:
		verbose = True
	
# Do some input sanity checks

	if len(arg) == 0:
		print("Client: Blank input")
		return 
		
	filename=arg[0]
	if not isinstance(filename,str):
		print("Client: Input must be a string")
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
	
	print(f"Client: Opening socket on {address[0]}:{address[1]}")
	sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(TIMEOUT)
	
# Send header

	print(f"Client: Sending header")
	sock.sendto(b'HEADER:' + header_data, address)
	
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
				print(f"Error: {e}")
				print("Client: Send failed")
				break
		f.close()
		if seq_num == num_packets:
			print(f'Client: File "{filename}" sent successfully')
	
	print("Client: Closing socket")
	sock.close()
		 
if __name__ == "__main__":
    send(filename)		