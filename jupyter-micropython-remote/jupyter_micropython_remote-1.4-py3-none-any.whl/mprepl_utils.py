import gc, uos, re, ubinascii, uhashlib

class Util:
    @staticmethod
    def exists(path):
        try:
            open(path, "r").close()
            return True
        except:
            return False

    @staticmethod
    def mkdirs(path):
        try:
            i = path.index('/')
            while True:
                i = path.index('/', i+1)

                p = path[0:i]
                try:
                    uos.mkdir(p)
                except Exception as e:
                    if 'EEXIST' not in str(e):
                        print(e)
        except ValueError:
            pass

    # From https://github.com/micropython/micropython-lib/blob/master/stat/stat.py
    S_IFDIR = 0o040000
    S_IFMT = 0o170000
    st_mode = 0
    st_size = 6

    @staticmethod
    def isdir(path):
        try:
            return uos.stat(path)[Util.st_mode] & Util.S_IFMT == Util.S_IFDIR
        except OSError as ex:
            if 'ENOENT' in str(ex):
                return False
            raise

    @staticmethod
    def getsize(path):
        try:
            return uos.stat(path)[Util.st_size]
        except OSError as ex:
            if 'ENOENT' in str(ex):
                return 0
            raise

    @staticmethod
    def walk(top):
        if not Util.isdir(top):
            yield top
        else:
            for d in uos.listdir(top):
                fullpath = '/'.join((top, d))
                if Util.isdir(fullpath):
                    for f in Util.walk(fullpath):  # recurse into subdir
                        yield f
                else:
                    yield fullpath

    @staticmethod
    def sha256(path):
        with open(path, 'rb') as hfile:
            if path.startswith('/remote/'):
                hash = ubinascii.unhexlify(hfile.sha256())
            else:
                hasher = uhashlib.sha256()
                while True:
                    r = hfile.read(256)
                    if r:
                        hasher.update(r)
                    else:
                        hash = hasher.digest()
                        break
        return hash

    @staticmethod
    def copy(src_path, tgt_path):
        copy = True
        if Util.exists(tgt_path):
            lhash = thash = None
            try:
                lhash = Util.sha256(src_path)
            except OSError as ex:
                print("Error reading file: %s (%s)" % (src_path, ex))

            try:
                thash = Util.sha256(tgt_path)
            except OSError as ex:
                print("Error reading file: %s (%s)" % (tgt_path, ex))

            if thash is not None and thash == lhash:
                print("Up to date: %s" % src_path)
                copy = False
            # else:
            #     print("Changed: %s - %s" % (ubinascii.hexlify(lhash), rhash))

        if copy:
            try:
                # src_size = uos.stat(src_path).st_size
                print("Copying: %s -> %s " % (src_path, tgt_path), end="")
                size = total = Util.getsize(src_path)
                chunk = 512
                b = bytearray(chunk)
                mv = memoryview(b)
                with open(src_path, 'rb') as sfile:
                    with open(tgt_path, 'wb') as tfile:
                        while size:
                            r = sfile.readinto(mv[0:min(size, chunk)])
                            # print(r)
                            size -= r
                            if r < chunk:
                                tfile.write(mv[0:r])
                                break
                            else:
                                tfile.write(b)
                        print("(%d bytes)" % total)
            except Exception as ex:
                print('\n', '\033[91m', "Error while copying , error code:", str(ex), '\033[0m')

    @staticmethod
    def sync(source, target, delete=True, include=None, exclude=None):
        #just_contents = source.endswith('/')
        # source = source.rstrip('/')
        rel_paths = []
        if target.endswith('/'):
            tdir = target
        else:
            tdir = target[0:target.rfind('/')+1]

        Util.mkdirs(tdir)

        if include is not None:
            include = re.compile(include)

        if exclude is not None:
            exclude = re.compile(exclude)

        for src_path in Util.walk(source):
            gc.collect()
            if include:
                if not include.match(src_path):
                    continue
            if exclude:
                if exclude.match(src_path):
                    continue
            rel_path = src_path[source.rfind('/') + 1:]
            tgt_path = target + rel_path

            rel_paths.append(rel_path)

            tgt_dir = tgt_path[0:tgt_path.rfind('/') + 1]
            Util.mkdirs(tgt_dir)

            Util.copy(src_path=src_path, tgt_path=tgt_path)

        if delete:
            if target.endswith('/'):
                tdir = target + source.split('/')[-1]
            else:
                tdir = target

            for existing in Util.walk(tdir):
                isdir = Util.isdir(existing)
                if isdir:
                    if len(uos.listdir(existing)):
                        continue
                if existing[tdir.rfind('/') + 1:] not in rel_paths:
                    if exclude:
                        if exclude.match(existing):
                            continue
                    if isdir:
                        uos.rmdir(existing)
                    else:
                        uos.remove(existing)
                    print("Deleted      %s" % existing)
                # else:
                #     print("Not Deleting %s" % existing)

gc.collect()
