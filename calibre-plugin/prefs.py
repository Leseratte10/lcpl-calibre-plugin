#!/usr/bin/env python3
# -*- coding: utf-8 -*-



# Standard Python modules.
import os
import traceback

from calibre.utils.config import JSONConfig             # type: ignore
from calibre_plugins.lcplinput.__init__ import PLUGIN_NAME  # type: ignore
from calibre.constants import isosx, islinux            # type: ignore


class LCPLInput_Prefs():
    def __init__(self):
        JSON_PATH = os.path.join("plugins", PLUGIN_NAME.strip().lower().replace(' ', '_') + '.json')
        self.lcplinputprefs = JSONConfig(JSON_PATH)

        self.lcplinputprefs.defaults['configured'] = False
        
        # Default custom User Agent to use for book downloading
        # This is not the UA that's used when "use_custom_ua" is False,
        # that one is hardcoded in __init__.py
        # It's the default value for the custom one instead.
        # This will be set OS-dependant
        if islinux:
            self.lcplinputprefs.defaults['useragent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        elif isosx:
            self.lcplinputprefs.defaults['useragent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        else:     
            self.lcplinputprefs.defaults['useragent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"

        # Default to the builtin UA
        self.lcplinputprefs.defaults['use_custom_ua'] = False

        # By default, the download script checks file integrity. 
        # This includes comparing the downloaded size with the "length" attribute in the license, 
        # comparing the downloaded size with the Content-Length header from the server, if present, 
        # and comparing the SHA256 hash with the hash included in the LCPL file, if present.
        # If you have a corrupt LCPL file where that causes errors, 
        # try setting this setting to True to ignore these errors. 
        self.lcplinputprefs.defaults['ignore_content_errors'] = False

        # A LCPL file can contain time limits (validity start and validity end).
        # These are used, for example, in libraries where you only rent book access. 
        # By default, this tool honors these time restrictions and refuses to download
        # expired eBooks. 
        # If you want, you can override that behaviour - however, A) the book might no
        # longer be available on the server, and B) the server will then definitely know
        # you are using a nonstandard client, so you might get banned ...
        self.lcplinputprefs.defaults['honor_license_time_limits'] = True


    def __getitem__(self,kind = None):
        if kind is not None:
            return self.lcplinputprefs[kind]
        return self.lcplinputprefs

    def get_system_ua(self):
        return self.lcplinputprefs.defaults["useragent"]

    def set(self, kind, value):
        self.lcplinputprefs[kind] = value

    def writeprefs(self,value = True):
        self.lcplinputprefs['configured'] = value

    def addnamedvaluetoprefs(self, prefkind, keyname, keyvalue):
        try:
            if keyvalue not in self.lcplinputprefs[prefkind].values():
                # ensure that the keyname is unique
                # by adding a number (starting with 2) to the name if it is not
                namecount = 1
                newname = keyname
                while newname in self.lcplinputprefs[prefkind]:
                    namecount += 1
                    newname = "{0:s}_{1:d}".format(keyname,namecount)
                # add to the preferences
                self.lcplinputprefs[prefkind][newname] = keyvalue
                return (True, newname)
        except:
            traceback.print_exc()
            pass
        return (False, keyname)

    def addvaluetoprefs(self, prefkind, prefsvalue):
        # ensure the keyvalue isn't already in the preferences
        try:
            if prefsvalue not in self.lcplinputprefs[prefkind]:
                self.lcplinputprefs[prefkind].append(prefsvalue)
                return True
        except:
            traceback.print_exc()
        return False

