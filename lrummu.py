from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        super().__init__(frames)
        self.access_order = []  # List to track access order (most recent at end)

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
        """Override load_page to update access order for LRU"""
        if page_number in self.page_table:
            # Page is already in memory - update access order
            frame_info = self.page_table[page_number]
            frame_info['modified'] = frame_info['modified'] or is_write
            
            # Move to end of access order (most recent)
            if page_number in self.access_order:
                self.access_order.remove(page_number)
            self.access_order.append(page_number)
            
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
            # Need to replace a page - select LRU victim
            victim_frame = self.select_victim()
            victim_page = self.frame_usage[victim_frame]
            
            # Check if victim page is modified
            if self.page_table[victim_page]['modified']:
                self.disk_writes += 1
                self.debug_print(f"Writing modified page {victim_page} to disk")
            
            # Remove victim page from page table and access order
            del self.page_table[victim_page]
            if victim_page in self.access_order:
                self.access_order.remove(victim_page)
            free_frame = victim_frame
            self.debug_print(f"Replaced page {victim_page} in frame {free_frame}")
        
        # Load new page
        self.page_table[page_number] = {
            'frame': free_frame,
            'modified': is_write
        }
        self.frame_usage[free_frame] = page_number
        self.access_order.append(page_number)  # Add to end (most recent)
        self.debug_print(f"Loaded page {page_number} into frame {free_frame}")
        
        return free_frame
        
    def select_victim(self):
        """Select the least recently used page for replacement"""
        if not self.access_order:
            # Fallback to first available frame
            return list(self.frame_usage.keys())[0]
        
        # Return frame of the least recently used page (first in access_order)
        lru_page = self.access_order[0]
        return self.page_table[lru_page]['frame']
