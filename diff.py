import re, collections

class DiffCommands():
    def __init__(self, file_name_or_diff):
        self.file_name_or_diff = file_name_or_diff
        self.contents = None
        if '.txt' in file_name_or_diff:
            self.check_contents()
        else:
            self.contents = file_name_or_diff

    def check_contents(self):
        with open(self.file_name_or_diff, 'r') as f:
            self.contents = [a.replace('\n', '') for a in f.readlines()]

        # test = re.compile(r'(?:^(\d+)(?:,(\d+))?(d)(\d+)$)|(?:^(\d+)(a)(\d+)(?:,(\d+))?$)|(?:^(\d+)(?:,(\d+))?(c)(\d+)(?:,(\d+))?$)')
        test = re.compile(r'(?:^(\d|[1-9]\d+)(?:,(\d|[1-9]\d+))?(d)(\d|[1-9]\d+)$)|(?:^(\d|[1-9]\d+)(a)(\d|[1-9]\d+)(?:,(\d|[1-9]\d+))?$)|(?:^(\d|[1-9]\d+)(?:,(\d|[1-9]\d+))?(c)(\d|[1-9]\d+)(?:,(\d|[1-9]\d+))?$)')

        try:
            container = [[a for a in test.match(c).groups() if a is not None] for c in self.contents]
        except AttributeError:
            raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')

        container_digit = [(0, 0)]
        for item in container:
            if 'd' in item:
                m1 = [int(x) for x in item[:item.index('d')]]
                m2 = [int(x) for x in item[item.index('d') + 1:]]
                container_digit.extend([(m1[0] - 1, m2[0]), (m1[-1] + 1, m2[-1] + 1)])
            if 'a' in item:
                m1 = [int(x) for x in item[:item.index('a')]]
                m2 = [int(x) for x in item[item.index('a') + 1:]]
                container_digit.extend([(m1[0], m2[0] - 1), (m1[-1] + 1, m2[-1] + 1)])
            if 'c' in item:
                m1 = [int(x) for x in item[:item.index('c')]]
                m2 = [int(x) for x in item[item.index('c') + 1:]]
                container_digit.extend([(m1[0] - 1, m2[0] - 1), (m1[-1] + 1, m2[-1] + 1)])

        container_var = [(container_digit[i + 1][0] - container_digit[i][0], container_digit[i + 1][1] - container_digit[i][1]) \
            for i in range(0, len(container_digit) - 1, 2)]

        if not all([i[0] == i[1] and i[0] >= 0 for i in container_var]):
            raise DiffCommandsError('Cannot possibly be the commands for the diff of two files')            

    def __str__(self):
        return '\n'.join(self.contents)

class DiffCommandsError(Exception):
    def __init__(self, message):
        self.message = message


