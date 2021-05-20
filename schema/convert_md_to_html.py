import os

path = os.path.dirname(os.path.abspath(__file__))

for root, d_names, f_names in os.walk(path):
    for f_name in f_names:
        filename, ext = os.path.splitext(os.path.basename(f_name))
        if ext == '.md':
            f_input = os.path.join(root, f_name)
            f_output = os.path.join(root, filename + '.html')
            command = f"pandoc {f_input} --webtex='https://latex.codecogs.com/svg.latex?' -o {f_output} --template=template.html --self-contained --metadata title=\"dummy\""
            # command = f'pandoc {f_input} --webtex -o {f_output}'
            print('execute command:')
            print(command)
            os.system(command)
            # print(root, f_name, dirname, filename, ext)
