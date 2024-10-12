import time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from os import listdir
from os.path import isfile, join


class App:
    def __init__(self):
        self.app = Application(backend='uia').start(r"C:\\Program Files (x86)\Quantachrome Instruments\VersaWin\VersaWin.exe")
        time.sleep(0.3)
        self.window = self.app.window(best_match='Quantachrome')

    def process_file(self, name):
        time.sleep(0.3)
        self.window.wait("ready")
        self.window.menu_select("0")
        time.sleep(0.3)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        file_dlg = self.app.window(best_match="Открыть", found_index=0)
        file_dlg.wait("ready")
        file_dlg.child_window(best_match="Имя файла:Edit").type_keys(name)
        time.sleep(0.5)
        file_dlg.child_window(best_match="Открыть4", control_type="Button").click()
        isotherm_window = self.app.window(best_match='Dialog')
        isotherm_window.click_input(button='right')
        time.sleep(0.5)
        send_keys('{DOWN}')
        time.sleep(0.3)
        send_keys('{DOWN}')
        time.sleep(0.3)
        send_keys('{ENTER}')
        # for i in range(13): DFT
        #     time.sleep(0.3)
        #     send_keys('{DOWN}')
        time.sleep(0.3)
        send_keys('{ENTER}')
        time.sleep(0.3)
        send_keys('{DOWN}')
        time.sleep(0.3)
        send_keys('{ENTER}')
        time.sleep(0.3)
        send_keys('{ENTER}')
        # windows = app.windows()
        # print([w.window_text() for w in windows])
        # confirmWin = app.window(best_match=u'Quantachrome® VersaWin™ Confirmation')  # Check your window header object name.
        # # Use timeout based on average pop up time in your application.
        # if confirmWin.exists(timeout=10, retry_interval=1):
        #     confirmWin.set_focus()
        #     yesBtn = confirmWin[u'&Да']
        #     # Check the object name of the Yes button. You can use Swapy tool(It is deprecated but it works, else you can use inspect.exe)
        #     yesBtn.click()

        ######################
        isotherm_window.click_input(button='right')
        for i in range(10):
            send_keys('{DOWN}')
            time.sleep(0.3)
        send_keys('{ENTER}')

        save_dlg = self.app.window(best_match="Name file", found_index=0)
        save_dlg.child_window(best_match="Сохранить4", control_type="Button").click()

        report_dlg = self.app.window(best_match="Dialog", found_index=0)
        report_dlg.child_window(best_match="Закрыть", control_type="Button").click()
        isotherm_window.child_window(best_match="Закрыть").click()
        time.sleep(0.3)


if __name__ == "__main__":
    QPS_path = r"C:\QCdata\Physisorb"
    files = [f for f in listdir(QPS_path) if isfile(join(QPS_path, f))]
    files = files[30:]
    app = App()
    for file in files:
        app.process_file(file)
