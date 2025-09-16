from mmu import MMU


class ClockMMU(MMU):
    def __init__(self, frames):
        super().__init__(frames)
        self.clock_hand = 0  # Clock hand position
        self.reference_bits = {}  # frame_number -> reference_bit

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
        
    def load_page(self, page_number, is_write=False):
        """Override load_page to update reference bits for Clock algorithm"""
        if page_number in self.page_table:
            # Page is already in memory - set reference bit
            frame_info = self.page_table[page_number]
            frame_info['modified'] = frame_info['modified'] or is_write
            
            # Set reference bit
            frame_num = frame_info['frame']
            self.reference_bits[frame_num] = 1
            
            self.debug_print(f"Page {page_number} already in frame {frame_num}")
            return frame_num
            
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
            # Need to replace a page - use clock algorithm
            victim_frame = self.select_victim()
            victim_page = self.frame_usage[victim_frame]
            
            # Check if victim page is modified
            if self.page_table[victim_page]['modified']:
                self.disk_writes += 1
                self.debug_print(f"Writing modified page {victim_page} to disk")
            
            # Remove victim page from page table and reference bits
            del self.page_table[victim_page]
            if victim_frame in self.reference_bits:
                del self.reference_bits[victim_frame]
            free_frame = victim_frame
            self.debug_print(f"Replaced page {victim_page} in frame {free_frame}")
        
        # Load new page
        self.page_table[page_number] = {
            'frame': free_frame,
            'modified': is_write
        }
        self.frame_usage[free_frame] = page_number
        self.reference_bits[free_frame] = 1  # Set reference bit for new page
        self.debug_print(f"Loaded page {page_number} into frame {free_frame}")
        
        return free_frame
        
    def select_victim(self):
        """Select victim using clock algorithm"""
        while True:
            # Check if current frame is in use
            if self.clock_hand in self.frame_usage:
                # Frame is in use, check reference bit
                if self.clock_hand not in self.reference_bits or self.reference_bits[self.clock_hand] == 0:
                    # Reference bit is 0, select this frame
                    victim_frame = self.clock_hand
                    self.clock_hand = (self.clock_hand + 1) % self.frames
                    return victim_frame
                else:
                    # Reference bit is 1, clear it and move clock hand
                    self.reference_bits[self.clock_hand] = 0
                    self.clock_hand = (self.clock_hand + 1) % self.frames
            else:
                # Frame is not in use, move clock hand
                self.clock_hand = (self.clock_hand + 1) % self.frames
