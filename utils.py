import binascii
import socket


def send_udp_message(message, address, port):

    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")


def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)


def convert_name_address(name_address):
    url = name_address.split(".")
    qname = ""
    for s in url:
        length = len(s)
        qname += hex(length).split('x')[-1].zfill(2)
        for c in s:
            asc = ord(c)
            qname += hex(asc).split('x')[-1].zfill(2)
    qname += '00'
    return qname


def build_message(name_address, qtype):
    id = 'aaaa'
    query_parameters = '0100'

    qdcount = '0001'
    ancount = '0000'
    nscount = '0000'
    arcount = '0000'

    query_header = id + query_parameters + qdcount + ancount + nscount + arcount

    qname = convert_name_address(name_address)
    qtype = qtype
    qclass = '0001'

    question = qname + qtype + qclass

    query = query_header + question

    return query


def get_ip(response):
    l = len(response)
    ip = response[l-8: l]
    res = ""
    i = 0
    while i < 8:
        temp = int(ip[i: i+2], 16)
        res += str(temp)
        i += 2
        if i < 8:
            res += '.'
    return res


def unhex(s):
    i = 0
    res = ''.join([chr(int(''.join(c), 16)) for c in zip(s[0::2], s[1::2])])
    # print(s)
    # print(type(s))
    return res


def get_rdata(response, name_address, start):
    qname = convert_name_address(name_address)
    l = len(qname)
    rdlength = int(response[20 + start: 24 + start], 16) * 2
    rtype = int(response[4 + start: 8 + start], 16)
    rdata = response[24+start: 24+start+rdlength]
    total_length = 24 + rdlength
    return rdata, total_length, rtype
