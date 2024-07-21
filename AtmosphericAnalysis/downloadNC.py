import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': [
            '100m_u_component_of_wind', '100m_v_component_of_wind', '10m_u_component_of_neutral_wind',
            '10m_u_component_of_wind', '10m_v_component_of_neutral_wind', '10m_v_component_of_wind',
            '10m_wind_speed', 'instantaneous_10m_wind_gust',
        ],
        'year': [
            '2022', '2023', '2024',
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'time': '00:00',
        'format': 'netcdf',
    },
    'download.nc')