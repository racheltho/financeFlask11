import re
import string

from collections import namedtuple

#from quantcast.baseconversion import tobase, frombase
#from .util import RecursiveAsDictMixin, Constants

#_Account = namedtuple("Account", ("id", "name"))
#
#
#class Account(_Account, RecursiveAsDictMixin):
#    """
#    Account information to be associated with the creative meta data.
#    """
#    def __new__(cls, id, name, id36=None):
#        pcode = PCode(id)
#
#        if id36 is not None:
#            # PCode36 must match the passed in value
#            assert pcode.pcode36 == id36, pcode.pcode36 + " != " + id36
#
#        return super(Account, cls).__new__(cls, PCode(id), name)
#
#    def _asdict(self):
#        # Override asdict to include the id36
#        d = super(Account, self)._asdict()
#        d['id36'] = self.id36
#
#        return d
#
#    @property
#    def id36(self):
#        """
#        Base36 representation of the pcode
#        """
#        return self.id.pcode36


class _IDBase(unicode):
    """
    Base class to use for string based ids.
    """

    # Parse pcodes such as p/p36-AAAAAAAAAAAAA-test as valid pcodes
    VALID_SUFFIXES = ("test", "preview")

    FORMAT = "{prefix}-{identifier:{zero}>{length}}"
    FORMAT_SUFFIX = FORMAT + "-{suffix}"
    PATTERN_FORMAT = "(?P<prefix>{prefix})-" \
                     "(?P<identifier>[{symbols}]{{{length}}})" \
                     "(?:-(?P<suffix>{suffixes}))?"

    TEST_SUFFIX = "test"
    PREVIEW_SUFFIX = "preview"

    def __new__(cls, s):
        # Early bailout for already existing pcode objects
        if isinstance(s, cls):
            return s

        if cls.pattern().match(s):
            return unicode.__new__(cls, s)

        raise ValueError("{!r} is not a valid {!r}".format(s, cls.__name__))

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, unicode(self))

    def _replace(self, prefix=None, identifier=None, suffix=None):
        """
        Replace the defined arguments. This should really only be used to
        replace the suffix or drop it.

        :param prefix: A target prefix.
        :param identifier: A target identifier.
        :param suffix: A target suffix.
        """
        prefix = prefix if prefix is not None else self.prefix
        identifier = identifier if identifier is not None else self.identifier
        suffix = suffix if suffix is not None else self.suffix


        if suffix:
            return self.__class__(self.FORMAT_SUFFIX.format(
                prefix=self.prefix,
                identifier=self.identifier,
                zero=self.SYMBOLS[0],
                length=self.LENGTH,
                suffix=suffix))
        else:
            return self.__class__(self.FORMAT.format(
                prefix=self.prefix,
                zero=self.SYMBOLS[0],
                length=self.LENGTH,
                identifier=self.identifier))

    @property
    def base(self):
        """
        :return: The base pcode, without suffixes.
        """
        return self._replace(suffix=None)

    @property
    def preview(self):
        """
        :return: A pcode for use in creative previews.
        """
        return self._replace(suffix=self.PREVIEW_SUFFIX)

    @property
    def test(self):
        """
        :return: An id for use in testing.
        """
        return self._replace(suffix=self.TEST_SUFFIX)

    @property
    def prefix(self):
        m = self.pattern().match(self)
        if m is not None:
            return m.group('prefix')

    @property
    def identifier(self):
        """
        :return: The identifier portion of the id.
        """
        m = self.pattern().match(self)
        if m is not None:
            return m.group('identifier')

    @property
    def suffix(self):
        m = self.pattern().match(self)
        if m is not None:
            return m.group('suffix')

    @classmethod
    def pattern_string(cls):
        """
        Return the unanchored pattern string for the id type.
        """
        return cls.PATTERN_FORMAT.format(prefix=re.escape(cls.PREFIX),
                                         symbols=re.escape(cls.SYMBOLS),
                                         length=cls.LENGTH,
                                         suffixes='|'.join(map(re.escape, cls.VALID_SUFFIXES)))

    @classmethod
    def pattern(cls):
        return re.compile("^" + cls.pattern_string() + "$")

    @classmethod
    def from_int(cls, u):
        """
        Convert an integer into a valid _IDBase

        :arg u: An integer.
        :return: A valid identifier in the base's format
        """
        return cls(cls.FORMAT.format(
            prefix=cls.PREFIX,
            identifier=tobase(u, cls.SYMBOLS),
            zero=cls.SYMBOLS[0],
            length=cls.LENGTH))

    def _convertto(self, type):
        sym = self.identifier
        suffix = self.suffix

        if sym is not None:
            return type.from_int(frombase(sym, self.SYMBOLS))._replace(suffix=suffix if suffix else None)


