import bimpy, sys, pysftp, os, tempfile, atexit, warnings, time
from win32 import win32file
from win32.lib import win32con
from PIL import Image
from threading import Thread
from win10toast import ToastNotifier

#12

if not sys.warnoptions:
    warnings.simplefilter("ignore")

### TEMP DIR SETUP ###
try:
    save_folder = os.path.join(tempfile.gettempdir(), "sftp-client-bimpy")
    os.mkdir(save_folder)
except:
    save_folder = os.path.join(tempfile.gettempdir(), "sftp-client-bimpy")
    print(save_folder)

### CONFIG ###
ctx = bimpy.Context()
ctx.init(1000, 750, "SFTP")

ACTIONS = {
  1 : "Created",
  2 : "Deleted",
  3 : "Updated",
  4 : "Renamed from something",
  5 : "Renamed to something"
}

FILE_LIST_DIRECTORY = 0x0001
kill_thread = False
toaster = ToastNotifier()

### ICONS ###
icon_folder = Image.open("foldericon.png")
icon_back = Image.open("back.png")
imf= bimpy.Image(icon_folder)
imb = bimpy.Image(icon_back)

code_editor = "code-insiders"

is_connected = False
current_dir = "/"
folderList = []
fileList = []
file_list_upload = []
file_dict_upload = {}

### INPUTS ###
ip_input = bimpy.String()
port_input = bimpy.String()
username_input = bimpy.String()
password_input = bimpy.String()
directory_input = bimpy.String(current_dir)
create_dir_input = bimpy.String()

### CONNECTION ###
sftp = None
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None 

### VISUALS ###
show_make_dir = False
show_delete_dir = False
right_click_menu_bln = False
is_folder_bln = False
is_file_bln = False
start_upload_screen = False

right_click_pos = None
right_click_details_name = None
start_upload_screen_name = None

def getItems(dir, get_c):
    try:
        global folderList, fileList, current_dir, directory_input
        if get_c == 0:
            if dir == "":
                dir += "/"
            elif dir[-1] != "/":
                dir += "/"

            folderList, fileList = [], []
            for i in sftp.listdir_attr(dir):
                if str(i)[:2] == "dr":
                    tempArr = []
                    tempArr.append(i.filename)
                    tempArr.append(str(i))
                    folderList.append(tempArr)
                else:
                    tempArr = []
                    tempArr.append(i.filename)
                    tempArr.append(str(i))
                    fileList.append(tempArr)
                ### RANDOM GLITCH NO CLUE ###
            current_dir = dir
            directory_input = bimpy.String(current_dir)
        else:
            if dir == "":
                dir += "/"
            elif dir[-1] != "/":
                dir += "/"

            folderList, fileList = [], []
            for i in sftp.listdir_attr(dir):
                if str(i)[:2] == "dr":
                    tempArr = []
                    tempArr.append(i.filename)
                    tempArr.append(str(i))
                    folderList.append(tempArr)
                else:
                    tempArr = []
                    tempArr.append(i.filename)
                    tempArr.append(str(i))
                    fileList.append(tempArr)
            current_dir = dir
    except:
        print("wrong input")
        pass
    
def get_last():
    global directory_input
    previous_dir = directory_input.value[:-1]
    previous_dir = previous_dir[0 : previous_dir.rfind('/') + 1 ]
    getItems(previous_dir, 1)
    directory_input = bimpy.String(current_dir)

def show_toast_message(name):
    toaster.show_toast("Bimpy SFTP", name + " has been downloaded", icon_path = None, duration = 2, threaded = True)
    while toaster.notification_active(): time.sleep(0.1) 

def get_file_open(name):
    global file_list_upload
    path = current_dir + name
    print(save_folder.replace("\\", "/"))
    sftp.get(path, save_folder.replace("\\", "/") + '/' + name, None)
    file_list_upload.append(name)
    file_list_upload.append(path)
    #show_toast_message(name)
    #os.system("code-insiders " + save_folder + '\\' + name)
    os.system(code_editor + " " + save_folder + '\\' + name)
    print(file_list_upload)

