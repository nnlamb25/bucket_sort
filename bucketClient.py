import socket
import thread
import struct

#Had help from: 
#https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.130', 1088))#('localhost', 1088))#

data = recv_msg(s)

print "Recieved."
array = map(int, data.split(' '))

array.sort()
print "Sorted."

st = str(array[0])
for i in range(1, len(array)):
    st += ' ' + str(array[i])

send_msg(s, st)

print "Sent."

s.close()
