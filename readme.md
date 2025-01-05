This is a utility program made to batch files in a given directory into subfolders with [batch size] files per folder. The user (whether another program or from command line exec) can generate every batch at once or generate batches one step at a time. I made it for personal use and used instrumented testing rather than unit testing.

Execute from the command line as:

(python3) main.py input_folder=[path to folder to batch files in] batch_size=[int up to 40] gen_mode=[either step or all]

Note that batch_size and gen_mode are optional; default is batch_size = 15 and gen_mode = all. Do not use spaces when running from command line, and you will be prompted if input is incorrect as well as errors during batch generation. 

Current plans do not feature further extension of this, as for the purpose I intend to use it for (audio mixing and editing) it is complete. I only share it publicly to be of use or interest to people who might want it.