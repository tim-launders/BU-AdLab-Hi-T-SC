# BU-AdLab-Hi-T-SC
Arduino/Python code to read in voltage and temperature data to measure the critical temperatures of superconducting materials.


Advanced Lab (AdLab) at BU (PY 581) provides students the opportunity to measure the critical temperature of high-temperature superconductoring samples of YBCO and BSCCO. An Arduino is used to read in temperature and voltage data digitally, from which the critical temperature can be computed. This repository is aimed for future students making these measurements. 

We recommend collecting data in the Arduino Serial Monitor and converting to a .txt file, then plotting in Python. The first and second columns of the Arduino readout are the voltage (in 0.1 mV) and a quantity linearly related to temperature (conversion in Python file). The Python file takes in the current passed through the sample, which gives resistance form Ohm's law. The error computation in the Python file uses reported manufacturer uncertainites and accounts for a reported 400 ms offset between temperature and voltage readouts. 
