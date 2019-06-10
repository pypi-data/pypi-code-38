class Tracer:
    def __init__(self, web3, transaction_id):
        self.web3 = web3
        self.transaction_id = transaction_id

    def get_base_logs(self):
        tracer = """
        {
            logs: [],

            step: function(log, db) {
                if (this.logs.length > 0) {
                    var prev_log = this.logs[this.logs.length-1];
                    var prev_op = prev_log.op.toString();

                    if ('CREATE' == prev_op) {
                        var addr = toHex(log.contract.getAddress()).toLowerCase().replace('0x', '');
                        prev_log.new_address = addr;
                    }

                    if (prev_op.startsWith('PUSH')) {
                        prev_log.arg = log.stack.peek(0);
                    }
                }
                var op = log.op.toString();

                var res = {pc: log.getPC(), op: op, stack_length: log.stack.length()};

                if (['CALL', 'STATICCALL', 'DELEGATECALL', 'CALLCODE'].indexOf(op) != -1) {
                    res.new_address = log.stack.peek(1);
                }

                this.logs.push(res);
            },

            result: function() {
                return this.logs;
            },

            fault: function() {
            }
        }
        """
        return self.do_request(tracer)

    def get_stack(self, position, i):
        tracer = """
        {
            val: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                   this.val = log.stack.peek(log.stack.length() - """+str(i)+""" - 1);
                }
                this.pos += 1;
            },

            result: function() {
                return this.val;
            },

            fault: function() {
            }
        }
        """
        return int(self.do_request(tracer)).to_bytes(32, "big")

    def get_all_stack(self, position):
        tracer = """
        {
            stack: [],
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    for (var i = 0; i < log.stack.length(); i++) {
                       this.stack.push(log.stack.peek(log.stack.length() - i - 1));
                    }
                }
                this.pos += 1;
            },

            result: function() {
                return this.stack;
            },

            fault: function() {
            }
        }
        """
        return list(map(lambda x: int(x).to_bytes(32, "big"), self.do_request(tracer)))

    def get_storage(self, position, key):
        tracer = """
        {
            val: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    this.val = toHex(db.getState(log.contract.getAddress(), toWord('"""+key+"""')));
                }
                this.pos += 1;
            },

            result: function() {
                return this.val;
            },

            fault: function() {
            }
        }
        """
        return bytes.fromhex(self.do_request(tracer).replace('0x', ''))

    def get_memory(self, position, i):
        tracer = """
        {
            val: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    this.val = toHex(log.memory.slice("""+str(i)+""", """+str(i)+"""+32));
                }
                this.pos += 1;
            },

            result: function() {
                return this.val;
            },

            fault: function() {
            }
        }
        """
        res = self.do_request(tracer)
        return bytes.fromhex(res.replace('0x', ''))

    def get_all_memory(self, position):
        tracer = """
        {
            mem: [],
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    for (var i = 0; i < 1000000; i++) {
                        var word = toHex(log.memory.slice(i*32, (i+1)*32));
                        if (word == '0x') {
                            break;
                        }
                        this.mem.push(word);
                    }
                }
                this.pos += 1;
            },

            result: function() {
                return this.mem;
            },

            fault: function() {
            }
        }
        """
        res = self.do_request(tracer)
        return  res

    def get_sender(self, position):
        tracer = """
        {
            res: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    this.res = toHex(log.contract.getCaller()).toLowerCase().replace('0x', '');
                }
                this.pos += 1;
            },

            result: function() {
                return this.res;
            },

            fault: function() {
            }
        }
        """
        res = self.do_request(tracer)
        return  res

    def get_value(self, position):
        tracer = """
        {
            res: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    this.res = log.contract.getValue();
                }
                this.pos += 1;
            },

            result: function() {
                return this.res;
            },

            fault: function() {
            }
        }
        """
        res = self.do_request(tracer)
        return  res

    def get_address(self, position):
        tracer = """
        {
            res: null,
            pos: 0,

            step: function(log, db) {
                if (this.pos == """+str(position)+""") {
                    this.res = toHex(log.contract.getAddress());
                }
                this.pos += 1;
            },

            result: function() {
                return this.res;
            },

            fault: function() {
            }
        }
        """
        res = self.do_request(tracer)
        return  res

    def do_request(self, tracer):
        return self.web3.manager.request_blocking("debug_traceTransaction", [self.transaction_id, {"tracer": tracer}])


