import numpy as np
import pandas as pd

def get_tracking_error(df_pos, df_sp):
    """
    Computes time-synchronized tracking error between vehicle position and setpoints.
    
    This function aligns the lower-frequency setpoint data to the higher-frequency 
    position data using a forward-fill. It accounts for flight mode transitions 
    where setpoints may be discontinuous.
    
    Returns a DataFrame with:
    - err_x, err_y, err_z: Raw error per axis (NED frame).
    - horiz_error: 2D Euclidean distance (sqrt(dx^2 + dy^2)).
    - vert_error: Absolute vertical distance (abs(dz)).
    """
    # 1. Prepare Timestamps
    for df in [df_pos, df_sp]:
        # Ensure the index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Localize to UTC
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
            
        df.sort_index(inplace=True)
    
    # 2. Resample & Align
    # We use df_pos as the "Master Clock" because it usually has a higher frequency.
    # .reindex(method='ffill') carries the last known setpoint forward to match 
    # the current position timestamp.
    df_sp_aligned = df_sp.reindex(df_pos.index, method='ffill')

    # 3. Calculate Error Signal
    # We use a copy of df_pos to store our continuous output
    res_df = pd.DataFrame(index=df_pos.index)
    res_df['err_x'] = df_pos['x'] - df_sp_aligned['x']
    res_df['err_y'] = df_pos['y'] - df_sp_aligned['y']
    res_df['err_z'] = df_pos['z'] - df_sp_aligned['z']
    
    # 4. Calculate Magnitudes
    res_df['horiz_error'] = np.sqrt(res_df['err_x']**2 + res_df['err_y']**2)
    res_df['vert_error'] = np.abs(res_df['err_z'])
    
    # Fill any remaining NaNs at the very start of the log with 0
    res_df.fillna(0, inplace=True)

    return res_df