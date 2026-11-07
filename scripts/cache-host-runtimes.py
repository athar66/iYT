from pathlib import Path
import tarfile
import shutil
r=Path(__file__).resolve().parents[1]
cache=Path('/home/athar/.cache/iyt-host-tools')
cache.mkdir(parents=True,exist_ok=True)
for version,alias in [('v22.23.0','node22'),('v8.16.2','node8')]:
    name='node-'+version+'-linux-x64'
    archive=r/'.tools'/(name+'.tar.xz')
    target=cache/alias
    if archive.exists():
        with tarfile.open(archive) as tar:
            source=tar.extractfile(name+'/bin/node')
            with target.open('wb') as dest: shutil.copyfileobj(source,dest)
    else:
        shutil.copyfile(r/'.tools'/name/'bin/node',target)
    target.chmod(0o755)
    bindir=cache/(alias+'-bin')
    bindir.mkdir(exist_ok=True)
    executable=bindir/'node'
    if not executable.exists(): executable.symlink_to(target)
    print(str(target),flush=True)
