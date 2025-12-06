class IntInputNotInLegalRangeError(Exception):
    def __init__(self, message: str='+1000 Aura'):
        """
        No magic here, just a custom exception to indicate that
        """
        self.message = message
        super().__init__(self.message)

if __name__ == '__main__':
    try:
        raise IntInputNotInLegalRangeError
    except IntInputNotInLegalRangeError as e:
        print(e.message)