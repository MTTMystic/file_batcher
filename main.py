from batch_packer import BatchPacker
import sys

test_dir = "batcher_test"
#convention: first is per-batch second is all batches at once?
gen_modes = ["step", "all"]
arg_eq_sym = "="
input_folder_arg_prefix = f"input_folder{arg_eq_sym}"
gen_mode_arg_prefix = f"gen_mode{arg_eq_sym}"
batch_size_arg_prefix = f"batch_size{arg_eq_sym}"
batch_size_limit = 30
gen_mode_default = "all"
def get_arg_prefix(arg_cml):
    return arg_cml.split(arg_eq_sym)[0]

def typo_in_arg(user_input, arg_prefix):
    missing_eq_sym = arg_eq_sym not in user_input
    prefix_end_before_eq_sym = -(len(arg_eq_sym))
    arg_name = arg_prefix[0:prefix_end_before_eq_sym]
    incorrect_prefix = get_arg_prefix(user_input) != arg_name
    if (missing_eq_sym or incorrect_prefix):
        print("missing eq or incorrect prefix for ", user_input)
        print("correct arg name is ", arg_name)
        print("actual prefix was", get_arg_prefix(user_input))
    return missing_eq_sym or incorrect_prefix

def get_arg_val(arg_cml):
    return arg_cml.split(arg_eq_sym)[1]

def process_args(user_args):
    input_folder_cml = None if len(user_args) < 1 else user_args[0]
    gen_mode_cml = None if len(user_args) < 2 else user_args[1]
    batch_size_cml = None if len(user_args) < 3 else user_args[2]
    
    
    typo_input_folder = typo_in_arg(input_folder_cml, input_folder_arg_prefix) if input_folder_cml else False
    typo_gen_mode = typo_in_arg(gen_mode_cml, gen_mode_arg_prefix) if gen_mode_cml else False
    typo_batch_size = typo_in_arg(batch_size_cml, batch_size_arg_prefix) if batch_size_cml else False
    
    invalid_gen_mode = get_arg_val(gen_mode_cml) not in gen_modes if gen_mode_cml else False
    invalid_batch_size = int(get_arg_val(batch_size_cml)) > batch_size_limit if batch_size_cml else False
    
    args_invalid = (not input_folder_cml) or typo_input_folder or typo_gen_mode or typo_batch_size\
                    or invalid_gen_mode or invalid_batch_size
    if args_invalid:
        gen_modes_list_str = ",".join(gen_modes)
        args = [f"\"{input_folder_arg_prefix}\"[folder path]", f"\"{batch_size_arg_prefix}\"[int <= {batch_size_limit}](optional)", f"\"{gen_mode_arg_prefix}\"{gen_modes_list_str}(optional)"]
        args_list_str = " ".join(args)
        cml_format = f"(python3) main.py {args_list_str}"
        print(f"Please call the program as \n {cml_format}")
        exit()
    #args contains all arguments that were given, including input_folder (mandatory) and non-None (False) args
    args = [get_arg_val(x) for x in [input_folder_cml, batch_size_cml, gen_mode_cml] if x]
    return args

def batch_step(packer_args):
    batcher = BatchPacker(*packer_args)
    continue_gen = True
    while continue_gen:
        if (batcher.gen_batch() and batcher.can_batch()):
            user_choice = input("Batch generated, would you like to continue? Please write true or false:  ")
            continue_gen = user_choice.lower() == "true"
        elif not batcher.can_batch():
            print("Batching complete")
            continue_gen = False
        else:
            print("Batching failed")
            continue_gen = False

if __name__ == "__main__":
    program_args = process_args(sys.argv[1:])
    gen_mode = gen_mode_default if len(program_args) < 3 else program_args[2]
    batcher_args = program_args if len(program_args) < 3 else program_args[:-2]
    if gen_mode == gen_modes[1]:
        batcher = BatchPacker(*batcher_args)
        batcher.gen_batch_all()
    elif gen_mode == gen_modes[0]:
        batch_step(batcher_args)
    #batcher = BatchPacker(test_dir)
    #batcher.gen_batch_all()

    