import pandas as pd

def get_tracking_error(position_df, setpoint_df):
    """
    Computes time-synchronized tracking error between vehicle position and setpoints.
    
    Returns a DataFrame with:
    - err_x, err_y, err_z: Raw error per axis (NED frame).
    - horiz_error: 2D Euclidean distance (sqrt(dx^2 + dy^2)).
    - vert_error: Absolute vertical distance (abs(dz)).
    """
    # Align setpoint data to position timeline using indexes
    aligned_df = pd.merge_asof(
        position_df,
        setpoint_df,
        left_index=True,
        right_index=True,
        direction='backward',
        suffixes=('', '_sp')
    )
    
    # Calculate tracking error
    res_df = pd.DataFrame(index=aligned_df.index)
    res_df['err_x'] = aligned_df['x'] - aligned_df['x_sp']
    res_df['err_y'] = aligned_df['y'] - aligned_df['y_sp']
    res_df['err_z'] = aligned_df['z'] - aligned_df['z_sp']
    
    res_df['horiz_error'] = (res_df['err_x']**2 + res_df['err_y']**2)**0.5
    res_df['vert_error'] = res_df['err_z'].abs()
    
    return res_df