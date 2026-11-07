from typing import List, Dict, Optional
from .ir_generator import TACInstruction
from .ast_nodes import Program

ARG_REGISTERS = ["edi", "esi", "edx", "ecx", "r8d", "r9d"]

class X86CodeGenerator:
    def __init__(self):
        self.asm_lines: List[str] = []
        self.stack_offsets: Dict[str, int] = {}
        self.current_stack_size = 0
        self.param_queue: List[str] = []

    def get_offset(self, var_name: str) -> int:
        if var_name not in self.stack_offsets:
            self.current_stack_size += 8
            self.stack_offsets[var_name] = self.current_stack_size
        return self.stack_offsets[var_name]

    def emit(self, line: str):
        self.asm_lines.append(line)

    def generate(self, tac_list: List[TACInstruction]) -> str:
        self.asm_lines.clear()
        self.param_queue.clear()

        self.emit(".intel_syntax noprefix")
        self.emit(".text")

        current_func: Optional[str] = None
        func_instructions: List[TACInstruction] = []

        for instr in tac_list:
            if instr.op == "FUNC_BEGIN":
                current_func = instr.result
                func_instructions = []
            elif instr.op == "FUNC_END":
                self._generate_function(current_func, func_instructions)
                current_func = None
                func_instructions = []
            elif current_func is not None:
                func_instructions.append(instr)

        return "\n".join(self.asm_lines)

    def _is_constant(self, s: Optional[str]) -> bool:
        if not s:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _generate_function(self, func_name: str, instructions: List[TACInstruction]):
        self.stack_offsets.clear()
        self.current_stack_size = 0
        self.param_queue.clear()

        for instr in instructions:
            if instr.result and not instr.result.startswith("L_"):
                self.get_offset(instr.result)
            if instr.arg1 and not self._is_constant(instr.arg1) and not instr.arg1.startswith("arg_"):
                self.get_offset(instr.arg1)
            if instr.arg2 and not self._is_constant(instr.arg2) and not instr.arg2.startswith("arg_"):
                self.get_offset(instr.arg2)

        frame_size = ((self.current_stack_size + 15) // 16) * 16
        if frame_size == 0:
            frame_size = 16

        self.emit(f"\n.globl {func_name}")
        self.emit(f".type {func_name}, @function")
        self.emit(f"{func_name}:")
        self.emit("    push rbp")
        self.emit("    mov rbp, rsp")
        self.emit(f"    sub rsp, {frame_size}")

        for instr in instructions:
            self._translate_instruction(instr, func_name)

        self.emit(f".size {func_name}, .-{func_name}")

    def _load_operand(self, reg: str, operand: str):
        if self._is_constant(operand):
            val = int(float(operand))
            self.emit(f"    mov {reg}, {val}")
        elif operand.startswith("arg_"):
            arg_idx = int(operand.split("_")[1])
            if arg_idx < len(ARG_REGISTERS):
                src_reg = ARG_REGISTERS[arg_idx]
                self.emit(f"    mov {reg}, {src_reg}")
            else:
                stack_arg_off = 16 + (arg_idx - 6) * 8
                self.emit(f"    mov {reg}, DWORD PTR [rbp + {stack_arg_off}]")
        else:
            off = self.get_offset(operand)
            self.emit(f"    mov {reg}, DWORD PTR [rbp - {off}]")

    def _store_result(self, dest: str, reg: str):
        off = self.get_offset(dest)
        self.emit(f"    mov DWORD PTR [rbp - {off}], {reg}")

    def _translate_instruction(self, instr: TACInstruction, func_name: str):
        op = instr.op

        if op == "LABEL":
            if not instr.result.startswith("func_"):
                self.emit(f".{instr.result}:")

        elif op == "ASSIGN":
            self._load_operand("eax", instr.arg1)
            self._store_result(instr.result, "eax")

        elif op in ("+", "-", "*"):
            self._load_operand("eax", instr.arg1)
            self._load_operand("ebx", instr.arg2)
            if op == "+":
                self.emit("    add eax, ebx")
            elif op == "-":
                self.emit("    sub eax, ebx")
            elif op == "*":
                self.emit("    imul eax, ebx")
            self._store_result(instr.result, "eax")

        elif op in ("/", "%"):
            self._load_operand("eax", instr.arg1)
            self._load_operand("ebx", instr.arg2)
            self.emit("    cdq")
            self.emit("    idiv ebx")
            if op == "/":
                self._store_result(instr.result, "eax")
            else:
                self._store_result(instr.result, "edx")

        elif op in ("==", "!=", "<", "<=", ">", ">="):
            self._load_operand("eax", instr.arg1)
            self._load_operand("ebx", instr.arg2)
            self.emit("    cmp eax, ebx")
            set_instr = {
                "==": "sete", "!=": "setne",
                "<": "setl", "<=": "setle",
                ">": "setg", ">=": "setge"
            }[op]
            self.emit(f"    {set_instr} al")
            self.emit("    movzx eax, al")
            self._store_result(instr.result, "eax")

        elif op in ("&&", "||"):
            self._load_operand("eax", instr.arg1)
            self._load_operand("ebx", instr.arg2)
            if op == "&&":
                self.emit("    and eax, ebx")
            else:
                self.emit("    or eax, ebx")
            self.emit("    setne al")
            self.emit("    movzx eax, al")
            self._store_result(instr.result, "eax")

        elif op == "NEG":
            self._load_operand("eax", instr.arg1)
            self.emit("    neg eax")
            self._store_result(instr.result, "eax")

        elif op == "NOT":
            self._load_operand("eax", instr.arg1)
            self.emit("    cmp eax, 0")
            self.emit("    sete al")
            self.emit("    movzx eax, al")
            self._store_result(instr.result, "eax")

        elif op == "GOTO":
            self.emit(f"    jmp .{instr.result}")

        elif op == "IF_FALSE":
            self._load_operand("eax", instr.arg1)
            self.emit("    cmp eax, 0")
            self.emit(f"    je .{instr.result}")

        elif op == "IF_TRUE":
            self._load_operand("eax", instr.arg1)
            self.emit("    cmp eax, 0")
            self.emit(f"    jne .{instr.result}")

        elif op == "PARAM":
            self.param_queue.append(instr.arg1)

        elif op == "CALL":
            num_args = int(instr.arg2) if instr.arg2 else len(self.param_queue)
            for i in range(min(num_args, len(ARG_REGISTERS))):
                p_arg = self.param_queue[i]
                target_reg = ARG_REGISTERS[i]
                self._load_operand(target_reg, p_arg)

            self.emit(f"    call {instr.arg1}")
            self.param_queue.clear()

            if instr.result:
                self._store_result(instr.result, "eax")

        elif op == "RETURN":
            if instr.arg1:
                self._load_operand("eax", instr.arg1)
            else:
                self.emit("    mov eax, 0")
            self.emit("    leave")
            self.emit("    ret")
