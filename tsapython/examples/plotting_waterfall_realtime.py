#!/usr/bin/python3
##-------------------------------------------------------------------------------
#   tinySA_python (tsapython)
#   './examples/plotting_waterfall_realtime.py'
#   A real-time waterfall plot example for tinySA using matplotlib.
#   The waterfall plot is shown and processed as the measurements are taken
#
#   Last update: August 17, 2025
##-------------------------------------------------------------------------------

# import tinySA_python (tsapython) package
from tsapython import tinySA


# imports FOR THE EXAMPLE
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
from datetime import datetime
import threading
import queue

def convert_data_to_arrays(start, stop, pts, data):
    #Convert the raw tinySA data to frequency and power arrays.
    # using the start and stop frequencies, and the number of points,
    freq_arr = np.linspace(start, stop, pts) # note that the decimals might go out to many places.
                                                # you can truncate this because its only used
                                                # for plotting in this example
    # As of the Jan. 2024 build in some data returned with SWEEP or SCAN calls there is error data.  
    # https://groups.io/g/tinysa/topic/tinasa_ultra_sweep_command/104194367  
    # this shows up as "-:.000000e+01".
    # TEMP fix - replace the colon character with a -10. This puts the 'filled in' points around the noise floor.
    # more advanced filtering should be applied for actual analysis.
   
    data1 = bytearray(data.replace(b"-:.0", b"-10.0"))
    
    # Get first value in each returned row (power in dBm)
    try:
        data_arr = [float(line.split()[0]) for line in data1.decode('utf-8').split('\n') if line.strip()]
    except (ValueError, IndexError):
        # If parsing fails, return zeros
        data_arr = [0.0] * pts
    
    # Ensure data array matches frequency array length
    if len(data_arr) != pts:
        # Pad or truncate to match expected points
        # We do this to visualize what might be going wrong rather than outright throwing an error
        # -100 is a very low noise floor, especially for a hand held device, so it's not a normal reading
        if len(data_arr) < pts:
            data_arr.extend([data_arr[-1] if data_arr else -100.0] * (pts - len(data_arr)))
        else:
            data_arr = data_arr[:pts]
    
    return freq_arr, np.array(data_arr)

