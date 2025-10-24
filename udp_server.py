import socket,threading,os,hashlib,tools
import udp_client as client

DOWNLOAD_DIR='C:\Python\Downloads'
PACKET_SIZE = 1024 + 50 

def stop(**kwargs):

	address=tools.address(**kwargs)
	host=address[0]
	port=address[1]
	
	if 'saved' not in globals():
		print("Server: No sockets open")
		return
		
	if address not in saved:
		print(f"Server: No socket open on {host}:{port}")
		return
		
	s_thread,status=saved[address]
	if not s_thread.is_alive():
		print(f"Server: Socket already closed on {host}:{port}")
		del saved[address]
		return
		
	saved[address]=(s_thread,False)
	client.send('Stop',host=host,port=port)
	
#####################################################################################		
def run(address):
	
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(address)
	received_packets = {}
	total_packets = -1
	filename = None
	file_size = 0
	host=address[0]
	port=address[1]
	
	while True:
		
# Check for stop signal

		if 'saved' in globals():
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
					print(f"Received text: {filename} ")
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
					print(f'File "{filename}" received successfully.')
					received_packets = {}
					total_packets = -1
						
		except s.timeout:
			print("Socket timeout.")
		except Exception as e:              		
			print(f"Error: {e}")
			print("Transfer failed or incomplete")
			
	if 'saved' in globals():
		del saved[(host,port)]
	print(f"Server: Socket closed on {host}:{port}")
		
#####################################################################################	
def start(**kwargs):
	global saved
	
	address=tools.address(**kwargs)
	host=address[0]
	port=address[1]
	
	if 'saved' not in globals():
		saved={}
			
	if address in saved:
		s_thread,started=saved[address]
		if s_thread.is_alive():
			print(f"Server: Socket already listening on {host}:{port}")
			return
		else: 
			del saved[address]
		
	print(f"Server: Socket listening for UDP packets on {host}:{port}")
	event=threading.Event()
	thread=threading.Thread(target=run,args=(address,))
	thread.start()
	saved[(host,port)]=(thread,True)
		
#####################################################################################
if __name__ == "__main__":
    start()