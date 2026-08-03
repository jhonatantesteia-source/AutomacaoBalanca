from pywinauto import Desktop


def dump(ctrl, nivel=0):
    try:
        print(
            " " * nivel,
            ctrl.window_text(),
            "|",
            ctrl.friendly_class_name(),
            "|",
            ctrl.element_info.control_type,
            "|",
            ctrl.element_info.automation_id,
        )
    except Exception:
        pass

    try:
        for filho in ctrl.children():
            dump(filho, nivel + 4)
    except Exception:
        pass


desktop = Desktop(backend="uia")

for w in desktop.windows():
    if "MGV 7" in w.window_text():
        dump(w)
        break