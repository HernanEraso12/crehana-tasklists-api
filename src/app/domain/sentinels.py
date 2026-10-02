"""Sentinel para distinguir "campo no enviado" de "campo enviado como
None" en actualizaciones parciales (C2)."""


class _Unset:
    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()
