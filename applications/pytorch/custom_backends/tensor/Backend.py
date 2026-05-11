import numpy as np
import tcu_hw


class TensorBackend:
    """Hardware matmul backend backed by a Verilated TCU simulation.

    Supports two operating modes selected at construction or at runtime:

    Golden mode  (fault_config=None)
        Uses TcuHardware — the standard simulation with no fault injection.
        All float-format operations pass through the clean pipeline.

    Fault-injection mode  (fault_config=tcu_hw.FaultConfig(...))
        Uses TcuFiHardware — the FI-instrumented simulation.
        Every tile execution programs the shift register and activates the
        saboteurs described by fault_config before reading the result.

    Parameters
    ----------
    bitwidth : int
        Quantisation bit-width (used only for format="int").
    format : str
        "float" routes through the hardware simulation (golden or FI).
        "int"   quantises inputs and runs a pure NumPy integer matmul;
                fault injection is not applied in this mode.
    tile_latency : int
        Clock cycles the hardware pipeline takes per 4×4 tile.
    persistent_core : bool
        When True a single hardware instance is created at init and reused
        across calls, avoiding the Verilated model construction overhead.
        When False a fresh instance is created for every matmul call.
    fault_config : tcu_hw.FaultConfig | None
        Active fault descriptor.  None = no fault (golden path).
        Can be changed at runtime via set_fault_config().
    sr_length : int
        Shift-register length of the FI-instrumented RTL variant.
        Must match the WIDTH_SR parameter of the targeted fpadd_3_pipe_sbtr
        instance (1534 for the current sub_tensor_core_fi_sbtr.v).
        Only relevant when fault_config is not None.
    """

    def __init__(
        self,
        bitwidth: int = 8,
        format: str = "float",
        tile_latency: int = 12,
        persistent_core: bool = True,
        fault_config: "tcu_hw.FaultConfig | None" = None,
        sr_length: int = 1534,
    ):
        self.bitwidth        = bitwidth
        self.format          = format
        self.tile_latency    = tile_latency
        self.persistent_core = persistent_core
        self.fault_config    = fault_config
        self.sr_length       = sr_length

        self._core = self._build_core() if persistent_core else None

    def _build_core(self):
        """Instantiate the hardware core matching the current fault state."""
        if self.fault_config is not None:
            return tcu_hw.TcuFiHardware(
                sr_length=self.sr_length,
                tile_latency=self.tile_latency,
            )
        return tcu_hw.TcuHardware(tile_latency=self.tile_latency)

    def set_fault_config(self, fault_config: "tcu_hw.FaultConfig | None") -> None:
        """Enable, update, or disable fault injection at runtime.

        If the required core type changes (golden ↔ FI) and persistent_core
        is True, the hardware instance is rebuilt transparently.

        Parameters
        ----------
        fault_config : tcu_hw.FaultConfig | None
            New fault descriptor, or None to return to the golden mode.
        """
        prev_is_fi   = self.fault_config is not None
        new_is_fi    = fault_config      is not None
        self.fault_config = fault_config

        # Rebuild the persistent core only when the mode actually changes.
        if self.persistent_core and (prev_is_fi != new_is_fi):
            self._core = self._build_core()

    def clear_fault(self) -> None:
        """Disable fault injection and return to the golden path."""
        self.set_fault_config(None)

    def matmul_fn(self, A, B, C) -> np.ndarray:
        """Execute A @ B + C on the configured hardware backend.

        Routes to the golden or FI simulation based on fault_config.
        The "int" format always uses a NumPy fallback regardless of fault state,
        because the hardware FI model operates on float32 only.
        """
        if self.format == "float":
            A = np.asarray(A, dtype=np.float32)
            B = np.asarray(B, dtype=np.float32)
            C = np.asarray(C, dtype=np.float32)
        elif self.format == "int":
            A = np.asarray(A, dtype=np.int32)
            B = np.asarray(B, dtype=np.int32)
            C = np.asarray(C, dtype=np.int32)
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        if A.ndim != 2 or B.ndim != 2 or C.ndim != 2:
            raise ValueError("A, B, and C must be 2D matrices")
        if A.shape[1] != B.shape[0]:
            raise ValueError(f"Incompatible shapes: A{A.shape} @ B{B.shape}")
        expected_c = (A.shape[0], B.shape[1])
        if C.shape != expected_c:
            raise ValueError(f"C must have shape {expected_c}, got {C.shape}")

        if self.format == "float":
            return self._run_float(A, B, C)

        # format == "int": pure NumPy path, no hardware simulation involved.
        return A @ B + C

    def _run_float(self, A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
        """Dispatch a float32 matmul to the golden or FI hardware core."""
        if self.fault_config is not None:
            # FI path: every tile is executed with the active fault configuration.
            if self._core is not None:
                return self._core.matmul_fi(A, B, C, self.fault_config)
            return tcu_hw.matmul_fi_hw(
                A, B, C, self.fault_config,
                sr_length=self.sr_length,
                tile_latency=self.tile_latency,
            )
        else:
            # Golden path: no fault active.
            if self._core is not None:
                return self._core.matmul(A, B, C)
            return tcu_hw.matmul_hw(A, B, C, tile_latency=self.tile_latency)

    def matmul(self, A, B, C) -> np.ndarray:
        return self.matmul_fn(A, B, C)
