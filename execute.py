import sys
import os
import subprocess
import colorama


args = sys.argv[1:]


def diff(source, destination):
    source_file = open(source, "r+")
    destination_file = open(destination, "r+")

    lines_source = source_file.readlines()
    lines_destination = destination_file.readlines()

    if len(lines_source) != len(lines_destination):
        return False

    return all(lines_source[idx] == lines_destination[idx] for idx in range(len(lines_source)))


#
def execute_command(command, timeout):
    try:
        output_console = subprocess.check_output(list(command.strip().split(" ")), timeout=timeout, shell=False)
        return output_console.decode('UTF-8').rstrip()
    except subprocess.CalledProcessError as e:
        return None


if len(args):
    dir_problem = args[0]
    path = ""

    if os.path.exists(dir_problem) and os.path.isdir(dir_problem):
        path = os.path.join(os.getcwd(), dir_problem)
    elif os.path.exists(os.path.join(os.getcwd(), dir_problem)) and os.path.isdir(
            os.path.join(os.getcwd(), dir_problem)):
        path = os.path.join(os.getcwd(), dir_problem)
    else:
        print("Problem's directory is invalid")
        sys.exit(0)

    testcases_dir = os.path.join(path, "testcases")

    if os.path.exists(testcases_dir) and os.path.exists(os.path.join(path, "main.cpp")):
        command_execute = []

        with open("execute_command.txt", "r") as f:
            command_execute = f.readlines()
            f.close()

        print("Compiling ...")
        print("---------------------------")

        # compile
        try:
            subprocess.check_call(command_execute[0]
                                  .replace("%main-file%", os.path.join(path, "main.cpp"))
                                  .replace("%execute-file%", os.path.join(path, "main.out")).strip().split(" "))
        except subprocess.CalledProcessError:
            sys.exit()

        for i in range(1, 100):
            if os.path.exists(os.path.join(testcases_dir, f"sample-input-{i}")):
                print(f"Running TestCase #{i} ...", end=" ")

                # running
                path_execute_file = os.path.join(path, "main.out")
                inputs = []
                expect_output = []

                with open(os.path.join(testcases_dir, f'sample-input-{i}')) as f:
                    for x in f.readlines():
                        inputs.append(x.strip())

                with open(os.path.join(testcases_dir, f'sample-output-{i}')) as f:
                    for x in f.readlines():
                        expect_output.append(x.strip())

                try:
                    p = subprocess.run(command_execute[1]
                                       .replace("%execute-file%", path_execute_file), timeout=5,
                                       universal_newlines=True, input="\n".join(inputs), capture_output=True)

                    output = p.stdout.strip().splitlines()

                    if output == expect_output:
                        print(colorama.Fore.GREEN + "Ok" + colorama.Fore.RESET)
                    else:
                        # print input
                        print(colorama.Fore.RED + "Wrong" + colorama.Fore.RESET)
                        print(colorama.Fore.CYAN + "==== Detail ====" + colorama.Fore.RESET)

                        print(colorama.Fore.YELLOW + "INPUT: " + colorama.Fore.RESET)
                        print("\n".join(inputs))
                        print(colorama.Fore.YELLOW + "EXPECT OUTPUT: " + colorama.Fore.RESET)
                        print("\n".join(expect_output))
                        print(colorama.Fore.YELLOW + "YOUR OUTPUT: " + colorama.Fore.RESET)
                        print("\n".join(output))

                        break

                except subprocess.CalledProcessError as error:
                    print(error.output)
                    break
            else:
                break

    else:
        print("Problem's directory is invalid")
        sys.exit(0)

else:
    print("Input problem's directory")
    sys.exit(0)
