from mmu import MMU
import random

class RandMMU(MMU):
    def __init__(self, frames):
        super().__init__(frames)

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def read_memory(self, page_number):
        self.load_page(page_number, is_write=False)

    def write_memory(self, page_number):
        self.load_page(page_number, is_write=True)

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
        
    def select_victim(self):
        """Randomly select a victim frame for replacement"""
        available_frames = list(self.frame_usage.keys())
        return random.choice(available_frames)
