#use utf-8 encoding
# -*- coding: utf-8 -*-
import glob
import os
import logging
import logging_level

logging.basicConfig(level = logging_level.logging_level,format = '%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger_traverse= logging.getLogger("traverse")

# Traverse all files in a directory,return the list contains all files' path 
def traverse_read_directory(directory_path):
    #print directory_path with annotation
    logger_traverse.debug("%s",["directory_path: " + directory_path])
    #use glob to get all files' path in the directory
    file_list = glob.glob(directory_path + '**{}**'.format(os.sep), recursive=True) #
    #print file_list with annotation
    logger_traverse.debug("%s",[file_list.__len__()]) 
    #write down the file_list into a txt file
    return file_list
