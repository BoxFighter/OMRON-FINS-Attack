import sys, socket, binascii, time, re

def send_receive(s,size,strdata):
    senddata = binascii.unhexlify(strdata)
    s.send(senddata)
    try:
        resp = s.recv(1024)
        return resp
    except socket.timeout:
        print('timeout:send commad but no respone')
    except socket.error:
        print ('socket error')

def validata(ip):
    ipdata = re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip)
    if not ipdata:
        return False
    return True

def check_len(string,length):
    if len(string) == length:
        return True
    else:
        return False

def str_to_ascii_hex(string):
    res = ''
    for s in string:
        res += str(hex(ord(s)))[2:]
    return res

def initconnect(s):
    init_address = send_receive(s,1024,'46494e530000000c000000000000000000000000')
    if len(init_address) > 23: 
        address_code = binascii.b2a_hex(init_address[23])
    else:
        print('len is wrong')
    getinfo = send_receive(s,1024,'46494e5300000015000000020000000080000200' + address_code + '000000ef05050100')
    # print(getinfo)
    print("Controller Model:" + getinfo[30:67])

def run_plc_cpu(s):
    send_receive(s,1024,'46494e5300000017000000020000000080000700000000ef00670401ffff04')

def run_monitor_cpu(s):
    send_receive(s,1024,'46494e5300000017000000020000000080000700000000ef00670401000002')

def stop_plc_cpu(s):
    send_receive(s,1024,'46494e5300000014000000020000000080000700000000ef00670402')

def reset_plc_cpu(s):
    send_receive(s,1024,'46494e5300000014000000020000000080000700000000ef00670403')

def loop_forced_set(s):
    iostate = raw_input('Set Forced State(on/off):')
    memory_area_code = raw_input('Memory Area Code(length:1 byte,please input hex values,like 30):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:2 byte,please input hex values,like 0064):')
    
    if iostate == 'on':
        coil_state_code = '0001'
        print('Forced set on')
    elif iostate == 'off':
        coil_state_code = '0000'
        print('Forced set off')
    else:
        print('Input io state is not supported')
    # else:
    #     print('Forced set on')
    #     coil_state_code = '01'
        #(to forced set CIO default physical output address(start at 100.00)
    for i in range(int(0),int(101)):
        # print('set default physical output at '+ memory_area_code +'out 100.%s' %(i))
        send_receive(s,1024,'46494e530000001c000000020000000080000700000000ef007e23010001' + coil_state_code + memory_area_code + beginning_address_byte + "%02x"%(i))

def cancel_forced_set(s):
    send_receive(s,1024,'46494e5300000014000000020000000080000700000000ef00722302')

def memory_area_read(s):
    print('IO Memory Area Code:Hex value(Data type)')
    print('CIO Area:0x30(Bit)/0xb0(Word), Work Area:0x31(Bit)/0xb1(Word),')
    print('Holding Bit Area:0x32(Bit)/0xb2(Word), Auxiliary Area:0x33(Bit)/0xb3(Word)')
    print('Data Memory Area:0x02(Bit)/0x82(Word), Timer/Counter Area:0x09(Completion Flag status)/0x89(PV),')
    print('Task flag:0x06(Bit)/0x46(Word), Index register:0xdc, Data register:0xbc, Clock pulses/Condition flags:0x07,')
    print('EM bank:0x20 to 0x2f or 0xe0 to 0xe8(Bit)/0xa0 to 0xaf or 0x50 to 0x5f or 0x60 to 0x68(Word)')
    print('EM current bank:0x0a(Bit)/0x98(Word)')

    memory_area_code = raw_input('\nMemory Area Code(length:1 byte,please input hex values,like 82):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:2 byte,please input hex values,like 0014):')
    num_bytes = raw_input('Number of items byte(length:2 byte,please input hex values,like 0003):')

    Bit  = ['30','31','32','33','02','09','06','07','0a','20','21','22','23','24','25','26','27','28','29','2a','2b','2c','2d','2e','2f','e0','e1','e2','e3','e4','e5','e6','e7','e8']
    Word = ['b0','b1','b2','b3','82','89','46','bc','98','a0','a1','a2','a3','a4','a5','a6','a7','a8','a9','aa','ab','ac','ad','ae','af','50','51','52','53','54','55','56','57','58','59','5a','5b','5c','5d','5e','5f','60','61','62','63','64','65','66','67','68']
    PV4  = ['dc']
    
    data_tip = ''
    data_type = 4
    if memory_area_code in Bit:
        data_type = 2
        data_tip = 'The data is binary values.For example,if you receive 00010101,it means 0111(binary).'
    elif memory_area_code in Word:
        data_type = 4
        data_tip = 'The data is hex values.'
    elif memory_area_code in PV4:
        data_type = 8

    if(check_len(memory_area_code,2) and check_len(beginning_address_byte,4) and check_len(num_bytes,4)):
        response = send_receive(s,1024,'46494e530000001a000000020000000080000700000000ef00670101' + memory_area_code + beginning_address_byte + '00' + num_bytes)
        print('\nData:')
        print(binascii.b2a_hex(response[-int('0x'+num_bytes,16)*data_type/2:]))
        print(data_tip)
    else:
        print('\nInput format is not supported')