class OriginalNewFiles():
    def __init__(self, file_name_1, file_name_2):
        self.all_diff_commands = None
        self.file_name_1 = file_name_1
        self.file_name_2 = file_name_2
        with open(self.file_name_1, 'r') as f1:
            self.contents_1 = [a.replace('\n', '') for a in f1.readlines()]
        with open(self.file_name_2, 'r') as f2:
            self.contents_2 = [a.replace('\n', '') for a in f2.readlines()]

    def is_a_possible_diff(self, file_DiffCommands):
        self.get_all_diff_commands()
        # print(str(file_DiffCommands))
        # print(self.all_diff_commands)
        return str(file_DiffCommands) in self.all_diff_commands

    def output_diff(self, file_DiffCommands):
        diff_list = str(file_DiffCommands).split()
        for item in diff_list:
            print(item)
            if 'd' in item:
                process = [int(a) for a in item.split('d')[0].split(',')]
                if len(process) == 1:
                    print('<', self.contents_1[process[0] - 1])
                else:
                    for i in self.contents_1[process[0] - 1: process[1]]:
                        print('<', i)
            elif 'a' in item:
                process = [int(a) for a in item.split('a')[1].split(',')]
                if len(process) == 1:
                    print('>', self.contents_2[process[0] - 1])
                else:
                    for i in self.contents_2[process[0] - 1: process[1]]:
                        print('>', i)
            else:
                process_1, process_2 = item.split('c')
                process_1 = [int(a) for a in process_1.split(',')]
                process_2 = [int(a) for a in process_2.split(',')]
                if len(process_1) == 1:
                    print('<', self.contents_1[process_1[0] - 1])
                else:
                    for i in self.contents_1[process_1[0] - 1: process_1[1]]:
                        print('<', i)
                print('---')
                if len(process_2) == 1:
                    print('>', self.contents_2[process_2[0] - 1])
                else:
                    for i in self.contents_2[process_2[0] - 1: process_2[1]]:
                        print('>', i)       

    def output_unmodified_from_original(self, file_DiffCommands):
        diff_list = str(file_DiffCommands).split()
        process_content = self.contents_1[:]
        for item in diff_list:
            if 'd' in item:
                process = [int(a) for a in item.split('d')[0].split(',')]
                for i in range(process[0] - 1, process[-1]):
                    process_content[i] = '...'
            elif 'a' in item:
                pass
            else:
                process = [int(a) for a in item.split('c')[0].split(',')]
                for i in range(process[0] - 1, process[-1]):
                    process_content[i] = '...'
        p_pre = None
        for p in process_content:
            if p == '...' and p_pre == '...':
                continue 
            print(p)
            p_pre = p

    def output_unmodified_from_new(self, file_DiffCommands):
        diff_list = str(file_DiffCommands).split()
        process_content = self.contents_2[:]
        for item in diff_list:
            if 'd' in item:
                pass
            elif 'a' in item:
                process = [int(a) for a in item.split('a')[-1].split(',')]
                for i in range(process[0] - 1, process[-1]):
                    process_content[i] = '...'
            else:
                process = [int(a) for a in item.split('c')[-1].split(',')]
                for i in range(process[0] - 1, process[-1]):
                    process_content[i] = '...'
        p_pre = None
        for p in process_content:
            if p == '...' and p_pre == '...':
                continue 
            print(p)
            p_pre = p  


    def get_all_diff_commands(self):
        all_diff = []
        all_diff_code = list(self.get_lcs())
        for diff_code in all_diff_code:
            diff_string = ''
            diff_code.insert(0, (0, 0))
            diff_code.append((len(self.contents_1) + 1, len(self.contents_2) + 1))
            diff_code_var = [a for a in [(diff_code[x + 1][0] - diff_code[x][0] - 1, diff_code[x + 1][1] - diff_code[x][1] - 1, \
                diff_code[x], diff_code[x + 1]) for x in range(len(diff_code) - 1)] if a[0] != 0 or a[1] != 0]
            # print('diff_code_var:', diff_code_var)
            for var in diff_code_var:
                if var[0] != 0 and var[1] == 0:
                    diff_string += str(var[2][0] + 1) + ',' + str(var[3][0] - 1) + 'd' + str(var[2][1]) + '\n' \
                        if var[0] > 1 else str(var[2][0] + 1) + 'd' + str(var[2][1]) + '\n'
                elif var[0] == 0 and var[1] != 0:
                    diff_string += str(var[2][0]) + 'a' + str(var[2][1] + 1) + ',' + str(var[3][1] - 1) + '\n' \
                        if var[1] > 1 else str(var[2][0]) + 'a' + str(var[2][1] + 1) + '\n'
                else:
                    diff_string += str(var[2][0] + 1) + ',' + str(var[3][0] - 1) + 'c' \
                        if var[0] > 1 else str(var[2][0] + 1) + 'c'
                    diff_string += str(var[2][1] + 1) + ',' + str(var[3][1] - 1) + '\n' \
                        if var[1] > 1 else str(var[2][1] + 1) + '\n'
            all_diff.append(diff_string.strip())
        if all_diff:
            self.all_diff_commands = all_diff
            return [DiffCommands(a.split('\n')) for a in sorted(all_diff)]
        else:
            # print('contents1:', self.contents_1)
            # print('contents2:', self.contents_2)
            if self.contents_1 == [] and self.contents_2 == []:
                self.all_diff_commands = ['']
                return [DiffCommands('')]
            elif self.contents_1 == [] and self.contents_2 != []:
                if len(self.contents_2) > 1:
                    self.all_diff_commands = ['0a1,' + str(len(self.contents_2))]
                else:
                    self.all_diff_commands = ['0a1']
                return [DiffCommands([self.all_diff_commands[0]])]
            elif self.contents_1 != [] and self.contents_2 == []:
                if len(self.contents_1) > 1:
                    self.all_diff_commands = ['1,' + str(len(self.contents_1)) + 'd0']
                else:
                    self.all_diff_commands = ['1d0']
                return [DiffCommands([self.all_diff_commands[0]])]
            else:
                str_c = ''
                if len(self.contents_1) > 1:
                    str_c = '1,' + str(len(self.contents_1)) + 'c'
                else:
                    str_c = '1c'
                if len(self.contents_2) > 1:
                    str_c += '1,' + str(len(self.contents_2))
                else:
                    str_c += '1'
                self.all_diff_commands = [str_c]
                # print(self.all_diff_commands[0])
                # print(DiffCommands(self.all_diff_commands[0]))
                return [DiffCommands([self.all_diff_commands[0]])]


    def get_lcs(self):
        len_1 = len(self.contents_1)
        len_2 = len(self.contents_2)
        matrix = [[0 for _ in range(len_2 + 1)] for _ in range(len_1 + 1)]
        target_dict = collections.defaultdict(list)
        for i in range(len_1):
            for j in range(len_2):
                if self.contents_1[i] == self.contents_2[j]:
                    matrix[i + 1][j + 1] = matrix[i][j] + 1
                    target_dict[matrix[i + 1][j + 1]].append((i + 1, j + 1))
                else:
                    matrix[i + 1][j + 1] = max(matrix[i][j + 1], matrix[i + 1][j])
        stack = [[a] for a in target_dict[1]]
        if len(target_dict) == 1:
            for a in stack:
                yield a
        else:
            while stack:
                path = stack.pop(0)
                for next_node in target_dict[matrix[path[-1][0]][path[-1][1]] + 1]:
                    if next_node[0] > path[-1][0] and next_node[1] > path[-1][1]:
                        if next_node in target_dict[max(target_dict.keys())]:
                            yield path + [next_node]
                        else:
                            stack.append(path + [next_node])



            


        





















