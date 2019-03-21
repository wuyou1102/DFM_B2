def _protocol_set():
    for x in range(3):
        result = None
        try:
            if len(result) == 16 and int(result) == 0:
                return True
        except ValueError and TypeError:
            pass
        # except TypeError:
        #     pass

    print("I got a wrong number : [%s]" % repr(result))
    return False


_protocol_set()
