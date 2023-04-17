import os
import glob


def test():
    filelist = glob.glob('../*')

    print(filelist)
    for filename in filelist:
        if os.path.isdir(filename):
            ismodule = len(glob.glob(filename+'/__init__.py'))>0
            if ismodule:
                print(os.path.basename(filename))

if __name__=='__main__':
    test()
