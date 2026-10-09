#rom pywinauto import Desktop

#rincipal = Desktop(backend="uia").window(
#   auto_id="frPrincipal"
#

#or ctrl in principal.descendants():

 #

from pywinauto import Desktop

desktop = Desktop(backend="uia")

for w in desktop.windows():
    print(
        repr(w.window_text()),
        "|",
        w.element_info.control_type,
        "|",
        w.element_info.automation_id
    )