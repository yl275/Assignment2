'''
* Interface for Memory Management Unit.
* The memory management unit should maintain the concept of a page table.
* As pages are read and written to, this changes the pages loaded into the
* the limited number of frames. The MMU keeps records, which will be used
* to analyse the performance of different replacement strategies implemented
* for the MMU.
*
'''
class MMU:
    def __init__(self, frames):
        self.frames = frames
        self.page_table = {}  # page_number -> frame_info
        self.frame_usage = {}  # frame_number -> page_number
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False
        
    def read_memory(self, page_number):
        pass

    def write_memory(self, page_number):
        pass

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
        
    def debug_print(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")
            
    def find_free_frame(self):
        """Find a free frame, return frame number or None if no free frame"""
        for frame_num in range(self.frames):
            if frame_num not in self.frame_usage:
                return frame_num
        return None
        
    def load_page(self, page_number, is_write=False):
        """Load a page into memory, handling page faults and replacement"""
        if page_number in self.page_table:
            # Page is already in memory
            frame_info = self.page_table[page_number]
            frame_info['modified'] = frame_info['modified'] or is_write
            self.debug_print(f"Page {page_number} already in frame {frame_info['frame']}")
            return frame_info['frame']
            
        # Page fault occurred
        self.page_faults += 1
        self.disk_reads += 1
        self.debug_print(f"Page fault for page {page_number}")
        
        # Find a free frame
        free_frame = self.find_free_frame()
        if free_frame is not None:
            # Use free frame
            self.debug_print(f"Using free frame {free_frame}")
        else:
            # Need to replace a page
            victim_frame = self.select_victim()
            victim_page = self.frame_usage[victim_frame]
            
            # Check if victim page is modified
            if self.page_table[victim_page]['modified']:
                self.disk_writes += 1
                self.debug_print(f"Writing modified page {victim_page} to disk")
            
            # Remove victim page from page table
            del self.page_table[victim_page]
            free_frame = victim_frame
            self.debug_print(f"Replaced page {victim_page} in frame {free_frame}")
        
        # Load new page
        self.page_table[page_number] = {
            'frame': free_frame,
            'modified': is_write
        }
        self.frame_usage[free_frame] = page_number
        self.debug_print(f"Loaded page {page_number} into frame {free_frame}")
        
        return free_frame
        
    def select_victim(self):
        """Select a victim frame for replacement - to be implemented by subclasses"""
        pass
