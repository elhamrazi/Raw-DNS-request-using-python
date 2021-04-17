from utils import *
from csv import *


def get_rddata(response, name_address):
    qname = convert_name_address(name_address)
    l = len(qname)
    rdlength = int(response[52 + l: 56 + l], 16) * 2
    rdata = response[56+l: 56+l+rdlength]
    return rdata


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
    # print("*******")
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
    # print("*******")

    return qdcount, ancount, nscount, arcount, qname


def print_all_answers(response, name_address, answer, qname):
    l = 32 + len(qname)
    x = ""
    for i in range(answer):
        _, s, _ = get_rdata(response, name_address, l)
        rdata, length, rtype = get_rdata(response, name_address, l)
        # print(rdata)
        h = unhex(rdata)
        if h is not None:
            print(h)
            x += ''.join([j if 128 > ord(j) > 31 else ' ' for j in h[2:]])
            x += " "
        l += s
    return x


with open('input.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    header = next(csv_reader)
    data = []
    if header is not None:
        for row in csv_reader:
            types = {'A': 1, 'NS': 2, 'CNAME': 3, 'TXT': 4, 'SOA': 5}
            name_address = row[0]
            # name_address = input("please enter the name address: ")
            message = ""
            response = ""
            t = types[row[1]]
            # t = int(input("please select query type:\n1-A\n2-NS\n3-CNAME\n4-TXT\n5-SOA "))
            if t == 1:
                print("Record type: A Address")
                message += build_message(name_address, '0001')
                response += send_udp_message(message, "1.1.1.1", 53)
                print("the ip address is:", get_ip(response))
                dic = {'name_address': name_address, 'record type': row[1], 'data': get_ip(response)}
            elif t == 2:
                print("Record type: CNAME")
                message += build_message(name_address, '0002')
                response += send_udp_message(message, "1.1.1.1", 53)

            elif t == 3:
                print("Record type: NS")
                message += build_message(name_address, '0005')
                response += send_udp_message(message, "1.1.1.1", 53)
            elif t == 4:
                print("Record type: TXT")
                message += build_message(name_address, '0010')
                response += send_udp_message(message, "1.1.1.1", 53)
            elif t == 5:
                print("Record type: SOA")
                message += build_message(name_address, '0006')
                response += send_udp_message(message, "1.1.1.1", 53)

            qdcount, ancount, nscount, arcount, qname = print_response_info(response, name_address)

            if t == 3:
                lst = print_all_answers(response, name_address, nscount, qname)
                dic = {'name_address': name_address, 'record type': row[1], 'data': lst}

            if t != 1 and t != 3:
                lst = print_all_answers(response, name_address, ancount, qname)
                # print(lst)
                dic = {'name_address': name_address, 'record type': row[1], 'data': lst}
            data.append(dic)
            print("--------------------------------------------------------\n")

    with open('output.csv', 'w', newline='') as file:
        names = ['name_address', 'record type', 'data']
        writer = DictWriter(file, fieldnames=names)
        writer.writeheader()
        for i in data:
            writer.writerow(i)

