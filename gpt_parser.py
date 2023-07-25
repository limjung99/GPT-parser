import struct
import sys
import uuid
_GPT_HEADER_STRUCT = "<8s4sIIIQQQQ16sQIII" # little endian
_GPT_HEADER_SIZE = struct.calcsize(_GPT_HEADER_STRUCT)
_GPT_ENTRY_STRUCT = "<16s16sQQQ72s" # littel endian
_GPT_ENTRY_SIZE = struct.calcsize(_GPT_ENTRY_STRUCT)

partitionType = {
    "00000000-0000-0000-0000-000000000000" : "Unused Entry" ,
    "C12A7328-F81F-11D2-BA4B-00A0C93EC93B" : "EFI System Partition ",
    "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7" : "Basic Data Partition",
    "0FC63DAF-8483-4772-8E79-3D69D8477DE4" : "Linux Filesystem Data ",
    "4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709" : "Root(x86-64)" ,
    "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F" : "Swap " ,
    "48465300-0000-11AA-AA11-00306543ECAC" : "HFS+" ,
    "7C3457EF-0000-11AA-AA11-00306543ECAC" : "APFS" , 
    "53746F72-6167-11AA-AA11-00306543ECAC" : "Core Storage " ,
    "426F6F74-0000-11AA-AA11-00306543ECAC" : "Boot Partition "
}

class GptParser:
    def __init__(self,path,sectorsize=512):
        self.sectorSize = sectorsize
        try:
            self.file = open(path,'rb')
        except IOError:
            exit(1)
    def getBytes(self,offset,size):
        self.file.seek(offset)
        try:
            data = self.file.read(size)
        except:
            print("can't read bytestream")
            exit(1)
        return data


if __name__=="__main__":
    filename = sys.argv[1]
    filepath = './' + filename
    gptparser = GptParser(filepath)
    # parse header
    """ Header Struct
     0.Signature (8 Bytes)
     1.Revision (4 Bytes)
     2.Header Size (4 Bytes)
     3.CRC32 of Header (4 Bytes)
     4.Reserved (4 Bytes)
     5.Current LBA (8 Bytes)
     6.Backup LBA (8 Bytes) -> 백업의 논리적 위치
     7.First usable LBA (8 Bytes) -> 할당가능한 파티션의 논리적 시작 위치 
     8.Last usable LBA (8 Bytes) -> 할당가능한 파티션의 마지막 논리적 위치
     9.Disk GUID (16 Bytes)
     10.Partition Entries Starting LBA(8 Bytes) --> 파티션 엔트리들의 첫 번째 논리적 시작 위치 ( 0: MBR , 1: Header 이므로 보통 2 ) 
     11.Number of Partition Entries(4 Bytes) --> partition entry의 최대 갯수 ( GPT에서 128개 )
     12.Size of Partition Entry(4 Bytes) --> partition entry가 가질 수 있는 최대 size ( 128 바이트)
     13.CRC32 of Partition array(4 Bytes)
    """
    gptheader = gptparser.getBytes(512,_GPT_HEADER_SIZE)
    gptheader = struct.unpack(_GPT_HEADER_STRUCT,gptheader)
    startingLBA = gptheader[10]
    #parse partition entries ( 보통 2~33 sector 에 할당)
    i=0
    while True: # partiton table entry 첫 16byte가 0일경우 break
        
        partitionTableEntry = gptparser.getBytes((startingLBA)*512+i*128,_GPT_ENTRY_SIZE)
        """
            0. Partition Type GUID (16 Bytes)
            1  Unique GUID (16 Bytes)
            2. First LBA (8 Bytes)
            3. Last LBA (8 Bytes)
            4. Attribute Flag (8 Bytes)
            5. Partition name 36 UTF-16LE (72 Bytes)
        """
        partitionTableEntry = struct.unpack(_GPT_ENTRY_STRUCT,partitionTableEntry)
        guidBytes = partitionTableEntry[0]
        if(guidBytes==16*b'\x00'):
            break
        guid_str = str(uuid.UUID(bytes_le=guidBytes)).upper()
        fileSystem = partitionType.get(guid_str,"Unkwon")
        realOffsetSector = partitionTableEntry[2]
        size = (partitionTableEntry[3]-partitionTableEntry[2]+1)*512
        print(f"partition {i}")
        print(f"    GUID :{guid_str}") 
        print(f"    FileSystem : {fileSystem}")
        print(f"    Offset(LBA) : {realOffsetSector}")
        print(f"    Size(Byte) : {size}")
        i+=1 
        

    

    

