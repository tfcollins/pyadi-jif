"""JESD parameterization definitions and helper functions."""
from abc import ABCMeta, abstractmethod
from typing import List


class jesd(metaclass=ABCMeta):
    """JESD interface class to manage JESD notations and definitions."""

    def __init__(
        self, sample_clock: int, M: int, L: int, Np: int, K: int, S: int
    ) -> None:
        """Initialize JESD device through link parameterization.

        Args:
            sample_clock (int): Human readable string describing the exception.
            M (int): Number of virtual converters
            L (int): Number of lanes
            Np (int): Number of bits per sample
            K (int): Frames per multiframe
            S (int): Samples per converter per frame

        """
        self.sample_clock = sample_clock
        self.K = K
        self.L = L
        self.M = M
        self.Np = Np
        self.S = S

    @property
    @abstractmethod
    def available_jesd_modes(self) -> List[str]:
        """Available JESD modes supported by device.

        Must be a list of strings

        Raises:
            NotImplementedError: If child classes do not implement method/property
        """
        raise NotImplementedError

    """ CS: Control bits per conversion sample 0-3"""
    _CS = 0

    """ CF: Control word per frame clock period per link 0-32 """
    _CF = 0

    """ HD: High density mode """
    _HD = 0

    # Encoding functions

    encodings_n = {"8b10b": 8, "64b66b": 64}
    encodings_d = {"8b10b": 10, "64b66b": 66}
    _encoding = "8b10b"

    @property
    def encoding(self) -> List[str]:
        """Get JESD FEC encoding.

        Current options are: "8b10b", "64b66b"

        Returns:
            List[str]: List of string of supported encodings.
        """
        return self._encoding

    @encoding.setter
    def encoding(self, value: List[str]) -> None:
        """Set JESD FEC encoding.

        Current options are: "8b10b", "64b66b"

        Args:
            value (str): List of strings of desired encoding to use

        Raises:
            Exception: If encoding selected that is not supported
        """
        if self._check_encoding(value):
            raise Exception("Must be {}".format(",".join(self.allowed_encodings)))
        self._encoding = value

    @property
    def encoding_d(self) -> int:
        """Get JESD FEC encoding denominator.

        Current options are: 10 or 66

        Returns:
            int: Denominator of link encoding.
        """
        return self.encodings_d[self._encoding]

    @property
    def encoding_n(self) -> int:
        """Get JESD FEC encoding numerator.

        Current options are: 8 or 64

        Returns:
            int: Numerator of link encoding.
        """
        return self.encodings_n[self._encoding]

    def _check_encoding(self, encode: str) -> bool:
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
    def data_path_width(self) -> int:
        """Get JESD data path width in bits.

        Current options are: 32 (204B) and 64 (204C)

        Returns:
            int: Numerator of link encoding.
        """
        return self._data_path_width

    @data_path_width.setter
    def data_path_width(self, value: int) -> None:
        """Set JESD data path width in bits.

        Current options are: 32 (204B) and 64 (204C)

        Args:
            value (int): Data path width in bits

        Raises:
            Exception: If DMA width is not an integer
        """
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
    def K(self) -> int:
        """Get Frames per multiframe.

        17/F <= K <= 32, is generally a multiple of 2

        Returns:
            int: Number of frames per multiframe
        """
        return self._K

    @K.setter
    def K(self, value: int) -> None:
        """Set Frames per multiframe.

        Args:
            value (int): Frames per multiframe

        Raises:
            Exception: K not an integer or not in range
        """
        if int(value) != value:
            raise Exception("K must be an integer")
        if value not in self.K_possible:
            raise Exception("K not in range for device")
        self._K = value

    @property
    def D(self) -> int:
        """FIXME."""
        return self._data_path_width * self.encoding_d / self.encoding_n

    """ S: Samples per converter per frame"""
    # _S = 1

    @property
    def S(self) -> int:
        """Get Samples per converter per frame.

        S == F/(M*Np) * encoding_p * L

        Returns:
            int: Samples per converter per frame
        """
        # F == self.M * self.S * self.Np / (self.encoding_n * self.L)
        return self.F / (self.M * self.Np) * self.encoding_n * self.L

    """ L: Lanes per link """
    L_min = 1
    L_max = 8
    L_possible = [1, 2, 4, 8]
    _L = 1

    @property
    def L(self) -> int:
        """Get lanes per link.

        Generally a multiple of 2

        Returns:
            int: Number of frames per multiframe
        """
        return self._L

    @L.setter
    def L(self, value: int) -> None:
        """Set lanes per link.

        Args:
            value (int): Lanes per link

        Raises:
            Exception: L not an integer or not in range
        """
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
    def M(self) -> int:
        """Get number of virtual converters.

        Generally a power of 2

        Returns:
            int: Number of frames per multiframe
        """
        return self._M

    @M.setter
    def M(self, value: int) -> None:
        """Set number of virtual converters.

        Args:
            value (int): Number of virtual converters

        Raises:
            Exception: M not an integer or not in range
        """
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
    def N(self) -> int:
        """Get number of non-dummy bits per sample.

        Generally a multiple of 2

        Returns:
            int: Number of non-dummy bits per sample
        """
        return self._N

    @N.setter
    def N(self, value: int) -> None:
        """Set Frames per multiframe.

        Args:
            value (int): Number of non-dummy bits per sample

        Raises:
            Exception: N not an integer or not in range
        """
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
    def Np(self) -> int:
        """Get number of bits per sample.

        Generally a multiple of 2

        Returns:
            int: Number of bits per sample
        """
        return self._Np

    @Np.setter
    def Np(self, value: int) -> None:
        """Set number of bits per sample.

        Args:
            value (int): Number of bits per sample

        Raises:
            Exception: Np not an integer or not in range
        """
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
    def F(self) -> int:
        """Get octets per frame per link.

        Generally a power of 2

        Returns:
            int: Number of octets per frame per link
        """
        return self._F

    @F.setter
    def F(self, value: int) -> None:
        """Set octets per frame per link.

        Args:
            value (int): Number of octets per frame per link

        Raises:
            Exception: F not an integer or not in range
        """
        if int(value) != value:
            raise Exception("F must be an integer")
        if value not in self.F_possible:
            raise Exception("F not in range for device")
        self._F = value

    # CLOCKS
    """ sample_clock: Data rate after decimation stages in Samples/second """

    _sample_clock = 122.88e6

    @property
    def sample_clock(self) -> int:
        """Data rate after decimation stages in Samples/second.

        Returns:
            int: Data rate in samples per second
        """
        return self._sample_clock

    @sample_clock.setter
    def sample_clock(self, value: int) -> None:
        """Data rate after decimation stages in Samples/second.

        Args:
            value (int): Number of octets per frame per link
        """
        self._sample_clock = value

    @property
    def frame_clock(self) -> int:
        """frame_clock in frames per second.

        frame_clock == sample_clock / S

        Returns:
            int: Data rate in samples per second
        """
        return self.sample_clock / self.S

    @property
    def multiframe_clock(self) -> int:
        """multiframe_clock: aka LMFC in frames per multiframe.

        multiframe_clock == frame_clock / K

        Returns:
            int: Frames per multiframe
        """
        return self.frame_clock / self.K

    @property
    def bit_clock(self) -> int:
        """bit_clock: aka line rate aka lane rate.

        bit_clock == (M * S * Np * encoding_d/encoding_n * frame_clock) / L

        Returns:
            int: Bits per second aka lane rate
        """
        return (
            self.M
            * self.S
            * self.Np
            * self.encoding_d
            / self.encoding_n
            * self.frame_clock
        ) / self.L

    @property
    def device_clock(self) -> int:
        """device_clock is the lane rate over D.

        device_clock == bit_clock / D

        Returns:
            int: bits per second per device
        """
        return self.bit_clock / self.D

    # def print_clocks(self) -> None:
    #     for p in dir(self):
    #         if p != "print_clocks":
    #             if "clock" in p and p[0] != "_":
    #                 print(p, getattr(self, p) / 1000000)
    #             if "rate" in p and p[0] != "_":
    #                 print(p, getattr(self, p) / 1000000)
