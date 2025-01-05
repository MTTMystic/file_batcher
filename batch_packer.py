import os
import shutil

placeholder = "$"
batch_dir_path_base = "batch_" + placeholder
default_batch_size = 15
wildcard_sym = "*"

class BatchPacker:
    _packer_path = ""
    _batch_dir_idx = 1
    _dirmap = {}
    #silly for now but readable indication that dirlist_rem tracks dirlist_all being decreased by batches
    _dirlist_rem = []
    _batch_dirlist = []
    _batch_valid = True
    _batch_dir_path = ""
    _valid_filetypes = []
    
    def _check_path_basic(self, fp, shouldBeDir = False):
        abspath = os.path.abspath(fp)
        as_should_be = "dir" if shouldBeDir else "file"
        not_as_should_be = "file" if shouldBeDir else "dir"
        
        if not os.path.exists(abspath):
            print(f"The specified item at path {fp} does not exist")
            return False
        
        invalid_type_should_be_file = os.path.isdir(abspath) and not shouldBeDir
        invalid_type_should_be_dir = not os.path.isdir(abspath) and shouldBeDir
        wrong_type = invalid_type_should_be_dir or invalid_type_should_be_file
        if wrong_type:
            print(f"The item at the specified path {fp} is a {not_as_should_be}, not a {as_should_be}")
            return False
       
        open_access = os.access(abspath, os.X_OK)
        if not open_access:
            print(f"The specified {as_should_be} at path {fp} cannot be opened, check its permissions")
            return False
        
        read_access = os.access(abspath, os.R_OK)
        if not read_access:
            print(f"The specified {as_should_be} at path {fp} cannot be read, check its permissions")
            return False
        
        write_access = os.access(abspath, os.W_OK)
        if not write_access:
            print("The specified {as_should_be} at path {fp} cannot be read, check its permissions")
            return False
        #congrats the type and permissions are correct and it literally exists at all!
        return True
    
    def _check_packer_dir_path(self, fp):
        return self._check_path_basic(fp, shouldBeDir=True)

        #now check if the audios to be mixed are in a correctly named subfolder
        
    def _get_batch_dir_fragment(self):
        return batch_dir_path_base.replace(placeholder, str(self._batch_dir_idx))
    
    def _update_batch_dir_path(self):
        self._batch_dir_path = os.path.join(self._packer_path, self._get_batch_dir_fragment())
        return self._batch_dir_path
    
    def _get_src_fp(self, fp):
        return os.path.join(self._packer_path, fp)
    
    def _select_batch_files(self):
        if self._batch_size <= len(self._dirlist_rem):
            #print("full batch can be made")
            #dirlist_rem_readout = "\n".join(self._dirlist_rem)
            #print(f"dirlist_rem before selecting batch: \n {dirlist_rem_readout}")
            self._batch_dirlist = self._dirlist_rem[:self._batch_size]
            #batch_dirlist_readout = "\n".join(self._batch_dirlist)
            #print(f"batchlist after selecting batch: \n {batch_dirlist_readout}" )
            self._dirlist_rem = self._dirlist_rem[self._batch_size:]
            #dirlist_rem_readout = "\n".join(self._dirlist_rem)
            #print(f"dirlist_rem after selecting batch: \n {dirlist_rem_readout}")
            return True
        elif len(self._dirlist_rem) > 0:
            self._batch_dirlist = self._dirlist_rem
            self._dirlist_rem = []
            return True
        else:
            self._batch_dirlist = []
            return False
            
    def _validate_batch_dirlist(self):
        for filepath in self._batch_dirlist:
            fp = self._get_src_fp(filepath) 
            if not self._check_path_basic(fp):
                print(f"The file in batch_dirlist {filepath} is invalid")
                return False
            #established file exists and correct permissions exist, now is it of valid filetype?
            """"file_ext = os.path.split(filepath)[1][1:]
            valid_filetype = (file_ext in self._valid_filetypes) or (self._valid_filetypes is [wildcard_sym])
            #TODO for now the batch does not continue after invalid filetype is found
            if not valid_filetype:
                print("The file {} is an invalid filetype, only {} files are allowed".format(filename = filepath, valid_types = ','.join(self._valid_filetypes)))
                return False"""
        return True
        
    
            
    def _move_batch_files(self):
        #first file ((1 - 1) * 15) = 0
        #first file of second batch ((2 - 1) * 15) = (1 * 15) = 15
        #dirlist_all_file_idx = ((self._batch_dir_idx - 1) * batch_size)
        batch_dirlist_prev = self._batch_dirlist
        for filepath in self._batch_dirlist:
            src = self._get_src_fp(filepath)
            if (self._check_path_basic(src)):
                dst =  os.path.join(self._batch_dir_path, filepath)
                try:
                    shutil.move(src, dst)
                except:
                    "There was an error while trying to move the file {filepath}"
                    self._dirmap[str(self._batch_dir_idx)] = []
                    return False
                #mark whether the file at filepath is part of a batch already
                #this is a caching function to not re-move the same files if a batch has to be re-started
                #future planning?
                self._dirmap[str(self._batch_dir_idx)] = batch_dirlist_prev
            else:
                return False
        return True
    #returns True or False based on success (made batch dir) or failure (did not make batch dir)
    def _make_batch_dir(self):
        if (os.path.exists(os.path.abspath(self._update_batch_dir_path()))):
            print(f"The folder {self._batch_dir_path} already exists.")
            return False
        try:
            os.mkdir(self._update_batch_dir_path())
            os.chmod(self._batch_dir_path, 0o755)
        except:
            print(f"An error occurred while trying to create the subdir for batch with path {self._batch_dir_path}")
            return False
        
        try:
            batch_created =  self._move_batch_files()
            if (batch_created):
                self._batch_dir_idx += 1
            return batch_created
        except:
            print(f"An error occurred while trying to move the batch files")
            return False
    
 
    
    def _gen_batch(self):
        #print(len(self._dirlist_rem))
        batch_success = self._select_batch_files() and self._validate_batch_dirlist() and self._make_batch_dir()
        return batch_success
        
            
    def gen_batch(self):
        return self._gen_batch()
        """"if (success):
            print("Generated batch {self._batch_dir_idx}")
        else:
            print("Batching failed")"""
            
    def _gen_batch_all(self):
        keep_batching = True
        prev_batch_succeeded = True
        while keep_batching:
            prev_batch_succeeded = self._gen_batch()
            keep_batching = prev_batch_succeeded and len(self._dirlist_rem) > 0
        return prev_batch_succeeded
    
    def gen_batch_all(self):
        self._gen_batch_all()
    
    def can_batch(self):
        return len(self._dirlist_rem) > 0
    
    def __init__(self, packer_target_dir, batch_size = default_batch_size):
        valid_input_dir = self._check_packer_dir_path(packer_target_dir)
        if valid_input_dir:
            self._packer_path = os.path.abspath(packer_target_dir)
            self._batch_dir = os.path.join(self._packer_path, self._get_batch_dir_fragment())
            self._batch_size = int(batch_size) if batch_size != default_batch_size else default_batch_size
            self._dirlist_rem = [x for x in os.listdir(self._packer_path) if not os.path.isdir(self._get_src_fp(x))]

            #file_list = os.listdir(self._packer_path)
            #file_count = len(file_list)
        else:
            "The specified directory does not exist"
            exit()