def memory_area_write(s):
    print('IO Memory Area Code:Hex value(Data type)')
    print('CIO Area:0x30(Bit)/0xb0(Word), Work Area:0x31(Bit)/0xb1(Word),')
    print('Holding Bit Area:0x32(Bit)/0xb2(Word), Auxiliary Area:0x33(Bit)/0xb3(Word)')
    print('Data Memory Area:0x02(Bit)/0x82(Word), Timer/Counter Area:0x09(Completion Flag status)/0x89(PV),')
    print('EM bank:0x20 to 0x2f or 0xe0 to 0xe8(Bit)/0xa0 to 0xaf or 0x50 to 0x5f or 0x60 to 0x68(Word)')
    print('EM current bank:0x0a(Bit)/0x98(Word)')

    memory_area_code = raw_input('\nMemory Area Code(length:1 byte,please input hex values,like 82):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:2 byte,please input hex values,like 000a):')
    num_bytes = raw_input('Number of items byte(length:2 byte,please input hex values,like 0003):')
    data = raw_input('Data that you want to write:')

    Bit  = ['30','31','32','33','02','09','0a','20','21','22','23','24','25','26','27','28','29','2a','2b','2c','2d','2e','2f','e0','e1','e2','e3','e4','e5','e6','e7','e8']
    Word = ['b0','b1','b2','b3','82','89','98','a0','a1','a2','a3','a4','a5','a6','a7','a8','a9','aa','ab','ac','ad','ae','af','50','51','52','53','54','55','56','57','58','59','5a','5b','5c','5d','5e','5f','60','61','62','63','64','65','66','67','68']

    data_type = 4
    if memory_area_code in Bit:
        data_type = 2
    elif memory_area_code in Word:
        data_type = 4
    else:
        print('The Memory can not be writed.')
        return

    if(check_len(memory_area_code,2) and check_len(beginning_address_byte,4) and check_len(num_bytes,4)):
        if(check_len(data,data_type*int('0x'+num_bytes,16))):
            pk_len = str(hex(26+len(data)/2))[2:]
            length = ('0'*(8-len(pk_len))) + pk_len
            response = send_receive(s,1024,'46494e53'+ length +'000000020000000080000700000000ef00670102' + memory_area_code + beginning_address_byte + '00' + num_bytes + data)
            print('Write successful')
        else:
            print('Length of data is wrong')    
    else:
        print('\nInput format is not supported')

def memory_area_fill(s):
    print('IO Memory Area Code:Hex value(Data type)')
    print('CIO Area:0x30(Bit)/0xb0(Word), Work Area:0x31(Bit)/0xb1(Word),')
    print('Holding Bit Area:0x32(Bit)/0xb2(Word), Auxiliary Area:0x33(Bit)/0xb3(Word)')
    print('Data Memory Area:0x02(Bit)/0x82(Word), Timer/Counter Area:0x09(Completion Flag status)/0x89(PV),')
    print('EM bank:0x20 to 0x2f or 0xe0 to 0xe8(Bit)/0xa0 to 0xaf or 0x50 to 0x5f or 0x60 to 0x68(Word)')
    print('EM current bank:0x0a(Bit)/0x98(Word)')

    memory_area_code = raw_input('\nMemory Area Code(length:1 byte,please input hex values,like 82):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:2 byte,please input hex values,like 000a):')
    num_bytes = raw_input('Number of items byte(length:2 byte,please input hex values,like 0003):')
    data = raw_input('Data that you want to fill(hex value,like 0001):')

    Bit  = ['30','31','32','33','02','09','0a','20','21','22','23','24','25','26','27','28','29','2a','2b','2c','2d','2e','2f','e0','e1','e2','e3','e4','e5','e6','e7','e8']
    Word = ['b0','b1','b2','b3','82','89','98','a0','a1','a2','a3','a4','a5','a6','a7','a8','a9','aa','ab','ac','ad','ae','af','50','51','52','53','54','55','56','57','58','59','5a','5b','5c','5d','5e','5f','60','61','62','63','64','65','66','67','68']

    if memory_area_code in Bit or memory_area_code in Word:
        print('The Memory can be filled.')
    else:
        print('The Memory can not be filled.')
        return

    if(check_len(memory_area_code,2) and check_len(beginning_address_byte,4) and check_len(num_bytes,4) and check_len(data,4)):
        response = send_receive(s,1024,'46494e530000001c000000020000000080000700000000ef00670103' + memory_area_code + beginning_address_byte + '00' + num_bytes + data)
        print('Fill successful')    
    else:
        print('\nInput format is not supported')

