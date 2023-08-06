#import sqllite
import sqlite3
import os
import sys
import time
import datetime
import random
import traverse_read_directory
import get_md5
import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger_database_op = logging.getLogger("database_op")



#since the max length of TEXT is 2^31-1, there is no need to save 

#define error 
FOLDER_DOES_NOT_EXIST=-123456.11312312
ROOT_FOLDER_DOES_NOT_EXIST=-22222.12343241
FILE_DOES_NOT_EXIST=-33333.134124321
FOLDER_ALREADY_EXISTS=-44444.21424123412
FILE_ALREADY_EXISTS=-121312.1029309128309

# Create database,set path
def create_database(db_path):
    #set database path
    db_path = db_path
    #create database
    conn = sqlite3.connect(db_path)
    #create cursor
    c = conn.cursor()
    #create table file, primary key is file_id, key: md5, size, file_name, created_time, modified_time,file_type, and a forign key is folder_id, which is the primary  key of table directory, a forign key is rar_id, which is the primary  key of table rar
    c.execute('''CREATE TABLE file
                    (file_id INTEGER PRIMARY KEY, md5 TEXT, size INTEGER, file_name TEXT, created_time TEXT, modified_time TEXT, file_type TEXT, folder_id INTEGER, rar_id INTEGER,random_file_name TEXT, CONSTRAINT fk_directory_id FOREIGN KEY(folder_id) REFERENCES directory(directory_id),CONSTRAINT fk_rar_id FOREIGN KEY(rar_id) REFERENCES rar(rar_id))''')
    #create table directory, primary key is directory_id, key: directory_name, created_time, modified_time, and a forign key is parent_id, which is the primary  key of table directory
    c.execute('''CREATE TABLE directory
                    (directory_id INTEGER PRIMARY KEY, is_root BOOLEAN NOT NULL CHECK ( is_root IN (0, 1)), directory_name TEXT, created_time TEXT, modified_time TEXT, parent_id INTEGER, CONSTRAINT fk_parent_id FOREIGN KEY(parent_id) REFERENCES directory(directory_id))''')
    #create table rar, primary key is rar_id, key: rar_name, created_time, rar_password, rar_md5, rar_size
    c.execute('''CREATE TABLE rar
                    (rar_id INTEGER PRIMARY KEY, rar_name TEXT, created_time TEXT, rar_password TEXT, rar_md5 TEXT, rar_size INTEGER, rar_count INTEGER)''')
    
    #create table sub_volume, primary key is sub_volume_id, key: sub_volume_name, created_time, sub_volume_password, sub_volume_md5, sub_volume_size, sub_volume_count, and a forign key is rar_id, which is the primary  key of table rar
    c.execute('''CREATE TABLE sub_volume
                    (sub_volume_id INTEGER PRIMARY KEY, sub_volume_name TEXT, created_time TEXT, sub_volume_password TEXT, sub_volume_md5 TEXT, sub_volume_size INTEGER, sub_volume_count INTEGER, rar_id INTEGER, CONSTRAINT fk_rar_id FOREIGN KEY(rar_id) REFERENCES rar(rar_id))''')
    
    
    #commit
    conn.commit()
    #close
    conn.close()

# given a cursor, add rar file into database, rar_name, created_time, rar_password, rar_md5, rar_size
def add_rar(c, rar_name, created_time, rar_password, rar_md5, rar_size,rar_count=0):
    #insert rar_name, created_time, rar_password, rar_md5, rar_size into table rar
    c.execute("INSERT INTO rar (rar_name, created_time, rar_password, rar_md5, rar_size, rar_count) VALUES (?, ?, ?, ?, ?, ?)", (rar_name, created_time, rar_password, rar_md5, rar_size, rar_count))
    #get the rar_id of the rar file that has just been added
    c.execute("SELECT rar_id FROM rar WHERE rar_name = ? AND created_time = ? AND rar_password = ? AND rar_md5 = ? AND rar_size = ?", (rar_name, created_time, rar_password, rar_md5, rar_size))
    #return the rar_id
    return c.fetchone()[0]

