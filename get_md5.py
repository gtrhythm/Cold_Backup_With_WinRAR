#get md5
import hashlib
import logging


def get_md5(file_path):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192): # 读取8192字节的数据块
            m.update(chunk) # 更新哈希值
    return m.hexdigest() # 打印最终的哈希值
