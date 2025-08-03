#!/usr/bin/env python

import re


def isin(val, listofvals):
    # assert isiterable( listofvals), "Expected a list as the second arg listofvals."
    for v in listofvals:
        if val == v:
            return True

    return False


def islist(obj):
    if isin(type(obj), [list, tuple]):
        return True

    # if hasattr( obj, '__iter__'):
    #    return True

    return False


def isiterable(obj):
    if isin(type(obj), [list, tuple]):
        return True

    if hasattr(obj, "__iter__"):
        return True

    if hasattr(obj, "collection"):
        return True

    return False


idxre = re.compile(r"(.*)\[(\d+)\]")


def getBeanValue(obj, attrname, defval=None, debug=False):
    global idxre
    """Given an attrname like solr_education.university pull the attribute out of the object."""

    def _getIndex(compstr):
        m = idxre.match(compstr)
        idx = None
        if m:
            idx = int(m.group(2))

        if debug:
            print(("getBeanValue.getIndex returns %s" % idx))
        return idx

    def _getArrayIndexValue(beanobj, idx):
        ret = None
        if debug:
            print(("getBeanValue: using index idx = %s" % idx))
        if idx is not None:
            try:
                ret = beanobj[idx]
            except IndexError:
                ret = None
        return ret

    beanobj = None

    if debug:
        print(("getBeanValue(attrname = %s, obj=%s" % (attrname, obj)))

    if obj:
        # TODO: add support for extracting elements out of an element.
        attrs = attrname.split(".")

        beanobj = obj
        pcomp = None
        for acomp in attrs:
            # print( "umm... not a list: %s %s" % (acomp, type(beanobj)))
            if debug:
                print(
                    (
                        "getBeanValue: acomp = %s, type_beanobj = %s, beanobj = %s"
                        % (acomp, type(beanobj), beanobj)
                    )
                )

            pcomp = acomp
            m = idxre.match(acomp)
            if m:
                acomp = m.group(1)
                if debug:
                    print(("getBeanValue: index ref into an array acomp = %s" % acomp))

                if islist(beanobj) or isiterable(beanobj):
                    if debug:
                        print(("getBeanValue: List baby! pcomp = %s" % pcomp))
                    if pcomp:
                        idx = _getIndex(pcomp)
                        if idx is not None:
                            beanobj = _getArrayIndexValue(beanobj, idx)
                            if debug:
                                print(
                                    (
                                        "getBeanValue: used indexed into array idx = %s and beanobj = %s"
                                        % (idx, beanobj)
                                    )
                                )

            if isinstance(beanobj, dict):
                if debug:
                    print(f"Extracting {acomp} from a dict: {beanobj}")
                beanobj = beanobj.get(acomp)
            elif beanobj:
                if hasattr(beanobj, acomp):
                    beanobj = getattr(beanobj, acomp)
                else:
                    beanobj = None

    if debug:
        print(("getBeanValue: beanobj = %s" % beanobj))

    if beanobj:
        return beanobj

    return defval


if __name__ == "__main__":
    msgid = 1
    message = {"time": 1, "id": f"{msgid}", "message": {"text": "Boo!"}}
    path = "message.text"
    val = getBeanValue(message, "id", None, debug=True)
    print(f"id -> {val}")
    val = getBeanValue(message, "time", None, debug=True)
    print(f"time -> {val}")
    val = getBeanValue(message, path, None, debug=True)
    print(f"{path} -> {val}")
