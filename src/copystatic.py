import os
import shutil

def prepare(src,dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.mkdir(dst)
    copy_static(src,dst)

def copy_static(src,dst):
    
    for item in os.listdir(src):
        src_path=os.path.join(src, item)
        dst_path=os.path.join(dst, item)
        if os.path.isfile(src_path):
            shutil.copy(src_path,dst_path)
        else: 
            os.mkdir(dst_path)
            copy_static(src_path,dst_path)


    