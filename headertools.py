import glob
import os.path
import sublime
import sublime_plugin

header_exts = ['.h', '.hpp', '.H', '.hxx', '.h++', '.hh', '.hp']
source_exts = ['.c', '.cpp', '.C', '.cxx', '.c++', '.cc', '.cp']

class HtSortCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return True

    def is_enabled(self):
        window = sublime.active_window()
        cur_sheet = window.active_sheet()
        cur_full = cur_sheet.view().file_name()
        cur_ext = os.path.splitext(cur_full)[1]
        return cur_ext in header_exts or cur_ext in source_exts

    def run(self, order=0):
        if order == 0:
            t = "Header"
        else:
            t = "Source"
        window = sublime.active_window()

        cur_sheet = window.active_sheet()

        file_groups = matchFiles()

        for group in file_groups.values():
            if group[order] is not None and group[order-1] is not None:
                hs = group[order-1]
                hg, hi = window.get_sheet_index(hs)
                ss = group[order]
                sg, si = window.get_sheet_index(ss)

                if hg == sg and hi < si:
                    window.set_sheet_index(hs, sg, si)
                else:
                    window.set_sheet_index(hs, sg, si+1)

        window.focus_sheet(cur_sheet)


class HtJumpCommand(sublime_plugin.WindowCommand):
    def is_visible(self):
        return True

    def is_enabled(self):
        window = sublime.active_window()
        cur_sheet = window.active_sheet()
        cur_full = cur_sheet.view().file_name()
        cur_ext = os.path.splitext(cur_full)[1]
        return cur_ext in header_exts or cur_ext in source_exts

    def run(self):
        window = sublime.active_window()
        cur_sheet = window.active_sheet()
        cur_full = cur_sheet.view().file_name()
        cur_dir = os.path.dirname(cur_full)
        cur_name = os.path.basename(cur_full)
        cur_base, cur_ext = os.path.splitext(cur_name)

        file_groups = matchFiles()

        jump_idx = file_groups[cur_base].index(cur_sheet)-1
        jump_to = file_groups[cur_base][jump_idx]
        if jump_to is not None:
            # Focus corresponding file
            window.focus_sheet(jump_to)
        else:
            # If file is not open, try to open it
            for new_file in glob.glob(os.path.join(cur_dir, cur_base + '.*')):
                new_ext = os.path.splitext(new_file)[1]
                if ((new_ext in source_exts and cur_ext in header_exts) or
                    (cur_ext in source_exts and new_ext in header_exts)):
                    window.open_file(new_file)


def matchFiles():
    window = sublime.active_window()
    file_groups = {}
    for sheet in window.sheets():
        # Get name of the file
        full_name = sheet.view().file_name()
        if full_name is None:
            continue
        dir_name = os.path.dirname(full_name)
        file_name = os.path.basename(full_name)
        base_name, ext = os.path.splitext(file_name)

        if ext in header_exts or ext in source_exts:
            if base_name not in file_groups:
                file_groups[base_name] = [None, None]
            if ext in source_exts:
                file_groups[base_name][0] = sheet
            else:
                file_groups[base_name][1] = sheet
    return file_groups