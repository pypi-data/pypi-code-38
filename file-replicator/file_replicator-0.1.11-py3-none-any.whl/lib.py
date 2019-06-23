import os.path
import subprocess
import time

import inotify.adapters
import pathspec

__all__ = ["Replicator", "replicate_all_files", "replicate_files_on_change"]


class Replicator:

    # Small receiver code (written in bash for minimum dependencies) which repeatadly
    # reads a one line command and performs an action (e.g. extract tar from stdin).
    # Note that this requires the full tar command, not the busybox "lightweight"
    # version.
    RECEIVER_CODE = """
set -e
if {clean_out_first}; then
    rm -rf {dest_dir}/*
fi
mkdir -p {dest_dir}
cd {dest_dir}
while read line; do
    case "$line" in
        "tar")
            echo -n "Copying file: "
            tar --no-same-owner --extract --verbose
            ;;
        "delete file")
            read file_to_delete
            echo "Deleting file: $file_to_delete"
            rm $file_to_delete
            ;;
        "delete directory")
            read directory_to_delete
            echo "Deleting directory: $directory_to_delete"
            rm -r $directory_to_delete
            ;;
        "end")
            echo "All done."
            break
            ;;
        *)
            echo "Unknown command: $line"
            echo "Aborting!"
            exit 1
            ;;
    esac
done
    """.strip()

    def __init__(
        self,
        src_dir,
        dest_parent_dir,
        bash_connection_command,
        clean_out_first=False,
        debugging=False,
    ):
        """Yield a replicator object for replicating files over a "bash connection".

        The object (this object) has methods like `delete_file` and `copy_file`. These
        must be passed a <src_filename> in the <src_dir> passed in to the Replicator
        when created. The final path in the <src_dir> becomes the destination directory
        in the <dest_parent_dir>.

        The <bash_connection_command> must be a list.

        """
        self.src_dir = os.path.abspath(src_dir)
        self.dest_parent_dir = os.path.abspath(dest_parent_dir)
        self.dest_dir = os.path.join(
            self.dest_parent_dir, os.path.basename(self.src_dir)
        )
        self.debugging = debugging

        self.p = subprocess.Popen(bash_connection_command, stdin=subprocess.PIPE)

        # Start the remote receiver.
        receiver_code = self.RECEIVER_CODE.format(
            dest_dir=self.dest_dir, clean_out_first=str(clean_out_first).lower()
        )
        self._send_text(receiver_code)

    def _send_text(self, text, add_newline=True):
        self.p.stdin.write(text.encode("ASCII"))
        if add_newline:
            self.p.stdin.write("\n".encode("ASCII"))
        self.p.stdin.flush()

    def copy_file(self, src_filename):
        src_filename = os.path.abspath(src_filename)
        rel_src_filename = os.path.relpath(src_filename, self.src_dir)
        if self.debugging:
            print(f"Sending {src_filename}...")
        self._send_text("tar")
        result = subprocess.run(
            [
                "tar",
                "--create",
                rel_src_filename,
                "--to-stdout",
                "--ignore-failed-read",
            ],
            cwd=self.src_dir,
            check=True,
            stdout=self.p.stdin,
            stderr=subprocess.PIPE,
        )
        if result.stderr:
            if "No such file or directory" in result.stderr.decode():
                # Ignore because file was removed before we had a chance to copy it.
                pass
            else:
                raise RuntimeError(f"ERROR: {result.stderr.decode()}")
        self.p.stdin.flush()

    def delete_file(self, src_filename):
        src_filename = os.path.abspath(src_filename)
        rel_src_filename = os.path.relpath(src_filename, self.src_dir)
        self._send_text("delete file")
        self._send_text(rel_src_filename)

    def delete_directory(self, src_directory):
        src_directory = os.path.abspath(src_directory)
        rel_src_directory = os.path.relpath(src_directory, self.src_dir)
        self._send_text("delete directory")
        self._send_text(rel_src_directory)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._send_text("end")
        self.p.stdin.close()
        self.p.wait()
        if exception_type:
            print(exception_type)
            raise


def get_pathspec(src_dir, use_gitignore=True):
    gitignore_filename = os.path.join(src_dir, ".gitignore")
    if use_gitignore and os.path.isfile(gitignore_filename):
        with open(gitignore_filename) as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
    else:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", [])
    return spec


def replicate_all_files(src_dir, replicator, use_gitignore=True, debugging=False):
    """Walk src_dir to copy all files using a Replicator instance."""
    spec = get_pathspec(src_dir, use_gitignore)
    for filename in pathspec.util.iter_tree(src_dir):
        if not spec.match_file(filename):
            replicator.copy_file(os.path.join(src_dir, filename))


def replicate_files_on_change(
    src_dir, replicator, timeout=None, use_gitignore=True, debugging=False
):
    """Wait for changes to files in src_dir and copy with Replicator instance.

    If provided, the timeout indicates when to return after that many seconds of
    no change.

    This is an imperfect solution because there are seemingly unavoidable race
    conditions when watching for file changes or additions and new directories are
    involved.

    Returns True to indicate that new directories have been added and the function
    should be called again. Otherwise returns False.

    """
    please_call_me_again = False
    i = inotify.adapters.InotifyTree(src_dir)
    spec = get_pathspec(src_dir, use_gitignore)
    for event in i.event_gen(yield_nones=False, timeout_s=timeout):
        (_, type_names, path, filename) = event
        full_path = os.path.abspath(os.path.join(path, filename))
        rel_to_src_dir_path = os.path.relpath(full_path, src_dir)
        if debugging:
            print(f"Detected change: {full_path} {type_names}")
        if not spec.match_file(rel_to_src_dir_path):
            type_names = set(type_names)
            if type_names == set(["IN_ISDIR", "IN_CREATE"]):
                # Race condition danger because a new directory was created
                # (see warning on https://pypi.org/project/inotify).
                # Wait a short while for things to settle, then replicate the new
                # directory, then start the watchers again.
                time.sleep(0.5)
                replicate_all_files(full_path, replicator)
                please_call_me_again = True
                break
            elif type_names == set(["IN_ISDIR", "IN_DELETE"]):
                replicator.delete_directory(full_path)
                please_call_me_again = True
                break
            elif type_names == set(["IN_CLOSE_WRITE"]):
                replicator.copy_file(full_path)
            elif type_names == set(["IN_DELETE"]):
                replicator.delete_file(full_path)
    return please_call_me_again
