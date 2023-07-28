#import sqllite
import sqlite3
import os
import sys
import time
import datetime
import random

#since the max length of TEXT is 2^31-1, there is no need to save 

#define error code in python
#-1: the folder does not exist
#-2: the root folder does not exist
FOLDER_DOES_NOT_EXIST=-11111
ROOT_FOLDER_DOES_NOT_EXIST=-22222

# Create timebase,set path
def create_database(db_path):
    #set timebase path
    db_path = db_path
    #create timebase
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
    
    
    #commit
    conn.commit()
    #close
    conn.close()

# given a cursor, add rar file into timebase, rar_name, created_time, rar_password, rar_md5, rar_size
def add_rar(c, rar_name, created_time, rar_password, rar_md5, rar_size):
    #insert rar_name, created_time, rar_password, rar_md5, rar_size into table rar
    c.execute("INSERT INTO rar (rar_name, created_time, rar_password, rar_md5, rar_size) VALUES (?, ?, ?, ?, ?)", (rar_name, created_time, rar_password, rar_md5, rar_size))

#the parameter parent_path does not include the head path, for example, if the head path is \\home\\xxx, then the parent_path is xxx
def find_parent_id(c, parent_path):
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
    #if the parent_path is empty, then return the root_id
    if parent_path == '':
        return root_id
    #split the parent_path by '\\', return a list of folder name
    if(parent_path[-1]=='\\'):
        parent_path=parent_path[0:-1]
    folder_list = parent_path.split('\\')
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
        #if the folder does not exist, then return -1

    return last_id



    

# given a cursor, add directory into timebase, directory_name, created_time, modified_time, and the full path of its parent folder
def add_directory(c, directory_path, created_time, modified_time, is_root=0):
    folder_name=directory_path.split('\\')[-1]
    #print directory_path and folder_name with annotation
    print("directory_path: " + directory_path + " folder_name: " + folder_name)
    parent_path=directory_path.replace(directory_path.split('\\')[-1],'')
    parent_id = find_parent_id(c, parent_path)
    #print parent_path and parent_id with annotation
    print("parent_path: " + parent_path + " parent_id: " + str(parent_id))
    #insert directory_name, created_time, modified_time, parent_id into table directory
    c.execute("INSERT INTO directory (is_root, directory_name, created_time, modified_time, parent_id) VALUES (?, ?, ?, ?, ?)", (is_root, folder_name, created_time, modified_time, parent_id))

#given a cursor, add file into timebase, md5, size, file_name, created_time, modified_time, file_type, folder_id
def add_file(c, md5, size, file_path, created_time, modified_time, file_type):
    file_name=file_path.split('\\')[-1]
    parent_id=find_parent_id(c, file_path.replace(file_path.split('\\')[-1],''))

    #insert md5, size, file_name, created_time, modified_time, file_type, folder_id into table file
    c.execute("INSERT INTO file (md5, size, file_name, created_time, modified_time, file_type, folder_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (md5, size, file_name, created_time, modified_time, file_type, parent_id))

#main function
if __name__ == '__main__':
    #get the current path
    current_path = os.getcwd()
    #get the parent path
    parent_path = os.path.dirname(current_path)
    #set the database path
    db_path = parent_path + '\\database\\database.db'
    #create timebase
    create_database(db_path)
    #connect to database
    conn = sqlite3.connect(db_path)
    #create cursor
    c = conn.cursor()
    #add rar file into timebase
    add_rar(c, 'test.rar', '2017-12-12 12:12:12', '123456', '123456', 123456)
    #add directory into timebase
    add_directory(c, '', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 1)
    add_directory(c, '\\home', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 0)
    add_directory(c, '\\home\\xxx', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 0)
    add_directory(c, '\\home\\xxx2', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 0)
    #add file into timebase
    add_file(c, '123456', 123456, '\\home\\xxx\\xxx.txt', '2017-12-12 12:12:12', '2017-12-12 12:12:12', 'txt')
    #commit
    conn.commit()
    #print the table file
    c.execute("SELECT * FROM file")
    print(c.fetchall())
    #print the table directory
    c.execute("SELECT * FROM directory")
    print(c.fetchall())
    #print the table rar
    c.execute("SELECT * FROM rar")
    print(c.fetchall())
    #close
    conn.close()
    #remove the database
    os.remove(db_path)





