import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

currs = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]    # mA

# Bin to desired delta time
scale = 3
binning=np.linspace(0, (550//scale)*scale, 550//scale+1, dtype=int)

d_curr = 0.001
v_rms = 0.003         # mV
v_scale = 10          # Converts input voltage reading to mV
dT = 0.01             # K

def R(V,I):
    return V/I

def dR(V,I,dV,dI):
    return np.sqrt((-R(V,I)*dI/I)**2 + (dV/I)**2)

def dRdT(Rs, Ts):
    derivative = []
    derivative.append((Rs[1]-Rs[0])/Ts[0])
    for i in range(1,len(Rs)-1):
        derivative.append((Rs[i+1]-Rs[i-1])/(Ts[i]+Ts[i-1]))
    derivative.append((Rs[-1]-Rs[-2])/Ts[-1])

    return np.array(derivative)

def delta_dRdT(Rs, Ts, delta_R):
    def prop(i, j):
        Ri = np.max((np.abs(Rs[i]), 1e-6))
        Rj = np.max((np.abs(Rs[j]), 1e-6))
        dR_tot = np.sqrt((delta_R[i]/Ri)**2 + (delta_R[j]/Rj)**2)
        if i == 0 or i == len(Rs)-1:
            dT_tot = dT / Ts[i]
        else:
            dT_tot = dT * np.sqrt(Ts[i]**(-2) + Ts[j]**(-2))
        return np.sqrt(dR_tot**2 + dT_tot**2)
    derivative = dRdT(Rs, Ts)
    delta = []
    delta.append(prop(0,1)*derivative[0])
    for i in range(1,len(Rs)-1):
        delta.append(prop(i-1,i+1)*derivative[i])
    delta.append(prop(-1,-2)*derivative[-1])
    return np.abs(np.array(delta))

def nearest_index(array, value):
    return np.abs(array - value).argmin()

fig, axs = plt.subplots(len(currs), 2, figsize=(15,17), sharey='col', dpi=500)
fig.subplots_adjust(wspace=0.4) 

total_max = 0

for i in range(len(currs)):
    curr = currs[i]
    filepath = f'Asher_Tim/feb27/data_{curr}_hi.txt'
    data = np.loadtxt(filepath, delimiter=',')

    voltage = data[:,0]
    for j in range(len(voltage)-4):
        # 400 ms delay in voltage readings
        voltage[j] = voltage[j+4]
    # Convert to A
    curr*=1e-3
    # Calculate temperature
    T = 2.45 * data[:,1] + 28.4
    
    # Bin to reduce resolution
    T = T[binning]
    voltage = voltage[binning]
    resistance = R(voltage, curr)
    d_res = dR(voltage, curr, v_rms, d_curr)
    derivative = dRdT(resistance, T)
    delta_der = delta_dRdT(resistance, T, d_res)
    
    # Calculate T_c
    i1 = nearest_index(T, 80)
    i2 = nearest_index(T, 90)
    dR_zero = derivative[i1:i2]
    dR_zero = resistance[i1:i2]
    dR_crit = np.mean(dR_zero) + 4*np.std(dR_zero)
    
    
    max_dRdT = np.max(derivative)

    crit_ind = 0
    for j in range(len(derivative)):
        dr = derivative[j]
        if dr > 0.1 * max_dRdT:
            crit_ind = j
            break
    T_crit = T[crit_ind]

    d_T_crit = np.abs(T_crit - np.max((T[crit_ind-1], T[crit_ind+1])))
    T_crit = round(T_crit, 1)
    d_T_crit = round(d_T_crit, 1)
    delta_der = np.zeros_like(delta_der)

    offset = 0.00005*1000
    if i == 0:
        total_max = np.max(derivative) * 1000

    if len(currs)==1:
        axs[0].errorbar(T, resistance, d_res, fmt='.', markersize=12, zorder=1, color=f'C{i}', label=f'{int(curr*1e3)} mA')
        axs[1].errorbar(T, 1000*derivative, delta_der, fmt='.', markersize=12, color=f'C{i}')
        axs[0].axvline(T_crit, color='black', linestyle='dashed')
        axs[1].axvline(T_crit, color='black', linestyle='dashed', label=rf'$T_c=$ ${T_crit}\pm{d_T_crit}$ K')
        axs[0].set_ylim(-0.05,1.1)
        axs[1].set_ylim(-0.00005,total_max+2*offset)
        axs[0].set_xlim(85,140)
        axs[1].set_xlim(85,140)
        axs[0].legend(loc='upper left', frameon=True, framealpha=1.0)
        axs[1].legend(loc='upper right', frameon=True, framealpha=1.0)
        axs[0].set_xlabel('T [K]')
        axs[1].set_xlabel('T [K]')
        axs[0].set_ylabel(r'R [m$\Omega$]')
        axs[1].set_ylabel(r'$\partial R/\partial T$ [m$\Omega$/K]')

    else:
        axs[i,0].errorbar(T, resistance, d_res, fmt='.', markersize=12, zorder=1, color=f'C{i}', label=f'{int(curr*1e3)} mA')
        axs[i,1].errorbar(T, 1000*derivative, delta_der, fmt='.', markersize=12, color=f'C{i}')
        axs[i,0].axvline(T_crit, color='black', linestyle='dashed')
        axs[i,1].axvline(T_crit, color='black', linestyle='dashed', label=rf'$T_c=$ {T_crit}$\pm${d_T_crit} K')
        axs[i,0].set_ylim(-0.05,1.1)
        axs[i,1].set_ylim(-offset,total_max+6.5*offset)
        axs[i,0].set_xlim(85,140)
        axs[i,1].set_xlim(85,140)
        axs[i,0].legend(loc='upper left', frameon=True, framealpha=1.0, handletextpad=-0.1)
        axs[i,1].legend(loc='upper right', handlelength=0, bbox_to_anchor=(1.03, 1.05))

        if i == len(currs)-1:
            axs[i,0].set_xlabel('T [K]')
            axs[i,1].set_xlabel('T [K]')
            axs[i,0].set_ylabel(r'R [m$\Omega$]', y=6*len(currs)/10)
            axs[i,1].set_ylabel(r'$\partial R/\partial T$ [$\mu\Omega$/K]', y=6*len(currs)/10)
        else:
            axs[i,0].set_xticklabels([])
            axs[i,1].set_xticklabels([])
            #axs[i,0].set_yticks([])
            #axs[i,1].set_yticks([])


plt.tight_layout()
plt.show()
