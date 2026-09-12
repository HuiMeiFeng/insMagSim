# Copyright (c) 2026 Hui-Mei Feng
# Distributed under MIT License, see LICENSE file.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table


def line_set(ax,
             xlabel: str,
             ylabel: str,
             direction: str = 'in',
             xlim: tuple | None = None,
             ylim: tuple | None = None,
             legend: bool = True,
             title: str | None = None,
             loc: str = 'best',
             size: dict | None = None,
             frameon: bool = True,
             fontfamily: str = "Times New Roman",
             minor_tick_scale: float = 0.6):
    # Default size config
    if size is None:
        size = {
            'mz': 1.0,    # spine and tick edge width
            'lz': 3.0,    # major tick length
            'lbz': 14,    # axis label fontsize
            'tkz': 12,    # tick label fontsize
        }
    mz = size['mz']
    lz = size['lz']
    lbz = size['lbz']
    tkz = size['tkz']
    minor_lz = lz * minor_tick_scale

    # Set spine (figure border) linewidth
    for s in ax.spines.values():
        s.set_linewidth(mz)

    # Enable minor ticks
    ax.minorticks_on()

    # Tick params: both major & minor ticks, four sides
    ax.tick_params(
        axis="both",
        which="major",
        direction=direction,
        length=lz,
        width=mz,
        labelsize=tkz,
        top=True,
        right=True,
        bottom=True,
        left=True
    )
    ax.tick_params(
        axis="both",
        which="minor",
        direction=direction,
        length=minor_lz,
        width=mz,
        top=True,
        right=True,
        bottom=True,
        left=True
    )

    # Axis limits
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    # Axis labels
    ax.set_xlabel(xlabel, fontsize=lbz, fontfamily=fontfamily)
    ax.set_ylabel(ylabel, fontsize=lbz, fontfamily=fontfamily)

    # Title
    if title is not None:
        ax.set_title(title, fontsize=lbz, fontfamily=fontfamily)

    # Legend
    if legend:
        ax.legend(loc=loc, fontsize=tkz, frameon=frameon, prop={"family": fontfamily})

    return ax


def temSpecPro(dataPath):
    '''
    read template spectrum from lamostEigenStar.fits
    '''

    # read lamostEigenStar.fits
    fileName = dataPath + '/lamostEigenStar.fits'
    lamost_spec = fits.open(fileName)
    data_tem = lamost_spec[0].data
    lamost_spec.close()

    coeff0 = 3.5871  #nm
    coeff1 = 0.0001
    wavele = []
    for i in range(data_tem[0].size):
        wavele.append(10 ** (coeff0 + i * coeff1))

    # convert to wavelength array
    tem_wl = np.array(wavele)/10
    return tem_wl, data_tem


def fgsTransPro(dataPath):
    '''
    aligning: fgs vs template spectrum
    '''

    data_fgs = pd.read_csv(dataPath + '/trans_sim.csv')
    
    # merge with template spectrum
    temSpec=temSpecPro(dataPath)
    tem_wl=temSpec[0]
    df_wl = pd.DataFrame(tem_wl, columns=['wavelength'])
    df_wl['wavelength'] = df_wl['wavelength'].astype(float)
    data_fgs['wavelength'] = data_fgs['wavelength'].astype(float)
    data_merge = pd.merge(data_fgs, df_wl, how='outer', on='wavelength')
    data_merge.sort_values(by=['wavelength'], inplace=True)
    data_merge.interpolate(inplace=True)
    fgs_sys_spec = pd.merge(data_merge, pd.DataFrame(tem_wl, columns=['wavelength']), how='inner', on='wavelength')
    
    return fgs_sys_spec


