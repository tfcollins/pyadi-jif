from abc import ABCMeta, abstractmethod


class jesd(metaclass=ABCMeta):
    """ JESD Rate Manager """

    @property
    @abstractmethod
    def available_jesd_modes(self):
        raise NotImplementedError

    """ CS: Control bits per conversion sample 0-3"""
    _CS = 0

    """ CF: Control word per frame clock period per link 0-32 """
    _CF = 0

    """ HD: High density mode """
    _HD = 0

    def __init__(self, sample_clock, M, L, Np, K, S):

        self.sample_clock = sample_clock
        self.K = K
        self.L = L
        self.M = M
        self.Np = Np
        self.S = S

    # Encoding functions

    encodings_n = {"8b10b": 8, "64b66b": 64}
    encodings_d = {"8b10b": 10, "64b66b": 66}
    _encoding = "8b10b"

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        if self._check_encoding(value):
            raise Exception("Must be {}".format(",".join(self.allowed_encodings)))
        self._encoding = value

    @property
    def encoding_d(self):
        return self.encodings_d[self._encoding]

    @property
    def encoding_n(self):
        return self.encodings_n[self._encoding]

    def _check_encoding(self, encode):
        if "jesd204C" in self.available_jesd_modes:
            allowed_encodings = ["8b10b", "64b66b"]
        else:
            allowed_encodings = ["8b10b"]
        return encode in allowed_encodings

    # SCALERS

    """ bits
        Usually:
            32 for JESD204B
            64 for JESD204C
    """
    _data_path_width = 32

    @property
    def data_path_width(self):
        return self._data_path_width

    @data_path_width.setter
    def data_path_width(self, value):
        if int(value) != value:
            raise Exception("data_path_width must be an integer")
        self._data_path_width = value

    """ K: Frames per multiframe
        17/F <= K <= 32
    """
    K_min = 4
    K_max = 32
    K_possible = [4, 8, 12, 16, 20, 24, 28, 32]
    _K = 4

    @property
    def K(self):
        return self._K

    @K.setter
    def K(self, value):
        if int(value) != value:
            raise Exception("K must be an integer")
        if value not in self.K_possible:
            raise Exception("K not in range for device")
        self._K = value

    @property
    def D(self):
        return self._data_path_width * self.encoding_d / self.encoding_n

    """ S: Samples per converter per frame"""
    # _S = 1

    @property
    def S(self):
        # F == self.M * self.S * self.Np / (self.encoding_n * self.L)
        return self.F / (self.M * self.Np) * self.encoding_n * self.L

    """ L: Lanes per link """
    L_min = 1
    L_max = 8
    L_possible = [1, 2, 4, 8]
    _L = 1

    @property
    def L(self):
        return self._L

    @L.setter
    def L(self, value):
        if int(value) != value:
            raise Exception("L must be an integer")
        if value not in self.L_possible:
            raise Exception("L not in range for device")
        self._L = value

    """ M: Number of virtual converters """
    M_min = 1
    M_max = 8
    M_possible = [1, 2, 4, 8, 16, 32]
    _M = 1

    @property
    def M(self):
        return self._M

    @M.setter
    def M(self, value):
        if int(value) != value:
            raise Exception("M must be an integer")
        if value not in self.M_possible:
            raise Exception("M not in range for device")
        self._M = value

    """ N: Number of non-dummy bits per sample """
    N_min = 12
    N_max = 16
    N_possible = [12, 14, 16]
    _N = 12

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, value):
        if int(value) != value:
            raise Exception("N must be an integer")
        if value not in self.N_possible:
            raise Exception("N not in range for device")
        self._N = value

    """ Np: Number of bits per sample """
    Np_min = 12
    Np_max = 16
    Np_possible = [12, 14, 16]
    _Np = 16

    @property
    def Np(self):
        return self._Np

    @Np.setter
    def Np(self, value):
        if int(value) != value:
            raise Exception("Np must be an integer")
        if value not in self.Np_possible:
            raise Exception("Np not in range for device")
        self._Np = value

    # DERIVED SCALERS
    """ F: Octets per frame per link
        This is read-only since it depends on L,M,Np,S, and encoding
    """
    F_min = 1
    F_max = 16
    F_possible = [1, 2, 4, 8, 16]
    _F = 1

    @property
    def F(self):
        return self._F

    @F.setter
    def F(self, value):
        if int(value) != value:
            raise Exception("F must be an integer")
        if value not in self.F_possible:
            raise Exception("F not in range for device")
        self._F = value

    # CLOCKS
    """ sample_clock: Data rate after decimation stages in Samples/second """

    _sample_clock = 122.88e6

    @property
    def sample_clock(self):
        """ Data rate after decimation stages in Samples/second """
        return self._sample_clock

    @sample_clock.setter
    def sample_clock(self, value):
        self._sample_clock = value

    @property
    def frame_clock(self):
        """frame_clock: FC"""
        return self.sample_clock / self.S

    @property
    def multiframe_clock(self):
        """ multiframe_clock: aka LMFC """
        return self.frame_clock / self.K

    @property
    def bit_clock(self):
        """ bit_clock: aka line rate aka lane rate"""
        return (
            self.M
            * self.S
            * self.Np
            * self.encoding_d
            / self.encoding_n
            * self.frame_clock
        ) / self.L

    @property
    def device_clock(self):
        return self.bit_clock / self.D

    def print_clocks(self):
        for p in dir(self):
            if p != "print_clocks":
                if "clock" in p and p[0] != "_":
                    print(p, getattr(self, p) / 1000000)
                if "rate" in p and p[0] != "_":
                    print(p, getattr(self, p) / 1000000)
