import ctypes
import os

class MonitorManager:
    @staticmethod
    def set_dpi_awareness():
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    
    @staticmethod
    def get_monitor_ppi(window_id):
        """Returns the PPI for the monitor the window is currently on."""
        if os.name != 'nt':
            return 96.0 # Default for non-windows
        
        try:
            hwnd = ctypes.windll.user32.GetParent(window_id)
            # MONITOR_DEFAULTTONEAREST = 2
            monitor = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)
            
            #MDT_EFFECTIVE_DPI = 0
            dpi_x = ctypes.c_uint()
            dpi_y = ctypes.c_uint()
            ctypes.windll.shcore.GetDpiForMonitor(monitor, 0, ctypes.byref(dpi_x), ctypes.byref(dpi_y))
            
            return dpi_x.value, monitor
        except Exception as e:
            print(f"DPI Detection failed: {e}")
            return 96, None