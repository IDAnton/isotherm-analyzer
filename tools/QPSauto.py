import time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from os import listdir
from os.path import isfile, join


class App:
    def __init__(self):
        self.app = Application(backend='uia').start(r"E:\\VersaWin\VersaWin.exe")
        time.sleep(0.3)
        self.window = self.app.window(best_match='Quantachrome')
        time.sleep(0.3)

    def process_file(self, name):
        self.window.menu_select("0->2")
        file_dlg = self.app.window(best_match="Открыть", found_index=0)
        file_dlg.child_window(best_match="Имя файла:Edit").type_keys(name)
        time.sleep(0.3)
        file_dlg.child_window(best_match="Открыть4", control_type="Button").click()
        isotherm_window = self.app.window(best_match='Dialog')
        isotherm_window.click_input(button='right')
        time.sleep(0.3)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{DOWN}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        time.sleep(0.1)
        send_keys('{ENTER}')
        time.sleep(0.1)
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
        time.sleep(0.3)


if __name__ == "__main__":
    QPS_path = r"C:\QCdata\Physisorb"
    files = [f for f in listdir(QPS_path) if isfile(join(QPS_path, f))]
    app = App()
    for file in files:
        app.process_file(file)
