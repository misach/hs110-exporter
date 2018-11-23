import itertools
import time
import json
import socket
from struct import pack

from prometheus_client import Metric, CollectorRegistry, generate_latest, Gauge, Info

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
	key = 171
	result = pack('>I', len(string))
	for i in string:
		a = key ^ ord(i)
		key = a
		result += chr(a)
	return result

def decrypt(string):
	key = 171
	result = ""
	for i in string:
		a = key ^ ord(i)
		key = ord(i)
		result += chr(a)
	return result

def collect_hs110(host):
  """Scrape a host and return prometheus text format for it"""

  start = time.time()
  # Set target IP, port and command to send
  ip = host
  port = 9999
  cmd_energy = '{"emeter":{"get_realtime":{}}}'
  cmd_info = '{"system":{"get_sysinfo":{}}}'

  registry = CollectorRegistry()
  #registry.register(Collector())
  duration = Gauge('hs110_scrape_duration_seconds', 'Time this HS110 scrape took, in seconds', registry=registry)
  STATUS  = Gauge('hs110_status','HS110 status', registry=registry)

  # Send command and receive reply
  try:
    socket.setdefaulttimeout(10)
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.connect((ip, port))
    sock_tcp.send(encrypt(cmd_energy))
    data = sock_tcp.recv(2048)
    sock_tcp.send(encrypt(cmd_info))
    data_info = sock_tcp.recv(2048)
    sock_tcp.close()
    success = True
    STATUS.set(1)
  except socket.error:
    STATUS.set(0)
    sock_tcp.close()
    success = False

  if success == False:
    duration.set(time.time() - start)
    return generate_latest(registry)

  received_data = decrypt(data[4:])
  json_result = json.loads(received_data)
  realtime_data =  json_result['emeter']['get_realtime']
  # print "Received: ", received_data
  # print "Data: ", realtime_data['total_wh']

  received_data = decrypt(data_info[4:])
  json_result = json.loads(received_data)
  info_data =  json_result['system']['get_sysinfo']

  REQUEST_REALTIME_VOLTAGE  = Gauge('hs110_realtime_voltage_mv','HS110 realtime voltage mv', registry=registry)
  REQUEST_REALTIME_CURRENT  = Gauge('hs110_realtime_current_ma','HS110 realtime current ma', registry=registry)
  REQUEST_REALTIME_POWER    = Gauge('hs110_realtime_power_mw','HS110 realtime power mw', registry=registry)
  REQUEST_REALTIME_TOTAL_WH = Gauge('hs110_realtime_total_wh','HS110 realtime total wh', registry=registry)
  
  REQUEST_REALTIME_VOLTAGE.set(realtime_data['voltage_mv'])
  REQUEST_REALTIME_CURRENT.set(realtime_data['current_ma'])
  REQUEST_REALTIME_POWER.set(realtime_data['power_mw'])
  REQUEST_REALTIME_TOTAL_WH.set(realtime_data['total_wh'])

  REQEUST_SYSINFO = Info('hs110_system', 'HS110 System Informations',registry=registry)

  REQEUST_SYSINFO.info({'sw_ver': info_data['sw_ver'], 
                        'mac': info_data['mac'], 
                        'alias': info_data['alias'],
                        'deviceId': info_data['deviceId']})

  REQUEST_SYSINFO_RELAY_STATE = Gauge('hs110_sysinfo_relay_state','HS110 relay state', registry=registry)
  REQUEST_SYSINFO_RELAY_STATE.set(info_data['relay_state'])

  duration.set(time.time() - start)
  return generate_latest(registry)
