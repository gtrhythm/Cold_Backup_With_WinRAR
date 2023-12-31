import rar_op
import get_md5
import database_op
import tempfile
import os
import glob
import datetime
import tempfile
import traverse_read_directory
import logging
import logging_level

logging.basicConfig(level = logging_level.logging_level,format = '%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger_file_scaner= logging.getLogger("file_scaner")

#all path should be absolute path except the work path of WinRAR
class File_Scanner(object):
    traversed_list=None
    file_list_txt=None
    subvolumue_list_txt=None
    working_directory=None
    database_class=None
    current_file_cursor=0
    stored_file_cursor=0 #the cursor of the file that has been stored in the database, the next file to be stored is stored_file_cursor+1
    #NOTICE: It does not mean that the file after the stored_file_cursor had been stored in the database, but all of the file before the stored_file_cursor had been stored in the database
    sub_volume_size='1g' #shoulb be str, like 500m, 1.5g, 20k......contact with -v, like -v500m, -v1.5g, -v20k
    rar_size_limit=1000 #the size limit of the rar file, the unit is MB
    rar_rr_percent=10 #the redundancy percent of the rar file, the unit is percent
    rar_level=5 #the compression level of the rar file, the range is 0-5
    rar_name_pattern='{time}_{data}_{random_str}' #the pattern of the rar file name, the placeholder should be {time}, {data}, {random_str}
    encrypted_name=True #whether the rar file name is encrypted
    enable_sub_volume=False #if the current file size is out of the limit, set this flag to True. If this flag is True, enable sub volume.
    random_str_length=6 #the length of the random string
    password_length=120 #the length of the password
    rar_folder=''

    


    rar_exec_path='C:\program files\WinRAR'

    

    def __init__(self, working_directory,database_path,sub_volume_size='1g',rar_size_limit=1000,rar_rr_percent=10,rar_level=5,rar_name_pattern='{time}_{data}_{random_str}',encrypted_name=True,rar_exec_path='C:\program files\WinRAR',rar_folder='',random_str_length=6,password_length=120):
        #set working directory
        self.working_directory=working_directory
        #set the directory that the program worked into self.working_directory
        os.chdir(self.working_directory)
        #traverse the working directory and get the file list
        self.traversed_list=traverse_read_directory.traverse_read_directory(self.working_directory)
        #set the file list txt file path as stored_file_list.txt in the temp directory
        logger_file_scaner.debug("%s",[tempfile.gettempdir()])
        self.file_list_txt=os.path.join(tempfile.gettempdir(),'stored_file_list.txt')
        logger_file_scaner.debug("%s",[self.file_list_txt])
        #set the sub volume list txt file path as sub_volume_list.txt in the temp directory
        self.subvolumue_list_txt=os.path.join(tempfile.gettempdir(),'sub_volume_list.txt')
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
        self.password_length=password_length

    def gen_rar_name(self):
        return rar_op.gen_rar_name(self.rar_name_pattern,datetime.datetime.now().strftime('%H-%M-%S'),datetime.datetime.now().strftime('%Y-%m-%d'),rar_op.generate_random_str(self.random_str_length))   
    
    # compress an rar file into several sub volume
    # it is not redundant that we both need rar_file_path and rar_name, the rar_file_path is used to generate rar command, and the rar_name used to get the list of all parts of subvolumes
    def compress_sub_volume(self,rar_file_path,rar_name,filename,rar_password=''):
        #generate the sub volume list txt file to store the path of the large file (only contains one file, this is for the consistency of the code)(ok that's because I'm a little lazy -_-|||)
        with open(self.subvolumue_list_txt,'w') as f:
            f.write(filename)
        rar_command=rar_op.gen_rar_subvolume_command(self.rar_exec_path,rar_file_path,rar_password='-hp'+rar_password,rar_level='-m'+str(self.rar_level),rar_method='-rr'+str(self.rar_rr_percent)+'p',verification='-t',sub_volume='-v'+self.sub_volume_size,file_list_txt=self.subvolumue_list_txt)
        rar_op.rar_op(rar_command)

        os.remove(self.subvolumue_list_txt)

        #generate rar file pattern
        rar_file_path_pattern=self.rar_folder+os.sep+rar_name[0:-4]+'.part*.rar'
        
        #generate the sub volume pattern
        sub_volume_list=glob.glob(rar_file_path_pattern)

        #get the md5, created time, size of all sub volumes
        sub_volume_md5_list=[]
        sub_volume_created_time_list=[]
        sub_volume_size_list=[]
        for sub_volume in sub_volume_list:
            sub_volume_md5_list.append(get_md5.get_md5(sub_volume))
            sub_volume_created_time_list.append(datetime.datetime.fromtimestamp(os.path.getctime(sub_volume)).strftime('%Y-%m-%d %H:%M:%S'))
            sub_volume_size_list.append(os.path.getsize(sub_volume))
        
        logger_file_scaner.debug("%s",["add rar for subvolume:",rar_name,sub_volume_list.__len__()])
        self.database_class.add_rar(rar_name,'',rar_password,'',' ',sub_volume_list.__len__())

        self.database_class.add_file(filename)

        #insert the sub volume info into the database
        for i in range(0,sub_volume_list.__len__()):
            self.database_class.add_sub_volume(sub_volume_list[i].split(os.sep)[-1],sub_volume_created_time_list[i],sub_volume_md5_list[i],sub_volume_size_list[i])
        
        #insert the father rar info into the database
        #the created time, md5, size does not exist because no real rar file there.
        

            


    def traverse_one_time(self):
        #gen rar info
        rar_name=self.gen_rar_name()
        rar_file_path=os.path.join(self.rar_folder,rar_name)
        rar_password=rar_op.generate_random_str(self.password_length)
        currentsize=0
        current_file_list=[]
        logger_file_scaner.debug("%s",["current file cursor is:",self.current_file_cursor])
        logger_file_scaner.debug("%s",["stored file cursor is:",self.stored_file_cursor])
        # logger_file_scaner.debug("%s",['traversed_list:',self.traversed_list])   
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
                    #compress the file into several sub volume without with other small files
                    logger_file_scaner.debug("%s",["compress the file into several sub volume without with other small files"])
                    currentsize-=os.path.getsize(self.traversed_list[file_i])
                    sub_volume_name=self.gen_rar_name()
                    self.compress_sub_volume(os.path.join(self.rar_folder,sub_volume_name),sub_volume_name,rar_password=rar_op.generate_random_str(self.password_length),filename=self.traversed_list[file_i])
                    #since the large file has been compressed into sub volumes, we do not break the loop here.
                    self.current_file_cursor+=1
                    continue

                else:
                    logger_file_scaner.debug("%s",["break because of the size of all files too large"])
                    logger_file_scaner.debug("%s",[self.traversed_list[file_i]])
                    logger_file_scaner.debug("%s",['current_size:{}'.format(currentsize)])
                    self.enable_sub_volume=False
                    break
            else:
                self.current_file_cursor=self.current_file_cursor+1
    
            self.current_file_cursor+=1
            current_file_list.append(self.traversed_list[file_i])
        
        #save the file list into a txt file in the temp directory, use tempfile, with open
        with open(self.file_list_txt,'w') as f:
            for file_path in current_file_list:
                #replace absolute path with relative path
                relative_path=file_path.replace(self.working_directory+os.sep,'')
                #compare relative path and file path
                logger_file_scaner.debug("%s",["relative path:{},file path:{}".format(relative_path,file_path)])
                f.write(relative_path+'\n')
        logger_file_scaner.debug("%s",["current file list is:",current_file_list])
        #generate the rar command
        if self.enable_sub_volume:
            rar_command=rar_op.gen_rar_subvolume_command\
                (self.rar_exec_path,rar_file_path,rar_password='-hp'+rar_password,\
                rar_level='-m'+str(self.rar_level),\
                rar_method='-rr'+str(self.rar_rr_percent)+'p',\
                verification='-t',sub_volume='-v'+self.sub_volume_size,file_list_txt=self.file_list_txt)
        else:
            rar_command=rar_op.gen_rar_command\
                (self.rar_exec_path,rar_file_path,rar_password='-hp'+rar_password,\
                 rar_level='-m'+str(self.rar_level),rar_method='-rr'+str(self.rar_rr_percent)+'p',\
                    verification='-t',file_list_txt=self.file_list_txt)
        #execute the rar command
        rar_op.rar_op(rar_command)
        #rar command done, update the rar info in the database,commit the modification to the database

        #get the md5 of the rar file
        rar_md5=get_md5.get_md5(rar_file_path)
        #get the created time of the rar file
        rar_created_time=datetime.datetime.fromtimestamp(os.path.getctime(rar_file_path)).strftime('%Y-%m-%d %H:%M:%S')
        #get the size of the rar file
        rar_size=os.path.getsize(rar_file_path)
        #update the rar info in the database
        self.database_class.add_rar(rar_name,rar_created_time,rar_password,rar_md5,rar_size)
        #insert the file info into the database
        for file_path in current_file_list:
            self.database_class.add_file(file_path)
        #commit the modification to the database
        self.database_class.commit()
        self.stored_file_cursor=self.current_file_cursor
        #delete the file list txt file
        os.remove(self.file_list_txt)


#test main
if __name__=='__main__':
    #test File_Scanner
    file_scanner=File_Scanner('E:\\workspace\\file compression\\large file test','E:\\workspace\\file compression\\database\\database.db',rar_exec_path='D:\\program files\\WinRAR\\WinRAR.exe',rar_folder='E:\\workspace\\file compression\\rar_files')
    for i in range(0,1):
        logger_file_scaner.info("%s",['traverse one time,i=',i])
        file_scanner.traverse_one_time()
    