def watch_files():
    global file_dict_upload, start_upload_screen, start_upload_screen_name
    hDir = win32file.CreateFile (
        save_folder,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    while True:
        results = win32file.ReadDirectoryChangesW(hDir, 1024, False, win32con.FILE_NOTIFY_CHANGE_LAST_WRITE, None, None)
        print(results)
        for x, y in results:
            try:
                file_dict_upload[y] += 1
                if file_dict_upload[y] >= 4:
                    start_upload_screen = True
                    start_upload_screen_name = y
                    print("Hello?")

            except:
                file_dict_upload[y] = 1
            print(file_dict_upload)
        
        


watch_files_thread = Thread(target = watch_files, daemon = True).start()

if __name__ == '__main__':
    while (not ctx.should_close()):
        ctx.new_frame()
        if (not is_connected):

            bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
            bimpy.set_next_window_size(bimpy.Vec2(600, 100), bimpy.Condition.Once)
            bimpy.begin("Connection-setup")

            bimpy.push_item_width(100.0)
            bimpy.input_text('Hostname', ip_input, 100)
            bimpy.same_line()
            bimpy.push_item_width(50.0)
            bimpy.input_text('Port', port_input, 100)
            bimpy.push_item_width(100.0)
            bimpy.input_text('Username', username_input, 100)
            bimpy.same_line()
            bimpy.input_text('Password', password_input, 100, bimpy.Password)
            bimpy.same_line()

            if bimpy.button("Connect"):
                print("start connecting")
                try:
                    sftp = pysftp.Connection(ip_input.value, username = username_input.value, password = password_input.value, port = int(port_input.value), cnopts = cnopts)
                    print(sftp)
                    is_connected = True
                    getItems(current_dir, 0)
                    #directory_input = bimpy.String(current_dir)
                except:
                    pass

            window_pos = bimpy.get_window_pos()
            center = bimpy.Vec2(100, 100) + window_pos
            bimpy.end()
        else:
            bimpy.set_next_window_pos(bimpy.Vec2(20, 20), bimpy.Condition.Once)
            bimpy.set_next_window_size(bimpy.Vec2(600, 700), bimpy.Condition.Once)
            bimpy.begin("FTP " + ip_input.value)

            bimpy.image(imb)
            if (bimpy.is_item_clicked(0)):
                print("back")
                get_last()

            bimpy.same_line()
            b_input_dir = bimpy.input_text("Directory", directory_input, 200, bimpy.EnterReturnsTrue)
            if bimpy.is_key_pressed(257, b_input_dir) & b_input_dir:
                print("input pressed enter")
                getItems(directory_input.value, 1)
                bimpy.set_keyboard_focus_here(-1)
            bimpy.same_line()
            if bimpy.button("View"):
                getItems(directory_input.value, 1)
                print(directory_input.value)

            bimpy.begin_child("Scrolling", bimpy.Vec2(0, 600), border = True)
            for i in folderList:
                bimpy.image(imf)
                bimpy.same_line()
                bimpy.text(i[0])
                if bimpy.is_item_hovered(0):
                    bimpy.begin_tooltip()
                    bimpy.set_tooltip(i[1])
                    bimpy.end_tooltip()
                if (bimpy.is_item_clicked(0)):
                    getItems(current_dir + i[0] + "/", 0)
                    #directory_input = bimpy.String(current_dir)
                    print(current_dir)
                if bimpy.is_item_clicked(1):
                    right_click_menu_bln = True 
                    is_folder_bln = True
                    right_click_details_name = i[0]
                    right_click_pos = bimpy.get_cursor_screen_pos()

            for i in fileList:
                bimpy.text(i[0])
                if bimpy.is_item_hovered(0):
                    bimpy.begin_tooltip()
                    bimpy.set_tooltip(i[1])
                    bimpy.end_tooltip()
                # if (bimpy.is_item_clicked(0)):
                #     getItems(current_dir + i[0] + "/", 0)
                if bimpy.is_item_clicked(1):
                    right_click_menu_bln = True 
                    is_file_bln = True
                    right_click_details_name = i[0]
                    right_click_pos = bimpy.get_cursor_screen_pos()

            bimpy.end_child()
            
            if right_click_menu_bln:
                bimpy.set_next_window_pos((right_click_pos))
                bimpy.set_next_window_content_size(bimpy.Vec2(200, 200))
                bimpy.open_popup("test")
                if bimpy.begin_popup_modal("test"):
                    if is_folder_bln:
                        bimpy.image(imf)
                        bimpy.same_line()
                        bimpy.text("Open folder")
                        if bimpy.is_item_clicked(0):
                            getItems(current_dir + right_click_details_name + "/", 0)
                            right_click_menu_bln, is_folder_bln, is_file_bln, right_click_details_name = False, False, False, None
                            bimpy.clode_current_popup()
                        if bimpy.is_mouse_clicked(0, 1) and bimpy.is_window_hovered(1) == False:
                            right_click_menu_bln, is_folder_bln, is_file_bln, right_click_details_name = False, False, False, None
                            bimpy.clode_current_popup()
                        bimpy.end_popup()
                    else:
                        bimpy.text("Open file")
                        if bimpy.is_item_clicked(0):
                            get_file_open(right_click_details_name)
                            right_click_menu_bln, is_folder_bln, is_file_bln, right_click_details_name = False, False, False, None
                            bimpy.clode_current_popup()
                        if bimpy.is_mouse_clicked(0, 1) and bimpy.is_window_hovered(1) == False:
                            right_click_menu_bln, is_folder_bln, is_file_bln, right_click_details_name = False, False, False, None
                            bimpy.clode_current_popup()
                        bimpy.end_popup()

            if start_upload_screen:
                #bimpy.set_next_window_pos(bimpy.Vec2(500, 325))
                bimpy.set_next_window_content_size(bimpy.Vec2(400, 100))
                bimpy.open_popup("Warning")
                if bimpy.begin_popup_modal("Warning"):
                    bimpy.text("Upload file: " + start_upload_screen_name)
                    bimpy.text("*If not this will delete the file - For now*")
                    if bimpy.button("Yes"):
                        print("Yes")
                        start_upload_screen = False
                        del file_dict_upload[start_upload_screen_name]
                        pos_upload_list = file_list_upload.index(start_upload_screen_name)
                        path_for_upload = file_list_upload[pos_upload_list + 1]
                        sftp.put(save_folder + "\\" + start_upload_screen_name, path_for_upload)
                        os.remove(save_folder + "\\" + start_upload_screen_name)
                        del file_list_upload[pos_upload_list:pos_upload_list + 2]
                        print(file_list_upload)
                        start_upload_screen_name = None
                    bimpy.same_line()
                    if bimpy.button("No"):
                        print("No")
                        start_upload_screen = False


            bimpy.end()

            bimpy.set_next_window_pos(bimpy.Vec2(620, 20), bimpy.Condition.Once)
            bimpy.set_next_window_size(bimpy.Vec2(350, 600), bimpy.Condition.Once)
            bimpy.begin("Actions")

            if bimpy.collapsing_header("Create directory"):
                bimpy.text("Name")
                bimpy.same_line()
                bimpy.input_text("", create_dir_input, 100)
                bimpy.same_line()
                if bimpy.button("Create"):
                    dir_remote_path = directory_input.value + create_dir_input.value
                    print(dir_remote_path)
                    sftp.mkdir(dir_remote_path, mode = 777)
                    getItems(directory_input.value, 1)

            bimpy.end()
        ctx.render()