#the parameter parent_path does not include the head path, for example, if the head path is \\home\\xxx, then the parent_path is xxx
def find_folder_id(c, folder_path):
    #find root path, return the directory_id of the root directory
    #select directory_id from table directory where is_root = 1
    c.execute("SELECT directory_id FROM directory WHERE is_root = 1")
    #fetch one
    root_id = c.fetchone()
    if root_id is None:
        print("root does not exist")
        return ROOT_FOLDER_DOES_NOT_EXIST
    root_id = root_id[0]
    print(root_id)
    #if the folder_path is empty, then return the root_id
    if folder_path == '':
        return root_id
    #if the last character of folder_path is os.sep, then remove it.for example, if folder_path is \\home\\xxx\\, then remove the last os.sep, and folder_path becomes \\home\\xxx
    if(folder_path[-1]==os.sep):
        folder_path=folder_path[0:-1]
    #split the folder_path by os.sep, return a list of folder name
    folder_list = folder_path.split(os.sep)
    print("folder_list: " + str(folder_list))
    i=0
    last_id=root_id
    #find the splited folder in each layer, respectively
    for i in range(1,folder_list.__len__()):
        print("i: " + str(i) + " folder_list[i]: " + folder_list[i]+ " last_id: " + str(last_id))
        #select directory_id from table directory where directory_name = folder_list[i] and parent_id = root_id
        c.execute("SELECT directory_id FROM directory WHERE directory_name = ? AND parent_id = ?", (folder_list[i], last_id))
        #fetch 
        fetch_result = c.fetchone()
        if fetch_result is not None:
            print("c.fetchone:",fetch_result)
            last_id = fetch_result[0]
        else:
            return FOLDER_DOES_NOT_EXIST
        #if the folder does not exist, then return FOLDER_DOES_NOT_EXIST

    return last_id


def find_file_id(c, file_path):
    #find root path, return the directory_id of the root directory
    folder_id=find_folder_id(c, file_path.replace(file_path.split(os.sep)[-1],''))
    #select file_id from table file where file_name = file_path.split(os.sep)[-1] and folder_id = folder_id
    c.execute("SELECT file_id FROM file WHERE file_name = ? AND folder_id = ?", (file_path.split(os.sep)[-1], folder_id))
    #fetch one
    file_id = c.fetchone()
    if file_id is None:
        print("file does not exist")
        return FILE_DOES_NOT_EXIST
    file_id = file_id[0]
    print("find file_id: " + str(file_id))
    print(file_id)
    return file_id
    

# given a cursor, add directory into database, directory_name, created_time, modified_time, and the full path of its parent folder
def add_directory(c, directory_path, created_time, modified_time, is_root=0):
    #make sure that the directory_path does not end with os.sep
    #check if the directory_path is empty
    if directory_path != '':
        #remove the last os.sep, if the last character of directory_path is os.sep
        if(directory_path[-1]==os.sep):
            directory_path=directory_path[0:-1]

    #check if the directory_path is already in the database
    folder_id=find_folder_id(c, directory_path)
    if isinstance(folder_id, int):
        print("directory already exists")
        return FOLDER_ALREADY_EXISTS
    #check if the parent folder of the directory_path is already in the database
    parent_id=find_folder_id(c, directory_path.replace(directory_path.split(os.sep)[-1],''))
    if parent_id == FOLDER_DOES_NOT_EXIST:
        add_directory(c, directory_path.replace(directory_path.split(os.sep)[-1],''), created_time, modified_time, 0)

    folder_name=directory_path.split(os.sep)[-1]
    #print directory_path and folder_name with annotation
    print("directory_path: " + directory_path + " folder_name: " + folder_name)
    parent_path=directory_path.replace(directory_path.split(os.sep)[-1],'')
    parent_id = find_folder_id(c, parent_path)
    if parent_id==ROOT_FOLDER_DOES_NOT_EXIST:
        #means the given folder is root folder
        parent_id=-999999999
    #print parent_path and parent_id with annotation
    print("parent_path: " + parent_path + " parent_id: " + str(parent_id))
    #insert directory_name, created_time, modified_time, parent_id into table directory
    c.execute("INSERT INTO directory (is_root, directory_name, created_time, modified_time, parent_id) VALUES (?, ?, ?, ?, ?)", (is_root, folder_name, created_time, modified_time, parent_id))

#given a cursor, add file into database, md5, size, file_name, created_time, modified_time, file_type, folder_id
def add_file(c, md5, size, file_path, created_time, modified_time, file_type, rar_id=None):
    if find_file_id(c, file_path) != FILE_DOES_NOT_EXIST:
        print("file already exists")
        return FILE_ALREADY_EXISTS
    
    file_name=file_path.split(os.sep)[-1]
    parent_id=find_folder_id(c, file_path.replace(file_path.split(os.sep)[-1],''))
    if parent_id == FOLDER_DOES_NOT_EXIST:
        add_directory(c, file_path.replace(file_path.split(os.sep)[-1],''), created_time, modified_time, 0)
        parent_id=find_folder_id(c, file_path.replace(file_path.split(os.sep)[-1],''))

    #insert md5, size, file_name, created_time, modified_time, file_type, folder_id into table file
    c.execute("INSERT INTO file (md5, size, file_name, created_time, modified_time, file_type, folder_id, rar_id) VALUES (?, ?, ?, ?, ?, ?, ?,?)", (md5, size, file_name, created_time, modified_time, file_type, parent_id, rar_id))

