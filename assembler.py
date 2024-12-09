import sys
import struct
import json
import argparse
import re

# Определение опкодов
OPCODES = {
    'LOAD_CONST': 9,
    'READ_MEM': 12,
    'WRITE_MEM': 27,
    'OR': 17
}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Ассемблер для учебной виртуальной машины (УВМ)')
    parser.add_argument('-i', '--input', required=True, help='Путь к входному ассемблерному файлу')
    parser.add_argument('-o', '--output', required=True, help='Путь к выходному бинарному файлу')
    parser.add_argument('-l', '--log', required=True, help='Путь к выходному JSON-файлу лога')
    return parser.parse_args()

def assemble_instruction(line_num, tokens):
    if not tokens:
        return b'', {}

    mnemonic = tokens[0].upper()
    if mnemonic not in OPCODES:
        raise ValueError(f"Строка {line_num}: Неизвестный мнемоник '{mnemonic}'")

    opcode = OPCODES[mnemonic]
    log_entry = {'mnemonic': mnemonic}

    try:
        if mnemonic == 'LOAD_CONST':
            if len(tokens) != 4:
                raise ValueError(f"Строка {line_num}: LOAD_CONST требует 3 операнда")
            A, B, C = map(int, tokens[1:4])
            encoded = bytes([opcode, A, B, C])
            log_entry.update({'A': A, 'B': B, 'C': C})
        elif mnemonic == 'READ_MEM':
            if len(tokens) != 5:
                raise ValueError(f"Строка {line_num}: READ_MEM требует 4 операнда")
            A, B, C, D = map(int, tokens[1:5])
            encoded = bytes([opcode, A, B, C, D])
            log_entry.update({'A': A, 'B': B, 'C': C, 'D': D})
        elif mnemonic == 'WRITE_MEM':
            if len(tokens) != 4:
                raise ValueError(f"Строка {line_num}: WRITE_MEM требует 3 операнда")
            A, B, C = map(int, tokens[1:4])
            encoded = bytes([opcode, A, B, C])
            log_entry.update({'A': A, 'B': B, 'C': C})
        elif mnemonic == 'OR':
            if len(tokens) != 5:
                raise ValueError(f"Строка {line_num}: OR требует 4 операнда")
            A, B, C, D = map(int, tokens[1:5])
            encoded = bytes([opcode, A, B, C, D])
            log_entry.update({'A': A, 'B': B, 'C': C, 'D': D})
    except ValueError as e:
        raise ValueError(f"Строка {line_num}: Некорректные операнды. {e}")

    return encoded, log_entry

def assemble(input_path, output_path, log_path):
    binary_output = bytearray()
    log_output = {}

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Прочитано {len(lines)} строк из файла {input_path}.")

    for line_num, line in enumerate(lines, 1):
        # Удаляем комментарии и лишние пробелы
        line = line.split('#', 1)[0].strip()
        if not line:
            continue  # Пропускаем пустые строки

        tokens = re.split(r'\s+', line)
        print(f"Строка {line_num}: токены -> {tokens}")  # Отладочный вывод

        try:
            encoded, log_entry = assemble_instruction(line_num, tokens)
            if encoded:
                print(f"Кодировка: {tokens} -> {encoded.hex()}")  # Отладочный вывод
                binary_output.extend(encoded)
                log_output[f'instruction_{line_num}'] = log_entry
        except ValueError as ve:
            print(f"Ошибка при обработке строки {line_num}: {ve}", file=sys.stderr)
            sys.exit(1)

    print(f"Готово к записи {len(binary_output)} байт в {output_path}.")

    # Запись бинарного файла
    with open(output_path, 'wb') as f:
        f.write(binary_output)

    # Запись файла лога
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_output, f, ensure_ascii=False, indent=2)

    print(f"Ассемблирование завершено. Бинарный файл: {output_path}, Лог файл: {log_path}")

def main():
    args = parse_arguments()
    assemble(args.input, args.output, args.log)

if __name__ == '__main__':
    main()
