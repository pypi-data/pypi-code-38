

def notify_errors(notification, stream):
    for error in notification.iterate_errors():
        print("ERROR:", error)
        stream.write(error + "\n")
