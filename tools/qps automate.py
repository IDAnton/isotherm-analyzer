from pywinauto.application import Application
app = Application(backend='uia').start(r"E:\\VersaWin\VersaWin.exe")

window = app.window(best_match='Quantachrome')
window.menu_select("0->3")
#app.AboutNotepad.OK.click()
#app.UntitledNotepad.Edit.type_keys("pywinauto Works!", with_spaces = True)