def parameter_area_read(s):
    print('Parameter Area : 8000 (range:0000 to 0fff)\n'
        + 'PC Setup:8010 (range:0000 to 00ff)\n'
        + 'Peripheral Device settings:8011 (range:0000 to 00bf)\n'
        + 'I/O table:8012(range:0000 to 03ff)\n'
        + 'Routing tables:8013(range:0000 to 01ff)\n'
        + 'CPU Bus Unit settings:8002(range:0000 to 083F)')

    memory_area_code = raw_input('\nParameter Area Code(length:2 byte,please input hex values,like 8010):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:2 byte,please input hex values,like 0001):')
    num_bytes = raw_input('Number of items byte(length:2 byte,please input hex values,like 0003):') 

    if(check_len(memory_area_code,4) and check_len(beginning_address_byte,4) and check_len(num_bytes,4)):
        response = send_receive(s,1024,'46494e530000001a000000020000000080000700000000ef00670201' + memory_area_code + beginning_address_byte + num_bytes)
        print('\nData:')
        print(binascii.b2a_hex(response[-int('0x'+num_bytes,16)*2:]))
    else:
        print('\nInput format is not supported')

def program_area_read(s):
    # memory_area_code = raw_input('\nProgram Area Code(length:2 byte,please input hex values,like 8010):')
    beginning_address_byte = raw_input('Beginning Address Byte(length:4 byte,please input hex values,like 00000001):')
    num_bytes = raw_input('Number of items byte(length:2 byte,please input hex values,like 0003):')

    if(check_len(beginning_address_byte,8) and check_len(num_bytes,4)):
        response = send_receive(s,1024,'46494e530000001c000000020000000080000700000000ef00670306' + '0000' + beginning_address_byte + num_bytes)
        print('\nData:')
        print(binascii.b2a_hex(response[-int('0x'+num_bytes,16)*2:]))
    else:
        print('\nInput format is not supported')

def write_single_file(s):
    disk_no = raw_input('Disk no(length:2 byte,EM file memory:8001):')
    parameter_code = raw_input('Parameter Code(length:2 byte,range 0000 to 0003):')
    filename = raw_input('Filename(length <= 12 byte,like PROGRAMS.IDX):')
    file_position = raw_input('File Position(length:4 byte,please input hex values,like 00000000):')
    data_length = raw_input('Data length(length:2 byte,please input hex values,like 0010):')
    data = raw_input('Data:')
    directory_length = '0000'
    # directory_length = raw_input('Directory_length(2 byte,num of characters < 65,0000(hex) is root directory):')
    # directory_path = raw_input('Absolute directory path:')

    filename = str_to_ascii_hex(filename)
    if len(filename)<24:
        filename = filename + '00'*int((24-len(filename))/2)

    if(check_len(disk_no,4) and check_len(parameter_code,4) and check_len(filename,24) and check_len(file_position,8) and check_len(data_length,4) and check_len(data,2*int('0x'+data_length,16))):
        pk_len = str(hex(44+len(data)/2))[2:]
        length = ('0'*(8-len(pk_len))) + pk_len
        
        response = send_receive(s,1024,'46494e53' + length + '000000020000000080000700000000ef00672203' + disk_no + parameter_code + filename + file_position + data_length + data + directory_length)
        if binascii.b2a_hex(response[-2:])=='0000':
            print('Write single file successful.') 
        else:
            print('Error code:' + binascii.b2a_hex(response[-2:]))  
    else:
        print('\nInput format is not supported')

