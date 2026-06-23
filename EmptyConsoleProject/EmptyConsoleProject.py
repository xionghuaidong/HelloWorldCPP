#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# -*- mode: python -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

class ProjectDirRewriter(object):
    def __init__(self):
        self._old_project_name = self._get_old_project_name()
        self._new_project_name = self._get_new_project_name()
        self._old_solution_guid = self._get_old_solution_guid()
        self._new_solution_guid = self._get_new_solution_guid()
        self._old_project_guid = self._get_old_project_guid()
        self._new_project_guid = self._get_new_project_guid()
        self._replace_dict = self._get_replace_dict()

    def _get_old_project_name(self):
        import os
        file_name = os.path.basename(__file__)
        base_name, _ = os.path.splitext(file_name)
        return base_name

    def _get_new_project_name(self):
        import os
        file_name = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_name)
        dir_name = os.path.basename(dir_path)
        return dir_name

    def _get_old_solution_guid(self):
        import io
        import os
        import re
        import uuid
        file_name = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_name)
        file_name = os.path.join(dir_path, self._old_project_name + ".sln")
        with io.open(file_name, "rb") as fin:
            buf = fin.read()
        pattern = re.compile(b"SolutionGuid = \\{(.+?)\\}")
        match = pattern.search(buf)
        if match is None:
            message = "can not find old solution guid"
            raise RuntimeError(message)
        guid = match.group(1).decode("utf-8")
        guid = uuid.UUID(guid)
        return guid

    def _get_new_solution_guid(self):
        import uuid
        guid = uuid.uuid4()
        return guid

    def _get_old_project_guid(self):
        import io
        import os
        import re
        import uuid
        file_name = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_name)
        file_name = os.path.join(dir_path, self._old_project_name + ".vcxproj")
        with io.open(file_name, "rb") as fin:
            buf = fin.read()
        pattern = re.compile(b"<ProjectGuid>\\{(.+?)\\}</ProjectGuid>")
        match = pattern.search(buf)
        if match is None:
            message = "can not find old project guid"
            raise RuntimeError(message)
        guid = match.group(1).decode("utf-8")
        guid = uuid.UUID(guid)
        return guid

    def _get_new_project_guid(self):
        import uuid
        guid = uuid.uuid4()
        return guid

    def _make_export_symbol(self, name):
        symbol = name.upper() + "_EXPORTS"
        return symbol.encode("utf-8")

    def _get_replace_dict(self):
        mapping = dict()

        # project name
        old_project_name = self._old_project_name.encode("utf-8")
        new_project_name = self._new_project_name.encode("utf-8")
        mapping[old_project_name] = new_project_name

        # solution guid
        old_solution_guid = str(self._old_solution_guid).upper().encode("utf-8")
        new_solution_guid = str(self._new_solution_guid).upper().encode("utf-8")
        mapping[old_solution_guid] = new_solution_guid

        # project guid
        old_project_guid = str(self._old_project_guid).upper().encode("utf-8")
        new_project_guid = str(self._new_project_guid).upper().encode("utf-8")
        mapping[old_project_guid] = new_project_guid
        mapping[old_project_guid.lower()] = new_project_guid.lower()

        # export symbol
        old_export_symbol = self._make_export_symbol(self._old_project_name)
        new_export_symbol = self._make_export_symbol(self._new_project_name)
        mapping[old_export_symbol] = new_export_symbol
        return mapping

    def _check_renamed(self):
        if self._new_project_name == self._old_project_name:
            message = "project is not renamed"
            raise RuntimeError(message)

    def _delete_self(self):
        import os
        os.remove(__file__)

    def _replace_file_content(self, file_name, buf):
        for key, value in self._replace_dict.items():
            buf = buf.replace(key, value)
        return buf

    def _move_file(self, file_name):
        import os
        new_file_name = file_name.replace(self._old_project_name, self._new_project_name)
        os.rename(file_name, new_file_name)

    def _replace_file_contents(self):
        import io
        import os
        import glob
        dir_path = os.path.dirname(os.path.abspath(__file__))
        pattern = os.path.join(dir_path, self._old_project_name + ".*")
        file_names = glob.glob(pattern)
        for file_name in file_names:
            with io.open(file_name, "rb") as fin:
                buf = fin.read()
            buf = self._replace_file_content(file_name, buf)
            with io.open(file_name, "wb") as fout:
                fout.write(buf)
            self._move_file(file_name)

    def run(self):
        self._check_renamed()
        self._delete_self()
        self._replace_file_contents()

def main():
    rewriter = ProjectDirRewriter()
    rewriter.run()

if __name__ == "__main__":
    main()