def gaiaTransPro(dataPath):
    '''
    aligning: gaia vs template spectrum
    '''
    
    # read gaia G transmission data
    data = np.loadtxt(dataPath + '/GAIA_GAIA3.G.dat')
    df_G = pd.DataFrame(data)
    df_G.columns = ['wavelength','G']
    df_G['wavelength'] = (df_G['wavelength']/10).astype(int)

    # read gaia Gbp transmission data
    data = np.loadtxt(dataPath + '/GAIA_GAIA3.Gbp.dat')
    df_Gbp = pd.DataFrame(data)
    df_Gbp.columns = ['wavelength','Gbp']
    df_Gbp['wavelength'] = (df_Gbp['wavelength']/10).astype(int)

    # read gaia Grp transmission data
    data = np.loadtxt(dataPath + '/GAIA_GAIA3.Grp.dat')
    df_Grp = pd.DataFrame(data)
    df_Grp.columns = ['wavelength','Grp']
    df_Grp['wavelength'] = (df_Grp['wavelength']/10).astype(int)

    # merge gaia G, Gbp, Grp transmission data
    df_bp_rp = pd.merge(df_Gbp,df_Grp,how='outer',on='wavelength')
    df_bp_rp_g = pd.merge(df_bp_rp, df_G, how='outer',on='wavelength')

    # merge with template spectrum
    temSpec=temSpecPro(dataPath)
    tem_wl=temSpec[0]
    df_wl2 = pd.DataFrame(tem_wl, columns=['wavelength'])
    df_wl2['wavelength'] = df_wl2['wavelength'].astype(float)
    df_bp_rp_g['wavelength'] = df_bp_rp_g['wavelength'].astype(float)
    gaia_spec = pd.merge(df_wl2, df_bp_rp_g, how='outer', on='wavelength')
    gaia_spec.sort_values(by=['wavelength'], inplace=True)
    gaia_spec.interpolate(inplace=True)
    gaia_spec = pd.merge(gaia_spec, pd.DataFrame(tem_wl, columns=['wavelength']), how='inner', on='wavelength')

    return gaia_spec


def conv2colorIdx(dataPath, outputPath):
    '''
    Calculate synthetic color indices by integrating template spectra multiplied by filter transmission curves.
    '''

    # merge fgs and gaia transmission data
    fgs_sys_spec = fgsTransPro(dataPath)
    gaia_spec = gaiaTransPro(dataPath)
    res_spec = pd.merge(fgs_sys_spec, gaia_spec, how='inner', on='wavelength')
    res_spec_bp = res_spec[res_spec['wavelength'] <= 750]
    res_spec_rp = res_spec[res_spec['wavelength'] >= 610]

    # read template spectra data from lamostEigenStar.fits
    temSpec=temSpecPro(dataPath)
    data_tem=temSpec[1]

    # calculate synthetic color indices
    m_G = []
    BP_RP = []
    for i in range(data_tem.shape[0]):
        #G
        g_mean=np.sum(np.array(res_spec['G']) * data_tem[i]) / np.sum(np.array(res_spec['G']))
        #FGS
        fgs_mean = np.sum(np.array(res_spec['eff']) * data_tem[i]) / np.sum(np.array(res_spec['eff']))
        #BP
        bp_mean = np.sum(np.array(res_spec_bp['Gbp']) * data_tem[i][:res_spec_bp.index.values[-1]+1]) / np.sum(np.array(res_spec_bp['Gbp']))
        #RP
        rp_mean = np.sum(np.array(res_spec_rp['Grp']) * data_tem[i][res_spec_rp.index.values[0]:]) / np.sum(np.array(res_spec_rp['Grp']))
        g = -2.5*(np.log10(g_mean))
        fgs = -2.5*(np.log10(fgs_mean))
        bp = -2.5*(np.log10(bp_mean))
        rp = -2.5*(np.log10(rp_mean))
        y = fgs - g 
        x = bp - rp
        m_G.append(y)
        BP_RP.append(x)

    # create a DataFrame to store the color indices
    X = BP_RP
    Y = m_G
    df = pd.DataFrame()
    df['BP_RP'] = X
    df['m_G'] = Y
    df = df.sort_values(by=['BP_RP'])
    df.to_csv(outputPath + '/colorIdx.csv', index=False)
    return df


def insMagSim(dataPath, outputPath):
    '''
    Plot the synthetic color indices and the polynomial fit.
    '''

    # read the synthetic color indices
    df = conv2colorIdx(dataPath, outputPath)
    x = np.array(df['BP_RP']) # X = BP_RP
    y = np.array(df['m_G']) # Y = m_G
    
    # Fit a 4th-degree polynomial to the data
    coeff = np.polyfit(x, y, 4)
    yval = np.polyval(coeff, x)

    # Plot the data and the polynomial fit
    fig,ax = plt.subplots(figsize=(6,4))
    ax.scatter(x, y, s=10, label='sample_point')
    ax.plot(x, yval, c='r', lw=1, label='poly_fit')
    ax.text(-0.6, -0.2, '{:.5f}x^4 - {:.4f}x^3 + {:.4f}x^2 + {:.2f}x + {:.3f}'.format(coeff[0], np.abs(coeff[1]), coeff[2], coeff[3], coeff[4]),
            fontsize = 8, color = 'red')
    ax = line_set(ax, xlabel="BP-RP", ylabel="m-G", direction="in", legend=True, loc='best', size={'mz': 1.0, 'lz': 3.0, 'lbz': 14, 'tkz': 12}, frameon=True, fontfamily="Times New Roman", minor_tick_scale=0.6)

    plt.savefig(outputPath + '/colorIdx_fit.png', dpi=300, bbox_inches='tight')
    plt.show()

