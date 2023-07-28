#use utf-8 encoding
# -*- coding: utf-8 -*-
import glob


# Traverse all files in a directory,return the list contains all files' path 
def traverse_read_directory(directory_path):
    #print directory_path with annotation
    print("directory_path: " + directory_path)
    #use glob to get all files' path in the directory
    file_list = glob.glob(directory_path + '**\*', recursive=True)
    #print file_list with annotation
    print(file_list.__len__()) 
    #write down the file_list into a txt file
    return file_list