class File_Database(object):
    db_path=None
    conn=None
    cursor=None
    cur_rar_id=None

    def __init__(self,db_path):
        self.db_path=db_path
        #if the database does not exist, then create it
        if not os.path.exists(self.db_path):
            create_database(self.db_path)
            #connect to database
            self.conn = sqlite3.connect(self.db_path)
            #create cursor
            self.cursor = self.conn.cursor()
            #add root directory into database
            add_directory(self.cursor, '', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 1)
            return
        #connect to database
        self.conn = sqlite3.connect(self.db_path)
        #create cursor
        self.cursor = self.conn.cursor()
        self.cur_rar_id=None

    def add_rar(self,rar_name, created_time, rar_password, rar_md5, rar_size,rar_count=0):
        self.cur_rar_id=add_rar(self.cursor, rar_name, created_time, rar_password, rar_md5, rar_size)
        return self.cur_rar_id
    
    def add_sub_volume(self,sub_volume_name, created_time, sub_volume_password, sub_volume_md5, sub_volume_size):
        self.cursor.execute("INSERT INTO sub_volume (sub_volume_name, created_time, sub_volume_password, sub_volume_md5, sub_volume_size, rar_id) VALUES (?, ?, ?, ?, ?, ?)", (sub_volume_name, created_time, sub_volume_password, sub_volume_md5, sub_volume_size, self.cur_rar_id))
    
    def updata_rar(self,rar_id,rar_name, created_time, rar_password, rar_md5, rar_size):
        self.cursor.execute("UPDATE rar SET rar_name = ?, created_time = ?, rar_password = ?, rar_md5 = ?, rar_size = ? WHERE rar_id = ?", (rar_name, created_time, rar_password, rar_md5, rar_size, rar_id))
        self.cur_rar_id=rar_id

    def updata_cur_rar(self,rar_name, created_time, rar_password, rar_md5, rar_size):
        self.cursor.execute("UPDATE rar SET rar_name = ?, created_time = ?, rar_password = ?, rar_md5 = ?, rar_size = ? WHERE rar_id = ?", (rar_name, created_time, rar_password, rar_md5, rar_size, self.cur_rar_id))

    def add_directory(self,directory_path):
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(directory_path)))
        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(directory_path)))
        add_directory(self.cursor, directory_path, created_time, modified_time, 0)

    def add_file(self,file_path):
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path)))
        modified_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        #find the type of the file with try and except block
        try:
            file_type=file_path.split('.')[-1]
        except:
            file_type=''
        add_file(self.cursor, get_md5.get_md5(file_path), os.path.getsize(file_path), file_path, created_time, modified_time, file_type, self.cur_rar_id)

    def only_add_file(self,file_path):
        #if the file_path is a file, then add it into database;if not, skip it
        if os.path.isfile(file_path):
            self.add_file(file_path)

    def find_file_id(self,file_path):
        return find_file_id(self.cursor, file_path)
    
    def find_folder_id(self,folder_path):
        return find_folder_id(self.cursor, folder_path)
    
    def is_file_stored(self,file_path):
        if isinstance(find_file_id(self.cursor, file_path), int):
            return True
        else:
            return False
        
    def show_all_files(self):
        self.cursor.execute('SELECT * FROM FILE')
        print(self.cursor.fetchall())

    def show_all_directories(self):
        self.cursor.execute('SELECT * FROM DIRECTORY')
        print(self.cursor.fetchall())

    def show_all_rars(self):
        self.cursor.execute('SELECT * FROM RAR')
        print(self.cursor.fetchall())
    
    def commit(self):
        self.cur_rar_id=None
        self.conn.commit()

    def close(self):
        self.conn.close()
    
    def rollback(self):
        self.cur_rar_id=None
        self.conn.rollback()
        

#test database_class
if __name__ == '__main__':
    #new class
    database_class=File_Database('E:\\workspace\\file compression\\database\\database.db')
    database_class.commit()

    database_class.show_all_directories()
    database_class.show_all_files()
    database_class.show_all_rars()
