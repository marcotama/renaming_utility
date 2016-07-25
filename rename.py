"""
Renaming utility, GUI based.
Comes with no guarantees, use at your own risk!

Author: Marco Tamassia
Email: tamassia.marco@gmail.com
"""

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

from functools import partial
from os import listdir, rename
from os.path import isfile, isdir, join, splitext, dirname, realpath


class RenameUtility:
    def __init__(self):
        self.root = Tk()

        self.prepend_checked = BooleanVar()
        self.append_checked = BooleanVar()
        self.append_before_ext_checked = BooleanVar()
        self.match_and_replace_checked = BooleanVar()
        self.match_and_replace_regex_checked = BooleanVar()
        self.rename_files_checked = BooleanVar()
        self.rename_directories_checked = BooleanVar()

        self.current_directory_str = StringVar()
        self.match_str = StringVar()
        self.replace_str = StringVar()
        self.match_regex_str = StringVar()
        self.replace_regex_str = StringVar()
        self.prepend_str = StringVar()
        self.append_str = StringVar()
        self.append_before_ext_str = StringVar()

        self._setup_gui()
        self._attach_bindings()
        self._init_gui()

        self.current_directory_str.set(dirname(realpath(__file__)))
        self.root.mainloop()
        self.root.quit()

    def browse_dialog(self):
        self.root.withdraw()
        directory = filedialog.askdirectory()
        self.root.deiconify()
        return directory

    def change_current_directory_text(self, _):
        directory = self.browse_dialog()
        if directory != "":
            self.current_directory_text.delete(0, END)
            self.current_directory_text.insert(0, directory)
        self.update_current_dir(None)

    @staticmethod
    def _patternify_str(text):
        if re.match(r"^\s+$", text):
            pattern = "(\\s+)"
        elif re.match(r"^\d+$", text):
            pattern = "(\\d+)"
        elif re.match(r"^[a-z]+$", text):
            pattern = "([a-z]+)"
        elif re.match(r"^[A-Z]+$", text):
            pattern = "([A-Z]+)"
        elif re.match(r"^[a-zA-Z]+$", text):
            pattern = "([a-zA-Z]+)"
        elif re.match(r"^\w+$", text):
            pattern = "(\\w+)"
        else:
            pattern = text
        return pattern

    def _patternify_selection(self, _):
        if not self.match_regex_text.selection_present():
            return
        sel_str = self.match_regex_text.selection_get()
        pattern = self._patternify_str(sel_str)
        self.match_regex_text.delete(SEL_FIRST, SEL_LAST)
        self.match_regex_text.insert(ANCHOR, pattern)

    def _get_relevant_files(self):
        directory = self.current_directory_str.get()
        if not isdir(directory):
            return []
        if self.rename_files_checked.get() and self.rename_directories_checked.get():
            files = [f for f in listdir(directory) if isfile(join(directory, f)) or isdir(join(directory, f))]
        elif self.rename_files_checked.get():
            files = [f for f in listdir(directory) if isfile(join(directory, f))]
        elif self.rename_directories_checked.get():
            files = [f for f in listdir(directory) if isdir(join(directory, f))]
        else:
            files = []
        return files

    def _produce_new_name(self, name):
        if self.match_and_replace_checked.get():
            name = name.replace(self.match_str.get(), self.replace_str.get())
        if self.match_and_replace_regex_checked.get():
            # noinspection PyBroadException
            try:
                name = re.sub(self.match_regex_str.get(), self.replace_regex_str.get(), name)
            except Exception:
                pass
        if self.prepend_str.get():
            name = self.prepend_str.get() + name
        if self.append_before_ext_checked.get():
            name, new_name_ext = splitext(name)
            name = name + self.append_before_ext_str.get() + new_name_ext
        if self.append_checked.get():
            name = name + self.append_str.get()
        return name

    def _produce_new_names(self):
        orig_names = self._get_relevant_files()
        new_names = [self._produce_new_name(name) for name in orig_names]
        return orig_names, new_names

    def apply_renaming(self, _):
        directory = self.current_directory_str.get()
        orig_names, new_names = self._produce_new_names()
        for orig, new in zip(orig_names, new_names):
            rename(join(directory, orig), join(directory, new))

    def update_current_dir(self, *_):
        orig_names, new_names = self._produce_new_names()
        output = '\n'.join("{orig} -> {new}".format(orig=orig, new=new) for orig, new in zip(orig_names, new_names))
        # self.preview_scrolledtext.configure(state=NORMAL)
        self.preview_text.delete("1.0", END)
        self.preview_text.insert("1.0", output)
        # self.preview_scrolledtext.configure(state=DISABLED)

    @staticmethod
    def update_text_state(variable, text_boxes, *_):
        state = NORMAL if variable.get() else DISABLED
        for text_box in text_boxes:
            text_box.configure(state=state)

    def _attach_bindings(self):
        callback = partial(self.update_text_state, self.prepend_checked, [self.prepend_text])
        self.prepend_checked.trace('w', callback)

        callback = partial(self.update_text_state, self.append_checked, [self.append_text])
        self.append_checked.trace('w', callback)

        callback = partial(self.update_text_state, self.append_before_ext_checked, [self.append_before_ext_text])
        self.append_before_ext_checked.trace('w', callback)

        callback = partial(self.update_text_state, self.match_and_replace_checked, [self.match_text, self.replace_text])
        self.match_and_replace_checked.trace('w', callback)

        callback = partial(self.update_text_state, self.match_and_replace_regex_checked, [self.match_regex_text,
                                                                                          self.replace_regex_text])
        self.match_and_replace_regex_checked.trace('w', callback)

        self.browse_button.bind('<ButtonRelease-1>', self.change_current_directory_text)
        self.browse_button.bind('<Key>', self.change_current_directory_text)

        self.patternify_selection_button.bind('<ButtonRelease-1>', self._patternify_selection)
        self.patternify_selection_button.bind('<Key>', self._patternify_selection)

        self.apply_button.bind('<ButtonRelease-1>', self.apply_renaming)
        self.apply_button.bind('<Key>', self.apply_renaming)

        self.current_directory_str.trace('w', self.update_current_dir)
        self.rename_files_checked.trace('w', self.update_current_dir)
        self.rename_directories_checked.trace('w', self.update_current_dir)

        self.prepend_checked.trace('w', self.update_current_dir)
        self.append_checked.trace('w', self.update_current_dir)
        self.append_before_ext_checked.trace('w', self.update_current_dir)
        self.match_and_replace_checked.trace('w', self.update_current_dir)
        self.match_and_replace_regex_checked.trace('w', self.update_current_dir)
        self.match_str.trace('w', self.update_current_dir)
        self.replace_str.trace('w', self.update_current_dir)
        self.match_regex_str.trace('w', self.update_current_dir)
        self.replace_regex_str.trace('w', self.update_current_dir)
        self.prepend_str.trace('w', self.update_current_dir)
        self.append_str.trace('w', self.update_current_dir)
        self.append_before_ext_str.trace('w', self.update_current_dir)

    def _init_gui(self):
        self.prepend_checkbox.deselect()
        self.append_checkbox.deselect()
        self.append_before_ext_checkbox.deselect()
        self.match_and_replace_checkbox.deselect()
        self.match_and_replace_regex_checkbox.deselect()
        self.rename_files_checkbox.select()
        self.rename_directories_checkbox.select()

    def _setup_gui(self):
        top = self.root

        top.geometry("623x436+486+375")
        top.title("Rename utility")
        top.configure(highlightcolor="black")
        checkbutton_style = {"activebackground": "#d9d9d9", "justify": LEFT}
        entry_style = {"background": "white", "font": "TkTextFont", "selectbackground": "#c4c4c4"}
        button_style = {"activebackground": "#d9d9d9"}
        label_style = {"activebackground": "#f9f9f9"}

        self.prepend_checkbox = Checkbutton(top, **checkbutton_style)
        self.prepend_checkbox.place(relx=0.06, rely=0.48, relheight=0.05, relwidth=0.12)
        self.prepend_checkbox.configure(text='''Prepend''')
        self.prepend_checkbox.configure(variable=self.prepend_checked)

        self.prepend_text = Entry(top, **entry_style)
        self.prepend_text.place(relx=0.08, rely=0.53, relheight=0.05, relwidth=0.23)
        self.prepend_text.configure(width=146)
        self.prepend_text.configure(textvariable=self.prepend_str)

        self.append_checkbox = Checkbutton(top, **checkbutton_style)
        self.append_checkbox.place(relx=0.32, rely=0.48, relheight=0.05, relwidth=0.12)
        self.append_checkbox.configure(text='''Append''')
        self.append_checkbox.configure(variable=self.append_checked)

        self.append_text = Entry(top, **entry_style)
        self.append_text.place(relx=0.34, rely=0.53, relheight=0.05, relwidth=0.23)
        self.append_text.configure(width=146)
        self.append_text.configure(textvariable=self.append_str)

        self.append_before_ext_checkbox = Checkbutton(top, **checkbutton_style)
        self.append_before_ext_checkbox.place(relx=0.58, rely=0.48, relheight=0.05, relwidth=0.22)
        self.append_before_ext_checkbox.configure(text='''Append before ext''')
        self.append_before_ext_checkbox.configure(variable=self.append_before_ext_checked)

        self.append_before_ext_text = Entry(top, **entry_style)
        self.append_before_ext_text.place(relx=0.59, rely=0.53, relheight=0.05, relwidth=0.23)
        self.append_before_ext_text.configure(width=146)
        self.append_before_ext_text.configure(textvariable=self.append_before_ext_str)

        self.match_and_replace_checkbox = Checkbutton(top, **checkbutton_style)
        self.match_and_replace_checkbox.place(relx=0.06, rely=0.11, relheight=0.05, relwidth=0.22)
        self.match_and_replace_checkbox.configure(text='''Match and replace''')
        self.match_and_replace_checkbox.configure(variable=self.match_and_replace_checked)

        self.match_text = Entry(top, **entry_style)
        self.match_text.place(relx=0.08, rely=0.16, relheight=0.05, relwidth=0.84)
        self.match_text.configure(width=526)
        self.match_text.configure(textvariable=self.match_str)

        self.replace_text = Entry(top, **entry_style)
        self.replace_text.place(relx=0.08, rely=0.21, relheight=0.05, relwidth=0.84)
        self.replace_text.configure(width=526)
        self.replace_text.configure(textvariable=self.replace_str)

        self.match_and_replace_regex_checkbox = Checkbutton(top, **checkbutton_style)
        self.match_and_replace_regex_checkbox.place(relx=0.06, rely=0.3, relheight=0.04, relwidth=0.33)
        self.match_and_replace_regex_checkbox.configure(text='''Match and replace (Perl regex)''')
        self.match_and_replace_regex_checkbox.configure(variable=self.match_and_replace_regex_checked)

        self.match_regex_text = Entry(top, **entry_style)
        self.match_regex_text.place(relx=0.08, rely=0.34, relheight=0.05, relwidth=0.84)
        self.match_regex_text.configure(width=526)
        self.match_regex_text.configure(textvariable=self.match_regex_str)

        self.replace_regex_text = Entry(top, **entry_style)
        self.replace_regex_text.place(relx=0.08, rely=0.39, relheight=0.05, relwidth=0.84)
        self.replace_regex_text.configure(width=526)
        self.replace_regex_text.configure(textvariable=self.replace_regex_str)

        self.apply_button = Button(top, **button_style)
        self.apply_button.place(relx=0.71, rely=0.89, height=26, width=130)
        self.apply_button.configure(text='''Apply''')

        self.patternify_selection_button = Button(top, text='Patternify selection', **button_style)
        self.patternify_selection_button.place(relx=0.42, rely=0.28, height=26, width=127)

        self.preview_text = Text(top, **entry_style)
        self.preview_text.place(relx=0.08, rely=0.67, relheight=0.19, relwidth=0.86)
        self.preview_text.configure(insertborderwidth="3")
        self.preview_text.configure(width=60)
        # self.preview_scrolledtext.configure(state=DISABLED)
        self.preview_text.configure(wrap=NONE)

        self.preview_label = Label(top, text='Preview', **label_style)
        self.preview_label.place(relx=0.08, rely=0.62, height=18, width=50)

        self.current_directory_label = Label(top, text='Current directory', **label_style)
        self.current_directory_label.place(relx=0.08, rely=0.05, height=18, width=108)

        self.current_directory_text = Entry(top, **entry_style)
        self.current_directory_text.place(relx=0.27, rely=0.05, relheight=0.05, relwidth=0.59)
        self.current_directory_text.configure(width=366)
        self.current_directory_text.configure(textvariable=self.current_directory_str)

        self.browse_button = Button(top, text='Browse', **button_style)
        self.browse_button.place(relx=0.87, rely=0.02, height=36, width=67)

        self.rename_files_checkbox = Checkbutton(top, **checkbutton_style)
        self.rename_files_checkbox.place(relx=0.29, rely=0.89, relheight=0.05, relwidth=0.16)
        self.rename_files_checkbox.configure(text='''Rename files''')
        self.rename_files_checkbox.configure(variable=self.rename_files_checked)

        self.rename_directories_checkbox = Checkbutton(top, **checkbutton_style)
        self.rename_directories_checkbox.place(relx=0.45, rely=0.89, relheight=0.05, relwidth=0.23)
        self.rename_directories_checkbox.configure(text='''Rename directories''')
        self.rename_directories_checkbox.configure(variable=self.rename_directories_checked)


if __name__ == '__main__':
    RenameUtility()
