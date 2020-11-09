#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket,time,random


class PLC_UDP:

    def __init__(self,ip,port):
        self.plc_ip = ip
        self.plc_port = port
        self.s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s1.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print('yooooooooooooooooooooooooo')

    def force_set(self,register_type,register_id):
        try:
            SET = "ST" + "20".decode("hex") + register_type + register_id + "0D".decode("hex")
            self.s1.sendto(SET.encode("ascii", "ignore"), (self.plc_ip, self.plc_port))
            print('force set',SET)
        except socket.error as e:
            print("Error -->"+str(e))

    def force_reset(self,register_type,register_id):
        try:
            RESET = "RS" + "20".decode("hex") + register_type + register_id + "0D".decode("hex")
            self.s1.sendto(RESET.encode("ascii", "ignore"), (self.plc_ip, self.plc_port))
        except socket.error as e:
            print("Error -->"+str(e))


    # def data_read(self,register_type,register_id):
    #     for i in range(0,3,1):
    #         try:
    #             READ = "RD" + "20".decode("hex") + register_type + register_id + "0D".decode("hex")
    #             self.server.sendall(READ)
    #             time.sleep(0.2)
    #             Rx = self.server.recv(1024)
    #             self.rec_msg = Rx
    #             print 'The register value is : ' + Rx 

    #             if Rx == "E1\r\n":
    #                 print "Command error"
    #             elif Rx == "E0\r\n":
    #                 print "Register number error"
    #             return

    #         except socket.error as e:
    #             print("Error -->"+str(e))
    #             self.server.sendall(READ)

        # 繼電器*2 R（可省略） 00000~199915*4 （位） 0001~1000 0001~0500
        # 鏈路繼電器B 0000~7FFF （位） 0001~1000 0001~0500
        # 內部輔助繼電器*2 MR 00000~399915*3 （位） 0001~1000 0001~0500
        # 鎖存繼電器*2 LR 00000~99915 （位） 0001~1000 0001~0500
        # 控制繼電器CR 0000~7915 （位） 0001~1000 0001~0500
        # 工作繼電器VB 0000~F9FF （位） 0001~1000 0001~0500
        # 資料記憶體*2 DM 00000~65534 .U 0001~1000 0001~0500


    # def consecutive_data_read(self,register_type, start_register_id,number):
    #     for i in range(0,3,1):
    #         try:
    #             READS = "RDS" + "20".decode("hex") + register_type + start_register_id + "20".decode("hex") + number + "0D".decode("hex")
    #             self.server.sendall(READS)
    #             time.sleep(0.2)
    #             Rx = self.server.recv(1024)
    #             self.rec_msg = Rx
    #             print 'The registers value are : ' + Rx 

    #             if Rx == "E1\r\n":
    #                 print "Command error"
    #             elif Rx == "E0\r\n":
    #                 print "Register number error"
    #             return

    #         except socket.error as e:
    #             print("Error -->"+str(e))
    #             self.server.sendall(READS)

        # data_format 
        # .U : Decimal, 16bit, unsigned 
        # .S : Decimal, 16bit, signed 
        # .D : Decimal, 32bit, unsigned 
        # .L : Decimal, 32bit, signed 
        # .H : Hex, 16bit

    def write_data(self,register_type,register_id,data_format,data):
        try:
            WRITE = "WR"+"20".decode("hex")+register_type+register_id+data_format+"20".decode("hex")+data+"0D".decode("hex")
            self.s1.sendto(WRITE.encode("ascii", "ignore"), (self.plc_ip, self.plc_port))
            print("write date",WRITE)
        except socket.error as e:
                print("Error -->"+str(e))
       

    def consecutive_write_data(self,register_type,start_register_id,data_format,data_list):
        try:
            WRITES = "WRS"+"20".decode("hex")+register_type+start_register_id+data_format+"20".decode("hex")+data_list+"0D".decode("hex")
            self.s1.sendto(WRITES.encode("ascii", "ignore"), (self.plc_ip, self.plc_port))
        except socket.error as e:
            print("Error -->"+str(e))



if __name__ =='__main__':
    plc = PLC_UDP('192.168.30.15',8501)
    plc.force_set('MR','505')
    # plc.force_reset('MR','505')
    plc.write_data('DM','50','.U','499') #油門 
    plc.write_data('DM','52','.L','0') 
      

        
