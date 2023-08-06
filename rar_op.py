import os
import winreg
import random
import string
import re
import logging
import logging_level

logging.basicConfig(level = logging_level.logging_level,format = '%(asctime)s - %(filename)s - %(lineno)d - %(funcName)s - %(name)s - %(levelname)s - %(message)s')

logger_rar_op= logging.getLogger("rar_op")


def generate_random_str(length=120):
    #pick 120 random characters from the set of ascii characters
    #and return the result as a string
    return ''.join(random.choice(string.ascii_letters+string.digits) for i in range(length))

#the rar_command should not contains the character "\"(except the path separator)
def deal_with_space(rar_command):
    rar_command=rar_command.replace(os.sep,'/')
    pattern = r"(?<=/)(.*?)(?=/)" # 定义一个正则表达式.这里的 (?<=/) 表示匹配前面是 / 的位置，(.*?) 表示匹配任意字符，但是尽量少地匹配，(?=/) 表示匹配后面是 / 的位置。
    matches = re.findall(pattern, rar_command) # 使用re.findall()函数搜索所有匹配的子字符串
    #delete the redundant element in matches
    matches=list(set(matches))
    for match in matches:
        #if match does not contains space, skip it
        if match.find(' ')==-1:
            continue
        #replace the space with double quotes
        rar_command=rar_command.replace('/'+match+'/', '/\"'+match+'\"/')
    rar_command=rar_command.replace('/',os.sep)
    return rar_command



def rar_op(rar_command):
    logger_rar_op.debug("%s",[rar_command])
    result=os.popen(rar_command)
    logger_rar_op.debug("%s",[result.read()])

def gen_rar_name(name_pattern, time_str='',data_str='',random_str=''):
    #use name_pattern.replace function to replace the placeholder with the real value
    return name_pattern.replace('{time}',time_str).replace('{data}',data_str).replace('{random_str}',random_str)+'.rar'

def gen_rar_command(rar_exec_path='D:\program files\WinRAR\WinRAR.exe',rar_file_path='filename.rar',rar_password='-hpThePassWord',rar_level='-m5',rar_method='-rr10p',verification='-t', file_list_txt='file_list.txt'):
    rar_exec_path=deal_with_space(rar_exec_path)
    rar_file_path=deal_with_space(rar_file_path)
    return rar_exec_path+' a '+rar_password+' '+rar_level+' '+rar_method+' '+verification+' '+rar_file_path+' @'+file_list_txt

def gen_rar_subvolume_command(rar_exec_path='D\program files\WinRAR\WinRAR.exe',rar_file_path='filename.rar',rar_password='-hpThePassWord',rar_level='-m5',rar_method='-rr10p',verification='-t', sub_volume='-v1g',file_list_txt='file_list.txt'):
    rar_exec_path=deal_with_space(rar_exec_path)
    return rar_exec_path+' a '+rar_password+' '+rar_level+' '+rar_method+' '+verification+' '+sub_volume+' '+rar_file_path+' @'+file_list_txt
    
# gen_rar_command()
# logger_rar_op.debug("%s",[gen_rar_command()])
# rar_op(gen_rar_command())
# logger_rar_op.debug("%s",['finish'])