class PCode(_IDBase):
    """
    Use to manage the display of pcodes. Contructed like a
    regular string, the pcode is parsed to ensure that it has a prefix and 13
    valid "digits". The "digits" belong to the character class defined by
    DIGITS, which are the digits from url-safe base64.
    """

    # Allow pcodes like "p-test" and "p-fake"
    VALID_ALIASES = ('p-test', 'p-fake')

    # Valid PCode Digits
    SYMBOLS = string.uppercase + string.lowercase + string.digits + "-_"
    PREFIX = "p"
    LENGTH = 13

    @property
    def pcode36(self):
        return self._convertto(PCode36)


class PCode36(_IDBase):
    """
    Use to manage the display of pcodes. Contructed like a
    regular string, the pcode is parsed to ensure that it has a prefix and 13
    valid "digits". The "digits" belong to the character class defined by
    DIGITS, which are the digits from url-safe base64.
    """

    # Allow pcodes like "p-test" and "p-fake"
    VALID_ALIASES = ('p36-test', 'p36-fake')

    # Valid PCode Digits, not used, but we'll note it
    SYMBOLS = string.digits + string.lowercase
    PREFIX = "p36"
    LENGTH = 16

    @property
    def pcode(self):
        return self._convertto(PCode)


#class PCodes(Constants):
#    """
#    Namespace for common pcode
#    """
#    ZERO = PCode("p-AAAAAAAAAAAAA")
#    QUANTCAST = PCode('p-9fYuixa7g_Hm2')  # Main quantcast pcode
#
#
#_Size = namedtuple("Size", ("width", "height"))
#
#
#class Size(_Size, RecursiveAsDictMixin):
#    """
#    A general size class, to be used with creative.
#    """
#
#    def __new__(cls, width, height):
#        # Force integer types
#        return super(Size, cls).__new__(cls, int(width), int(height))
#
#    @classmethod
#    def from_string(cls, s):
#        """
#        Parse WxH string into Size object.
#        """
#        try:
#            w, h = s.split('x', 1)
#
#            return cls(w, h)
#        except Exception as e:
#            raise ValueError("Expected 'WxH': {!r}".format(s))
#
#    def __repr__(self):
#        # Override to be more compact
#        return "{cls}({w:d}, {h:d})".format(cls=self.__class__.__name__, w=self.width, h=self.height)
#
#    def __unicode__(self):
#        return u"{w:d}x{h:d}".format(w=self.width, h=self.height)
#
#    __str__ = __unicode__
#
#
#_Creative = namedtuple("Creative", ("id", "name", "size", "landing"))
#
#
#class Creative(_Creative, RecursiveAsDictMixin):
#    """
#    Creative meta data information.
#    """
#
#    # TODO(sday): Use constants metaclass to encode these.
#    SIZES = {
#        Size(300, 250),
#        Size(160, 600),
#        Size(728, 90),
#        Size(120, 600),
#        Size(468, 60),
#        Size(180, 150),
#        Size(100, 72), # Facebook creative size
#    }
#
#    def __new__(cls, id, name, size, landing=None):
#        return super(Creative, cls).__new__(
#            cls,
#            id if isinstance(id, int) else int(id),
#            name,
#            Size(**size) if isinstance(size, dict) else size,
#            landing
#        )
#
#
#class Exchange(unicode):
#    """
#    QObject representing information about an exchange.
#
#    Just a string for now.
#
#    Generally, these should only be accessed as constants.
#    """
#    EXCHANGE_NAMES = (
#        'google',
#        'admeld',
#        'appnexus',
#        'rubicon',
#        'pubmatic',
#        'openx',
#        'facebook'
#    )
#
#    def __new__(cls, s):
#        s = s.lower()
#        if s not in cls.EXCHANGE_NAMES:
#            raise ValueError(s)
#
#        return unicode.__new__(cls, s)
#
#    def __repr__(self):
#        return "{}({!r})".format(self.__class__.__name__,
#                                 unicode(self))
#
## Provides uppercase constant-like access
#_Exchanges = namedtuple("Exchanges", tuple(e.upper() for e in Exchange.EXCHANGE_NAMES))
#
## TODO(sday): Use constants metaclass to encode these.
#Exchanges =_Exchanges(*(Exchange(e) for e in Exchange.EXCHANGE_NAMES))
