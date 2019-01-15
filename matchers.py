import re

class MaximumDepthExceeded(Exception):
    pass

class AndMatcher:

    def __init__(self, fun=None):
        self._matchers = []
        self._fun = fun
        self.value = None

    def match(self, string, maxdepth=None):
        if maxdepth is not None:
            if maxdepth <= 0:
                raise MaximumDepthExceeded()
            maxdepth -= 1

        matched = ""
        remaining = string
        values = []
        for matcher in self._matchers:
            res = matcher.match(remaining, maxdepth)
            if res is None:
                return res

            values.append(matcher.value)
            matched += res[0]
            remaining = res[1]

        if self._fun is not None:
            self.value = self._fun(values)

        return (matched, remaining)

    def add(self, matcher):
        self._matchers.append(matcher)

    def copy(self):
        my_copy = AndMatcher(self._fun)
        for matcher in self._matchers:
            my_copy.add(matcher.copy())
        return my_copy

class Terminal:

    def __init__(self, regex, fun=None):
        self._regex = re.compile(regex)
        self._fun = fun
        self.value = None

    def match(self, string, maxdepth=None):
        if maxdepth is not None:
            if maxdepth <= 0:
                raise MaximumDepthExceeded()
            maxdepth -= 1

        match = self._regex.match(string)
        if match is None:
            return match

        group = match.group()
        if self._fun is not None:
            self.value = self._fun(group)

        return (group, string[len(group):])

    def copy(self):
        my_copy = Terminal(self._regex.patterj, self._fun)
        return my_copy


class NonTerminal:

    def __init__(self):
        self._matchers = []
        self.value = None

    def match(self, string, maxdepth=None):
        if maxdepth is not None:
            if maxdepth <= 0:
                raise MaximumDepthExceeded()
            maxdepth -= 1

        matches = []
        values = []
        for matcher in self._matchers:
            matches.append(matcher.match(string, maxdepth))
            values.append(matcher.value)

        if not any(matches):
            return None

        max_match_idx = None
        for i in xrange(len(matches)):
            if matches[i] is not None:
                if max_match_idx is None:
                    max_match_idx = i
                    continue
                if len(matches[i][0]) > len(matches[max_match_idx][0]):
                    max_match_idx = i

        # self.value = self._matchers[max_match_idx].value
        self.value = values[max_match_idx]
        return matches[max_match_idx]

    def add(self, matchers, fun=None):
        if len(matchers) <= 0:
            return
        andMatcher = AndMatcher(fun)
        for matcher in matchers:
            andMatcher.add(matcher)

        self._matchers.append(andMatcher)

    def copy(self):
        my_copy = NonTerminal()
        for matcher in self._matchers:
            my_copy._matchers.append(matcher.copy())
        return my_copy

def match(matcher, string, maxdepth=None):
    matched, remaining = matcher.match(string, maxdepth)
    if len(remaining) > 0:
        return None
    return matcher.value

def expr_matcher():
    integer = Terminal(r"0|([1-9][0-9]*)", lambda x: int(x))
    plus = Terminal(r"\+")
    star = Terminal(r"\*")
    minus = Terminal(r"-")
    slash = Terminal(r"/")
    open_paranthesis = Terminal(r"\(")
    closed_paranthesis = Terminal(r"\)")

    term = NonTerminal()
    addition = NonTerminal()
    multiplication = NonTerminal()

    term.add([integer], lambda x: x[0])
    term.add([open_paranthesis, addition, closed_paranthesis], lambda x: x[1])

    multiplication.add([term], lambda x : x[0])
    multiplication.add([term, star, multiplication], lambda x: x[0] * x[2])
    multiplication.add([term, slash, multiplication], lambda x: x[0] / x[2])

    addition.add([multiplication], lambda x :x[0])
    addition.add([multiplication, plus, addition], lambda x :x[0] + x[2])
    addition.add([multiplication, minus, addition], lambda x :x[0] - x[2])

    return addition

def expr_matcher2():
    def t(name):
        def terminal(value):
            return {"name" : name, "value" : value}
        return terminal

    def nt(name):
        def nonterminal(values):
            return {"name" : name, "productions" : values}
        return nonterminal

    integer = Terminal(r"0|([1-9][0-9]*)", t("integer"))
    plus = Terminal(r"\+", t("plus"))
    star = Terminal(r"\*", t("star"))
    minus = Terminal(r"-", t("minus"))
    slash = Terminal(r"/", t("slash"))
    open_paranthesis = Terminal(r"\(", t("open_paranthesis"))
    closed_paranthesis = Terminal(r"\)", t("closed_paranthesis"))

    term = NonTerminal()
    addition = NonTerminal()
    multiplication = NonTerminal()

    term.add([integer], nt("term"))
    term.add([open_paranthesis, addition, closed_paranthesis], nt("term"))

    multiplication.add([term], nt("multiplication"))
    multiplication.add([term, star, multiplication], nt("multiplication"))
    multiplication.add([term, slash, multiplication], nt("multiplication"))

    addition.add([multiplication], nt("addition"))
    addition.add([multiplication, plus, addition], nt("addition"))
    addition.add([multiplication, minus, addition], nt("addition"))

    return addition

def expr_matcher3():
    def t(name):
        def terminal(value):
            return "<{0}>{1}</{0}>".format(name, value);
        return terminal

    def nt(name):
        def nonterminal(values):
            return "<{0}>{1}</{0}>".format(name, "".join(values));
        return nonterminal

    integer = Terminal(r"0|([1-9][0-9]*)", t("integer"))
    plus = Terminal(r"\+", t("plus"))
    star = Terminal(r"\*", t("star"))
    minus = Terminal(r"-", t("minus"))
    slash = Terminal(r"/", t("slash"))
    open_paranthesis = Terminal(r"\(", t("open_paranthesis"))
    closed_paranthesis = Terminal(r"\)", t("closed_paranthesis"))

    term = NonTerminal()
    addition = NonTerminal()
    multiplication = NonTerminal()

    term.add([integer], nt("term"))
    term.add([open_paranthesis, addition, closed_paranthesis], nt("term"))

    multiplication.add([term], nt("multiplication"))
    multiplication.add([term, star, multiplication], nt("multiplication"))
    multiplication.add([term, slash, multiplication], nt("multiplication"))

    addition.add([multiplication], nt("addition"))
    addition.add([multiplication, plus, addition], nt("addition"))
    addition.add([multiplication, minus, addition], nt("addition"))

    return addition

def expr_to_xml(string):
    import xml.dom.minidom

    xml = xml.dom.minidom.parseString(match(expr_matcher3(), string))
    print xml.toprettyxml()
