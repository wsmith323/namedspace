namedspace
==========

The namedspace factory generates a simple class that encapsulates
a namespace and provides various means to access it.

It is inspired by namedtuple (and shamelessly copies some of the
namedtuple code), and was motivated by my realization that I was
often abusing namedtuple, using a namedtuple as a base class for
numerous simple custom classes that I was writing.

In these cases, it was the named attribute access and immutability of
the namedtuple that was desirable, and the sequence behavior was not
needed. In fact, when properties were used to override the returned
value of a named attribute, the values available from the underlying
tuple would not match. Fixing this behavior in a sub-class proved much
more difficult than expected, which was especially frustrating since
this was behavior that wasn't needed anyway.

So, namedspace was born. Orginally, I called it "namespace" (without
the 'd'), but there was already a namespace project on PyPi, and
calling it "namedspace" gives a nod to its namedtuple ancestry.

Enjoy!

--Warren A. Smith

Read the docs: http://namedspace.readthedocs.org/
