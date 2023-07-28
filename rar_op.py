import os
import winreg

def rar_op(rar_command):
    print(rar_command)
    result=os.popen(rar_command)
    print(result.read())

os.chdir('E:\\workspace\\file compression\\rar_file_list_test')
rar_op('D:\"program files"\WinRAR\WinRAR.exe a -p123456 -rr50p backup @file_list.txt')