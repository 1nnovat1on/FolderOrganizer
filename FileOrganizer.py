import os
import shutil
import tkinter
from tkinter import filedialog
from tkinter import *
from sys import exit


# code by Leo, edited by Colin
# inspired by this link: https://www.youtube.com/watch?v=KBjBPQExJLw&t=8s

class FileUtils:
    @staticmethod

    def organizeFilesIntoFolders(path:str):
        if path == '':
            return
        files = os.listdir(path)
        if not files: print('this path has no files');return
        for file in files:
            try:
                filename,ext = os.path.splitext(file) # name of the file followed by .[ext]
                ext = ext[1:] # remove the leading period
                # print(filename, ext)
                currentFilePath = f'{path}/{file}'
                destinationFilePath = f'{path}/{ext}/{file}'

                # we need to create that folder first and then move it inside
                if not os.path.exists(f'{path}/{ext}'):
                    print(f'{path}/{ext} does not exist, so making a directory for it now')
                    os.makedirs(f'{path}/{ext}')
                shutil.move(currentFilePath, destinationFilePath)
            except Exception as e:
                print(e)

    def selectDir():

        root = Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory()
        print(folder_selected)
        root.destroy()

        return folder_selected

    def popupmsg(msg = None, title = None):
        root = Tk()
        root.title(title)
        label = tkinter.Label(root, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(root, text="Okay", command = root.destroy)
        B1.pack()
        def on_closing():
                root.destroy()
                exit()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    
def main():

    errorBoolean = True
    FileUtils.popupmsg("Select Directory to organize into file folders.", "Directory Organizinator")
    directory = FileUtils.selectDir()
    if directory == '' or directory is None:
        FileUtils.popupmsg("No Directory Selected.", "Directory Organizinator")
        exit()
    FileUtils.organizeFilesIntoFolders(directory)
    FileUtils.popupmsg("Ding! Directory Organized.", "Directory Organizinator")

if __name__=="__main__":
    main()

