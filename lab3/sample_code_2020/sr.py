import config
import threading
import time
import udt
import util


# Selective Repeat reliable transport protocol.
class SelectiveRepeat:

  NO_PREV_ACK_MSG = "Don't have previous ACK to send, will wait for server to timeout."

  # "msg_handler" is used to deliver messages to application layer
  def __init__(self, local_port, remote_port, msg_handler):
    util.log("Starting up `Selective Repeat` protocol ... ")
    self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
    self.msg_handler = msg_handler
    self.sender_base = 0
    self.receiver_base = 0
    self.next_sequence_number = 0
    self.timers = [self.set_timer(None)]*config.WINDOW_SIZE # Each packet has an individual timer
    self.sender_window = [b'']*config.WINDOW_SIZE
    self.sender_ack_list = [0]*config.WINDOW_SIZE # This is to keep track of which packet has been ACK-ed

    self.receiver_window = [b'']*config.WINDOW_SIZE
    self.receiver_ack_list = [0]*config.WINDOW_SIZE

    self.receiver_last_ack = b''
    self.is_receiver = True
    self.sender_lock = threading.Lock()


  def set_timer(self, seq_number):
    return threading.Timer((config.TIMEOUT_MSEC/1000.0), self._timeout, [seq_number])


  # "send" is called by application. Return true on success, false otherwise.
  def send(self, msg):
    self.is_receiver = False
    # If seq num is within sender's window, data is packetized and sent
    if self.next_sequence_number < (self.sender_base + config.WINDOW_SIZE):
      self._send_helper(msg)
      return True
    else:
      util.log("Window is full. App data rejected.")
      time.sleep(1)
      return False


  # Helper fn for thread to send the next packet
  def _send_helper(self, msg):
    self.sender_lock.acquire()

    packet = util.make_packet(msg, config.MSG_TYPE_DATA, self.next_sequence_number)
    packet_data = util.extract_data(packet)
    index = (self.next_sequence_number - self.sender_base) % config.WINDOW_SIZE
    self.sender_window[index] = packet
    util.log("Sending data: " + util.pkt_to_string(packet_data))
    self.network_layer.send(packet) 

    # We are setting timer for each packet
    if self.timers[index].is_alive(): self.timers[index].cancel()
    self.timers[index] = self.set_timer(self.next_sequence_number)
    self.timers[index].start()
    self.next_sequence_number += 1
    
    self.sender_lock.release()
    return


  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    msg = self.network_layer.recv()
    msg_data = util.extract_data(msg)

    # Ignore corrupted messages
    if(msg_data.is_corrupt):
        return

    # If ACK message, assume its for sender
    if msg_data.msg_type == config.MSG_TYPE_ACK:
      self.sender_lock.acquire()
      index = (msg_data.seq_num - self.sender_base) % config.WINDOW_SIZE
      self.sender_ack_list[index] = 1 # Track the received ACK for each packet
      util.log("Received ACK: " + util.pkt_to_string(msg_data) + ". Cancelling timer...")
      self.timers[index].cancel() # Stop timer for packet when ACK received by sender

      # Move window base forward to unacknowledged packet with smallest seq number
      if(self.sender_base == msg_data.seq_num):
        util.log("ACK with seq # " + str(msg_data.seq_num) + " matches sender base.")
        count = 0

        # Get consequtive ack-ed packet
        for i in range(len(self.sender_ack_list)):
          # Once an unack detected, immediately break from loop
          if self.sender_ack_list[i] == 0:
              break
          else:
              count += 1
              self.sender_base += 1

        # shift all the required buffers and windows by number of consequtive ack-ed packets
        self.sender_window = self.sender_window[count:] + [b'']*count
        self.sender_ack_list = self.sender_ack_list[count:] + [0]*count
        self.timers = self.timers[count:] + [self.set_timer(None)]*count
        util.log("Sender window moved forward to " + str(self.sender_base) + "-" + str(self.sender_base + config.WINDOW_SIZE))
              
      self.sender_lock.release()

    # If DATA message, assume its for receiver
    else:
      assert msg_data.msg_type == config.MSG_TYPE_DATA
      util.log("Received DATA: " + util.pkt_to_string(msg_data))

      # If received packet is within window
      if self.receiver_base <=  msg_data.seq_num < self.receiver_base + config.WINDOW_SIZE:
        util.log("DATA Seq # " + str(msg_data.seq_num) + " is within window.")
        ack_pkt = util.make_packet(b'', config.MSG_TYPE_ACK, msg_data.seq_num)
        self.network_layer.send(ack_pkt)

        index = (msg_data.seq_num - self.receiver_base) % config.WINDOW_SIZE

        self.receiver_ack_list[index] = 1
        self.receiver_window[index] = msg_data.payload
        util.log("Sent ACK: " + util.pkt_to_string(util.extract_data(ack_pkt)))

        # Move window base forward to expected but not yet received packet
        if(self.receiver_base == msg_data.seq_num):
          util.log("DATA with seq # " + str(msg_data.seq_num) + " matches the receiver base.")
          count = 0
          for i in range(len(self.receiver_ack_list)):
            if self.receiver_ack_list[i] == 0:
                break
            else:
                count += 1
                self.receiver_base += 1
                self.msg_handler(self.receiver_window[i])

          self.receiver_window = self.receiver_window[count:] + [b'']*count
          self.receiver_ack_list = self.receiver_ack_list[count:] + [0]*count
          util.log("Receiver window moved forward to " + str(self.receiver_base) + "-" + str(self.receiver_base + config.WINDOW_SIZE))

      # When received packet is before receiver base
      elif (msg_data.seq_num  < self.receiver_base):
        # This is necessary because the receiver does not know whether the sender has actually received the ACK.
        # If the ACK was not received by the sender before timeout, the sender will treat it as a lost packet,
        # while the receiver will think that it has successfully sent the ACK. In this scenario, the receiver
        # window can be ahead of the sender window. Hence, the data received by the receiver can fall before
        # the receiver base, which to the receiver's knowledge, should have already been acknowledged. Thus, the
        # receiver must ACK this receiver data again.
        util.log("Received DATA. Seq # " + str(msg_data.seq_num) + " is smaller than receive base ")
        ack_pkt = util.make_packet(b'', config.MSG_TYPE_ACK, msg_data.seq_num)
        self.network_layer.send(ack_pkt)
        util.log("Resent ACK: " + util.pkt_to_string(util.extract_data(ack_pkt)))
      return


  # Cleanup resources.
  def shutdown(self):
    if not self.is_receiver: self._wait_for_last_ACK()
    for timer in self.timers:
      try:
          if timer.is_alive(): self.timer.cancel()
      except:
          continue
    util.log("Connection shutting down...")
    self.network_layer.shutdown()


  def _wait_for_last_ACK(self):
    while self.sender_base < self.next_sequence_number-1:
      util.log("Waiting for last ACK from receiver with sequence # "
              + str(int(self.next_sequence_number-1)) + ".")
      time.sleep(1)


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
