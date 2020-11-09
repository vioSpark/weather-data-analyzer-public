# coding: utf-8
import logging


# score counts how many -1 are in the condition.. it is only counted in Péczely on purpose
def get_significant_standalone(input_path, threshold=0.05, output_path=None):
    if not output_path:
        output_path = input_path + '/_tmp_results.txt'
    get_significant(input_path, threshold, output_path)


# score counts how many -1 are in the condition.. it is only counted in Péczely on purpose
def get_significant(input_path, threshold, output_path):
    log = logging.getLogger(__name__)

    def filter_func(block):
        day = block[1]
        condition = block[2]
        peczely_string = block[4].split('=')[0]
        peczely_value = block[4].split('=')[1]
        front = block[5]
        payload = ''
        count = 0
        if float(peczely_value) < threshold:
            tmp = condition.split(',')
            tmp[0] = ' ' + tmp[0].split('[')[1]
            tmp[-1] = tmp[-1].split(']')[0]
            for element in tmp:
                if element == ' -1':
                    count += 1
            payload = day[0:-1] + '\t' + 'score:\t' + str(count) + '\t' + condition[0:-1] + peczely_string + \
                      '=\t' + peczely_value
        if float(front.split('=')[1]) > threshold:
            log.warning('Not significant Front condition')
            payload = day[0:-2] + '\t' + condition[0:-2] + '\t' + block[5].split('=')[0] + '\t' + block[5].split('=')[1]
        return payload

    with open(output_path, 'w') as out_f, open(input_path) as in_f:
        out_f.write(
            """This file contains the significant Péczely conditions, and the NOT significant Front conditions
            (A better UI will be developed soon)\n""")
        lines = in_f.readlines()
        n = 0
        for i in range(int(len(lines) / 6)):
            out_f.write(filter_func(lines[n:n + 6]))
            n += 6


def small(inches=1):
    if float(inches) < 0:
        print('You must be a girl 🤔')
        return
    if float(inches) > 100:
        print("I'm reconsidering my sexual orientation")
        if float(inches) > 1000:
            print('\tWhat about tomorrow 6 pm, at my place?')
        return
    if float(inches) == 0 or inches == 'zero':
        print("I'm sorry to hear that")
    tmp = 'inches'
    if float(inches) == 1 or inches == 'one':
        tmp = 'inch'
    print("sorry I can't help if your pp is {0} {1} small".format(inches, tmp))
    return
