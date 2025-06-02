# a class for device configuration settings
# this is for the CURRENT device config settings and some error logging

import os
import pandas as pd

try:
    from src.device_config.presets import config_tinysa_basic as tinyBasic
    from src.device_config.presets  import config_tinysa_ultra_ZS405 as tinyUZS405
    from src.device_config.presets  import config_tinysa_ultra_p_ZS406 as tinyUPZS406
    from src.device_config.presets  import config_tinysa_ultra_p_ZS407 as tinyUPZS407
except:
    from device_config.presets import config_tinysa_basic as tinyBasic
    from device_config.presets  import config_tinysa_ultra_ZS405 as tinyUZS405
    from device_config.presets  import config_tinysa_ultra_p_ZS406 as tinyUPZS406
    from device_config.presets  import config_tinysa_ultra_p_ZS407 as tinyUPZS407


class deviceConfig():
    def __init__(self, parent=None):
        self.name = "tinySA_device"
        self.deviceModel = None
        self.deviceConfig = None
        self.presetSelected = None

            
    def select_preset_model(self, model):
        self.deviceModel = model
        if model == "":
            self.presetSelected = tinyBasic
        elif model == "":
            self.presetSelected = tinyUZS405
        elif model == "":
            self.presetSelected = tinyUPZS406
        elif model == "":
            self.presetSelected = tinyUPZS407
        else:
            self.presetSelected = None
            self.deviceModel = None
            print("ERROR: selected preset not in library")
        
    # DEVICE CONFIG
    def set_default_params(self):
            df = pd.DataFrame({})

            #custom
            df['device_type'] = pd.Series(int(self.presetSelected.SCREEN_WIDTH))
            df['device_name'] = pd.Series(str(self.name))


            #screen
            df['screen_width'] = pd.Series(int(self.presetSelected.SCREEN_WIDTH))
            df['screen_height'] = pd.Series(int(self.presetSelected.SCREEN_HEIGHT))
            df['screen_size'] = pd.Series(int(self.presetSelected.SCREEN_SIZE_IN))
            df['screen_disp_pts'] = pd.Series(int(self.presetSelected.DISPLAY_PTS)) #default MAX

            ## battery
            df['device_battery'] = pd.Series(int(self.presetSelected.MAX_DEVICE_BATTERY))

            ## storage
            df['has_sd_card'] = pd.Series(int(self.presetSelected.HAS_SD_CARD))
            df['loc_sd_card'] = pd.Series(None) #needs to be set
            
            #other modes
            df['max_level_calibration'] = pd.Series(int(self.presetSelected.MAX_LEVEL_CAIBRATION))
            ## ultra
            df['has_ultra_mode'] = pd.Series(bool(self.presetSelected.ULTRA_MODE_OPTION))
            df['ultra_on'] = pd.Series(False) #needs to be set
            ## harmonic            
            df['has_harmonic_mode'] = pd.Series(bool(self.presetSelected.HARMONIC_MODE_OPTION))
            df['harmonic_on'] = pd.Series(False) #needs to be set

            # input mode 
            ## spectrum analyzer
            df['sa_mode_on'] = pd.Series(True) #needs to be set, but ON by default
            df['sa_input_freqs'] = pd.Series(self.presetSelected.SA_INPUT_FREQS)
            df['sa_input_freqs_ultra'] = pd.Series(self.presetSelected.SA_INPUT_FREQS_ULTRA) 
            df['sa_harmonic_mode_freqs'] = pd.Series(self.presetSelected.SA_HARMONIC_MODE_FREQS) 


            # output mode
            ## signal generator
            df['sg_mode_on'] = pd.Series(False) #needs to be set, but OFF by default
            df['sg_max_low_output_freq'] = pd.Series(self.presetSelected.MAX_LOW_OUTPUT_FREQ) 
            df['sg_max_high_output_freq'] = pd.Series(self.presetSelected.MAX_HIGH_OUTPUT_FREQ) 
            df['sg_output_level'] = pd.Series(self.presetSelected.OUTPUT_LEVEL) 

            df['sg_device_freqs_sine'] = pd.Series(self.presetSelected.SG_DEVICE_FREQS_SINE) 
            df['sg_device_freqs_square'] = pd.Series(self.presetSelected.SG_DEVICE_FREQS_SQUARE) 
            df['sg_device_freqs_test'] = pd.Series(self.presetSelected.SG_DEVICE_FREQS_TEST) 


            # resolution
            df['res_filters'] = pd.Series(self.presetSelected.RESOLUTION_FILTERS) 
            df['res_filter_steps'] = pd.Series(self.presetSelected.RES_FILTER_STEPS) 

            # built in LNA
            df['has_internal_lna'] = pd.Series(self.presetSelected.HAS_INTERNAL_LNA) 
            df['num_internal_lna'] = pd.Series(self.presetSelected.NUM_INTERNAL_LNA) 
            df['iternal_lna_range'] = pd.Series(self.presetSelected.LNA_RANGE) 
            df['internal_lna_gain'] = pd.Series(self.presetSelected.LNA_GAIN_DB) 

            
            # attenuator
            df['internal_step_atten_normal'] = pd.Series(self.presetSelected.INTERNAL_STEP_ATTENUATOR_NORMAL) 
            df['internal_step_atten_high'] = pd.Series(self.presetSelected.INTERNAL_STEP_ATTENUATOR_HIGH) 

            # MODULATION_FREQ
            df['modulation_freq'] = pd.Series(self.presetSelected.LNA_GAIN_DB) 

            self.deviceConfig = df
    
    def get_default_params(self):
        return self.deviceConfig
    

    # CUSTOM DEVICE NAME
    def set_device_name(self, n):
        self.name = str(n)
    
    def get_device_name(self):
        return self.name
    
    # LOAD/SAVE USER DEVICE CONFIGS
    def load_device_config(self, filepath):           
        if os.path.exists(filepath):
            self.deviceConfig = pd.read_table(filepath, sep=",", index_col=False)
        else:
            print("ERROR: path " + str(filepath) + " is not found")
    
    def save_device_config(self, filepath):
        if os.path.exists(filepath):
            self.deviceConfig.to_csv(filepath, delimiter=',', index=False)
        else:
            print("ERROR: path " + str(filepath) + " is not found")
    
    # TODO: add setters/getters for some of the options.
    # NOTE: not all of those should be easily changable to discourage internal hardware check changes
