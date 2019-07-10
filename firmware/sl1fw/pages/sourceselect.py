# part of SL1 firmware
# 2014-2018 Futur3d - www.futur3d.net
# 2018-2019 Prusa Research s.r.o. - www.prusa3d.com

import os
import logging
from time import sleep
import glob

from sl1fw import defines
from sl1fw.libPages import page, Page, PageWait


class SourceDir:

    class NotProject(Exception):
        pass
    #endclass

    def __init__(self, root, name):
        self.root = root
        self.name = name
        self.logger = logging.getLogger(__name__)
    #enddef


    def list(self, current_root):
        path = os.path.join(self.root, current_root)

        if not os.path.isdir(path):
            return
        #endif

        for item in os.listdir(path):
            try:
                yield self.processItem(item, path)
            except SourceDir.NotProject:
                continue
            except Exception as e:
                self.logger.exception("Ignoring source project for exception")
                continue
            #endtry
        #endfor
    #enddef


    def processItem(self, item, path):
        # Skip . link
        if item.startswith('.'):
            raise SourceDir.NotProject(". dir")
        #endif

        # Skip files that fail to decode as utf-8
        try:
            item.decode('utf-8')
        except ValueError:
            raise Exception('Invalid filename')
        except AttributeError as e:
            pass  # Python3 compat
        #endtry

        # Add directory to result
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            # Count number of projects in current root and number of dirs that contain some projects
            nonempty_dirs = set()
            root_projects = 0
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    (_, ext) = os.path.splitext(file)
                    if ext not in defines.projectExtensions:
                        continue
                    #endif

                    rel_path = os.path.relpath(root, os.path.normpath(full_path))
                    if rel_path == ".":
                        root_projects += 1
                    else:
                        nonempty_dirs.add(rel_path.split(os.sep)[0])
                    #endif
                #endfor
            #endfor

            num_items = len(nonempty_dirs) + root_projects
            if num_items == 0:
                raise SourceDir.NotProject("No project in dir")
            #endif

            return {
                'type': 'dir',
                'name': item,
                'path': item,
                'fullpath': full_path,
                'numitems': num_items
            }
        #endif

        # Add project as result
        (name, extension) = os.path.splitext(item)
        if extension in defines.projectExtensions:
            return {
                'type': 'project',
                'name': name,
                'fullpath': full_path,
                'source': self.name,
                'filename': item,
                'path': item,
                'time': os.path.getmtime(full_path),
                'size': os.path.getsize(full_path),
            }
        #endif

        raise SourceDir.NotProject("Invalid extension: %s" % name)
    #enddef

#endclass


@page
class PageSrcSelect(Page):
    Name = "sourceselect"

    def __init__(self, display):
        super(PageSrcSelect, self).__init__(display)
        self.pageUI = "sourceselect"
        self.pageTitle = N_("Projects")
        self.currentRoot = "."
        self.old_items = None
        self.sources = {}
        self.updateDataPeriod = 1
    #enddef


    def in_root(self):
        return self.currentRoot == "."
    #enddef


    def source_list(self):
        # Get source directories
        sourceDirs = [SourceDir(defines.internalProjectPath, "internal")]
        sourceDirs += [SourceDir(path, "usb") for path in glob.glob(os.path.join(defines.mediaRootPath, "*"))]

        # Get content items
        dirs = {}
        files = []
        for source_dir in sourceDirs:
            for item in source_dir.list(self.currentRoot):
                if item['type'] == 'dir':
                    if item['name'] in dirs:
                        item['numitems'] += dirs[item['name']]['numitems']
                    #endif
                    dirs[item['name']] = item
                else:
                    files.append(item)
                #endif
            #endfor
        #endfor

        # Flatten dirs, sort by name
        dirs = sorted(dirs.values(), key=lambda x: x['name'])

        # Add <up> virtual directory
        if not self.in_root():
            dirs.insert(0, {
                'type': 'dir',
                'name': '<up>',
                'path': '..'
            })
        #endif

        # Sort files
        files.sort(key=lambda x: x['time'])
        files.reverse()

        # Compose content
        content = dirs
        content += files

        # Number items as choice#
        content_map = {}
        for i, item in enumerate(content):
            choice = "choice%d" % i
            item['choice'] = choice
            content_map[choice] = item
        #endfor

        return content, content_map
    #enddef


    def fillData(self):
        ip = self.display.inet.getIp()
        if ip != "none" and self.octoprintAuth:
            text = "%s%s (%s)" % (ip, defines.octoprintURI, self.octoprintAuth)
        else:
            text = _("Not connected to network")
        #endif

        content, self.sources = self.source_list()

        return {
            'text': text,
            'sources': content
        }
    #enddef


    def show(self):
        self.items = self.fillData()
        super(PageSrcSelect, self).show()
    #enddef


    def updateData(self):
        items = self.fillData()
        if self.old_items != items:
            self.showItems(**items)
            self.old_items = items
        #endif
    #enddef


    def sourceButtonSubmit(self, data):
        try:
            item = self.sources[data['choice']]
        except KeyError:
            self.logger.info("Invalid choice id passed %s", data['choice'])
            return
        #endtry

        if item['type'] == 'dir':
            self.currentRoot = os.path.join(self.currentRoot, item['path'])
            self.currentRoot = os.path.normpath(self.currentRoot)
            self.logger.info("Current project selection root: %s" % self.currentRoot)
            self.show()
        else:
            return self.loadProject(item['fullpath'])
        #endif
    #enddef


    def deleteButtonSubmit(self, data):
        try:
            item = self.sources[data['choice']]
        except KeyError:
            self.logger.info("Invalid choice id passed %s", data['choice'])
            return
        #endtry

        if item['type'] == 'dir':
#            for root, dirs, files in os.walk(item['fullpath']):
#                for file in files:
#                    (name, ext) = os.path.splitext(file)
#                    if ext in defines.projectExtensions:
#                        os.remove(os.path.join(root, file))
#            return
            raise NotImplementedError
        else:
            try:
                os.remove(item['fullpath'])
            except OSError:
                self.logger.error("Failed to remove project file")
            return
        #endif
    #enddef


    def netChange(self):
        ip = self.display.inet.getIp()
        if ip != "none" and self.octoprintAuth:
            self.showItems(text = "%s%s (%s)" % (ip, defines.octoprintURI, self.octoprintAuth))
        else:
            self.showItems(text = _("Not connected to network"))
        #endif
    #enddef


    def loadProject(self, project_filename):
        pageWait = PageWait(self.display, line1 = _("Reading project data"))
        pageWait.show()
        config = self.display.config
        config.parseFile(project_filename)
        if config.zipError is not None:
            sleep(0.5)
            self.display.pages['error'].setParams(
                    text = _("Your project has a problem: %s\n\n"
                        "Re-export it and try again.") % config.zipError)
            return "error"
        #endif

        return "printpreview"
    #endef

#endclass