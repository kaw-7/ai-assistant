from Preprocessor.AbstractPreprocessor import AbstractPreprocessor
import os, sys
from typing import List
import traceback
from typing_extensions import override

import config

class TextChunkerPreprocessor(AbstractPreprocessor):
    
    def __init__(self, ai_provider):
        self.ai_engine = ai_provider
        self.it = 0
        self.end = False
        self.slice_position = -1
        
    def End(self):
        return self.end
        
    @override
    def preprocess_file(self, release_notes_file_path):
        self.end = False
        if not os.path.exists(release_notes_file_path):
            print(f"[ERROR] Input file not found: {release_notes_file_path}")
            sys.exit(1)
    
        chunk_text = self._generate_chunk(release_notes_file_path)
        # --- SAVE OUTPUT ---                
        self.save_output(chunk_text, config.TEMP_CHUNK_FILE)        
        self._slice_input(release_notes_file_path)
        print("Chunk output saved!\n")
        
        return chunk_text
            
    def _slice_input(self, release_notes_file_path):
        
        if(self.slice_position == 0):
            raise Exception("Should not slice from position 0 to position 0. Slice is empty!")
        
        release_notes = ""
        with open(release_notes_file_path, mode="r", encoding="utf-8") as f:
            release_notes = f.read()
        
        with open(release_notes_file_path, mode="w", encoding="utf-8") as f:
            f.write(release_notes[self.slice_position:])
  
    def _generate_chunk(self, release_notes_file_path):
        import re

        release_notes = ""
        print("[1/3] Splitting input release notes using internal algorithms")
        with open(release_notes_file_path, "r", encoding="utf-8", errors="replace") as f:
            release_notes = f.read()
            if(self.slice_position == -1):
                self.check_characters(release_notes)
            
            if(len(release_notes) < 3*config.CHUNK_SIZE/2 ):
                self.slice_position = len(release_notes)
                self.end = True
                return release_notes
            
            self.slice_position = release_notes.find(config.CHUNK_DELIMITER)
            if(self.slice_position != -1):
                return release_notes[:self.slice_position]
            
            pattern = re.compile(r'(?:\r?\n[ \t\f\v]*)(?:\r?\n[ \t\f\v]*)(?:\r?\n[ \t\f\v]*)+')
            matches = pattern.search(release_notes, config.CHUNK_SIZE)
            if matches is not None:
                self.slice_position = matches.end()
                return release_notes[:matches.end()]
            
            pattern = re.compile(r'\r?\n[ \t\f\v]*\r?\n')
            matches = pattern.search(release_notes, config.CHUNK_SIZE)
            if matches is not None:
                self.slice_position = matches.end()
                return release_notes[:matches.end()]
                
        raise Exception("Could not split release notes into chunks!")



            