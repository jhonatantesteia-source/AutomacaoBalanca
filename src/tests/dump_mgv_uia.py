from pywinauto import Desktop

desktop = Desktop(backend="uia")

for w in desktop.windows():
    if "MGV 7" in w.window_text():
        print(w.window_text())

        for filho in w.children():
            print(
                filho.window_text(),
                "|",
                filho.friendly_class_name(),
                "|",
                filho.element_info.control_type
            )

        break