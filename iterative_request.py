from utils import *


def get_ipv4(ip):
    res = ""
    i = 0
    while i < 8:
        temp = int(ip[i: i+2], 16)
        res += str(temp)
        i += 2
        if i < 8:
            res += '.'
    return res


def get_response_info(response, name_address):
    header = response[: 24]
    id = header[: 4]
    flag = header[4: 8]
    flags = bin(int(flag, 16))[2:].zfill(16)
    qdcount = int(header[8: 12], 16)
    ancount = int(header[12: 16], 16)
    nscount = int(header[16: 20], 16)
    arcount = int(header[20: 24], 16)

    qname = convert_name_address(name_address)

    Qtype = response[24 + len(qname): 28 + len(qname)]

    return qdcount, ancount, nscount, arcount, qname


def print_response_info(response, name_address):
    header = response[: 24]
    id = header[: 4]
    flag = header[4: 8]
    flags = bin(int(flag, 16))[2:].zfill(16)
    qr = flags[0]
    opcode = flags[1: 5]
    aa = flags[5]
    tc = flags[6]
    rd = flags[7]
    ra = flags[8]
    z = flags[9: 12]
    rcode = flags[12: 16]
    qdcount = int(header[8: 12], 16)
    ancount = int(header[12: 16], 16)
    nscount = int(header[16: 20], 16)
    arcount = int(header[20: 24], 16)
    print("\n*******")
    print("Header information:")
    print("ID:", id)

    if qr == '1':
        print("This message is a response.")
    else:
        print("This message is a query")

    print("Opcode:", opcode)

    if aa == '1':
        print("This server is an authority for the domain name {}".format(name_address))
    else:
        print("This server is not an authority for the domain name {}".format(name_address))

    if rd == '1':
        print("Recursion was desired for this request.")
    else:
        print("Recursion was not desired for this request.")

    if ra == '1':
        print("Recursion was available for this request.")
    else:
        print("Recursion was not available for this request.")

    if rcode == '0000':
        print("No error condition")
    elif rcode == '0001':
        print("Format error - the The name server was unable to interpret the query.")
    elif rcode == '0010':
        print("Server failure - The name server was unable to process this query due to a problem with the name server.")
    elif rcode == '0011':
        print("Name Error - Meaningful only for responses from an authoritative name server,"
              " this code signifies that the"
              " domain name referenced in the query does not exist.")
    elif rcode == '0100':
        print("Not Implemented - The name server does not support the requested kind of query.")
    else:
        print("Refused - The name server refuses to perform the specified operation "
              "for policy reasons.  For example, a name server may not wish to provide "
              "the information to the particular requester, or a name server may "
              "not wish to perform a particular operation (e.g., zone)")

    print("Number of questions:", qdcount)
    print("Number of answers:", ancount)
    print("Number of authority records:", nscount)
    print("Number of additional records:", arcount)

    qname = convert_name_address(name_address)
    # print(qname)
    # print(len(qname))
    Qtype = response[24+len(qname): 28+len(qname)]
    print("The query type is: ", Qtype)
    print("*******\n")

    return ancount, qname


def iterative_req(initial_ip, name_address):
    answer = 0
    ip_list = [initial_ip]
    while len(ip_list):
        message = ""
        response = ""
        ip = ip_list.pop()
        print(ip)
        message += build_message(name_address, '0001')
        response += send_udp_message(message, ip, 53)
        _, answer, nscount, arcount, qname = get_response_info(response, name_address)
        if answer > 0:
            return response
        l = 32 + len(qname)
        for i in range(nscount):
            _, s, _ = get_rdata(response, name_address, l)
            l += s

        for i in range(arcount):
            rdata, length, rtype = get_rdata(response, name_address, l)
            if rtype == 1:
                # print(rdata)
                d_ip = get_ipv4(rdata)
                print(d_ip)
                ip_list.append(d_ip)
            l += length

    print("could not find the ip")


def print_all_ips(response, name_address, answer, qname):
    l = 32 + len(qname)
    for i in range(answer):
        _, s, _ = get_rdata(response, name_address, l)
        rdata, length, rtype = get_rdata(response, name_address, l)
        if rtype == 1:
            # print(rdata)
            d_ip = get_ipv4(rdata)
            print(d_ip)
        l += s


if __name__ == '__main__':
    name_address = input("please enter the name address: ")
    response = iterative_req("198.41.0.4", name_address)
    if response is not None:
        answer, qname = print_response_info(response, name_address)
        print("ip address(es):")
        print_all_ips(response, name_address, answer, qname)
    #



