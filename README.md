# Ncv and Zcv Calculator (Tkinter GUI)

This application calculates **Carrier Density** $N_{cv}$($cm^{-3}$) and **Depth** $Z_{cv}$ $(nm)$ from **$C(V)$** data files using a **Tkinter GUI** interface. It supports plotting and visualization of forward and backward capacitance sweeps to derive key parameters for High Electron Mobility Transistors (HEMTs) and similar semiconductor structures.

---

### **Features**  
- **Graphical User Interface (GUI):** Simple Tkinter-based interface for file selection and input.  
- **Multiple File Support:** Process multiple C(V) text files at different frequencies.  
- **Plotting:** Generates $N_{cv}$ vs $Z_{cv}$ plots with forward and backward sweeps on a log scale.  
- **Sheet Carrier Density Integration:** Automatically calculates sheet carrier density using:  
 $$\sigma_{cv} = \int N_{cv} \, dZ_{cv}$$ 

- **User Inputs:**  
   - Capacitor diameter (in µm).  
   - Relative permittivity $\varepsilon_r$.  
   - Expected interface depth (in nm) for visualization.  

---

### **Formulas Used**  
- **Carrier Density** $N_{cv}$:  
  $$N_{cv} = \frac{C^3}{\varepsilon_0 \varepsilon_r A^2 q} \cdot \frac{dV}{dC}$$ 

- **Depth** $Z_{cv}$:  
  $$Z_{cv} = \frac{\varepsilon_0 \varepsilon_r A}{C}$$ 

- **Sheet Carrier Density** $\sigma_{cv}$:  
  $$\sigma_{cv} = \int N_{cv} dZ_{cv}$$ 

Where:  
- $$\varepsilon_0 = 8.854 \times 10^{-12} \, F/m$$ (Permittivity of free space)  
- $$q = 1.602 \times 10^{-19} \, C$$ (Electron charge)  
- $A$ is the area of the capacitor  
  $$A =\pi\left(\frac{d}{2}\right)^2$$  
- $C$ is capacitance, and $\frac{dV}{dC}$ is the voltage derivative.  

---

### **Installation**  
1. **Clone the Repository**  
   
```
   git clone https://github.com/chkydebug/NcvZcvHEMT.git
   cd NcvZcvHEMT
```

2. **Install Dependencies**
   
```
   pip install -r requirements.txt
```

---

### **Running the Application**  
1. **GUI Mode (With Display)**
Run the following command:  

```
python sheetcarrierdensityvsdepthplotter.py
```
The GUI interface will launch for file selection and parameter input.  
### **Usage**
1. **Select C(V) Data Files**
   Click "Select C(V) Files" and choose the .txt files containing capacitance-voltage data.

2. **Input Parameters**
   - Enter **capacitor diameter** in µm.
   - Specify $\varepsilon_r$ (relative permittivity).
   - Provide the **expected interface depth** for visualization.

3. **Process and Plot**
   Click "Process and Plot" to generate $N_{cv}$ vs $Z_{cv}$ plots. The sheet carrier density will be displayed in the legend.

---

2. **CLI Mode (Headless Systems)**
In environments without display (e.g., servers, Codespaces), the application automatically switches to CLI mode.
Alternatively, you can explicitly invoke CLI mode by passing arguments.

**Usage:**

```
python sheetcarrierdensityvsdepthplotter.py \
--files C(V)_sample1_1kHz.txt C(V)_sample1_10kHz.txt \
--diameter 50 --epsilon 9 --interface 30
```
Sample CLI Input Code:  
Suppose you have the following .txt files:  
"C(V)_0_Ox2068_-15_0V_1kHz_-15,0V to 0,0V_1.txt"   
"C(V)_0_Ox2068_-15_0V_10kHz_-15,0V to 0,0V_1.txt"   
"C(V)_0_Ox2068_-15_0V_100kHz_-15,0V to 0,0V_1.txt"   
"C(V)_0_Ox2068_-15_0V_1000kHz_-15,0V to 0,0V_1.txt"  
You can process them using the CLI by running:  
```
python3 sheetcarrierdensityvsdepthplotter.py \
--files "C(V)_0_Ox2068_-15_0V_1kHz_-15,0V to 0,0V_1.txt" \  
       "C(V)_0_Ox2068_-15_0V_10kHz_-15,0V to 0,0V_1.txt" \  
       "C(V)_0_Ox2068_-15_0V_100kHz_-15,0V to 0,0V_1.txt" \  
       "C(V)_0_Ox2068_-15_0V_1000kHz_-15,0V to 0,0V_1.txt" \  
--diameter 750 --epsilon 9 --interface 30
```
**Parameters:**

**files**: List of .txt files containing C(V) measurement data.  
**diameter**: Capacitor diameter in micrometers (µm).  
**epsilon**: Relative permittivity (εr).  
**interface**: Expected interface depth (Z) in nanometers (nm).  
Output  
**Plots**: Saved as Ncv_vs_Zcv_Plots.png in the results folder.  
**Excel Results**: Saved in Ncv_Zcv_Results_<timestamp>.xlsx with data for each frequency in separate sheets.


### **Output**
- Plots showing $N_{cv}$ vs $Z_{cv}$ for forward and backward sweeps.
- Visualization of the interface depth marked by an orange vertical line.
- Calculated sheet carrier densities will appear in the legend of each plot.
---  
### **Reference Paper:**

The above formulas are derived from:  
*"Two-dimensional electron gases induced by spontaneous and piezoelectric polarization charges in N- and Ga-face AlGaN/GaN heterostructures"*  
by O. Ambacher, J. Smart, J. R. Shealy, et al. (Journal of Applied Physics, 1999).  
DOI: [10.1063/1.371866](http://dx.doi.org/10.1063/1.371866)

