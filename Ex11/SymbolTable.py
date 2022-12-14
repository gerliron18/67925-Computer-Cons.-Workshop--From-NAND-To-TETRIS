"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


CONST = "CONST"
LOCAL = "LOCAL"
THIS = "THIS"
THAT = "THAT"
POINTER ="POINTER"
TEMP="TEMP"

STATIC, FIELD, ARG, VAR = "STATIC", "FIELD", "ARG", "VAR"
SUBROUTINE_VARS = [ARG, VAR]
CLASS_VARS = [FIELD, STATIC]
TYPE = 'type'
KIND = 'kind'
IDX = 'idx'


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.indices_dict = {FIELD: 0, STATIC: 0, VAR: 0, ARG: 0}
        self.class_symbols = dict()
        self.subroutine_symbols = dict()

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_symbols = dict()
        self.indices_dict[VAR] = 0
        self.indices_dict[ARG] = 0

    def includes(self, name: str) -> bool:
        return name in self.subroutine_symbols.keys() or name in self.class_symbols.keys()


    def define(self, name: str, symbol_type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            symbol_type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in SUBROUTINE_VARS:
            self.subroutine_symbols[name] = {TYPE: symbol_type, KIND: kind, IDX: self.indices_dict[kind]}
        if kind in CLASS_VARS:
            self.class_symbols[name] = {TYPE: symbol_type, KIND: kind, IDX: self.indices_dict[kind]}
        self.indices_dict[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.indices_dict[kind]

    def _get_symbol_prop(self, name: str, prop: str):
        if name in self.subroutine_symbols.keys():
            return self.subroutine_symbols[name][prop]
        if name in self.class_symbols.keys():
            return self.class_symbols[name][prop]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        return self._get_symbol_prop(name, KIND)

    def segment_of(self, name: str) -> str:
        kind = self.kind_of(name)
        if kind == "VAR":
            return "LOCAL"
        if kind == "FIELD":
            return "THIS"
        return kind  # STATIC or ARG

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        return self._get_symbol_prop(name, TYPE)

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        return self._get_symbol_prop(name, IDX)

