import sys
import struct
import json
import argparse
import re

def parse_arguments():
    parser = argparse.ArgumentParser(description='Интерпретатор для учебной виртуальной машины (УВМ)')
    parser.add_argument('-i', '--input', required=True, help='Путь к входному бинарному файлу')
    parser.add_argument('-r', '--range', required=True, help='Диапазон памяти для сохранения в формате start:end')
    parser.add_argument('-o', '--output', required=True, help='Путь к выходному JSON-файлу результата')
    return parser.parse_args()

class VirtualMachine:
    def __init__(self, memory_size=256):
        self.registers = {}  # Регистр: номер -> значение
        self.memory = [0] * memory_size  # Память
        self.program = []  # Список байт программы
        self.pc = 0  # Счетчик программы

    def load_program(self, binary_data):
        self.program = list(binary_data)
        print(f"Загружена программа: {self.program}")

    def execute(self):
        while self.pc < len(self.program):
            opcode = self.program[self.pc]
            print(f"\nPC={self.pc}, opcode={opcode}")
            if opcode == 9:  # LOAD_CONST
                if self.pc + 3 >= len(self.program):
                    raise ValueError("Недостаточно байт для команды LOAD_CONST")
                A = self.program[self.pc + 1]
                B = self.program[self.pc + 2]
                C = self.program[self.pc + 3]
                self.registers[B] = C
                print(f"LOAD_CONST: Регистр {B} загружен значением {C}")
                self.pc += 4
            elif opcode == 12:  # READ_MEM
                if self.pc + 4 >= len(self.program):
                    raise ValueError("Недостаточно байт для команды READ_MEM")
                A = self.program[self.pc + 1]
                B = self.program[self.pc + 2]
                C = self.program[self.pc + 3]
                D = self.program[self.pc + 4]
                base_address = self.registers.get(B, 0)
                offset = C
                address = base_address + offset
                if address < 0 or address >= len(self.memory):
                    raise ValueError(f"Недопустимый адрес памяти: {address}")
                self.registers[D] = self.memory[address]
                print(f"READ_MEM: Читаем значение {self.memory[address]} по адресу {address}, сохраняем в регистр {D}")
                self.pc += 5
            elif opcode == 27:  # WRITE_MEM
                if self.pc + 3 >= len(self.program):
                    raise ValueError("Недостаточно байт для команды WRITE_MEM")
                A = self.program[self.pc + 1]
                B = self.program[self.pc + 2]
                C = self.program[self.pc + 3]
                address = self.registers.get(B, 0)
                value = self.registers.get(C, 0)
                print(f"WRITE_MEM: Пытаемся записать значение {value} по адресу {address}")
                if address < 0 or address >= len(self.memory):
                    raise ValueError(f"Недопустимый адрес памяти: {address}")
                self.memory[address] = value
                print(f"WRITE_MEM: Значение {value} записано по адресу {address}")
                self.pc += 4
            elif opcode == 17:  # OR
                if self.pc + 4 >= len(self.program):
                    raise ValueError("Недостаточно байт для команды OR")
                A = self.program[self.pc + 1]
                B = self.program[self.pc + 2]
                C = self.program[self.pc + 3]
                D = self.program[self.pc + 4]
                operand1 = self.registers.get(B, 0)
                operand2 = self.registers.get(C, 0)
                result = operand1 | operand2
                self.registers[D] = result
                print(f"OR: Регистр {D} получает значение {result} (Регистр {B}: {operand1} | Регистр {C}: {operand2})")
                self.pc += 5
            else:
                raise ValueError(f"Неизвестный opcode: {opcode} на позиции {self.pc}")

            # Вывод состояния регистров после каждой команды
            print(f"Состояние регистров: {self.registers}")

    def get_memory_slice(self, start, end):
        return self.memory[start:end + 1]

def parse_memory_range(memory_range_str, memory_size):
    match = re.match(r'^(\d+):(\d+)$', memory_range_str)
    if not match:
        raise ValueError("Диапазон памяти должен быть в формате start:end")
    start, end = map(int, match.groups())
    if start < 0 or end >= memory_size or start > end:
        raise ValueError("Некорректный диапазон памяти")
    return start, end

def main():
    args = parse_arguments()

    # Чтение бинарного файла
    try:
        with open(args.input, 'rb') as f:
            binary_data = f.read()
    except FileNotFoundError:
        print(f"Ошибка: Файл {args.input} не найден.", file=sys.stderr)
        sys.exit(1)

    # Инициализация виртуальной машины
    vm = VirtualMachine()
    vm.load_program(binary_data)

    # Выполнение программы
    try:
        vm.execute()
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    # Парсинг диапазона памяти
    try:
        start, end = parse_memory_range(args.range, len(vm.memory))
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    # Извлечение диапазона памяти
    memory_slice = vm.get_memory_slice(start, end)

    # Сохранение результата в JSON
    result = {'memory': memory_slice}
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Выполнение программы завершено. Результат сохранен в {args.output}")

if __name__ == '__main__':
    main()
