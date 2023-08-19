class TestFloat:
    def __init__(self, value: int) -> None:
        self.real = value
        self.bin = bin(value)[2:]
        
        if len(self.bin) == 64:
            self.sign = -1
        else:
            self.bin = "0" * (64 - len(self.bin)) + self.bin
            self.sign = 1

        self.man = 1
        self.exponent = -((2**15)-1)
        
        self._get_exponent()
        self._get_man()
    
    def _get_exponent(self) -> None:
        for index, bit in enumerate(self.bin[1:17]):
            if bit == "1":
                self.exponent += 2**(15-index)
    
    def _get_man(self) -> None:
        for index, bit in enumerate(self.bin[17:], 1):
            if bit == "1":
                self.man += 1/(1<<index)
    
    def __repr__(self) -> str:
        return str(self.man * (2**self.exponent))

    def __add__(self, x):
        if x.exponent == self.exponent:
            self.man += x.man
            return self
        
        larger = max(x.exponent, self.exponent)
        print(larger)
        
        return self
    
    def __mul__(self, x):
        if x.exponent == self.exponent:
            self.exponent <<= 1
            self.man *= x.man
            return self
        

print(TestFloat(0b0100000000000000000000000000000000000000000000000000000000000000) *
      TestFloat(0b0100000000000000011000000000000000000000000000000000000000000000))
