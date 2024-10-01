def parse_qps_file(filename, pars_header_only=False):
    try:
        with open(filename, 'rb') as f:
            b = f.read()

        if len(b) < 1000:
            return False

        qps_type = -1
        hdr_type = chr(b[0x55]) + chr(b[0x56])
        print(f"Тип заголовка: {hdr_type}")

        # Количество строковых переменных
        string_count = int.from_bytes(b[22:26], byteorder='little')
        print(f"Количество строк: {string_count}")
        i = 22
        while i < len(b):
            sting = read_string_from_bytes(b, i, 4)
            print(sting)
            print(int.from_bytes(b[i:i+4], byteorder='little'))
            i += 4

            print()



    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return False


def read_string_from_bytes(data, start_index, length):
    return data[start_index:start_index + length].decode('utf-8', errors='ignore')

parse_qps_file("test.qps")