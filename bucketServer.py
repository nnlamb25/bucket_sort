import socket
import threading
import time
import sys
import struct
from random import randint

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


def client_thread(clientsocket, address, bucket, index):
    send_msg(clientsocket, bucket)
    
    buckets[index] = recv_msg(clientsocket)

    clientsocket.close()
    print "Recieved sorted array from " + str(address)

#Displays the array in a readable format
def printArray(array):
    ind = 0
    for i in array:
        sys.stdout.write(str(i))
        ind = ind + 1
        if ind == 12:
            sys.stdout.write('\n')
            ind = 0
        else:
            sys.stdout.write('\t')
    print '\n'

#Divides the array contents into buckets
def divideBuckets(array, buckets, bucketSize, numClients):
    for i in array:
        for c in range(numClients):
            if i < bucketSize * (c + 1):
                buckets[c] += ' ' + str(i)
                break

numClients = 0
numNums = 0

#Get user's input
while numClients < 1:
    numClients = input('Enter number of desired clients: ')
    if numClients < 1:
        print "Please enter a positive number."

while numNums < 1 or numNums < numClients:
    numNums = input('Enter desired size of array to sort: ')
    if numNums < 1:
        print "Please enter a positive number."
    elif numNums < numClients:
        print "Please enter a number larger than your number of desired clients."

#To determine the range each bucket will hold
bucketSize = int(numNums // numClients) + 1

#Makes an array of random ints the size the user specified
array = []
for _ in range(numNums):
    array.append(randint(1, numNums))

#Sets up the buckets
buckets = [""] * numClients
bucketThread = threading.Thread(group=None, target=divideBuckets, name=None,
                                        args=(array,buckets, bucketSize, numClients))
bucketThread.start()

print "UNSORTED LIST:"
printArray(array)

print "Dividing contents of array into buckets."
#Puts all the numbers in their bucket
bucketThread.join()

#Delete leading space
for i in range(len(buckets)):
    buckets[i] = buckets[i][1:]

#Sets up socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1088))
s.listen(numClients)

print "Ready to recieve clients."

threadsList = []
index = numClients - 1

#Sends the clients their lists to sort
while index >= 0:
    (clientsocket, address) = s.accept()
    print str(address) + " connected"
    if index > 0:
        print "Need " + str(index) + " more client(s) to continue.\n"
    else:
        print ''

    threadsList.append(threading.Thread(group=None, target=client_thread, name=None,
                                        args=(clientsocket, address, buckets[index], index)))
    index = index - 1

#Starts the sorting!
for i in range(numClients):
    threadsList[i].start()

#Waits for the clients to finish
for t in threadsList:
    t.join()

#Places the numbers back into an array
arrayIndex = 0
for b in buckets:
    for number in b.split(' '):
        array[arrayIndex] = int(number)
        arrayIndex += 1

#Prints the sorted list
print "\n\nSORTED LIST:"
printArray(array)