def read_single_file(s):
    disk_no = raw_input('Disk no(length:2 byte,EM file memory:8001):')
    filename = raw_input('Filename(length <= 12 byte,like PROGRAMS.IDX):')
    file_position = raw_input('File Position(length:4 byte,please input hex values,like 00000000):')
    data_length = raw_input('Data length(length:2 byte,please input hex values,like 0010):')
    directory_length = '0000'
    # directory_length = raw_input('Directory_length(2 byte,num of characters < 65,0000(hex) is root directory):')
    # directory_path = raw_input('Absolute directory path:')

    filename = str_to_ascii_hex(filename)
    if len(filename)<24:
        filename = filename + '20'*int((24-len(filename))/2)

    if(check_len(disk_no,4) and check_len(filename,24) and check_len(file_position,8) and check_len(data_length,4)):
        response = send_receive(s,1024,'46494e530000002a000000020000000080000700000000ef00672202' + disk_no + filename + file_position + data_length + directory_length)
        print('\nFile Data:')
        print(binascii.b2a_hex(response[-int('0x'+data_length,16):]))   
    else:
        print('\nInput format is not supported')

def delete_file(s):
    disk_no = raw_input('Disk no(length:2 byte,EM file memory:8001):')
    num_of_file = raw_input('Num of Files(length:2 byte,please input hex values,like 0000):')
    filename = raw_input('Filename(length <= 12 byte,like PROGRAMS.IDX):')
    directory_length = '0000'
    # directory_length = raw_input('Directory_length(2 byte,num of characters < 65,0000(hex) is root directory):')
    # directory_path = raw_input('Absolute directory path:')

    filename = str_to_ascii_hex(filename)
    if len(filename)<24:
        filename = filename + '20'*int((24-len(filename))/2)

    if(check_len(disk_no,4) and check_len(filename,24) and check_len(num_of_file,4)):
        response = send_receive(s,1024,'46494e5300000026000000020000000080000700000000ef00672205' + disk_no + num_of_file + filename + directory_length)
        if binascii.b2a_hex(response[-4:-2])=='0000':
            print('Delete file successful.') 
        else:
            print('Error code:' + binascii.b2a_hex(response[-2:]))    
    else:
        print('\nInput format is not supported')    

# Main function
if __name__ == "__main__":

    # Input PLC IP
    # print('Please input the PLC IP that you want to connect to:')
    # ip = raw_input('Target PLC IP:')
    ip = '192.168.20.122'
    OMRON_FINS_PORT = 9600
    if not validata(ip):
        print('IP format is wrong')
        sys.exit()

    # Init socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # # no respone timeout
    # s.settimeout(3)

    # Connect PLC
    s.connect((ip,OMRON_FINS_PORT))
    print('\nConnect to the PLC successful...')
    print('Start read device information...\n')
    initconnect(s)

    tip = ('\nOmron Fins Protocol Command Menu: \n'
            + '1-Run, 2-Stop, 3-Monitor, 4-Reset, \n'
            + '5-Set Forced State, 6-Cancel Forced State, \n'
            + '7-Memory Area Read, 8-Memory Area Write, 9-Memory Area Fill, \n'
            + '10-Parameter Area Read, 11-Program Area Read, \n'
            + '12-Write Single File, 13-Read Single File, 14-Delete File \n'
            + '88-End the script \n'
            + 'Please input the number of function you want the PLC to execute: \n')

    # Choose Command 
    while(True):
        print(tip)
        cmd = raw_input('Commad:')
        if cmd == '1':
            run_plc_cpu(s)
        elif cmd == '2':
            stop_plc_cpu(s)
        elif cmd == '3':
            run_monitor_cpu(s)
        elif cmd == '4':
            reset_plc_cpu(s)
        elif cmd == '5':
            loop_forced_set(s)
        elif cmd == '6':
            cancel_forced_set(s)
        elif cmd == '7':
            memory_area_read(s)
        elif cmd == '8':
            memory_area_write(s)
        elif cmd == '9':
            memory_area_fill(s)
        elif cmd == '10':
            parameter_area_read(s)
        elif cmd == '11':
            program_area_read(s)
        elif cmd == '12':
            write_single_file(s)
        elif cmd == '13':
            read_single_file(s)
        elif cmd == '14':
            delete_file(s)
        elif cmd == '88':
            print 'Byebye!'
            break
        else:
            print('Input command is not supported')
 
    # Close Socket   
    s.close()