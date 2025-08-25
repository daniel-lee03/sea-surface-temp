import streamlit as st
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

# --- Streamlit 앱의 기본 설정 ---
st.set_page_config(layout="wide")
st.title("해수면 온도 편차 시각화")

# --- 데이터 로드 ---
# 예제용 가상 NetCDF 데이터 생성 (실제로는 파일 경로를 지정)
@st.cache_data
def create_dummy_data(filepath='dummy_sst_data.nc'):
    try:
        # 기존 파일이 있으면 로드
        data = xr.open_dataset(filepath)
    except FileNotFoundError:
        # 없으면 새로 생성
        lon = np.arange(120, 136, 0.25)
        lat = np.arange(28, 42, 0.25)
        # 이미지와 유사한 패턴의 데이터 생성
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        temp_anomaly = (np.sin(np.deg2rad(lat_grid) * 5) *
                        np.cos(np.deg2rad(lon_grid) * 3) * 2 +
                        np.random.randn(len(lat), len(lon)) * 0.5)
        data = xr.Dataset(
            {'sst_anomaly': (('lat', 'lon'), temp_anomaly)},
            coords={'lat': lat, 'lon': lon}
        )
        data.to_netcdf(filepath)
    return data

# 데이터 로드
data = create_dummy_data()
sst_data = data['sst_anomaly']


# --- 지도 시각화 함수 ---
def create_map_figure(data_array):
    fig, ax = plt.subplots(
        figsize=(10, 8),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )

    # pcolormesh를 사용한 데이터 플로팅
    im = data_array.plot.pcolormesh(
        ax=ax,
        x='lon',
        y='lat',
        transform=ccrs.PlateCarree(),
        cmap='coolwarm',
        add_colorbar=False # xarray plot에서 자동 컬러바 생성 방지
    )

    # 해안선 및 육지 추가
    ax.coastlines()
    ax.add_feature(cfeature.LAND, zorder=1, facecolor='lightgray', edgecolor='black')

    # 그리드라인 설정
    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    # 컬러바 추가
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', pad=0.05, aspect=40)
    cbar.set_label('Temperature Anomaly (°C)')

    # 제목 및 범위 설정
    ax.set_title('2025 JJA', fontsize=16, color='purple', weight='bold')
    ax.set_extent([120, 135, 28, 42], crs=ccrs.PlateCarree()) # 이미지와 유사한 범위로 설정

    return fig

# --- Streamlit에 시각화 표시 ---
st.subheader("해수면 온도 편차 지도")
fig = create_map_figure(sst_data)
st.pyplot(fig)

# --- 데이터 테이블 표시 (선택 사항) ---
st.subheader("데이터 미리보기")
st.write(data)