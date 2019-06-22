import pysftp
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None   
sftp = pysftp.Connection('diskstation', username='openProduction', password='passwd', cnopts=cnopts)

sftp.put(r"D:\work\openProductionTestRepo\hook_executor.py", remotepath="openProduction/test.py")
#
# ... do sftp operations
#
sftp.close()    # close your connection to hostname