
import attr
import pickledb

from .pathname import PathName

@attr.s
class Misc(object):
    repo = attr.ib()
    filepath = attr.ib()
    debug = attr.ib()
    #pn = PathName(self.repo, self.filepath)
    
    def hash2rev(self, hash):
        pn = PathName(self.repo, self.filepath, self.debug)
        #hrdb = pickledb.load(self._get_pname_hrdbpath(filepath),
        hrdb = pickledb.load(pn.hrdbpath(), 'False')
        return hrdb.get(hash)
    
