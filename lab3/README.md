# Networks Lab 3 - Implementing a Reliable Data Transfer Protocol

## About

In this lab, I have written an implementation of the Selective Repeat (SR) protocol to achieve reliable data transfer.

**Note: Make sure that you are using Python 3**

## How to run code

1. Open 2 terminals.

2. In the 1st terminal, run `python3 file_receiver.py sr <output file name>`

    For example,
    
    `python3 file_receiver.py sr output.txt`

3. In the 2nd terminal, run `python3 file_sender.py sr <input file name>`

    For example,

    `python3 file_sender.py sr test_file.txt`

4. After the program **sender program** shuts down, shut down the **receiver program** by using:

    `Ctrl + C`

You should be able to check that the contents of `output.txt` is the same as `test_file.txt`

## Code explanation

In SR, it is important to note that the **both the send and receiver** require a buffer and window, so that it will be able to keep track of whether a packet has successfully arrived at the sender or receiver ends.

This is done by initalizing:
```
self.sender_base = 0
self.receiver_base = 0
self.next_sequence_number = 0

self.sender_window = [b'']*config.WINDOW_SIZE
self.sender_ack_list = [0]*config.WINDOW_SIZE 

self.receiver_window = [b'']*config.WINDOW_SIZE
self.receiver_ack_list = [0]*config.WINDOW_SIZE
```

Also, the SR is different from the GBN and SS protocols as it requires a timer for each individual packet. The timers are first initialized to None
```
self.timers = [self.set_timer(None)]*config.WINDOW_SIZE
```

The **set_timer** function serves to create a timer for each packet with a **_timeout** callback function and the **_timeout** callback function is invoked whenever each packet times out. The timeout function serves to resend the lost individual packet and restarts the timer for that packet when doing so.
```
def set_timer(self, seq_number):
    return threading.Timer((config.TIMEOUT_MSEC/1000.0), self._timeout, [seq_number])

def _timeout(self, seq_number):
    util.log("Timeout! Resend lost packet sequence # " + str(seq_number))
    self.sender_lock.acquire()
    timer_index = (seq_number - self.sender_base) % config.WINDOW_SIZE
    if self.timers[timer_index].is_alive(): self.timers[timer_index].cancel()

    # Must restart timer when re-transmitting packet
    self.timers[timer_index] = self.set_timer(seq_number)
    pkt = self.sender_window[timer_index]
    self.network_layer.send(pkt)
    util.log("Resending packet: " + util.pkt_to_string(util.extract_data(pkt)))
    self.timers[timer_index].start() 
    self.sender_lock.release()
    return

```

For the sender, it first checks if the sequence number is within the sender's window, and calls the **_send_helper** function if so. The **_send_helper** function helps packetize the data and send it to the receiver. Once the data is sent, the timer for that packet is started and the sequence number is increased.
```
def _send_helper(self, msg):
    self.sender_lock.acquire()

    packet = util.make_packet(msg, config.MSG_TYPE_DATA, self.next_sequence_number)
    packet_data = util.extract_data(packet)
    index = (self.next_sequence_number - self.sender_base) % config.WINDOW_SIZE
    self.sender_window[index] = packet
    util.log("Sending data: " + util.pkt_to_string(packet_data))
    self.network_layer.send(packet) 

    if self.timers[index].is_alive(): self.timers[index].cancel()
    self.timers[index] = self.set_timer(self.next_sequence_number)
    self.timers[index].start()
    self.next_sequence_number += 1
    
    self.sender_lock.release()
    return
```

The **handle_arrival_msg** function contains what the sender will do when it receives an ACK message. When an ACK for a packet arrives, the sender basically stops the timer for that packet and moves the window base forward until it reaches an unack-ed packet.


For the **receiver side**, the code is also in the **handle_arrival_msg** function. When the data arrives, it first checks if the packet is within the receiver window. 

If within the window, it sends an ACK and updates the receiver window to indicate that it has sent out the ACK. It then moves the receiver window base forward until it meets an expected but not yet received packet.

However, if the received packet is before the receiver base, the receiver must send out an ACK packet to the sender again.