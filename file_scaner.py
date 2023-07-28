import rar_op
import get_md5
import database_op
import tempfile
import os
import glob
import datetime
import tempfile

#all path should be absolute path except the work path of WinRAR
class File_Scanner(object):
    traversed_list=None
    file_list_txt=None
    working_directory=None
    database_class=None
    current_file_cursor=0
    stored_file_cursor=0 #the cursor of the file that has been stored in the database, the next file to be stored is stored_file_cursor+1
    sub_volume_size='1g' #shoulb be str, like 500m, 1.5g, 20k......contact with -v, like -v500m, -v1.5g, -v20k
    rar_size_limit=1000 #the size limit of the rar file, the unit is MB
    rar_rr_percent=10 #the redundancy percent of the rar file, the unit is percent
    rar_level=5 #the compression level of the rar file, the range is 0-5
    rar_name_pattern='{time}_{data}_{random_str}' #the pattern of the rar file name, the placeholder should be {time}, {data}, {random_str}
    rar_folder=''
    encrypted_name=True #whether the rar file name is encrypted
    enable_sub_volume=False #if the current file size is out of the limit, set this flag to True. If this flag is True, enable sub volume.
    random_str_length=6 #the length of the random string

    


    rar_exec_path='C:\program files\WinRAR'

    

    def __init__(self, working_directory,database_path,sub_volume_size='1g',rar_size_limit=1000,rar_rr_percent=10,rar_level=5,rar_name_pattern='{time}_{data}_{random_str}',encrypted_name=True,rar_exec_path='C:\program files\WinRAR',rar_folder='',random_str_length=6):
        #set working directory
        self.working_directory=working_directory
        #set the directory that the program worked into self.working_directory
        os.chdir(self.working_directory)
        #traverse the working directory and get the file list
        self.traversed_list=self.traverse_read_directory(self.working_directory)
        #set the file list txt file path as stored_file_list.txt in the temp directory
        self.file_list_txt=tempfile.gettempdir()+'\\stored_file_list.txt'
        #initialize the database class
        self.database_class=database_op.File_Database(database_path)
        #set the sub volume size
        self.sub_volume_size=sub_volume_size
        #set the rar size limit
        self.rar_size_limit=rar_size_limit
        #set the rar redundancy percent
        self.rar_rr_percent=rar_rr_percent
        #set the rar compression level
        self.rar_level=rar_level
        #set the rar file name pattern
        self.rar_name_pattern=rar_name_pattern
        #set whether the rar file name is encrypted
        self.encrypted_name=encrypted_name
        #set the rar exec path
        self.rar_exec_path=rar_exec_path
        #set the rar folder
        self.rar_folder=rar_folder
        #set enable_sub_volume
        self.enable_sub_volume=False
        #set the random string length
        self.random_str_length=random_str_length
        

    def traverse_one_time(self):
        currentsize=0
        current_file_list=[]
        #traverse the file list,all the files that has been stored in the database will be skipped
        for file_i in range(self.stored_file_cursor,self.traversed_list.__len__()):
            #if the path is a directory, skip it
            if os.path.isdir(self.traversed_list[file_i]):
                continue
            #if the file is already stored in the database, skip it
            if self.database_class.is_file_stored(self.traversed_list[file_i]):
                self.current_file_cursor+=1
                continue
            currentsize+=os.path.getsize(self.traversed_list[file_i])
            if currentsize>self.rar_size_limit*1024*1024:
                #if the size of the single file is out of the rar size limit, set the flag to True, and break the loop
                if os.path.getsize(self.traversed_list[file_i])>self.rar_size_limit*1024*1024:
                    self.enable_sub_volume=True
                    self.current_file_cursor+=1
                    current_file_list.append(self.traversed_list[file_i])
                    break
                else:
                    self.enable_sub_volume=False
                    break
            else:
                self.current_file_cursor=self.current_file_cursor+1
    
            self.current_file_cursor+=1
            current_file_list.append(self.traversed_list[file_i])
        
        #get the current data with the format of YYYYMMDD, use library datetime
        current_data=datetime.datetime.now().strftime('%Y-%m-%d')
        #get the current time with the format of HHMMSS, use library datetime
        current_time=datetime.datetime.now().strftime('%H-%M-%S')
        #get the random string with the length of 120
        random_str=rar_op.generate_random_str(self.random_str_length)
        #generate the rar file name
        rar_file_name=rar_op.gen_rar_name(self.rar_name_pattern,current_time,current_data,random_str)
        #generate the rar file path with os.join
        rar_file_path=os.path.join(self.rar_folder,rar_file_name)
        #save the file list into a txt file in the temp directory, use tempfile, with open
        with open(self.file_list_txt,'w') as f:
            for file_path in current_file_list:
                f.write(file_path+'\n')
        #generate the rar command
        if self.enable_sub_volume:
            rar_command=rar_op.gen_rar_subvolume_command(self.rar_exec_path,rar_file_path,rar_password='-hpThePassWord',rar_level='-m'+str(self.rar_level),rar_method='-rr'+str(self.rar_rr_percent)+'p',verification='-t',sub_volume='-v'+self.sub_volume_size,file_list_txt=self.file_list_txt)
        else:
            rar_command=rar_op.gen_rar_command(self.rar_exec_path,rar_file_path,rar_password='-hpThePassWord',rar_level='-m'+str(self.rar_level),rar_method='-rr'+str(self.rar_rr_percent)+'p',verification='-t',file_list_txt=self.file_list_txt)
        #execute the rar command
        rar_op.rar_op(rar_command)
        


    
    