class LiveSpectrumPlotter:
    def __init__(self, tsa, start, stop, pts, outmask, max_history=50):
        self.tsa = tsa
        self.start = start
        self.stop = stop
        self.pts = pts
        self.outmask = outmask
        self.max_history = max_history
        
        # Data storage
        self.freq_arr = None
        self.power_history = deque(maxlen=max_history)
        self.timestamps = deque(maxlen=max_history)
        
        # Threading for data acquisition
        self.data_queue = queue.Queue()
        self.running = False
        self.data_thread = None
        
        # Current data for single-trace plots
        self.current_power = None
        
        # Twin axis reference for proper cleanup
        self.ax3_twin = None
        
    def data_acquisition_thread(self):
        #Background thread for continuous data acquisition
        while self.running:
            try:
                # Get scan data
                data_bytes = self.tsa.scan(self.start, self.stop, self.pts, self.outmask)
                
                # Convert to arrays
                freq_arr, power_arr = convert_data_to_arrays(
                    self.start, self.stop, self.pts, data_bytes)
                
                # Put data in queue for main thread
                self.data_queue.put({
                    'freq': freq_arr,
                    'power': power_arr,
                    'timestamp': datetime.now()
                })
                
                time.sleep(0.2)  # Small delay to prevent overwhelming the device
                
            except Exception as e:
                print(f"Data acquisition error: {e}")
                time.sleep(0.5)  # Wait a bit before retrying
                continue
    
    def start_acquisition(self):
        #Start the data acquisition thread
        self.running = True
        self.data_thread = threading.Thread(target=self.data_acquisition_thread)
        self.data_thread.daemon = True
        self.data_thread.start()
    
    def stop_acquisition(self):
        #Stop the data acquisition thread
        self.running = False
        if self.data_thread:
            self.data_thread.join()
    
    def update_plots(self, frame):
        #Update the matplotlib plots with new data
        
        # Get all available data from queue
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                
                # Store frequency array (first time only)
                if self.freq_arr is None:
                    self.freq_arr = data['freq']
                
                # Update current data
                self.current_power = data['power']
                
                # Add to history
                self.power_history.append(data['power'])
                self.timestamps.append(data['timestamp'])
                
            except queue.Empty:
                break
        
        # Clear plots
        ax1.clear()  # Waterfall
        ax2.clear()  # Live spectrum 
        ax3.clear()  # Peak tracking
        
        # Clear any existing twin axes completely
        if hasattr(self, 'ax3_twin') and self.ax3_twin is not None:
            self.ax3_twin.clear()
            self.ax3_twin.remove()
            self.ax3_twin = None
        
        if self.freq_arr is not None and self.current_power is not None:
            # Plot 1: Waterfall (left side - larger)
            if len(self.power_history) > 1:
                waterfall_data = np.array(list(self.power_history))
                # Create time array in reverse order so newest (highest index) appears at top
                time_arr = np.arange(len(waterfall_data))
                freq_mesh, time_mesh = np.meshgrid(self.freq_arr, time_arr)
                
                im = ax1.pcolormesh(freq_mesh/1e9, time_mesh, waterfall_data, 
                                   shading='nearest', cmap='viridis')
                ax1.set_xlabel('Frequency (GHz)')
                ax1.set_ylabel('Scan Number (newest at top)')
                ax1.set_title('Spectrum History (Waterfall)')
                
                # Add colorbar to waterfall plot
                if not hasattr(self, 'colorbar_created'):
                    self.colorbar = plt.colorbar(im, ax=ax1, shrink=0.8)
                    self.colorbar.set_label('Power (dBm)')
                    self.colorbar_created = True
            
            # Plot 2: Current Spectrum (top right)
            ax2.plot(self.freq_arr/1e9, self.current_power, 'b-', linewidth=1.5)
            ax2.set_xlabel('Frequency (GHz)')
            ax2.set_ylabel('Power (dBm)')
            ax2.set_title('Live Spectrum')
            ax2.grid(True, alpha=0.3)
            
            # Set reasonable y-axis limits
            if len(self.current_power) > 0:
                y_min = np.min(self.current_power) - 5
                y_max = np.max(self.current_power) + 5
                ax2.set_ylim(y_min, y_max)
            
            # Plot 3: Peak tracking over time (bottom right)
            if len(self.power_history) > 1:
                peak_powers = [np.max(scan) for scan in self.power_history]
                peak_freqs = [self.freq_arr[np.argmax(scan)]/1e9 for scan in self.power_history]
                
                # Plot peak power over time
                scan_numbers = list(range(len(peak_powers)))
                
                # Create fresh twin axis for frequency (store reference for proper cleanup)
                self.ax3_twin = ax3.twinx()
                
                ax3.plot(scan_numbers, peak_powers, 'r-o', markersize=2, 
                        label='Peak Power', linewidth=1.5)
                self.ax3_twin.plot(scan_numbers, peak_freqs, 'g-s', markersize=2, 
                                   label='Peak Freq', linewidth=1.5)
                
                ax3.set_xlabel('Scan Number')
                ax3.set_ylabel('Peak Power (dBm)', color='r')
                self.ax3_twin.set_ylabel('Peak Freq (GHz)', color='g')
                ax3.set_title('Peak Tracking')
                ax3.grid(True, alpha=0.3)
                
                # Color the y-axis labels to match the lines
                ax3.tick_params(axis='y', labelcolor='r', labelsize=8)
                self.ax3_twin.tick_params(axis='y', labelcolor='g', labelsize=8)
                
                # Force immediate redraw of the twin axis
                self.ax3_twin.relim()
                self.ax3_twin.autoscale_view()
        
        # Add timestamp and scan info
        if self.timestamps:
            scan_count = len(self.timestamps)
            time_str = self.timestamps[-1].strftime("%H:%M:%S")
            fig.suptitle(f'Live tinySA Spectrum - {time_str} (Scan #{scan_count})', 
                        fontsize=14)


if __name__ == "__main__":
    # create a new tinySA object    
    tsa = tinySA()
    # set the return message preferences
    tsa.set_verbose(True)
    tsa.set_error_byte_return(True)

    # attempt to autoconnect
    found_bool, connected_bool = tsa.autoconnect()

    if not connected_bool:
        print("ERROR: could not connect to port")
    else:
        try:
            print("Starting live spectrum measurement...")
            print("Close the plot window to stop measurement")
            
            # Scan parameters
            start = int(1e9)  # 1 GHz
            stop = int(3e9)   # 3 GHz
            pts = 200         # Reduced points for faster updates
            outmask = 2       # get measured data
            
            # Create plotter
            plotter = LiveSpectrumPlotter(tsa, start, stop, pts, outmask, max_history=30)
            
            # Set up the plot - 2x2 layout with waterfall taking left column
            fig = plt.figure(figsize=(14, 10))
            
            # Create grid layout: waterfall on left (spans 2 rows), two plots on right
            gs = fig.add_gridspec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1],
                                hspace=0.3, wspace=0.3)
            
            ax1 = fig.add_subplot(gs[:, 0])  # Waterfall - spans both rows, left column
            ax2 = fig.add_subplot(gs[0, 1])  # Live spectrum - top right
            ax3 = fig.add_subplot(gs[1, 1])  # Peak tracking - bottom right
            
            # Start data acquisition
            plotter.start_acquisition()
            
            # Create animation
            ani = animation.FuncAnimation(fig, plotter.update_plots, 
                                        interval=300, blit=False)
            
            # Show plot (this blocks until window is closed)
            plt.show()
            
            # Cleanup
            plotter.stop_acquisition()
            tsa.resume()
            tsa.disconnect()
            
            print("Live measurement stopped")
            
        except KeyboardInterrupt:
            print("\nMeasurement interrupted by user")
            tsa.resume()
            tsa.disconnect()
        except Exception as e:
            print(f"Error occurred: {e}")
            tsa.resume()
            tsa.disconnect()