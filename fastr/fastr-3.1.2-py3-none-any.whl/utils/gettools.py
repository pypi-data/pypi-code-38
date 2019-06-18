import os
import shutil
import subprocess
import tempfile

FASTR_TOOLS_REPO = 'ssh://hg@bitbucket.org/bigr_erasmusmc/fastr-tools'


def main():
    try:
        # Clone the fastr-tools repository
        print('Creating temporary directory...')
        tmpdir = tempfile.mkdtemp()
        print('Created {}'.format(tmpdir))
        print('Cloning the fastr-tools repository...')
        hg_proc = subprocess.Popen(['hg', 'clone', FASTR_TOOLS_REPO], cwd=tmpdir)
        hg_proc.wait()
        print('Mercurial clone done...')
        print('Dirs in tmpdir: {}'.format(os.listdir(tmpdir)))
    
        # Copy the ~/.fastr/tools and ~/.fastr/types
        print('Copy tools...')
        tooldir = os.path.expanduser('~/.fastr/tools')
        if os.path.exists(tooldir):
            print('Removing old tools...')
            shutil.rmtree(tooldir)
        shutil.copytree(os.path.join(tmpdir, 'fastr-tools', 'image_analysis', 'tools'), tooldir)

        print('Copy types...')
        typesdir = os.path.expanduser('~/.fastr/datatypes')
        if os.path.exists(typesdir):
            print('Removing old types...')
            shutil.rmtree(typesdir)
        shutil.copytree(os.path.join(tmpdir, 'fastr-tools', 'image_analysis', 'datatypes'), typesdir)

    except OSError:
        print('Could not find/call mercurial correctly! Please make sure mercurial is installed!')
    finally:
        print('Cleaning up temporary directory')
        if 'tmpdir' in locals():
            shutil.rmtree(tmpdir)

if __name__ == '__main__':
    main()
