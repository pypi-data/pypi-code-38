"""
    Defines connection state structs as specified in the Linux kernel.
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/net/tcp_states.h
    Accessed from /proc/net/tcp.
"""

class C_STATE:
    established     = 0x1
    syn_sent        = 0x2
    syn_recv        = 0x3
    fin_wait1       = 0x4
    fin_wait2       = 0x5
    time_wait       = 0x6
    close           = 0x7
    close_wait      = 0x8
    last_ack        = 0x9
    listen          = 0xA
    tcp_closing     = 0xB

    strings = {
        0x1: "established",
        0x2: "syn_sent",
        0x3: "syn_recv",
        0x4: "fin_wait1",
        0x5: "fin_wait2",
        0x6: "time_wait",
        0x7: "close",
        0x8: "close_wait",
        0x9: "last_ack",
        0xA: "listen",
        0xB: "tcp_closing"
    }

    lower_bound = 0x1
    upper_bound = 0xB

    @staticmethod
    def check_bounds(value):
        """
            Verifies if value inside argument is within class bounds.
            Returns the same value.
            Exceptions:
                ValueError
        """
        sv = C_STATE.lower_bound
        ev = C_STATE.upper_bound
        if value < sv or value > ev:
            raise ValueError("Value provided was out of bounds.")

        return value

    @staticmethod
    def string_from_hex(value):
        """
            Returns connection type name, defined the C_STATE class or by
            net/tcp_states.h in the Linux kernel.
        """
        C_STATE.check_bounds(value)
        return C_STATE.strings[value] if value in C_STATE.strings else None

    @staticmethod
    def hex_from_string(string):
        """
            Returns value correlated to the connection state string.
            Defined by C_STATE class, or net/tcp_states.h
        """
        if type(string) is not str:
            raise TypeError("Function requires str as argument.")

        for value in range(C_STATE.lower_bound, C_STATE.upper_bound + 1):
            if C_STATE.strings[value] == string:
                return value

        return None
