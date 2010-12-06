from ckanclient import CkanClient
log = __import__("logging").getLogger("work")

class _WorkQueue(object):
    def __init__(self):
        self.flush()

    def flush(self):
        self.updates = {}

    def add(self, dataset, key, value):
        dsd = self.updates.setdefault(dataset, {})
        self.__merge__(dsd, { key: value })

    def __merge__(self, dst, src):
        for key, value in src.items():
            if isinstance(value, list):
                vl = dst.setdefault(key, [])
                [vl.append(x) for x in value if x not in vl]
            elif isinstance(value, dict):
                vd = dst.setdefault(key, {})
                vd.update(value)
            else:
                dst[key] = value
        
    def __iter__(self):
        for k,v in self.updates.items():
            yield k,v

    def __fixup__(self, pkg):
        balky = ("id", "metadata_created", "metadata_modified", "relationships",
                 "ratings_average", "ratings_count", "ckan_url")
        for remove in balky:
            if remove in pkg: del pkg[remove]
        
    def process(self, *av, **kw):
        ckan = CkanClient(*av, **kw)
        for dataset, descr in self:
            _, pkgname = dataset.rsplit("/", 1)
            pkg = ckan.package_entity_get(pkgname)
            self.__merge__(pkg, descr)
            groups = pkg.get("groups", [])
            self.__fixup__(pkg)
            ckan.package_entity_put(pkg)
            self.log_api_result(pkgname, ckan)
            for groupname in groups:
                group = ckan.group_entity_get(groupname)
                pkglist = group.setdefault("packages", [])
                if pkgname not in pkglist:
                    pkglist.append(pkgname)
                ckan.group_entity_put(group)
                self.log_api_result(groupname, ckan)
        self.flush()

    def log_api_result(self, entity, ckan):
        if ckan.last_status != 200:
            message = " %s" % ckan.last_message
        else:
            message = ""
        log.info("PUT %s: %s%s" % (entity, ckan.last_status, message))

queue = _WorkQueue()
