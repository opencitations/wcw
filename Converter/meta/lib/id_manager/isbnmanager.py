from meta.lib.id_manager.identifiermanager import IdentifierManager
from re import sub


class ISBNManager(IdentifierManager):
    def __init__(self):
        self.p = "isbn:"
        super(ISBNManager, self).__init__()

    def is_valid(self, id_string):
        isbn = self.normalise(id_string)
        return isbn is not None and ISBNManager.__check_digit(isbn)

    def normalise(self, id_string, include_prefix=False):
        try:
            isbn_string = sub("[^X0-9]", "", id_string.upper())
            return "%s%s" % (self.p if include_prefix else "", isbn_string)
        except:  # Any error in processing the ISBN will return None
            return None

    @staticmethod
    def __check_digit(isbn):
        check_digit = False
        if len(isbn) == 13:
            total = 0
            val = 1
            for x in isbn:
                if x == "X":
                    x = 10
                total += int(x)*val
                val = 3 if val == 1 else val == 1
            if (total % 10) == 0:
                check_digit = True
        elif len(isbn) == 10:
            total = 0
            val = 10
            for x in isbn:
                if x == "X":
                    x = 10
                total += int(x)*val
                val -= 1
            if (total % 11) == 0:
                check_digit = True
        return check_digit
