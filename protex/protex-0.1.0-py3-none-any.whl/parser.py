from .ast import (
    CommandTok, CloseBra, OpenBra, Word, Command, Group, NewParagraph,
    WhiteSpace, Root, BlankToken, CloseSqBra, OpenSqBra
)


class ParserError(Exception):
    pass


class UnpairedBracketError(ParserError):
    def __init__(self, pos, filename):
        super().__init__('Found unpaired closing bracket in {} at {}.'
                         .format(filename, pos))


class UnexpectedEndOfFile(ParserError):
    def __init__(self, filename):
        super().__init__('End of file {} reached unexpectedly.'
                         .format(filename))


class Parser:
    def __init__(self, lexer, commands, filename='anonym', **opts):
        self._tok_back_stack = []
        self.lexer = lexer
        self._tokens = lexer.tokens()
        self.commands = commands
        self.options = opts
        self.filename = filename

    def next_tok(self):
        if self._tok_back_stack:
            return self._tok_back_stack.pop()
        else:
            try:
                return next(self._tokens)
            except StopIteration:
                pass

    def tok_push_back(self, tok):
        self._tok_back_stack.append(tok)

    def parse(self):
        root, _ = self._parse(0)
        return Root(self.filename, root)

    def _parse(self, deep, cmd_mode=False):
        nodes = []
        node = self._parse_node(deep, cmd_mode)
        while not (node is None or isinstance(node, CloseBra)
                   or (isinstance(node, CloseSqBra) and cmd_mode)):
            nodes.append(node)
            node = self._parse_node(deep, cmd_mode)

        if deep == 0 and node is not None:
            raise UnpairedBracketError(node.src_end, self.filename)

        if deep > 0 and node is None:
            raise UnexpectedEndOfFile(self.filename)
        return nodes, node

    def _parse_command(self, prototype, deep):
        if prototype.expected_narg == 0:
            return []
        args = []
        next_arg = self._parse_node(deep, cmd_mode=True)
        c = 0
        while not (c == prototype.expected_narg
                   or isinstance(next_arg, (CloseBra, WhiteSpace, Word))
                   or next_arg is None):
            args.append(next_arg)
            c += 1
            next_arg = self._parse_node(deep, cmd_mode=True)

        if c == prototype.expected_narg:
            # reached the end of the arg list
            self.tok_push_back(next_arg)

        elif isinstance(next_arg, Word):
            # non bracketed arg ?
            if len(next_arg.content) == 1 and len(args) == 0:
                # very likely
                args.append(next_arg)
            else:
                # propably not
                self.tok_push_back(next_arg)

        elif isinstance(next_arg, WhiteSpace):
            if isinstance(next_arg, NewParagraph):
                # keep the NewParagraph
                self.tok_push_back(next_arg)

        return args

    def _parse_input(self, input_tok, deep):
        next_node = self._parse_node(deep)
        if not (isinstance(next_node, Group)
                and next_node.elems
                and isinstance(next_node.elems[0], Word)):
            raise SyntaxError(
                'Illformed input command at {}'.format(next_node.src_start)
            )
        blank = BlankToken(input_tok.src_start, next_node.src_end)
        if self.options.get('expand_input', False):
            filename = next_node.elems[0].content
            content, _ = self.__class__(self.lexer.open_newfile(filename),
                                        self.commands)._parse(0)
            self.tok_push_back(Root(filename, content))
        return blank

    def _parse_node(self, deep, cmd_mode=False):
        tok = self.next_tok()
        if isinstance(tok, OpenBra):
            group, close_bra = self._parse(deep + 1)
            return Group(tok.src_start, close_bra.src_end, group)

        elif isinstance(tok, OpenSqBra) and cmd_mode:
            group, close_bra = self._parse(deep + 1, cmd_mode=True)
            return Group(tok.src_start, close_bra.src_end, group)

        elif isinstance(tok, CommandTok):
            if tok.name == 'input':
                return self._parse_input(tok, deep)
            else:
                start_pos = tok.src_start
                prototype = self.commands.get(tok.name)
                args = self._parse_command(prototype, deep)
                if args:
                    end_pos = args[-1].src_end
                else:
                    end_pos = tok.src_end
                return Command(start_pos, end_pos, args, prototype)
        else:
            return tok
