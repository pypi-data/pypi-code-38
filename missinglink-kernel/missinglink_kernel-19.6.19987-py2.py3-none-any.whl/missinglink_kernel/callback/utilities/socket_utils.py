import select


def _is_poll_supported():
    """
    Checks that the current operating system supports select.poll()
    @see: https://docs.python.org/2/library/select.html#select.poll
    """
    try:
        # select.poll() objects won't fail until used.
        p = select.poll()
        p.poll(0)

        return True

    except (OSError, AttributeError):
        return False


def _check_socket_ready_to_read_poll(socket, timeout=0):
    READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR | select.POLLNVAL

    poller = select.poll()
    poller.register(socket, READ_ONLY)
    events = poller.poll(timeout)

    if len(events) == 0:
        return False

    all_valid = all(flag & (select.POLLIN | select.POLLPRI) for fd, flag in events)

    return all_valid


def _check_socket_ready_to_read_select(socket, timeout=0):
    read_list = [socket]

    try:
        readable, _, _ = select.select(read_list, [], [], timeout)
    except ValueError:
        # select() can't accept a FD > FD_SETSIZE (usually around 1024) which throws
        # ValueError: filedescriptor out of range in select()
        return False

    if len(readable) == 0:
        return False

    return True


def is_socket_ready_to_read(socket, timeout):
    """
    When possible prefer poll over select, which is less robust since
    select() can't accept a FD > FD_SETSIZE (usually around 1024) which throws
    ValueError: filedescriptor out of range in select()

    @see: https://docs.python.org/2/library/select.html
    """

    if _is_poll_supported():
        return _check_socket_ready_to_read_poll(socket, timeout)
    else:
        return _check_socket_ready_to_read_select(socket, timeout)
